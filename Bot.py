import discord
import time
import datetime
import asyncio
import gspread # Install by ' python3.6 -m pip install gspread '
from oauth2client.service_account import ServiceAccountCredentials # Install by ' python3.6 -m pip install oauth2client '
import json


''' TODO unready
pee
credit score
time remaining
current status
mention
'''

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client_sheet = gspread.authorize(creds)
sheet = client_sheet.open('Credit Score').sheet1

with open("bot_info.json") as file:
    bot_data = json.load(file)


TOKEN = bot_data["token"]

client = discord.Client()

settings = {
    "prefix": "t!"
}

units = ["hours", "minutes"]
units.extend([t[:-1] for t in units])

status_list = [

    ]


command_list = [
    "hello", "mem", "prefix", "schedule", "ready", "unready", "cancel"
]

help_text = {
    "schedule": '''Try **<prefix>schedule <time>**
    Example: **<prefix>schedule 2 hourse 20 minutes** 
I can't believe you are this dumb, how can you be in nova land
    ''',
    "prefix": '''Use **<prefix>prefix** to find out the current prefix
    Or **<prefix>prefix <new prefix>** to change my prefix

    Example: **<prefix>prefix duh!
    Use it wisely, I'm old, I'm not used to changes.
    ''',
    "add_credit": "**" + settings["prefix"] + '''add_credit <person> <amount>**
Example: **''' + settings["prefix"] + '''add_credit TerroristBot 100**''',
    "minus_credit": "**" + settings["prefix"] + '''minus_credit <person> <amount>**
Example: **''' + settings["prefix"] + '''minus_credit TerroristBot 100**''',


}

pre_text = '''

Use **''' + settings["prefix"]+ '''schedule <time>** to schedule your battle
For example ** ''' + settings["prefix"] + '''schedule 2 hours 20 minutes**

My current prefix is ''' + settings["prefix"] + '''
To change prefix use **<prefix>prefix <new prefix>**

'''

@client.event
async def on_ready():
    print("Ready")
    await client.change_presence(game=discord.Game(name="Kick Ass"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:

        m = message.content
        
        ######################################
        ##### General User interactions ######
        ######################################

        # Hello world

        if m.startswith(settings["prefix"] + "hello"):
            msg = "How dare you say hello to me. I am your general. Show some respect. {0.author.mention} do 50 push ups for me".format(message)
            await client.send_message(message.channel, msg)

            
        if m.startswith(settings["prefix"] + "link"):
            em = discord.Embed(title='Link to Credit Score', colour=0xDEADBF, url="https://docs.google.com/spreadsheets/d/1CNsWa3avZbJRTpsxBGGy-iKTEaQ9__WaX_Oe3UNVd1Q/edit?usp=sharing")
            await client.send_message(message.channel, embed=em)
            
        # PREFIX CHANGING

        if m.startswith(settings["prefix"] + "prefix"):
            dmsg, tmsg = m.split("prefix")
            new_prefix = tmsg.strip()
            if not new_prefix:
                return await client.send_message(message.channel, "Your prefix is currently **" + settings["prefix"]+ "**")
            if new_prefix == "prefix":
                return await client.send_message(message.channel, "Prefix cannot be prefix. Don't try to be a smartass")
            settings["prefix"] = new_prefix
            await client.send_message(message.channel, "Congrats. Your new prefix is **"+ settings["prefix"]+ "**. Don't forget.")

        # DISPLAY MEMBER IDS in SERVER

        if m.startswith(settings["prefix"] + "mem"):
            for mem in message.channel.server.members:
                if mem == client.user or mem.bot:
                    continue
                msg = "This is {0.mention}".format(mem)
                await client.send_message(message.channel, msg)

        # DISPLAY HELP MESSAGE

        if m == (settings["prefix"] + "help"):
            command_str = ""
            for command in command_list:
                command_str += (command + "   ")
            msg = pre_text + '''**```Current commands```**```''' + command_str + "```"
            await client.send_message(message.channel, msg)

        # READY SCHEDULE CHECK

        if m == (settings["prefix"] + "ready"):
            status = find_channel_status(message.channel)
            if status["schedule"] == True:
                if status["mems"][message.author] == False:
                    status["mems"][message.author] = True
                    await client.send_message(message.channel, "{0.mention} has finished getting high on laughing gas.".format(message.author) ,embed=create_em_list_sol(status["mems"]))
                else:
                    await client.send_message(message.channel, "{0.mention} Easy now boy. No need to be so eager".format(message.author) ,embed=create_em_list_sol(status["mems"]))    
        
        # UNREADY SCHEDULE CHECK

        if m == (settings["prefix"] + "unready"):
            status = find_channel_status(message,channel)
            if status["schedule"] == True:
                if status["mems"][message.author] == True:
                    status["mems"][message.author] = False
                    await client.send_message(message.channel, "{0.mention} decided he has enough and is gonna go grab some more laughing gas.".format(message.author) ,embed=create_em_list_sol(status["mems"]))
                else:
                    await client.send_message(message.channel, "{0.mention} Don't try to be a smartass. You haven't readied yet".format(message.author) ,embed=create_em_list_sol(status["mems"]))

        # GAME SCHEDULER

        if m.startswith(settings["prefix"] + "schedule"):
            msg = "You have called for your comrads to go to battle in {}. Type **{}ready** after you have finished wearing your diapers.".format(m[len(settings["prefix"] + "schedule"):].strip(), settings["prefix"])
            listsol = ""
            
            mems = {}
            for mem in message.channel.server.members:
                if mem == client.user or mem.bot:
                    continue
                listsol += "{0.mention}: Not Ready\n".format(mem)
                mems[mem] = False
            em = discord.Embed(title ='Soldiers', description=listsol, colour=0xDEADBF)

            dmsg, tmsg = m.split("schedule")

            splits = tmsg.lower().strip().split(" ")

            if not splits or len(splits) < 2:
                return await send_help_text(client, message.channel, "schedule")

            res =[0,0]
            while len(splits) !=0:
                num = splits.pop(0)
                if not num.isnumeric():
                    return await send_help_text(client, message.channel, "schedule")
                unit = splits.pop(0)
                if unit not in units:
                    return await send_help_text(client, message.channel, "schedule")
                index = units.index(unit) % (len(units)//2)
                if res[index] != 0:
                    return await send_help_text(client, message.channel, "schedule")
                res[index] = int(num)

            if not any(res):
                return await send_help_text(client, message.channel, "schedule")

            print(res)
        
        # Battle commence reminder

        if m == (settings["prefix"] + "status"):
            status = find_channel_status(message.channel)
            if status["schedule"] == True:
                time_remaining = status["time"] - int(time.time()) 
                res = [0,0,0] #hour, minute, second
                res[0] = time_remaining // 3600
                res[1] = (time_remaining - res[0]*3600)//60
                res[2] = (time_remaining - res[0]*3600 - res[1]*60)
                await client.send_message(message.channel, "Battle will commence in about {} hours {} minutes {} seconds".format(res[0], res[1], res[2]), embed=create_em_list_sol(status["mems"]))
            else:
                await client.send_message(message.channel,"There is currently no scheduled battle. So booooooooring!")

        # Cancel battle commencement

        if m == (settings["prefix"] + "cancel"):
            status = find_channel_status(message.channel)
            if status["schedule"] == True :
                status["schedule"] = False
                await client.send_message(message.channel, "You have canceled your scheduled battle! What a pussy.")
            else :
                await client.send_message(message.channel, "Huh?")

        ########################################
        ########## CREDIT RELATED ##############
        ########################################

        #  Reset credit

        if m == (settings["prefix"] + "reset_credit"):
            count = 2
            for mem in message.channel.server.members:
                if mem == client.user or mem.bot:
                    continue
                sheet.update_cell(count, 1, mem.name)
                sheet.update_cell(count, 3, '1000')
                print(mem.name)
                count +=1

        # Add credt

        if m.startswith(settings["prefix"] + "add_credit"):
            dmsg = m[len(settings["prefix"] + "add_credit"):].strip()
            splits = dmsg.split(" ")
            if not splits or len(splits) < 2:
                return await send_help_text(client, message.channel, "add_credit")
            addee = splits[0]
            amount = splits[1]
            try:
                cell = sheet.find(addee)
                sheet.update_cell(cell.row, 3, str(int(sheet.cell(cell.row, 3).value) + int(amount)))
                await client.send_message(message.channel, addee + " has been awarded " + amount + " points by the ultimate leader " + message.author.name + " for exceptional bravery")
            except gspread.exceptions.CellNotFound:
                await client.send_message(message.channel, "Member not found")

        # Subtract Credits            

        if m.startswith(settings["prefix"] + "minus_credit"):
            dmsg = m[len(settings["prefix"] + "minus_credit"):].strip()
            splits = dmsg.split(" ")
            if not splits or len(splits) < 2:
                return await send_help_text(client, message.channel, "minus_credit")
            addee = splits[0]
            amount = splits[1]
            try:
                cell = sheet.find(addee)
                sheet.update_cell(cell.row, 3, str(int(sheet.cell(cell.row, 3).value) - int(amount)))
                await client.send_message(message.channel, addee + " has been punished for " + amount + " points by the ultimate leader " + message.author.name + " for being a pussy")
            except gspread.exceptions.CellNotFound:
                await client.send_message(message.channel, "Member not found")
            

            status = {}
            
            status["schedule"] = True
            status["time"] = int(create_offset(res))
            status["channel"] = message.channel
            status["mems"] = mems

            status_list.append(status)

            print(status["time"])
            print(int(time.time()))
            print(status["schedule"])
            print(mems)
            await client.send_message(message.channel, msg, embed=em)



def create_offset(time_arr):
    offset = 3600*time_arr[0] + 60*time_arr[1]
    return int(time.time() + offset)

def create_em_list_sol(mems):
    listsol = ""
    for mem, status in mems.items():
        if status:
            listsol += "{0.mention}: Ready\n".format(mem)
        else:
            listsol += "{0.mention}: Not Ready\n".format(mem)
    em = discord.Embed(title ='Soldiers', description=listsol, colour=0xDEADBF)
    return em

def check_all_ready(status):
    for mem, status in status["mems"].items():
        if not status:
            return False
    return True

def find_channel_status(channel):
    for status in status_list:
        if status["channel"] == channel:
            return status
    return None

async def check_reminders(client):
    await client.wait_until_ready()
    
    while not client.is_closed:
        for status in status_list:
            if status["schedule"] == True:
                if check_all_ready(status):
                    await client.send_message(status["channel"], "Everyone is ready, leggo")
                    status["schedule"] = False
                print(int(time.time()))
                if status["time"] <= int(time.time()):
                    await client.send_message(status["channel"], "Time to go to battle bois", embed=create_em_list_sol(status["mems"]))
                    status["schedule"] = False
        await asyncio.sleep(5)

async def send_help_text(client, channel, command):
    return await client.send_message(channel, help_text[command])
    
    
client.loop.create_task(check_reminders(client))

client.run(TOKEN)







