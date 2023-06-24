import discord
from discord import app_commands
from discord.ext import commands
import requests
import json
from bs4 import BeautifulSoup
from credentials import *

def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="/", intents=intents)

    #Sync commands with Discord Server
    #Could take up to 1h
    @bot.event
    async def on_ready():
        print(f'{bot.user} is now running')

        try:
            synced = await bot.tree.sync()
            print(f'Bot is up to date - Synced {len(synced)} command(s)')
        except Exception as e:
            print(f"Encountered and exception: {e}")

    #simple /clan command
    #Takes any Clan Name as argument
    #Displays specified Clan's member count, member names and their level
    @bot.tree.command(name="clan")
    @app_commands.describe(clan = "Clan Name")
    async def clan(interaction: discord.Interaction, clan: str):
        gotData = False
        try:
            r = requests.get("https://xero.gg/api/clan/" + clan, headers={"x-api-access-key-id" : key, "x-api-secret-access-key": secret})
            doc = BeautifulSoup(r.text, "html.parser")
            doc = str(doc)
            data = json.loads(doc)
            data = json.dumps(data, indent=4)
            data = json.loads(data)
            gotData = True
        except Exception as e:
            print(f"Unable to reach Xero API! {str(e)}")

        if gotData:
            if data['success'] == True:
                clan_name = data['clan']['name']
                names = "Clan: " + clan_name + "\n\nMembers:\n"
                names = ""
                levels = ""
                onlines = ""
                for x in data['clan']['members']:
                    names+= x['name'] + "\n"
                    levels+= str(x['progression']['level']['value']) + "\n"
                    onlines+= "WIP\n"

                clan_url = "https://xero.gg/clan/" + clan_name
                
                embed = discord.Embed(
                    colour=discord.Colour.brand_green(),
                    title=clan_name,
                    description="Number of members: " + str(len(data['clan']['members'])) + "\n[View Clan on xero.gg](" + clan_url + ")"
                )

                embed.set_author(name="Xero Clan Helper", icon_url=bot.user.avatar.url)
                embed.set_thumbnail(url=data['clan']['image'])
                embed.set_footer(text="Created by @notashlek")

                embed.add_field(name="Members", value=names)
                embed.add_field(name="Level", value=levels)

                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"Error processing your command {clan}: {data['text']}")

    #/myclan command
    #Currently configured to get clan data of bot owner
    #Bot is currently intended to be used in a private Discord server of a Xero clan
    #TODO: Make it possible to /register users and displays their Clan members
    @bot.tree.command(name="myclan")
    async def myclan(interaction: discord.Interaction):
        gotData = False
        try:
            r = requests.get("https://xero.gg/api/self/social/clan", headers={"x-api-access-key-id" : key, "x-api-secret-access-key": secret})
            doc = BeautifulSoup(r.text, "html.parser")
            doc = str(doc)
            data = json.loads(doc)
            data = json.dumps(data, indent=4)
            data = json.loads(data)
            gotData = True
        except Exception as e:
            print(f"Unable to reach Xero API! {str(e)}")

        if gotData:
            if data['success'] == True:
                names = ""
                levels = ""
                onlines = ""
                onlines_web = ""
                online_counter = 0
                for x in data['players']:
                    names+= x['name'] + "\n"
                    levels+= str(x['progression']['level']['value']) + "\n"
                    if x['game']['online'] == True:
                        onlines+= "__**Online**__" + "\n"
                        online_counter+=1
                    else:
                        onlines+= "Offline" + "\n"
                    if x['web']['online'] == True:
                        onlines_web+= "Online" + "\n"
                    else:
                        onlines_web+= "Offline" + "\n"
                
                embed = discord.Embed(
                    colour=discord.Colour.brand_green(),
                    title="Memebers list",
                    description=str(online_counter) + " clan members online" 
                )

                embed.set_author(name="Xero Clan Helper", icon_url=bot.user.avatar.url)
                embed.set_thumbnail(url="https://assets.xero.gg/avatars/e0fd498f37a249815f11f788c3c65ba49e8148dd63ba97a5414bf42969d4dfce/4fF8HuqOSiOJ.png")
                embed.set_footer(text="Created by @notashlek")

                embed.add_field(name="Members", value=names)
                embed.add_field(name="Status", value=onlines)

                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"Error processing your command: {data['text']}")
    
    #/help command
    #Displays all available commands, their use-case and function
    @bot.tree.command(name="help")
    async def help(interaction: discord.Interaction):
        embed = discord.Embed(
            colour=discord.Colour.blurple(),
            title="Supported Commands"
        )

        cmds = "/clan [Clan Name]\n/myclan\n/help"
        descs = "Displays members and levels of desired Clan\nDisplays members and statuses of your clan\nDisplays supported commands"
        embed.add_field(name="Command", value=cmds)
        embed.add_field(name="Description", value=descs)
        embed.set_author(name="Xero Clan Helper", icon_url=bot.user.avatar.url)
        embed.set_footer(text="Created by @notashlek")

        await interaction.response.send_message(embed=embed)

    #/eventcheck command
    #Check challenge count (> 3 means there is a bonus challenge meaning an ongoing event)
    @bot.tree.command(name="eventcheck")
    async def eventcheck(interaction: discord.Interaction):
        gotData = False
        try:
            r = requests.get("https://xero.gg/api/challenge", headers={"x-api-access-key-id" : key, "x-api-secret-access-key": secret})
            doc = BeautifulSoup(r.text, "html.parser")
            doc = str(doc)
            data = json.loads(doc)
            data = json.dumps(data, indent=4)
            data = json.loads(data)
            gotData = True
        except Exception as e:
            print(f"Unable to reach Xero API! {str(e)}")

        if gotData:
            challenges = ""
            nChallenges = 0

            for x in data['challenges']:
                challenges+= x['name'] + "\n"
                nChallenges+=1
            
            #Testing purposes - no event at time of testing
            #challenges+= "Limited"
            #nChallenges+=1

            if nChallenges > 3:
                embed = discord.Embed(
                    colour = discord.Colour.gold(),
                    title="**!!! NEW EVENT !!!**",
                    description="Head over to [Challenges](https://xero.gg/challenges) to check it out"
                )
            else:
                embed = discord.Embed(
                    colour = discord.Colour.blue(),
                    title="No event",
                    description="There is currently no ongoing event"
                )

            embed.add_field(name="Challenges", value=challenges)
            embed.set_author(name="Xero Clan Helper", icon_url=bot.user.avatar.url)
            embed.set_footer(text="Created by @notashlek")

            await interaction.response.send_message(embed=embed)

            

    bot.run(TOKEN)