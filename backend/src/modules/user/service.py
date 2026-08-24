from typing import Any, cast

from crudauth import get_password_hash
from fastcrud import JoinConfig
from fastcrud.types import GetMultiResponseDict
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.logging import get_logger
from ..common.exceptions import PermissionDeniedError, TierNotFoundError, UserExistsError, UserNotFoundError, ValidationError
from ..rate_limit.models import RateLimit
from ..rate_limit.schemas import RateLimitRead
from ..tier.crud import crud_tiers
from ..tier.models import Tier
from ..tier.schemas import TierRead
from .crud import crud_users
from .enums import UserType
from .models import User
from .schemas import (
    User as UserSchema,
)
from .schemas import (
    UserAnonymize,
    UserCreate,
    UserCreateInternal,
    UserRead,
    UserTierUpdate,
    UserUpdate,
)

logger = get_logger()


class UserService:
    async def create(self, user: UserCreate, db: AsyncSession) -> dict[str, Any]:
        email_exists = await crud_users.exists(db=db, email=user.email)
        if email_exists:
            raise UserExistsError("Email already registered")

        user_internal_dict = user.model_dump()
        user_internal_dict["user_type"] = UserType.APPLICANT.value
        user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
        del user_internal_dict["password"]

        user_internal = UserCreateInternal(**user_internal_dict)
        created_user = await crud_users.create(db=db, object=user_internal, schema_to_select=UserRead)
        if not created_user:
            raise UserExistsError("Failed to create user")
        return created_user

    async def get_paginated(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> GetMultiResponseDict:
        if db is None:
            raise ValueError("Database session cannot be None")

        return await crud_users.get_multi(
            db=db,
            offset=skip,
            limit=limit,
            schema_to_select=UserRead,
            is_deleted=False,
        )

    async def get_active_and_inactive_by_email(self, email: str, db: AsyncSession) -> dict[str, Any]:
        user = await crud_users.get(db=db, schema_to_select=UserRead, email=email)
        if not user:
            raise UserNotFoundError(f"User with email '{email}' not found")
        return user

    async def get_by_email(self, email: str, db: AsyncSession) -> dict[str, Any]:
        user = await crud_users.get(
            db=db,
            schema_to_select=UserRead,
            email=email,
            is_deleted=False,
        )
        if not user:
            raise UserNotFoundError(f"User with email '{email}' not found")
        return user

    async def update(self, user_id: int, user_update: UserUpdate, db: AsyncSession) -> dict[str, Any]:
        existing_user = await crud_users.get(db=db, id=user_id, is_deleted=False)
        if not existing_user:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        update_data = user_update.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] != existing_user["email"]:
            email_exists = await crud_users.exists(db=db, email=update_data["email"])
            if email_exists:
                raise UserExistsError("Email already registered")

        updated_user = await crud_users.update(
            db=db, object=user_update, id=user_id, return_columns=list(UserSchema.model_fields.keys())
        )
        if not updated_user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return updated_user

    async def check_update_permission(self, requester_user: dict[str, Any], target_email: str) -> bool:
        if requester_user.get("is_superuser", False):
            return True

        return requester_user.get("email") == target_email

    async def verify_user_permission(
        self, requester_user: dict[str, Any], target_email: str, action_description: str = "perform this action"
    ) -> None:
        has_permission = await self.check_update_permission(requester_user, target_email)
        if not has_permission:
            raise PermissionDeniedError(f"You don't have permission to {action_description} on this user")

    async def delete(self, user_id: int, db: AsyncSession) -> None:
        try:
            await crud_users.delete(db=db, id=user_id)
        except NoResultFound:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        except MultipleResultsFound:
            raise ValidationError("Multiple users found with same ID")

    async def permanent_delete(self, user_id: int, db: AsyncSession) -> None:
        try:
            await crud_users.db_delete(db=db, id=user_id)
        except NoResultFound:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        except MultipleResultsFound:
            raise ValidationError("Multiple users found with same ID")

    async def anonymize_user(self, user_id: int, db: AsyncSession) -> None:
        try:
            existing_user = await crud_users.get(db=db, schema_to_select=UserRead, id=user_id)
            if not existing_user:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            logger.info(
                "User anonymization requested",
                extra={
                    "user_id": user_id,
                    "email": existing_user.get("email"),
                    "action": "user_anonymization_start",
                },
            )

            anonymize_data = UserAnonymize(
                name="[DELETED]",
                phone_number=f"090{user_id % 100_000_000:08d}",
                hashed_password="DELETED_INVALID_HASH",
                profile_image_url="https://deleted.com/deleted.jpg",
                tier_id=None,
                is_superuser=False,
                google_id=None,
                github_id=None,
                oauth_provider=None,
                email_verified=False,
                oauth_created_at=None,
                oauth_updated_at=None,
            )

            await crud_users.update(db=db, object=anonymize_data, commit=False, id=user_id)
            await crud_users.delete(db=db, id=user_id)

            anonymized_fields = list(anonymize_data.model_dump(exclude_unset=True).keys())
            logger.info(
                "User anonymization completed",
                extra={
                    "user_id": user_id,
                    "retained_data": ["email", "created_at", "updated_at", "id"],
                    "anonymized_fields": anonymized_fields,
                    "action": "user_anonymization_complete",
                    "foreign_keys_preserved": True,
                },
            )

        except NoResultFound:
            logger.warning(
                "User anonymization failed - user not found",
                extra={"user_id": user_id, "action": "user_anonymization_failed", "reason": "user_not_found"},
            )
            raise UserNotFoundError(f"User with ID {user_id} not found")

    async def update_tier(self, user_id: int, tier_update: UserTierUpdate, db: AsyncSession) -> dict[str, Any]:
        existing_user = await crud_users.get(db=db, id=user_id, is_deleted=False)
        if not existing_user:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        tier_exists = await crud_tiers.exists(db=db, id=tier_update.tier_id)
        if not tier_exists:
            raise TierNotFoundError(f"Tier with ID {tier_update.tier_id} not found")

        updated_user = await crud_users.update(
            db=db, object=tier_update, id=user_id, return_columns=list(UserSchema.model_fields.keys())
        )
        if not updated_user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return updated_user

    async def get_rate_limits(self, user_id: int, db: AsyncSession) -> dict[str, Any]:
        user = await crud_users.get(db=db, id=user_id, is_deleted=False, schema_to_select=UserRead)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        if user["tier_id"] is None:
            user["rate_limits"] = []
            return user

        joins_config = [
            JoinConfig(
                model=Tier,
                join_on=User.tier_id == Tier.id,
                join_prefix="tier_",
                schema_to_select=TierRead,
                join_type="left",
            ),
            JoinConfig(
                model=RateLimit,
                join_on=Tier.id == RateLimit.tier_id,
                join_prefix="rate_limits_",
                schema_to_select=RateLimitRead,
                join_type="left",
                relationship_type="one-to-many",
            ),
        ]

        result = await crud_users.get_joined(
            db=db, schema_to_select=UserRead, joins_config=joins_config, nest_joins=True, id=user_id
        )

        if not result:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        return result

    async def get_user_with_tier(self, user_id: int, db: AsyncSession) -> dict[str, Any]:
        user_dict = await crud_users.get(db=db, id=user_id, is_deleted=False, schema_to_select=UserRead)
        if not user_dict:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        if user_dict.get("tier_id") is None:
            user_dict["tier"] = None
            return user_dict

        tier_exists = await crud_tiers.exists(db=db, id=user_dict["tier_id"])
        if not tier_exists:
            user_dict["tier"] = None
            return user_dict

        result = await crud_users.get_joined(
            db=db,
            join_model=Tier,
            join_prefix="tier_",
            schema_to_select=UserRead,
            join_schema_to_select=TierRead,
            id=user_id,
            nest_joins=True,
        )

        return cast(dict[str, Any], result)
