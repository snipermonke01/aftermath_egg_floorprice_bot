
import discord
import asyncio
import requests
import os
import yaml

base_dir = os.path.dirname(__file__)


def get_config():
    """
    Load Config from yaml file
    """

    config = yaml.safe_load(open(os.path.join(base_dir,
                                              "config.yaml")))

    if config['discord_bot_token'] is None:

        raise Exception("Discord bot token is not set!")

    if config['indexer_user'] is None:

        raise Exception("Indexer username is not set!")

    if config['indexer_pword'] is None:

        raise Exception("Indexer password is not set!")

    return config


def _get_floor_price():
    """
    Query indexer graph for floor price of aftermath egg collection

    Returns
    -------
    float
        price in SUI of floor price.

    """

    base_url = "https://api.indexer.xyz/graphql"

    headers = {"x-api-user": config['indexer_user'],
               "x-api-key": config['indexer_pword']}

    query = """
            query MyQuery {
      sui {
        collections(
          where: {slug: {_eq: "0x484932c474bf09f002b82e4a57206a6658a0ca6dbdb15896808dcd1929c77820"}}
        ) {
          title
          slug
          floor
          volume
          usd_volume
        }
      }
    }
        """

    result = requests.post(base_url,
                           json={'query': query},
                           headers=headers)

    return result.json()['data']['sui']['collections'][0]['floor']/1000000000


config = get_config()

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = discord.Bot(intents=intents)


async def update_status():

    while True:
        # Set the bot's status
        await bot.change_presence(
            activity=discord.Activity(

                type=discord.ActivityType.watching,
                name="Floor Price: {} SUI".format(_get_floor_price())
            ),

            status=discord.Status.online
        )

        await asyncio.sleep(30)  # Wait for 30 seconds before updating the status again


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    # Start the status update loop
    bot.loop.create_task(update_status())


bot.run(config["discord_bot_token"])
