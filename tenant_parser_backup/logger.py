import logging

logger = logging.getLogger("tenant_parser")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    file_handler = logging.FileHandler("database1.log")
    formatter = logging.Formatter("%(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
