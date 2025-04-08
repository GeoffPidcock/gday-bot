import discord

# Your bot's client ID (NOT the token)
# Find this in the Discord Developer Portal under "General Information"
CLIENT_ID = "1359040402807586888"  # Replace with your bot's client ID

# Create the permission integer
permissions = discord.Permissions(
    send_messages=True,
    read_messages=True,
    read_message_history=True,
    view_channel=True,
    # Add any other permissions your bot needs
)

# Generate the invite link
link = discord.utils.oauth_url(
    client_id=CLIENT_ID,
    permissions=permissions,
    scopes=["bot", "applications.commands"]
)

print(f"Bot invite link: {link}")