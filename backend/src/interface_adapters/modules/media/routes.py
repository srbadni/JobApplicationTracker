"""Authenticated media upload and download endpoints."""

import re
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile, status
from starlette.responses import StreamingResponse

from ....frameworks.dependencies import AsyncSessionDep, CurrentUserDep, CSRFTokenHeaderDep
from .dependencies import MediaServiceDep
from .enums import MediaCategory
from .exceptions import MediaAccessDeniedError, MediaNotFoundError, MediaStorageError, MediaValidationError
from .schemas import MediaCategoryInfo, MediaResponse

router = APIRouter(tags=["Media"])


@router.get("/categories", response_model=list[MediaCategoryInfo])
async def get_media_categories(service: MediaServiceDep) -> list[MediaCategoryInfo]:
    """List accepted categories, extensions, and maximum sizes."""
    return service.get_categories()


@router.post("", response_model=MediaResponse, status_code=status.HTTP_201_CREATED)
async def upload_media(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    service: MediaServiceDep,
    category: Annotated[MediaCategory, Form()],
    file: Annotated[UploadFile, File()],
    csrf_token_header: CSRFTokenHeaderDep = None,
) -> MediaResponse:
    """Upload one private file; resume uploads are attached to ApplicantProfile."""
    try:
        media = await service.upload(
            db=db,
            current_user=current_user,
            category=category,
            upload=file,
        )
        return MediaResponse.model_validate(media)
    except MediaValidationError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error
    except MediaAccessDeniedError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except MediaStorageError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.get("/{media_id}", response_class=StreamingResponse)
async def download_media(
    media_id: int,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    service: MediaServiceDep,
) -> StreamingResponse:
    """Download a private file owned by the current user."""
    try:
        download = await service.download(db=db, current_user=current_user, media_id=media_id)
    except MediaNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found") from error
    except MediaAccessDeniedError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except MediaStorageError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error

    return StreamingResponse(
        download.stream,
        media_type=download.mime_type,
        headers={
            "Content-Disposition": _content_disposition(download.filename),
            "Content-Length": str(download.size_bytes),
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: int,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    service: MediaServiceDep,
) -> Response:
    """Delete a private file owned by the current user."""
    try:
        await service.delete(db=db, current_user=current_user, media_id=media_id)
    except MediaNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found") from error
    except MediaAccessDeniedError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except MediaStorageError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _content_disposition(filename: str) -> str:
    ascii_fallback = re.sub(r"[^A-Za-z0-9._-]", "_", filename) or "download"
    encoded_filename = quote(filename, safe="")
    return f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{encoded_filename}"
