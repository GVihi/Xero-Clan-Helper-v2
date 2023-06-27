import discord
from discord import app_commands
from discord.ext import commands
import requests
import json
from bs4 import BeautifulSoup
from credentials import *
import os.path

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
    @bot.tree.command(name="myclanlegacy")
    async def myclanoldlegacy(interaction: discord.Interaction):
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
                    description=str(online_counter) + " clan members online\n__**This is a legacy command that only works for LastGunners. Please use the /myclan command**__" 
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

        cmds = "/clan [Clan Name]\n/myclan\n/help\n/eventcheck\n/eventchecksubscribe\n\n/eventcheckunsubscribe\n/registermyclan\n/unregistermyclan"
        descs = "Displays members and levels of desired Clan\nDisplays members and statuses of your clan\nDisplays supported commands\nCheck if there is an ongoing event\nSubscribes you to receive be mentioned any time there's an ongoing event\nUnsubscribe from event checks\nA way to register your clan for use with /myclan\nUnregister your clan"
        embed.add_field(name="Command", value=cmds)
        embed.add_field(name="Description", value=descs)
        embed.set_author(name="Xero Clan Helper", icon_url=bot.user.avatar.url)
        embed.set_footer(text="Created by @notashlek")

        await interaction.response.send_message(embed=embed)

    #/eventcheck command
    #Check challenge count (> 3 means there is a bonus challenge meaning an ongoing event)
    @bot.tree.command(name="eventcheck")
    async def eventcheck(interaction: discord.Interaction):

        #####
        ##### TODO: For the time being, implement a broadcast method in here, so only one
        ##### clan member needs to run the command and in the 'event' of an ongoing game event
        ##### Broadcast "New Event" message to registered users' DM's
        #####
        file_name = "user_ids.json"
        if not os.path.isfile(file_name):
            await interaction.response.send_message(f"```JSON file containing ID data missing. Contact the developer!\n@notashlek```")
        else:

            ids = ""
            with open(file_name, "r") as f:
                ids = json.load(f)

            ids = json.dumps(ids, indent=4)
            ids = json.loads(ids)

            mentions = ""
            for x in ids['ids']:
                mentions+= "<@" + str(x['id']) + "> "

            #dm = await interaction.user.create_dm()
            #await dm.send("Test")

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
                        description= mentions + "\nHead over to [Challenges](https://xero.gg/challenges) to check it out"
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

    @bot.tree.command(name="eventchecksubscribe")
    async def eventchecksubscribe(interaction: discord.Interaction):
        file_name = "user_ids.json"
        if not os.path.isfile(file_name):
            empty_file = {
                "ids" : [
                    
                ]
            }
            with open(file_name, 'w') as f:
                json.dump(empty_file, f, ensure_ascii=False, indent=4)

        if os.path.isfile(file_name):
            data = ""
            with open(file_name, 'r') as f:
                data = json.load(f)
            
            data = json.dumps(data, indent=4)
            data = json.loads(data)

            user_id = interaction.user.id

            user_exists = False

            for x in data['ids']:
                if x['id'] == interaction.user.id:
                    user_exists = True

            if user_exists:
                await interaction.response.send_message("You are already subscribed to updates")
            else:
                with open(file_name, "w") as f:

                    new_user = {
                        "id": user_id
                    }

                    data['ids'].append(new_user)

                    json.dump(data, f, ensure_ascii=False, indent=4)
                
                with open(file_name, "r") as f:
                    data = json.load(f)

                    data = json.dumps(data, indent=4)
                    data = json.loads(data)

                    #print(data)

                    user_added = False

                    for x in data['ids']:
                        if x['id'] == interaction.user.id:
                            user_added = True
                    
                    if user_added:
                        await interaction.response.send_message("Subscribed successfully!")
                    else:
                        await interaction.response.send_message("Something went wrong, please try again")

    @bot.tree.command(name="registermyclan")
    @app_commands.describe(api_key = "Xero API Key", api_secret = "Xero API Secret")
    async def registermyclan(interaction: discord.Interaction, api_key: str, api_secret: str):
        file_name = "api_keys.json"
        if not os.path.isfile(file_name):
            empty_file = {
                "keys": [
                    
                ]
            }
            with open(file_name, "w") as f:
                json.dump(empty_file, f, ensure_ascii=False, indent=4)

        if os.path.isfile(file_name):
            data = ""
            with open(file_name, "r") as f:
                data = json.load(f)

            data = json.dumps(data, indent=4)
            data = json.loads(data)

            user_id = interaction.user.id

            user_exists = False

            for x in data['keys']:
                if x['id'] == user_id:
                    user_exists = True

            if user_exists:
                await interaction.response.send_message("You have already registered your clan")
            else:
                r = requests.get("https://xero.gg/api/self/social/clan", headers={"x-api-access-key-id" : api_key, "x-api-secret-access-key": api_secret})
                doc = BeautifulSoup(r.text, "html.parser")

                doc = str(doc)
                res = json.loads(doc)
                res = json.dumps(res, indent=4)
                res = json.loads(res)

                if res['success'] == True:
                    with open(file_name, "w") as f:

                        new_entry = {
                            "id": user_id,
                            "key": api_key,
                            "secret": api_secret
                        }

                        data['keys'].append(new_entry)

                        json.dump(data, f, ensure_ascii=False, indent=4)

                    with open(file_name, "r") as f:
                        data = json.load(f)

                        data = json.dumps(data, indent=4)
                        data = json.loads(data)

                        keys_added = False

                        for x in data['keys']:
                            if x['id'] == user_id:
                                keys_added = True

                        if keys_added:
                            await interaction.response.send_message("Clan registered successfully")
                        else:
                            await interaction.response.send_message("Something went wrong, please try again")
                else:
                    await interaction.response.send_message(f"Failed to register your clan: {res['text']}")

    @bot.tree.command(name="myclan")
    async def myclan(interaction: discord.Interaction):
        file_name = "api_keys.json"
        if not os.path.isfile(file_name):
           await interaction.response.send_message(f"```JSON file containing API data missing. Contact the developer!\n@notashlek```")
        else:
            data = ""
            with open(file_name, "r") as f:
                data = json.load(f)

            data = json.dumps(data, indent=4)
            data = json.loads(data)

            user_id = interaction.user.id
            registered = False

            for x in data['keys']:
                if x['id'] == user_id:
                    registered = True
                    api_key = x['key']
                    api_secret = x['secret']

            if not registered:
                await interaction.response.send_message(f"Clan not yet registered. Please use the /registermyclan command first")
            else:
                r = requests.get("https://xero.gg/api/self/social/clan", headers={"x-api-access-key-id" : api_key, "x-api-secret-access-key": api_secret})
                doc = BeautifulSoup(r.text, "html.parser")

                doc = str(doc)
                data = json.loads(doc)
                data = json.dumps(data, indent=4)
                data = json.loads(data)

                if data['success']:
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

    @bot.tree.command(name="crashtest")
    async def crashtest(interaction: discord.Interaction):
        myid = 305035767170990081
        if interaction.user.id != myid:
            await interaction.response.send_message(f"You do not have permission to use this command")
        else:
            word = "lol"
            await interaction.response.send_message(f"{word[10]}")

    @bot.tree.error
    async def on_app_command_error(interaction: discord.Integration, error):
        myid = '<@305035767170990081>'
        await interaction.response.send_message(f"{myid}\n**Something went wrong**\n```{error}```")

    @bot.tree.command(name="eventcheckunsubscribe")
    async def eventcheckunsubscribe(interaction: discord.Interaction):
        file_name = "user_ids.json"
        if not os.path.isfile(file_name):
           await interaction.response.send_message(f"```JSON file containing ID data missing. Contact the developer!\n@notashlek```")
        else:
            with open(file_name, "r") as f:
                data = json.load(f)

            data = json.dumps(data, indent=4)
            data = json.loads(data)

            rm_id = interaction.user.id

            subbed = False
            for x in data['ids']:
                if x['id'] == rm_id:
                    subbed = True

            if not subbed:
                await interaction.response.send_message(f"You are not currently subscribed to event checks!")
            else:
                new_data = {
                    "ids": [

                    ]
                }

                for x in data['ids']:
                    if x['id'] != rm_id:
                        entry = {
                            "id": x['id']
                        }

                        new_data["ids"].append(entry)

                with open(file_name, "w") as f:
                    json.dump(new_data, f, indent=4)

                with open(file_name, "r") as f:
                    data = json.load(f)

                data = json.dumps(data, indent=4)
                data = json.loads(data)

                subbed = False
                for x in data['ids']:
                    if x['id'] == rm_id:
                        subbed = True

                if not subbed:
                    await interaction.response.send_message(f"Unsubscribed successfully!")
                else:
                    await interaction.response.send_message(f"Something went wrong, please try again!")

    @bot.tree.command(name="unregistermyclan")
    async def unregistermyclan(interaction: discord.Interaction):
        file_name = "api_keys.json"
        if not os.path.isfile(file_name):
            await interaction.response.send_message(f"```JSON file containing API data missing. Contact the developer!\n@notashlek```")
        else:
            with open(file_name, "r") as f:
                data = json.load(f)
            
            data = json.dumps(data, indent=4)
            data = json.loads(data)

            rm_id = interaction.user.id

            registered = False
            for x in data['keys']:
                if x['id'] == rm_id:
                    registered = True

            if not registered:
                await interaction.response.send_message(f"Your clan is currently not registered!")
            else:
                new_data = {
                    "keys": [

                    ]
                }

                for x in data['keys']:
                    if x['id'] != rm_id:
                        entry = {
                            "id": x['id'],
                            "key": x['key'],
                            "secret": x['secret']
                        }

                        new_data['keys'].append(entry)

                with open(file_name, "w") as f:
                    json.dump(new_data, f, indent=4)

                with open(file_name, "r") as f:
                    data = json.load(f)
            
                data = json.dumps(data, indent=4)
                data = json.loads(data)

                registered = False
                for x in data['keys']:
                    if x['id'] == rm_id:
                        registered = True

                if not registered:
                    await interaction.response.send_message(f"Unsubscribed successfully!")
                else:
                    await interaction.response.send_message(f"Something went wrong, please try again!")

    bot.run(TOKEN)