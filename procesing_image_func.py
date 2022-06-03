from PIL import Image

def resize_image(save_image):
        try:
            image = Image.open(save_image)
            return image.resize((224,224), Image.ANTIALIAS)
        except Exception:
            pass
