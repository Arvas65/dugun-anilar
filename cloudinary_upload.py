import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name='djjy2cqpc',
    api_key='336236266214479',
    api_secret='pPeUaKJuGtNuWh2VfT0Zon21nSQ'
)

def upload_to_cloudinary(local_path, resource_type="auto"):
    result = cloudinary.uploader.upload(local_path, resource_type=resource_type)
    return result['secure_url']
