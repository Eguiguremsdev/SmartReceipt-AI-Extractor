import json
import logging
from openai import OpenAI
from config import Config

from typing import Optional

logger = logging.getLogger(__name__)

class ReceiptProcessor:
    """Processor to interact with OpenAI Vision API and extract data."""

    def __init__(self):
        Config.validate()
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def extract_data(self, base64_image: str) -> Optional[dict]:
        """
        Sends the image to GPT-4o to extract receipt/invoice data.
        Returns a dictionary with the extracted fields.
        """
        prompt = '''
        You are an expert OCR AI specialized in accounting and finance. 
        Extract the following information from the provided receipt or invoice image.
        If a field is not found, use null.
        Return the result STRICTLY as a JSON object with no markdown formatting or extra text.
        
        Fields to extract:
        - date: The date of the transaction (YYYY-MM-DD format if possible).
        - vendor_name: The name of the merchant or vendor.
        - category: Categorize the expense (e.g., Tax, Travel, Food, Office Supplies, Software, etc.).
        - subtotal: The total amount before tax (as a float).
        - tax: The tax amount (as a float).
        - total: The final total amount paid (as a float).
        - currency: The currency code (e.g., USD, EUR, GBP).

        Ensure that the values for subtotal, tax, and total are numeric.
        '''

        messages = [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]

        try:
            logger.info("Sending image to OpenAI Vision API...")
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000,
                temperature=0.0,
                response_format={ "type": "json_object" }
            )

            result_text = response.choices[0].message.content
            logger.info("Received response from OpenAI API.")
            
            data = json.loads(result_text)
            validated_data = self._validate_and_clean(data)
            return validated_data

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return None

    def _validate_and_clean(self, data: dict) -> dict:
        """
        Validates the extracted numeric data.
        Verifies if Total == Subtotal + Tax.
        """
        # Ensure numeric fields are floats
        for field in ['subtotal', 'tax', 'total']:
            val = data.get(field)
            if val is not None:
                try:
                    data[field] = float(val)
                except ValueError:
                    logger.warning(f"Could not convert {field} value '{val}' to float. Setting to 0.0")
                    data[field] = 0.0
            else:
                 data[field] = 0.0

        subtotal = data['subtotal']
        tax = data['tax']
        total = data['total']

        # Validation Logic
        validation_passed = abs(total - (subtotal + tax)) < 0.05

        data['validation_passed'] = validation_passed
        if not validation_passed:
            logger.warning(f"Validation failed: Total ({total}) != Subtotal ({subtotal}) + Tax ({tax})")
        else:
            logger.info("Validation passed: Total matches Subtotal + Tax.")

        return data
