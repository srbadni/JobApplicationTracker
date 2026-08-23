from collections.abc import AsyncIterator
from typing import Any, NoReturn
from urllib.parse import quote

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile, status

from ...infrastructure.dependencies import AsyncSessionDep, CurrentUserDep
from ..common.exceptions import PermissionDeniedError, ResourceNotFoundError
from ..common.utils.error_handler import handle_exception
from .dependencies import MediaServiceDep
from .enums import MediaCategory
from .schemas import MediaCreate, MediaRead

router = APIRouter(tags=["Media"])


def _user_access(current_user: dict[str, Any]) -> tuple[int, bool]:
    return int(current_user["id"]), bool(current_user.get("is_superuser", False))


async def _file_chunks(file: UploadFile, chunk_size: int = 1024 * 1024) -> AsyncIterator[bytes]:
    while chunk := await file.read(chunk_size):
        yield chunk


def _raise_media_http_error(error: Exception) -> NoReturn:
    if isinstance(error, ResourceNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, PermissionDeniedError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    http_exception = handle_exception(error)
    if http_exception:
        raise http_exception
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.post("/", response_model=MediaRead, status_code=status.HTTP_201_CREATED)
async def upload_media(
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    media_service: MediaServiceDep,
    category: MediaCategory = Form(...),
    file: UploadFile = File(...),
) -> MediaRead:
    """Upload a private file for the authenticated user."""
    metadata = MediaCreate(
        category=category,
        original_name=file.filename or "unnamed",
        mime_type=file.content_type or "application/octet-stream",
    )
    try:
        media = await media_service.upload(db, metadata, _file_chunks(file), uploaded_by_id=int(current_user["id"]))
        return MediaRead.model_validate(media)
    except Exception as error:
        _raise_media_http_error(error)


@router.get("/{media_id}", response_model=MediaRead)
async def get_media(
    media_id: int,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    media_service: MediaServiceDep,
) -> MediaRead:
    """Return metadata to the uploader or a superuser."""
    user_id, is_superuser = _user_access(current_user)
    try:
        media = await media_service.get(db, media_id, user_id, is_superuser)
        return MediaRead.model_validate(media)
    except Exception as error:
        _raise_media_http_error(error)


@router.get("/{media_id}/download")
async def download_media(
    media_id: int,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    media_service: MediaServiceDep,
) -> Response:
    """Download private content as the uploader or a superuser."""
    user_id, is_superuser = _user_access(current_user)
    try:
        media, content = await media_service.download(db, media_id, user_id, is_superuser)
        encoded_name = quote(media.original_name, safe="")
        return Response(
            content=content,
            media_type=media.mime_type,
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}"},
        )
    except Exception as error:
        _raise_media_http_error(error)


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: int,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    media_service: MediaServiceDep,
) -> Response:
    """Delete private media as the uploader or a superuser."""
    user_id, is_superuser = _user_access(current_user)
    try:
        await media_service.delete(db, media_id, user_id, is_superuser)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as error:
        _raise_media_http_error(error)
