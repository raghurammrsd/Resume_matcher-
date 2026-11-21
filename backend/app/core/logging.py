import logging
import re
import sys

# PII masking patterns
EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
PHONE_PATTERN = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')

class PIIMaskingFormatter(logging.Formatter):
    def format(self, record):
        orig_msg = super().format(record)
        # Mask emails
        masked = EMAIL_PATTERN.sub('[EMAIL_REDACTED]', orig_msg)
        # Mask phone numbers
        masked = PHONE_PATTERN.sub('[PHONE_REDACTED]', masked)
        return masked

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = PIIMaskingFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = get_logger("talentmatch")
