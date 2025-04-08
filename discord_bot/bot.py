"""
Discord bot implementation for G'Day Bot
"""
import os
import asyncio
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp
import json
from typing import Dict, List, Any

from .logger import log_interaction, log_error
from .commands import setup_commands

# Load environment variables
load_dotenv()

# Get Discord token from environment
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not found in environment variables")

# Get RAG API URL from environment
RAG_API_URL = os.environ.get("RAG_API_URL", "https://geoffpidcock--gday-rag-api-serve.modal.run")

# Create bot instance with message content intents
intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content
# Only enable other privileged intents if you've enabled them in the portal
# intents.members = True  # Enable only if needed and enabled in portal
# intents.presences = True  # Enable only if needed and enabled in portal


bot = commands.Bot(command_prefix="!", intents=intents)

# Event: Bot is ready
@bot.event
async def on_ready():
    """
    Called when the bot has connected to Discord
    """
    print(f"{bot.user.name} has connected to Discord!")
    
    # Setup custom status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name="for mentions, mate!"
        )
    )
    
    # Register slash commands
    await setup_commands(bot)
    print("Slash commands registered")
    
    # Initialize the RAG database if needed
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{RAG_API_URL}/init") as response:
                if response.status == 201:
                    result = await response.json()
                    print(f"RAG database initialized: {result.get('message')}")
                else:
                    print(f"Failed to initialize RAG database: {response.status}")
    except Exception as e:
        print(f"Error initializing RAG database: {str(e)}")

# Event: Message received
@bot.event
async def on_message(message):
    """
    Called when a message is sent in a channel the bot can see
    """
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands first (for slash commands)
    await bot.process_commands(message)
    
    # Check if the bot is mentioned or if "gday" is in the message
    bot_mentioned = bot.user.mentioned_in(message)
    gday_in_message = "gday" in message.content.lower() or "g'day" in message.content.lower()
    
    if bot_mentioned or gday_in_message:
        # Extract the actual message without the mention
        content = message.content
        for mention in message.mentions:
            content = content.replace(f"<@{mention.id}>", "").replace(f"<@!{mention.id}>", "")
        
        content = content.strip()
        
        # If no content after removing mentions, use a default query
        if not content or content == "":
            content = "Say hello"
        
        # Query the RAG API
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "query": content,
                    "max_results": 3,
                    "threshold": 0.5
                }
                
                async with session.post(
                    f"{RAG_API_URL}/query", 
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        matches = result.get("matches", [])
                        
                        # Format and send response
                        if matches:
                            # Get the best match
                            best_match = matches[0]
                            
                            # Format the response message
                            response_text = (
                                f"**{best_match['phrase']}** - {best_match['meaning']}\n"
                                f"Example: *{best_match['usage_example']}*"
                            )
                            
                            # If there are more matches, add them
                            if len(matches) > 1:
                                response_text += "\n\nOther phrases you might be interested in:"
                                for match in matches[1:]:
                                    response_text += f"\n• **{match['phrase']}** - {match['meaning']}"
                            
                            await message.reply(response_text)
                            
                            # Log the successful interaction
                            log_interaction(
                                query=content,
                                response=response_text,
                                user_id=str(message.author.id),
                                username=message.author.name,
                                guild_id=str(message.guild.id) if message.guild else "DM",
                                channel_id=str(message.channel.id),
                                message_id=str(message.id),
                                matches=matches
                            )
                        else:
                            # No matches found
                            fallback_responses = [
                                "Crikey! I don't quite understand that one, mate.",
                                "Strewth! That's not in my Aussie vocabulary.",
                                "Fair dinkum, I'm not sure what you're asking."
                            ]
                            
                            await message.reply(random.choice(fallback_responses))
                            
                            # Log the interaction with no matches
                            log_interaction(
                                query=content,
                                response="No matches found",
                                user_id=str(message.author.id),
                                username=message.author.name,
                                guild_id=str(message.guild.id) if message.guild else "DM",
                                channel_id=str(message.channel.id),
                                message_id=str(message.id),
                                matches=[]
                            )
                    else:
                        # API error
                        await message.reply("Sorry mate, I'm having a bit of a technical hiccup.")
                        log_error(
                            error_type="API Error",
                            details=f"Status code: {response.status}",
                            user_id=str(message.author.id),
                            message_id=str(message.id)
                        )
        except Exception as e:
            # Log the error
            await message.reply("Crikey! Something went wrong, mate.")
            log_error(
                error_type="Exception",
                details=str(e),
                user_id=str(message.author.id),
                message_id=str(message.id)
            )

# Event: Reaction added
@bot.event
async def on_reaction_add(reaction, user):
    """
    Called when a reaction is added to a message
    """
    # Ignore reactions from the bot itself
    if user == bot.user:
        return
        
    # Only process reactions to the bot's messages
    if reaction.message.author != bot.user:
        return
        
    # Log the reaction
    from .logger import log_reaction
    
    log_reaction(
        message_id=str(reaction.message.id),
        user_id=str(user.id),
        username=user.name,
        emoji=str(reaction.emoji),
        is_positive="👍" in str(reaction.emoji) or "❤️" in str(reaction.emoji) 
    )

def run_bot():
    """
    Run the Discord bot
    """
    bot.run(DISCORD_TOKEN)