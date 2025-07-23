import os
import discord
import requests
import asyncio
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
POLYGON_KEY = os.getenv("POLYGON_KEY")
PREMIUM_CHANNEL_ID = int(os.getenv("PREMIUM_CHANNEL_ID"))
FREE_CHANNEL_ID = int(os.getenv("FREE_CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    fetch_flow_alerts.start()

@tasks.loop(seconds=60)
async def fetch_flow_alerts():
    url = f"https://api.polygon.io/v1/unusual_options_activity?apiKey={POLYGON_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if not data.get("results"): return

        for item in data["results"]:
            ticker = item["ticker"]
            expiry = item["expiration_date"]
            strike = item["strike_price"]
            option_type = item["type"]
            size = item["size"]
            premium = item["premium"]

            message_full = f"🚨 {ticker} {option_type.upper()} | Strike: {strike} | Exp: {expiry} | Size: {size} | Premium: ${premium}"
            message_censored = f"🚨 FLOW ALERT: {ticker} | Exp: {expiry} | More info in Premium!"

            premium_channel = client.get_channel(PREMIUM_CHANNEL_ID)
            free_channel = client.get_channel(FREE_CHANNEL_ID)

            if premium_channel and free_channel:
                await premium_channel.send(message_full)
                await free_channel.send(message_censored)

            await asyncio.sleep(1)

    except Exception as e:
        print(f"⚠️ Error: {e}")

client.run(TOKEN)
