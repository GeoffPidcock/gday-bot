"""
Modal deployment wrapper for the G'Day Bot Discord bot
"""
import os
import sys
import modal

# Add the parent directory to sys.path to allow imports from the discord_bot package
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Get the project root directory
BASE_DIR = parent_dir
DISCORD_BOT_DIR = os.path.join(BASE_DIR, "discord_bot")

# Create a Modal image with required dependencies
image = modal.Image.debian_slim().pip_install(
    "discord.py",
    "python-dotenv",
    "aiohttp",
)

# Add only the specific files we need from discord_bot
for py_file in ["__init__.py", "bot.py", "commands.py", "logger.py"]:
    file_path = os.path.join(DISCORD_BOT_DIR, py_file)
    if os.path.exists(file_path):
        image = image.add_local_file(file_path, f"/app/discord_bot/{py_file}")

# Define the Modal app
app = modal.App("gday-discord-bot")

@app.function(
    image=image,
    concurrency_limit=1,  # Only one Discord bot instance
    secrets=[
        modal.Secret.from_name("discord-bot-secret"),  # Secret for Discord token
    ]
)
def run_discord_bot():
    """
    Run the Discord bot
    """
    # Create necessary directories
    os.makedirs("/app/discord_bot", exist_ok=True)
    os.makedirs("/root/logs", exist_ok=True)
    
    import sys
    sys.path.append("/app")  # Add /app to Python path
    
    # Set environment variables
    os.environ["LOG_DIR"] = "/root/logs"
    # IMPORTANT: Hard-code the RAG API URL to ensure it's correct
    os.environ["RAG_API_URL"] = "https://geoffpidcock--gday-rag-api-serve.modal.run"
    
    print(f"Using RAG API URL: {os.environ['RAG_API_URL']}")
    
    try:
        print("Starting Discord bot...")
        import sys
        print(f"Python version: {sys.version}")
        print(f"Python path: {sys.path}")
        
        # Existing bot initialization
        from discord_bot.bot import run_bot
        
        print("About to run bot...")
        run_bot()
    except Exception as e:
        print(f"Critical error starting bot: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.function(
    image=image,
    concurrency_limit=1,
    secrets=[
        modal.Secret.from_name("discord-bot-secret"),  # Same secret for access to logs
    ],
    schedule=modal.Cron("0 0 * * *")  # Run daily at midnight
)
def backup_logs():
    """
    Create a simple log of the backup job
    """
    import datetime
    
    # Log the backup attempt
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"[{timestamp}] Log backup would normally run here.")
    print("Note: In this simplified version, logs are stored in the container.")
    print("For persistent logs, consider using Modal's web UI to view logs or implement")
    print("an external storage solution like AWS S3, Google Cloud Storage, etc.")
    
    return f"Backup job completed at {timestamp}"

@app.local_entrypoint()
def main():
    """
    Local development entry point
    """
    # Create local logs directory
    local_log_dir = "./logs"
    os.makedirs(local_log_dir, exist_ok=True)
    os.environ["LOG_DIR"] = local_log_dir
    
    # IMPORTANT: Hard-code the RAG API URL for testing
    os.environ["RAG_API_URL"] = "https://geoffpidcock--gday-rag-api-serve.modal.run"
    
    print(f"Using RAG API URL: {os.environ['RAG_API_URL']}")
    print("Starting Discord bot for local development...")
    run_discord_bot.remote()