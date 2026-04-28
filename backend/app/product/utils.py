from io import BytesIO
from pathlib import Path
from uuid import uuid4

from decouple import config
from fastapi import UploadFile, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from minio import Minio
from slugify import slugify  # это теперь python-slugify

MINIO_ENDPOINT = config("MINIO_ENDPOINT")
MINIO_ROOT_USER = config("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = config("MINIO_ROOT_PASSWORD")
MINIO_BUCKET_NAME = config("MINIO_BUCKET_NAME")
MINIO_PUBLIC_URL = config("MINIO_PUBLIC_URL").rstrip("/")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False,
)


def _ensure_bucket() -> None:
    if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
        minio_client.make_bucket(MINIO_BUCKET_NAME)


def _upload_to_minio(
    object_name: str, data: BytesIO, length: int, content_type: str | None
) -> None:
    _ensure_bucket()
    minio_client.put_object(
        bucket_name=MINIO_BUCKET_NAME,
        object_name=object_name,
        data=data,
        length=length,
        content_type=content_type or "application/octet-stream",
    )


def generate_slug(text: str) -> str:
    """Генерирует slug из названия товара"""
    if not text or not isinstance(text, str):
        return ""

    return slugify(text.strip(), lowercase=True, separator="-")


async def save_upload_file(upload_file: UploadFile | None, sub_dir: str = "images"):
    if not upload_file or not upload_file.filename:
        return None

    try:
        ext = Path(upload_file.filename).suffix.lower() or ".jpg"
        filename = f"{uuid4().hex}{ext}"
        object_name = f"{sub_dir}/{filename}"

        content = await upload_file.read()
        if len(content) == 0:
            raise ValueError("Empty file")

        data = BytesIO(content)

        await run_in_threadpool(
            _upload_to_minio,
            object_name,
            data,
            len(content),
            upload_file.content_type,
        )

        return f"{MINIO_PUBLIC_URL}/{MINIO_BUCKET_NAME}/{object_name}"

    except Exception as e:
        print(f"Image upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}",
        )
