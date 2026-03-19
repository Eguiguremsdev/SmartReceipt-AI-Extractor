import os
import shutil
import base64
from io import BytesIO
import logging
from PIL import Image
from pdf2image import convert_from_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def encode_image(image_path: str, max_size=(1024, 1024)):
    """
    Reads an image, optionally resizes it to save tokens, and returns a base64 encoded string.
    """
    try:
        with Image.open(image_path) as img:
            # Resize image if it's too large
            if img.width > max_size[0] or img.height > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {img.size}")
            
            # Convert to RGB if necessary (e.g. if it's RGBA/PNG)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
                
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image {image_path}: {e}")
        return None

def process_pdf(pdf_path: str):
    """
    Converts a PDF to a list of PIL Images (one per page).
    Requires poppler installed on the system.
    """
    try:
        images = convert_from_path(pdf_path)
        logger.info(f"Extracted {len(images)} pages from PDF {pdf_path}")
        return images
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {e}")
        return []

def move_file(source_path: str, dest_dir: str):
    """
    Moves a file to the destination directory.
    """
    try:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        filename = os.path.basename(source_path)
        dest_path = os.path.join(dest_dir, filename)
        
        # Handle duplicate filenames
        count = 1
        while os.path.exists(dest_path):
            name, ext = os.path.splitext(filename)
            dest_path = os.path.join(dest_dir, f"{name}_{count}{ext}")
            count += 1
            
        shutil.move(source_path, dest_path)
        logger.info(f"Moved {source_path} to {dest_path}")
        return dest_path
    except Exception as e:
        logger.error(f"Error moving file {source_path}: {e}")
        return None
