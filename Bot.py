import discord
from discord.ext import commands

import sqlite3
from config import settings

intents = discord.Intents.all()
intents.members = True
intents.presences = True

client = commands.Bot(command_prefix='!', intents=intents, help_command=None, activity = discord.Game('!help', status = discord.Status.online))

connection = sqlite3.connect('server.db')
cursor = connection.cursor()

@client.event
async def on_ready():
	#cursor.execute("""CREATE TABLE users (
	#	name TEXT,
	#	id INT,
	#	cash BIGINT,
	#	bank BIGINT,
	#	rep INT,
	#	lvl INT
	#)""")

	for guild in client.guilds:
		for member in guild.members:
			if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
				cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 0, 0)")
			else:
				pass

@client.event
async def on_member_join(member):
	if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
		cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 0, 0)")
		connection.commit()
	else:
		pass

@client.command()
async def balance(ctx, member: discord.Member = None):
	if member is None:
		await ctx.send(embed = discord.Embed(	
			description = f"""User balance **{ctx.author}** is **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} :leaves:**"""
			
			))
	else:
		await ctx.send(embed = discord.Embed(
			description = f"""User balance **{member}** is **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]}**"""

			))


client.run('MTA5MTI5MTcwMjM5ODAyNTc1OQ.GxR3SB.PWy0P8Vp1nsoVnaVfbQrtI66Zx2hg-vVmSxjrA')