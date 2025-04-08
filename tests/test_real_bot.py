# test_real_bot.py
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the parent directory to sys.path to allow imports from discord_bot
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from discord_bot.bot import run_bot

load_dotenv()

# Set environment variables
os.environ["LOG_DIR"] = "./logs"
os.environ["RAG_API_URL"] = "https://geoffpidcock--gday-rag-api-serve.modal.run"

# Create logs directory if it doesn't exist
os.makedirs(os.environ["LOG_DIR"], exist_ok=True)

# Run the bot for testing
if __name__ == "__main__":
    print("Starting Discord bot for testing...")
    print("The bot will run for 2 minutes and then exit.")
    print("Send a message mentioning the bot or using the !gday command to test.")
    
    # Run the bot in a separate thread
    import threading
    import time
    
    # Start the bot
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Wait for 2 minutes then exit
    time.sleep(120)
    print("Test complete. Exiting...")