import time
import traceback
import discord
from discord import app_commands
from discord.ext import tasks
import os
import openai
import sqlite3
import tiktoken
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']
db = sqlite3.connect('tokens.db')
typing = []
intents = discord.Intents.default()
intents.members = True
intents.dm_messages = True

class App(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(client=self)

    async def setup_hook(self) -> None:
        return

app = App()

@tasks.loop(seconds=5)
async def typing_loop():
    for channel in typing:
        try:
            await channel.typing()
        except:
            typing.remove(channel)

@app.event
async def on_ready():
    print('We have logged in as {0.user}'.format(app))
    await app.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your direct messages!"))
    typing_loop.start()

encoding = tiktoken.get_encoding('cl100k_base')
def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = len(encoding.encode(string))
    return num_tokens

@app.event
async def on_message(message: discord.Message):
    if not isinstance(message.channel, discord.DMChannel): return
    if message.author.id == app.user.id: return
    try:
        c = db.cursor()
        c.execute('SELECT * FROM message_history WHERE user_id = ? ORDER BY timestamp DESC', (message.author.id,))
        msgs = c.fetchall()
        message_token_usage = num_tokens_from_string(message.content)
        max_token = int(os.environ['MAX_TOKEN_PER_REQUEST'])
        with open('base-prompt.txt', 'r', encoding='utf-8') as f:
            bprompt = f.read()

        activs = ""

        for activity in message.author.mutual_guilds[0].get_member(message.author.id).activities:
            if isinstance(activity, discord.Spotify):
                activs += f"- Listening to {activity.title} by {activity.artist} on Spotify\n"
            elif isinstance(activity, discord.Streaming):
                activs += f"- Streaming {activity.name}\n"
            elif isinstance(activity, discord.Game):
                activs += f"- Playing {activity.name}\n"
            elif isinstance(activity, discord.CustomActivity):
                activs += f"- Custom Activity: {activity.name}\n"
            elif isinstance(activity, discord.Activity):
                activs += f"- {activity.type.name.capitalize()} {activity.name}\n"

        arguments = {
            "username": message.author.name,
            "status": message.author.mutual_guilds[0].get_member(message.author.id).raw_status,
            "activities": activs.strip('\n')
        }

        for arg in arguments.keys(): bprompt = bprompt.replace(f'|{arg}|', arguments[arg])
    
        previous_tokens = 200+len(bprompt)+message_token_usage
        # (message_id, user_id, content, token, role, timestamp)
        # order by timestamp (most recent to least recent)
        usable_messages = []
        for msg in msgs:
            d = previous_tokens + msg[3]
            if d >= max_token:
                break
            previous_tokens += msg[3]
            usable_messages.append(msg)
        
        usable_messages.reverse()

        
        messages = [{"role": "system", "content": bprompt}]
        for v in usable_messages: messages.append({"role": v[4], "content": v[2]})
        messages.append({"role": "user", "content": message.content})
        await message.channel.typing()
        typing.append(message.channel)
        req = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=max_token-(previous_tokens-200),
            messages=messages
        )
        typing.remove(message.channel)
        response = req['choices'][0]['message']['content']
        prompt_used_tokens = req['usage']['prompt_tokens']
        completion_used_tokens = req['usage']['completion_tokens']
        r=await message.reply(response, allowed_mentions=discord.AllowedMentions.none())
        c.execute('INSERT INTO message_history VALUES (?, ?, ?, ?, ?, ?)', (message.id, message.author.id, message.content, prompt_used_tokens, 'user', int(message.created_at.timestamp())))
        c.execute('INSERT INTO message_history VALUES (?, ?, ?, ?, ?, ?)', (r.id, message.author.id, response, completion_used_tokens, 'assistant', int(time.time())))
        db.commit()
    except Exception as e:
        traceback.print_exc()
        if message.channel in typing: typing.remove(message.channel)
        await message.reply('I just uncountered an issue. Can you please report this problem to the administrator of the bot, or try again later?\n```py\n'+str(e)+'```')

    


app.run(os.environ['TOKEN'])

