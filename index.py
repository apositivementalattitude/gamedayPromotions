import os
import discord
import requests
from bs4 import BeautifulSoup
import asyncio

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Get the channel ID and bot token from environment variables
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Debug: Print the loaded environment variables
print(f"DISCORD_BOT_TOKEN: {DISCORD_BOT_TOKEN}")
print(f"DISCORD_CHANNEL_ID: {DISCORD_CHANNEL_ID}")

# Ensure the bot token and channel ID are not None
if not DISCORD_BOT_TOKEN:
    print("Error: DISCORD_BOT_TOKEN is not set.")
if not DISCORD_CHANNEL_ID:
    print("Error: DISCORD_CHANNEL_ID is not set.")

async def get_dodgers_home_wins():
    url = "https://www.mlb.com/dodgers/schedule"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    print(f"URL: {url}")  # Debugging: print the URL to ensure it's correct
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        games = soup.find_all('li', class_='schedule-list-item')

        home_wins = []

        for game in games:
            if 'home' in game['class']:
                result = game.find('div', class_='schedule-list-item-result')
                if result and 'win' in result.text.lower():
                    date = game.find('div', class_='schedule-list-item-date').text.strip()
                    opponent = game.find('div', class_='schedule-list-item-opponent').text.strip()
                    score = result.text.strip()
                    home_wins.append({'date': date, 'opponent': opponent, 'score': score})
                    print(f"Date: {date}, Opponent: {opponent}, Score: {score}")

        return home_wins

    except AttributeError as e:
        print(f"Error parsing the page: {e}")
        return []

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel = client.get_channel(int(DISCORD_CHANNEL_ID))
    if channel is None:
        print("Failed to retrieve channel. Check the channel ID.")
    else:
        await check_games_periodically()

async def check_games_periodically():
    await client.wait_until_ready()
    channel = client.get_channel(int(DISCORD_CHANNEL_ID))

    while not client.is_closed():
        home_wins = await get_dodgers_home_wins()

        for game in home_wins:
            message = f"The Dodgers won a home game on {game['date']} against {game['opponent']} with a score of {game['score']}."
            await channel.send(message)

        # Sleep for a specified duration (e.g., 1 hour) before checking again
        await asyncio.sleep(3600)

if DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID:
    client.run(DISCORD_BOT_TOKEN)
else:
    print("Environment variables DISCORD_BOT_TOKEN or DISCORD_CHANNEL_ID are not set correctly.")
