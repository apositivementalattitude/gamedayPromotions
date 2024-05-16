import discord
import requests

client = discord.Client()

@client.event
async def on_ready():
        print('Logged in as {0.user}'.format(client))

async def check_game_results():
    # Fetch game data
    # response = requests.get()
    last_game = data['games'][0]
    # checks for a win and will push a notification for peopl that can view the channel
    if last_game['result'] == 'win':
        channel = client.get_channnel(550804481906835493)
        await channel.send('$5 panda tomorrow @here')
        # Sleep
        await request.sleep(36000)

# runs the check_game_results function
client.loop.create_task(check_game_results())

# discord bot token
client.run('1adcbd7424ccdf01a433758634a6f4546fe524ae407d43a726aa7745a75d7cc2')