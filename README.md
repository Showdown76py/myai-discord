# myai-discord
Alternative to "My AI", by Snapchat, but on Discord.
## Installation Steps
### Preparing your environnement
- Create your Discord bot [here](https://discord.com/developers/applications)
- Enable **Members**, **Messages** and **Presence** intents.
- Create your OpenAI Developer Account [here](https://platform.openai.com)
### Setting up the bot
1. Install Python >= 3.8.10
2. Install requirements with `python3 -m pip install -U -r requirements.txt`
3. Create a `.env` file to setup your environnement variables.
```
MAX_TOKEN_PER_REQUEST = [Maximum tokens per request] (recommended: 1800-2000)
TOKEN = [Your Discord bot's token]
OPENAI_API_KEY = [OpenAI Token -- can be found at https://platform.openai.com/account/api-keys]
```

#### The `tokens.db` database is blank and contains no data.
