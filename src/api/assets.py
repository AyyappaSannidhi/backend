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

        # get all s3 folder items data
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

        if "Contents" not in response:
            return {"images": [], "total": 0, "total_pages": 0, "next_page": None}
        
        image_keys = [content["Key"] for content in response["Contents"]]
        image_keys.pop(0) # popping first element as it is like meta data

        total_images = len(image_keys)
        total_pages = (total_images + limit_per_page - 1) // limit_per_page  # Calculate total pages
        paginated_keys = image_keys[start_index:start_index + limit_per_page]

        # Generating presigned URLs
        signed_urls = []
        for key in paginated_keys:
            signed_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": key},
                ExpiresIn=1200
            )
            signed_urls.append(signed_url)

        # checking if there i a next page
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
    