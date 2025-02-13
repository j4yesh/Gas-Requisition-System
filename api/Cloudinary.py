import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv
import os
load_dotenv()    


cloudinary.config( 
    cloud_name = os.getenv('cloud_name'), 
    api_key_cloudinary = os.getenv('api_key_cloudinary'),
    api_secret = os.getenv('api_secret'),
    secure=True
)

def upload_file(file, public_id=None, folder=None):
    try:
        upload_options = {}

        if public_id:
            upload_options["public_id"] = public_id
        if folder:
            upload_options["folder"] = folder

        upload_result = cloudinary.uploader.upload(file, **upload_options)
        return upload_result["secure_url"]

    except Exception as e:
        return f"Upload failed: {str(e)}"