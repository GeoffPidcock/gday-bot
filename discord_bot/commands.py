"""
Command definitions for the G'Day Bot Discord bot
"""
import os
import discord
from discord import app_commands
import aiohttp
import random
from typing import Dict, List, Any

from .logger import log_interaction, log_error

# Get RAG API URL from environment
RAG_API_URL = os.environ.get("RAG_API_URL", "https://geoffpidcock--gday-rag-api-serve.modal.run")

async def setup_commands(bot):
    """
    Register slash commands with Discord
    """
    # Create a command tree
    # This is already handled by the discord.py Bot class
    
    @bot.tree.command(name="gday", description="Get an Australian phrase or slang term")
    async def gday_command(interaction: discord.Interaction, query: str = None):
        """
        /gday command handler
        """
        # If no query provided, use a random phrase
        if not query:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{RAG_API_URL}/query",
                        json={"query": "random", "max_results": 1}
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            matches = result.get("matches", [])
                            
                            if matches:
                                match = matches[0]
                                response_text = (
                                    f"**{match['phrase']}** - {match['meaning']}\n"
                                    f"Example: *{match['usage_example']}*"
                                )
                                await interaction.response.send_message(response_text)
                            else:
                                fallbacks = ["G'day mate!", "How ya going?", "Fair dinkum!"]
                                await interaction.response.send_message(random.choice(fallbacks))
                        else:
                            await interaction.response.send_message("Crikey! Something went wrong.")
            except Exception as e:
                await interaction.response.send_message("Strewth! I'm having some troubles.")
                log_error(
                    error_type="Command Exception",
                    details=str(e),
                    user_id=str(interaction.user.id),
                    message_id="slash_command"
                )
        else:
            # Query the RAG API with the provided query
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "query": query,
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
                                
                                await interaction.response.send_message(response_text)
                                
                                # Log the successful interaction
                                log_interaction(
                                    query=query,
                                    response=response_text,
                                    user_id=str(interaction.user.id),
                                    username=interaction.user.name,
                                    guild_id=str(interaction.guild_id) if interaction.guild_id else "DM",
                                    channel_id=str(interaction.channel_id),
                                    message_id="slash_command",
                                    matches=matches
                                )
                            else:
                                # No matches found
                                fallback_responses = [
                                    "Crikey! I don't quite understand that one, mate.",
                                    "Strewth! That's not in my Aussie vocabulary.",
                                    "Fair dinkum, I'm not sure what you're asking."
                                ]
                                
                                await interaction.response.send_message(random.choice(fallback_responses))
                                
                                # Log the interaction with no matches
                                log_interaction(
                                    query=query,
                                    response="No matches found",
                                    user_id=str(interaction.user.id),
                                    username=interaction.user.name,
                                    guild_id=str(interaction.guild_id) if interaction.guild_id else "DM",
                                    channel_id=str(interaction.channel_id),
                                    message_id="slash_command",
                                    matches=[]
                                )
                        else:
                            # API error
                            await interaction.response.send_message("Sorry mate, I'm having a bit of a technical hiccup.")
                            log_error(
                                error_type="API Error",
                                details=f"Status code: {response.status}",
                                user_id=str(interaction.user.id),
                                message_id="slash_command"
                            )
            except Exception as e:
                # Log the error
                await interaction.response.send_message("Crikey! Something went wrong, mate.")
                log_error(
                    error_type="Command Exception",
                    details=str(e),
                    user_id=str(interaction.user.id),
                    message_id="slash_command"
                )
    
    @bot.tree.command(name="help", description="Get help with using G'Day Bot")
    async def help_command(interaction: discord.Interaction):
        """
        Show help information
        """
        help_text = """
**G'Day Bot Help**

I'm a bot that knows Australian slang and phrases! Here's how to use me:

• **Mention me** in a message to ask about Australian slang
• Use the **/gday** command followed by a term to learn about Australian phrases
• Use **/gday** without any term to get a random Australian phrase
• React to my messages with 👍 or ❤️ if you like them!

Cheers, mate!
        """
        
        await interaction.response.send_message(help_text)
    
    # Sync the commands with Discord
    await bot.tree.sync()