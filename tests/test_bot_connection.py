# test_bot_init.py
# not possible in jupyter
import os
import discord
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Get Discord token from environment
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not found in environment variables")

# Create bot instance with intents
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} has successfully connected to Discord!")
    print(f"Bot ID: {bot.user.id}")
    print("Bot is in the following guilds:")
    for guild in bot.guilds:
        print(f"- {guild.name} (id: {guild.id})")
    await bot.close()  # Close the connection after initialization

# Run the bot
print("Starting bot initialization test...")
bot.run(DISCORD_TOKEN)