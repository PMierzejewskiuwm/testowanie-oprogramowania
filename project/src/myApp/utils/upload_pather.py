import os

def dynamic_image_upload_pather(instance, image_name):
    return os.path.join(instance.__class__.__name__.lower() + 's', image_name)
