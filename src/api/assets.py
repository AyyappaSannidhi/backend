from fastapi import APIRouter, Depends, status

from src.common.dependencies import get_s3_client
from src.common.methods import internal_server_error
from src.core.config import Config
from botocore.exceptions import ClientError
from src.core.logging import logger


assets_router = APIRouter()

@assets_router.get("/picture_gallery", status_code=status.HTTP_200_OK)
def get_picture_gallery(page: int = 1, size: int = 20, s3=Depends(get_s3_client)):
    try:
        bucket_name = Config.AWS_S3_BUCKET_NAME
        folder_prefix = "pictures/"
        limit_per_page = size  # Use the provided size for pagination
        
        # Calculate the starting index for pagination
        start_index = (page - 1) * limit_per_page

        # Get all S3 folder items data
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

        if "Contents" not in response:
            return {"images": [], "total": 0, "total_pages": 0, "next_page": None}

        # Get all objects excluding the first one if it is metadata
        image_objects = response["Contents"]
        image_objects.pop(0)  # Remove metadata object if needed

        # Sort objects by `LastModified` in descending order (newest first)
        sorted_objects = sorted(image_objects, key=lambda obj: obj["LastModified"], reverse=True)

        # Extract keys for pagination
        total_images = len(sorted_objects)
        total_pages = (total_images + limit_per_page - 1) // limit_per_page  # Calculate total pages
        paginated_objects = sorted_objects[start_index:start_index + limit_per_page]

        # Generate presigned URLs for paginated objects
        signed_urls = [
            s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": obj["Key"]},
                ExpiresIn=1200
            )
            for obj in paginated_objects
        ]

        # Check if there is a next page
        next_page = page + 1 if page < total_pages else None

        return {
            "images": signed_urls,
            "total": total_images,
            "total_pages": total_pages,
            "next_page": next_page
        }

    except ClientError as e:
        logger.info(f"An error occurred: {e}")
        return internal_server_error()
    
@assets_router.get("/carousel", status_code=status.HTTP_200_OK)
def get_carousel(s3=Depends(get_s3_client)):
    try:
        bucket_name = Config.AWS_S3_BUCKET_NAME
        folder_prefix = "carousel/"
        
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

        # Check if there are objects in the folder
        if "Contents" not in response:
            return {"images": []}

        # Get all objects excluding the first one if it is metadata
        image_objects = response["Contents"]
        image_objects.pop(0)  # Remove metadata object if needed

        # Sort objects by `LastModified` in descending order (newest first)
        sorted_objects = sorted(image_objects, key=lambda obj: obj["LastModified"], reverse=True)

        # Generate signed URLs for the sorted objects
        signed_urls = [
            s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": obj["Key"]},
                ExpiresIn=1200
            )
            for obj in sorted_objects
        ]

        return {"images": signed_urls}

    except ClientError as e:
        logger.info(f"An error occurred: {e}")
        return internal_server_error()