from rembg import remove
from PIL import Image
import io

def remove_background(pil_img):
    """
    Remove background from a Pillow image using rembg.
    Args:
        pil_img: Pillow Image
    Returns:
        Pillow Image with transparent background
    """
    # Convert PIL image to bytes
    img_byte_arr = io.BytesIO()
    pil_img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Remove background
    output = remove(img_byte_arr)
    
    # Convert back to PIL Image
    return Image.open(io.BytesIO(output)) 