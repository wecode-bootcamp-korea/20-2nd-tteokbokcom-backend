import boto3, uuid, io, os
from PIL         import Image

from django.conf import settings

class S3FileUtils:
    s3 = boto3.resource(
        's3',
        aws_access_key_id     = settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
    )
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

    @staticmethod
    def generate_filename(**kwargs):
        filename = {}

        for k, v in kwargs.items():
            file_name   = uuid.uuid1()
            filename[k] = file_name

        return filename

    @staticmethod
    def resize_image(**kwargs):
        STANDARD_WIDTH_SIZE   = 1024
        STANDARD_HEIGHT_SIZE  = 768
        IMAGE_RATIO           = 1.33

        resized_images = {}

        for k, v in kwargs.items():
            with Image.open(v) as opened_image:
                width_size  = opened_image.size[0]
                height_size = opened_image.size[1]

                if width_size / height_size < IMAGE_RATIO:
                    size = (STANDARD_WIDTH_SIZE, int(opened_image.size[1] * (STANDARD_WIDTH_SIZE / opened_image.size[0])))
                else:
                    size = (int(opened_image.size[0] * (STANDARD_HEIGHT_SIZE / opened_image.size[1])), STANDARD_HEIGHT_SIZE)

                resized_image = opened_image.resize(size)
                image_io      = io.BytesIO()
                resized_image.save(image_io, "JPEG")
                image_io.seek(0)
                resized_images[k] = image_io

        return resized_images

    @classmethod
    def file_upload(cls, folder_name, filename, **kwargs):
        file_path = f'{folder_name}/%s'

        for k, v in kwargs.items():
            cls.bucket.put_object(
                Key  = file_path % filename[k],
                Body = v,
                ContentType='image/jpeg'
            )

    @classmethod
    def file_delete(cls, folder_name, file_url):
        filename = file_url.split('/')[-1]
        file_path = f'{folder_name}/{filename}'
        cls.bucket.delete_objects(
            Delete={
                'Objects' : [
                    {'Key': file_path}
                ]
            }
        )