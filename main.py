import os
import time
import logging
from config import Config
from processor import ReceiptProcessor
from exporter import Exporter
from utils import encode_image, process_pdf, move_file

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def process_file(filepath: str, processor: ReceiptProcessor, exporter: Exporter):
    """Processes a single file (image or PDF)."""
    filename = os.path.basename(filepath)
    logger.info(f"Processing file: {filename}")
    
    encoded_images = []
    
    # Handle PDF
    if filepath.lower().endswith('.pdf'):
        logger.info("PDF detected. Converting to images...")
        images = process_pdf(filepath)
        if not images:
            exporter.log_error(filename, "Failed to convert PDF to images (Is poppler installed?).")
            return False
            
        for i, img in enumerate(images):
            # Save temp image to encode it
            temp_path = os.path.join(Config.INPUT_DIR, f"temp_{i}_{filename}.jpg")
            img.save(temp_path, "JPEG")
            encoded = encode_image(temp_path)
            if encoded:
                encoded_images.append(encoded)
            os.remove(temp_path) # Clean up temp file
    else:
        # Handle regular image
        encoded = encode_image(filepath)
        if encoded:
            encoded_images.append(encoded)

    if not encoded_images:
        exporter.log_error(filename, "Failed to encode image(s).")
        return False

    # Process each page/image
    success = True
    for idx, base64_img in enumerate(encoded_images):
        logger.info(f"Extracting data from page/image {idx + 1}...")
        data = processor.extract_data(base64_img)
        
        if data:
            logger.info(f"Data extracted successfully for {filename} (Page {idx + 1})")
            exporter.export_all(f"{filename}_page_{idx+1}" if len(encoded_images) > 1 else filename, data)
        else:
            exporter.log_error(filename, f"Extraction failed for page {idx + 1}")
            success = False

    return success

def main():
    logger.info("Starting SmartReceipt-AI-Extractor...")
    
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
        return

    processor = ReceiptProcessor()
    exporter = Exporter()

    logger.info(f"Monitoring folder: {Config.INPUT_DIR}")
    
    while True:
        try:
            files = [f for f in os.listdir(Config.INPUT_DIR) if os.path.isfile(os.path.join(Config.INPUT_DIR, f))]
            
            # Filter valid extensions
            valid_exts = ('.jpg', '.jpeg', '.png', '.pdf')
            filesToProcess = [f for f in files if f.lower().endswith(valid_exts)]
            
            for file in filesToProcess:
                filepath = os.path.join(Config.INPUT_DIR, file)
                
                success = process_file(filepath, processor, exporter)
                
                if success:
                    move_file(filepath, Config.PROCESSED_DIR)
                else:
                    logger.warning(f"File {file} processed with errors. Kept in input folder.")
                    
            # Wait before checking again (e.g. 10 seconds)
            time.sleep(10)
            
        except KeyboardInterrupt:
            logger.info("Application stopped by user.")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
