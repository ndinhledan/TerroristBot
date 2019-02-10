import discord
import time
import datetime
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json


''' TODO 
make every function asynchronous so that there is no delay
pee 

'''

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client_sheet = gspread.authorize(creds)
sheet = client_sheet.open('Credit Score')

with open("bot_info.json") as file:
	bot_data = json.load(file)


TOKEN = bot_data["token"]

client = discord.Client()

settings = {
	"prefix": "t!"
}

units = ["hours", "minutes", "seconds"]
units.extend([t[:-1] for t in units])

status_list = [

	]


command_list = [
	"hello", "link", "mem", "prefix", "rules","schedule", "ready", "unready", "cancel", "status", "reset_credit", "add_credit", "minus_credit"
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
	"add_credit": "**" + settings["prefix"] + '''add_credit <person> <amount> <reason>**
Example: **''' + settings["prefix"] + '''add_credit TerroristBot 100**''',
	"minus_credit": "**" + settings["prefix"] + '''minus_credit <person> <amount> <reason>**
Example: **''' + settings["prefix"] + '''minus_credit TerroristBot 100**''',


}

pre_text = '''

Use **''' + settings["prefix"]+ '''schedule <time>** to schedule your battle
For example ** ''' + settings["prefix"] + '''schedule 2 hours 20 minutes**

My current prefix is ''' + settings["prefix"] + '''
To change prefix use **<prefix>prefix <new prefix>**

'''
rule_text = ''' 
Each person starts with 1000 credit points.
Every time a battle is scheduled, you will have as late as 10 minutes to ready up.

If you ready up early, 15 points will be awarded to your credit score, up to maximum of 1000.
If you ready up within 10 minutes late, you will receive no deduction

However,
	-20 minutes late, 5 points will be deducted
	-30 minutes late, 10 points will be deducted
	-1 hour late, 15 points will be deducted
	-After 2 hours, 20 points will be deducted
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

		if m == (settings["prefix"] + "test"):
			await client.send_message(message.channel, message.channel.server.name)
		
		# Hello world

		if m.startswith(settings["prefix"] + "hello"):
			msg = "How dare you say hello to me. I am your general. Show some respect. {0.author.mention} do 50 push ups for me".format(message)
			await client.send_message(message.channel, msg)

			
		if m.startswith(settings["prefix"] + "link"):
			em = discord.Embed(title='Link to Credit Score', colour=0xDEADBF, url="https://docs.google.com/spreadsheets/d/1CNsWa3avZbJRTpsxBGGy-iKTEaQ9__WaX_Oe3UNVd1Q/edit?usp=sharing")
			await client.send_message(message.channel, embed=em)
			

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

		if m == (settings["prefix"] + 'rules'):
			return await client.send_message(message.channel, "``` {} ```".format(rule_text))

		# READY SCHEDULE CHECK

		if m == (settings["prefix"] + "ready"):
			client_sheet.login()
			status = find_channel_status(message.channel)
			ready_time = int(time.time())

			ws = get_worksheet(sheet, message.channel.server.name, client, message.channel.server.members)
			cell = ws.find(message.author.name)
			
			score = int(ws.cell(cell.row, 3).value)
				
			if status["schedule"] == True: #ready early    
				if status["mems"][message.author] == False:
					status["mems"][message.author] = True
					await client.send_message(message.channel, "{0.mention} has finished getting high on laughing gas.".format(message.author) ,embed=create_em_list_sol(status["mems"]))
					if score == 1000:
						return await client.send_message(message.channel, "{0.mention} is on perfect score so no points awarded, only a C4!".format(message.author))
					else:
						if score + 15 > 1000:
							ws.update_cell(cell.row, 3, "1000")
						else:    
							ws.update_cell(cell.row, 3, str(score + 15))
						return await client.send_message(message.channel, "15 points have been awarded for {0.mention} for arriving early, or just because I want to".format(message.author))
					
				else:
					await client.send_message(message.channel, "{0.mention} Easy now boy. No need to be so eager".format(message.author) ,embed=create_em_list_sol(status["mems"]))    
			else:
				if status["mems"][message.author] == False:
					status["mems"][message.author] = True
					await client.send_message(message.channel, "{0.mention} has finally figured out the way home.".format(message.author) ,embed=create_em_list_sol(status["mems"]))
					remaining_time = ready_time - status["time"]
					if (remaining_time // 60) < 11: #10 minutes
						return await client.send_message(message.channel, "Luckily {0.mention} arrived within 10 minutes so no points deducted".format(message.author))                 
					else:
						deduction = 0
						if (remaining_time // 60) < 21: #20 minutes
							deduction = 5
						elif (remaining_time // 60) < 31: #30 minutes
							deduction = 10
						elif (remaining_time // 60) < 61: #60 minutes
							deduction = 15
						elif (remaining_time // 60) < 121: #2 hours
							deduction = 20
						else:
							deduction = 30
						ws.update_cell(cell.row, 3, str(score - deduction))
						res = [0,0,0] #hours minutes seconds
						res[0] = remaining_time // 3600
						res[1] = (remaining_time - 3600*res[0]) // 60
						res[2] = remaining_time - 3600*res[0] - 60*res[1]
						return await client.send_message(message.channel, "{0} points has been deducted from {1.mention} for being {2} hours {3} minutes {4} seconds late".format(deduction, message.author, res[0], res[1], res[2]))
				else:
					return await client.send_message(message.channel, "No battle scheduled yet")
					   

		# UNREADY SCHEDULE CHECK

		if m == (settings["prefix"] + "unready"):
			client_sheet.login()
			status = find_channel_status(message.channel)
			if status["schedule"] == True:
				if status["mems"][message.author] == True:
					status["mems"][message.author] = False
					await client.send_message(message.channel, "{0.mention} decided he has enough and is gonna go grab some more laughing gas.".format(message.author) ,embed=create_em_list_sol(status["mems"]))
				else:
					await client.send_message(message.channel, "{0.mention} Don't try to be a smartass. You haven't readied yet".format(message.author) ,embed=create_em_list_sol(status["mems"]))

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

		if m == (settings["prefix"] + "cancel"):
			status = find_channel_status(message.channel)
			if status["schedule"] == True :
				status["schedule"] = False
				await client.send_message(message.channel, "You have canceled your scheduled battle! What a pussy.")
			else :
				await client.send_message(message.channel, "Huh?")

		if m.startswith(settings["prefix"] + "mention"):
			name = m[len(settings["prefix"] + "mention"):].strip()

			for mem in message.channel.server.members:
				if mem.name == name:
					return await client.send_message(message.channel, "Yo {0.mention} hurry up, everyone is waiting! Stop getting high! ".format(mem))
			await client.send_message(message.channel, "Who are you talking to bro?")

		if m == (settings["prefix"] + "reset_credit"):
			client_sheet.login()
			ws = get_worksheet(sheet, message.channel.server.name, client, message.channel.server.members)
		
			reset_credit(client, ws, message.channel.server.members)

			await client.send_message(message.channel, "Everyone's credit has been reset back to 1000")

		if m.startswith(settings["prefix"] + "credit"):
			client_sheet.login()
			dmsg = m[len(settings["prefix"] + "credit"):].strip()
			splits = dmsg.split(" ")
			if not splits or len(splits) != 1:
				return await send_help_text(client, message.channel, "credit")
			name = splits[0]
			ws = get_worksheet(sheet, message.channel.server.name, client, message.channel.server.members)
			try:
				cell = ws.find(name)
				await client.send_message(message.channel, "``" + name + "   ----------   " + ws.cell(cell.row, 3).value + "``")
			except gspread.exceptions.CellNotFound:
				await client.send_message(message.channel, name + " does not exist")

		if m.startswith(settings["prefix"] + "add_credit"):
			client_sheet.login()
			dmsg = m[len(settings["prefix"] + "add_credit"):].strip()
			splits = dmsg.split(" ")
			if not splits or len(splits) < 2:
				return await send_help_text(client, message.channel, "add_credit")
			addee = splits[0]
			amount = splits[1]
			if not amount.isnumeric():
				return await send_help_text(client, message.channel, "add_credit")
			if len(splits) > 2:
				reasons = ' '.join(str(reason) for reason in splits[2::]) 
			else:
				reasons = 'no reasons'
			ws = get_worksheet(sheet, message.channel.server.name, client, message.channel.server.members)
			try:
				cell = ws.find(addee)
				ws.update_cell(cell.row, 3, str(int(ws.cell(cell.row, 3).value) + int(amount)))
				await client.send_message(message.channel, addee + " has been awarded " + amount + " points by the ultimate leader " + message.author.name + " for " + reasons)
			except gspread.exceptions.CellNotFound:
				await client.send_message(message.channel, "Member not found")
			
		if m.startswith(settings["prefix"] + "minus_credit"):
			client_sheet.login()
			dmsg = m[len(settings["prefix"] + "minus_credit"):].strip()
			splits = dmsg.split(" ")
			if not splits or len(splits) < 3:
				return await send_help_text(client, message.channel, "minus_credit")
			addee = splits[0]
			amount = splits[1]
			if not amount.isnumeric():
				return await send_help_text(client, message.channel, "add_credit")
			reasons = ' '.join(str(reason) for reason in splits[2::]) 
			ws = get_worksheet(sheet, message.channel.server.name, client, message.channel.server.members)
			try:
				cell = ws.find(addee)
				ws.update_cell(cell.row, 3, str(int(ws.cell(cell.row, 3).value) - int(amount)))
				await client.send_message(message.channel, addee + " has been punished " + amount + " points by the ultimate leader " + message.author.name + " for " + reasons)
			except gspread.exceptions.CellNotFound:
				await client.send_message(message.channel, "Member not found")
			

		# GAME SCHEDULER


		if m.startswith(settings["prefix"] + "schedule"):
			client_sheet.login()
			status = find_channel_status(message.channel)
			if status == None:
				status = {}
			else:
				if status["schedule"] == True:
					return await client.send_message(message.channel, "A battle has already been scheduled, use **{}cancel** to cancel the battle first if you'd like to".format(settings["prefix"]))
			
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

			res =[0,0,0] #hours, minutes, seconds
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
	offset = 3600*time_arr[0] + 60*time_arr[1] + time_arr[2]
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

def reset_credit(client, worksheet, mems):
	count = 2
	worksheet.update_cell(1, 1, 'Name')
	worksheet.update_cell(1, 3, 'Score')
	for mem in mems:
		if mem == client.user or mem.bot:
			continue
		worksheet.update_cell(count, 1, mem.name)
		worksheet.update_cell(count, 3, '1000')
		print(mem.name)
		count +=1

def get_worksheet(sheet, name, client, mems):
	try:
		ws = sheet.worksheet(name)
	except gspread.exceptions.WorksheetNotFound:
		ws = sheet.add_worksheet(title=name, rows=100, cols=20)
		reset_credit(client, ws, mems)
	return ws

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







