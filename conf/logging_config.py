import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def setup_logging():
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Enable logging
    log_handler = TimedRotatingFileHandler(
        filename=f"telegram_bot_{current_date}.log",
        when="midnight",
        interval=1,
        backupCount=7
    )
    log_handler.suffix = "%Y-%m-%d"
    log_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[log_handler]
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger("telegram_bot")
    return logger

# Initialize the logger once
logger = setup_logging()