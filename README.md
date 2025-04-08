# G'Day Bot

A Discord bot that responds to mentions with Australian slang and phrases using a Retrieval Augmented Generation (RAG) system.
WARNING: this is a product of vibe-coding.

## Architecture

The system is composed of two main components:

1. **RAG API System**: A FastAPI application that handles the retrieval and serving of Australian slang/phrases.
2. **Discord Bot**: A Discord.py bot that interacts with users and communicates with the RAG API.

Both components are designed to be deployed on Modal.com, eliminating the need for multiple hosting platforms.

## Project Structure

```
gday-bot/
├── README.md                   # Project documentation
├── .env                        # Environment variables (gitignored)
├── .gitignore                  # Git ignore file
├── requirements.txt            # Python dependencies
├── data/
│   └── australianisms.json     # Dataset of Australian phrases
├── rag_system/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── modal_wrapper.py        # Modal deployment wrapper
│   ├── embedding.py            # Embedding generation logic
│   ├── retrieval.py            # RAG retrieval logic
│   └── storage.py              # Vector database interface
├── discord_bot/
│   ├── __init__.py
│   ├── bot.py                  # Discord bot implementation
│   ├── modal_wrapper.py        # Modal deployment wrapper
│   ├── commands.py             # Bot command definitions
│   └── logger.py               # Interaction logging
└── tests/
    ├── generate_invite_link.py # Creates a discord bot invite link
    ├── test_bot_commands.py    # tests the slash commands
    ├── test_bot_connection.py  # tests the discord and rag connections
    └── test_real_bot.py        # locally tests the discord bot
    └── test.ipynb              # various rag_api tests    

```

## Features

- Responds to mentions and messages containing "g'day" with Australian slang explanations
- Provides slash commands for direct querying
- Logs all interactions and reactions for lightweight evaluation
- Daily backups of log data


## Prerequisites

- Python 3.8+
- Discord Bot Token
- OpenAI API Key

## Running Locally

For development purposes, you can run the components locally:

1. Run the RAG API:
   ```bash
   modal run rag_system/modal_wrapper
   ```

2. Run the Discord bot:
   ```bash
   modal run discord_bot/modal_wrapper.py
   ```

### Deployment

Both components are designed to be deployed on Modal.com:

1. Deploy the RAG API:
   ```bash
   modal deploy rag_system/modal_wrapper.py
   ```

2. Deploy the Discord bot:
   ```bash
   modal deploy discord_bot/modal_wrapper.py
   ```

## Usage

Once the bot is running and added to a Discord server:

- Mention the bot: `@GDayBot What is a barbie?`
- Use slash commands: `/gday barbie`
- Get a random phrase: `/gday`
- View help: `/help`

## Evaluation

The bot logs all interactions to JSON files that can be analyzed for evaluation:

- `interactions.json`: Logs all queries and responses
- `reactions.json`: Logs user reactions to bot messages
- `errors.json`: Logs any errors that occur

## Adding More Australianisms

Simply add more entries to the `data/australianisms.json` file and rerun the initialization:

```bash
curl -X POST https://your-rag-api-url/init
```

## Adding New Commands

1. Add new commands in `discord_bot/commands.py`
2. Update the Discord application commands by running the bot again

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Based on the simple_rag.py implementation
- Uses Discord.py for the Discord bot interface
- Uses Modal.com for deployment