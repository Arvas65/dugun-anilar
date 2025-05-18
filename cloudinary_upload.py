import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

def upload_to_cloudinary(local_path, resource_type="auto"):
    result = cloudinary.uploader.upload(local_path, resource_type=resource_type)
    return result['secure_url']