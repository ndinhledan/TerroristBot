import discord
import asyncio
import oauth2client
import json
import Bot.py

if m.startswith(settings["prefix"] + "hello"):
    msg = "How dare you say hello to me. I am your general. Show some respect. {0.author.mention} do 50 push ups for me".format(message)
    await client.send_message(message.channel, msg)
