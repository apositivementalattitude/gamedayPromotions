import os
import discord
import requests
from bs4 import BeautifulSoup
import asyncio
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID')) # Must be an integer

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Site to scrape
async def fetch_dodgers_scores():
    url = "https://sports.yahoo.com/mlb/teams/la-dodgers/"

    # Site will block you with this -- mimics Mozilla
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the section with recent games
        games_section = soup.find('section', attrs={'class': 'simple-carousel'})
        if not games_section:
            print("Failed to find games section")
            return []

        games = games_section.find_all('div', class_='simple-carousel-item')
        scores = []

        for game in games:
            date = game.find('span', class_='date').text.strip()
            teams = game.find_all('span', class_='D(ib)')
            home_team = teams[1].text.strip() if len(teams) > 1 else "N/A"
            away_team = teams[0].text.strip() if len(teams) > 0 else "N/A"
            result = game.find('div', class_='score').text.strip()

            if 'Dodgers' in home_team:
                scores.append((date, home_team, away_team, result))

        return scores
    except Exception as e:
        print(f"Error fetching the page: {e}")
        return []

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    guild = client.guilds[0]  # Assuming the bot is only in one guild
    print(f'Guild: {guild.name} (ID: {guild.id})')

    for channel in guild.text_channels:
        print(f' - Channel: {channel.name} (ID: {channel.id})')

    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if channel is None:
        print(f"Failed to retrieve channel. Check the channel ID: {DISCORD_CHANNEL_ID}")
    else:
        print(f"Successfully retrieved channel: {channel.name} (ID: {channel.id})")
        await check_scores_periodically(channel)

async def check_scores_periodically(channel):
    while True:
        print("Checking for new scores...")
        scores = await fetch_dodgers_scores()
        print(f"Fetched {len(scores)} scores.")
        for date, home_team, away_team, result in scores:
            message = f"The Dodgers played against {away_team} on {date} at home. Result: {result}." # Message to send
            print(f"Sending message: {message}")
            await channel.send(message)
        await asyncio.sleep(3600)  # Check every hour

if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
