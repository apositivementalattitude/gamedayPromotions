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

async def get_dodgers_home_wins():
    url = 'https://www.espn.com/mlb/team/schedule/_/name/lad/los-angeles-dodgers'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='Table')
        rows = table.find_all('tr', class_='Table__TR')
    except AttributeError as e:
        print(f"Error parsing the page: {e}")
        return []

    games = []

    for row in rows:
        columns = row.find_all('td')
        if len(columns) > 1:
            opponent = columns[1].text
            result = columns[2].text
            # Check if the game is a home game (no "@" in opponent column) and if the Dodgers won
            if '@' not in opponent and 'W' in result:
                game = {
                    'date': columns[0].text,
                    'opponent': opponent,
                    'result': result,
                    'score': columns[3].text,
                }
                games.append(game)

    return games

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
            message = f"@here The Dodgers won a home game on {game['date']} against {game['opponent']} with a score of {game['score']}. $5 Panda"
            await channel.send(message)

        # Sleep for a specified duration (e.g., 1 hour) before checking again
        await asyncio.sleep(3600)

if DISCORD_BOT_TOKEN is None or DISCORD_CHANNEL_ID is None:
    print("Environment variables DISCORD_BOT_TOKEN or DISCORD_CHANNEL_ID are not set correctly.")
else:
    client.run(DISCORD_BOT_TOKEN)