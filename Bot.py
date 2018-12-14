import discord
import time
import datetime
import asyncio

''' TODO unready
pee
credit score
time remaining
current status
mention
'''

TOKEN = "NTE5ODIzMzM3MTA3NzUwOTEy.Duk65g.BQQ5Zp42G1E-SngTHW73ATaZzts"

client = discord.Client()

settings = {
    "prefix": "t!"
}

units = ["hours", "minutes"]
units.extend([t[:-1] for t in units])

status_list = [

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
    '''
}

pre_text = '''

Use ''' + settings["prefix"]+ '''**schedule <time>** to schedule your battle
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
        
        if m.startswith(settings["prefix"] + "hello"):
            msg = "How dare you say hello to me. I am your general. Show some respect. {0.author.mention} do 50 push ups for me".format(message)
            await client.send_message(message.channel, msg)
            
        if m.startswith(settings["prefix"] + "em"):
            em = discord.Embed(title='Title', description='My Embed Content.', colour=0xDEADBF)
            em.add_field(name ='Yes', value='Haha', inline=False)
            em.add_field(name ='No', value='HoHo', inline=True)
            await client.send_message(message.channel, embed=em, content = "Hello you fuck")
            
        if m.startswith(settings["prefix"] + "mem"):
            for mem in message.channel.server.members:
                if mem == client.user or mem.bot:
                    continue
                msg = "This is {0.mention}".format(mem)
                await client.send_message(message.channel, msg)

        if m == (settings["prefix"] + "help"):
            await client.send_message(message.channel, pre_text)

        if m == (settings["prefix"] + "ready"):
            for status in status_list:
                if message.channel == status["channel"] and status["schedule"] == True:
                    if status["mems"][message.author] == False:
                        status["mems"][message.author] = True
                        await client.send_message(message.channel, "{0.mention} has finished getting high on laughing gas.".format(message.author) ,embed=create_em_list_sol(status["mems"]))
                    else:
                        await client.send_message(message.channel, "{0.mention} Easy now boy. No need to be so eager".format(message.author) ,embed=create_em_list_sol(status["mems"]))    
        
        if m == (settings["prefix"] + "unready"):
            for status in status_list:
                if message.channel == status["channel"] and status["schedule"] == True:
                    if status["mems"][message.author] == True:
                        status["mems"][message.author] = False
                        await client.send_message(message.channel, "{0.mention} decided he has enough and is gonna go grab some more laughing gas.".format(message.author) ,embed=create_em_list_sol(status["mems"]))
                    else:
                        await client.send_message(message.channel, "{0.mention} Don't try to be a smartass.".format(message.author) ,embed=create_em_list_sol(status["mems"]))
                    break    

        if m.startswith(settings["prefix"] + "prefix"):
            dmsg, tmsg = m.split("prefix")
            new_prefix = tmsg.strip()
            if not new_prefix:
                return await client.send_message(message.channel, "Your prefix is currently **" + settings["prefix"]+ "**")
            if new_prefix == "prefix":
                return await client.send_message(message.channel, "Prefix cannot be prefix. Don't try to be a smartass")
            settings["prefix"] = new_prefix
            await client.send_message(message.channel, "Congrats. Your new prefix is **"+ settings["prefix"]+ "**. Don't forget.")

        if m.startswith(settings["prefix"] + "schedule"):
            msg = "You have called for your comrads to go to battle in {}. Type **" + settings["prefix"] + "ready** after you finished wearing your diapers.".format(m[len("t!schedule"):].strip())
            listsol = ""
            
            mems = {}
            for mem in message.channel.server.members:
                if mem == client.user or mem.bot:
                    continue
                listsol += "{0.mention}: Not Ready\n".format(mem)
                mems[mem] = False
            em = discord.Embed(title ='Soldiers', description=listsol)

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
    em = discord.Embed(title ='Soldiers', description=listsol)
    return em

def check_all_ready(status):
    for mem, status in status["mems"].items():
        if not status:
            return False
    return True


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







