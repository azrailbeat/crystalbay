#!/usr/bin/env python3
import os
import logging
from telegram_bot import main

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    
    # Check if required environment variables are set
    required_vars = ["TELEGRAM_BOT_TOKEN", "SAMO_OAUTH_TOKEN", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in the .env file")
        exit(1)
    
    logger.info("Starting Crystal Bay Travel Telegram Bot...")
    main()