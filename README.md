# This project is no longer maintained on GitHub. [See here](https://git.tarkacore.dev/showdown/myai-discord)
# myai-discord
Alternative to "My AI", by Snapchat, but on Discord.
## Installation Steps
### Preparing your environnement
- Create your Discord bot [here](https://discord.com/developers/applications)
- Enable **Members** and **Messages** intents.
- Create your OpenAI Developer Account [here](https://platform.openai.com)
### Setting up the bot
1. Install Python >= 3.8.10
2. Install requirements with `python3 -m pip install -U -r requirements.txt`
3. Rename `tokens.db.example` to `tokens.db`
3. Create a `.env` file to setup your environnement variables.
```
MAX_TOKEN_PER_REQUEST = [Maximum tokens per request] (recommended: 1800-2000)
TOKEN = [Your Discord bot's token]
OPENAI_API_KEY = [OpenAI Token -- can be found at https://platform.openai.com/account/api-keys]
```

#### The `tokens.db.example` database is blank and contains no data.
