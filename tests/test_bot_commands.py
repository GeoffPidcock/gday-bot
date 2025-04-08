# test_bot_commands.py
import os
import discord
from discord.ext import commands
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Get Discord token and API URL
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
RAG_API_URL = "https://geoffpidcock--gday-rag-api-serve.modal.run"

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")
    
    # Test API connection
    print("Testing API connection...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{RAG_API_URL}/health") as response:
                print(f"API health check: {response.status} - {await response.text()}")

            # Initialize the database
            print("\nInitializing the database...")
            async with session.post(f"{RAG_API_URL}/init") as response:
                if response.status == 201:
                    print(f"Database initialization successful: {await response.text()}")
                else:
                    print(f"Database initialization failed: {response.status} - {await response.text()}")
            
            # Wait a moment for initialization to complete
            await asyncio.sleep(2)

            # Test a query
            payload = {"query": "g'day", "max_results": 1, "threshold": 0.5}
            async with session.post(f"{RAG_API_URL}/query", json=payload) as response:
                result = await response.json()
                print(f"API query test: {response.status}")
                print(f"Query result: {result}")
        except Exception as e:
            print(f"API test failed: {str(e)}")
    
    # Exit after tests
    await bot.close()

# Run the bot
bot.run(DISCORD_TOKEN)