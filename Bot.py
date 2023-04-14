﻿import time
import discord
import sqlite3
import random
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True
intents.presences = True

client = commands.Bot(command_prefix='/', intents=intents, help_command=None, activity = discord.Game('!help', status = discord.Status.online))

connection = sqlite3.connect('server.db')
cursor = connection.cursor()

@client.event
async def on_member_join(member):
	if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
		cursor.execute(f"INSERT INTO users VALUES ({member.id}, 0, 0, 0, 0, 0, 0, 0, 0, 0)")
		connection.commit()
	else:
		pass

async def false_message(ctx, value):
	emb = discord.Embed(title = '', color = 0xFF7575)
	emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
	emb.add_field(name = f'**{value}.**', value = '')
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()

async def true_message(ctx, value1, member, cash):
	emb = discord.Embed(title = f'{value1}', color = 0xB9FFA8)
	emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
	emb.add_field(name = 'Кому', value =f"**{member.mention}**")
	emb.add_field(name = 'Сколько', value = f"**{cash}** :coin:")
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()
	connection.commit()

async def balance_message(ctx, value, value1, value2):
	emb = discord.Embed(title = 'Баланс', color = 0xB9FFA8)
	emb.set_author(name = value1, icon_url = value2)
	local_cash = f"""{cursor.execute("SELECT cash FROM users WHERE id = {}".format(value)).fetchone()[0]}"""
	local_bank = f"""{cursor.execute("SELECT bank FROM users WHERE id = {}".format(value)).fetchone()[0]}"""
	local_cash = int(local_cash)
	local_bank = int(local_bank)
	emb.add_field(name = 'Наличные', value = f"**{local_cash}** :coin:")
	emb.add_field(name = 'В банке', value = f"**{local_bank}** :coin:")
	emb.add_field(name = 'В общем', value = f"**{local_cash + local_bank}** :coin:")
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()
	connection.commit()

async def deposit_message(ctx, value, value1, value2, value3):
	emb = discord.Embed(title = value2, color = 0xB9FFA8)
	emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
	emb.add_field(name = value3, value = f":coin: **{value}**")
	emb.add_field(name = 'Комиссия 5%', value = f":coin: **{value1}**")
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()
	connection.commit()

@client.command()
async def balance(ctx, member: discord.Member = None):
	if member is None:
		await balance_message(ctx, ctx.author.id, ctx.author.name, ctx.author.avatar)
	else:
		await balance_message(ctx, member.id, member.name, member.avatar)

@client.command()
async def deposit(ctx, amount: str = None):
	if amount is None:
		await false_message(ctx, 'Сумма не была указана')
	else:
		if amount == "all":
			local_cash = f"""{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
			local_cash = int(local_cash)
			commission = local_cash / 100 * 5
			commission = int(commission)
			cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(local_cash, ctx.author.id))
			cursor.execute("UPDATE users SET bank = bank + {} WHERE id = {}".format(local_cash, ctx.author.id))
			cursor.execute("UPDATE users SET bank = bank - {} WHERE id = {}".format(commission, ctx.author.id))
			await deposit_message(ctx, local_cash - commission, commission, 'Депозит', 'Положил')
		else:
			amount = int(amount)
			if amount <= 0:
				await false_message(ctx, 'Указанная сумма должна быть больше нуля')
			else:
				local_cash = f"""{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
				local_cash = int(local_cash)
				commission = amount / 100 * 5
				commission = int(commission)
				if amount  > local_cash:
					await false_message(ctx, 'На балансе недостаточно денег')
				else:
					cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(amount, ctx.author.id))
					cursor.execute("UPDATE users SET bank = bank + {} WHERE id = {}".format(amount, ctx.author.id))
					cursor.execute("UPDATE users SET bank = bank - {} WHERE id = {}".format(commission, ctx.author.id))
					await deposit_message(ctx, amount- commission, commission, 'Депозит', 'Положил')

@client.command()
async def withdraw(ctx, amount: str = None):
	if amount is None:
		await false_message(ctx, 'Сумма не была указана')
	else:
		if amount == "all":
			local_bank = f"""{cursor.execute("SELECT bank FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
			local_bank = int(local_bank)
			commission = local_bank / 100 * 5
			commission = int(commission)
			cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(local_bank, ctx.author.id))
			cursor.execute("UPDATE users SET bank = bank - {} WHERE id = {}".format(local_bank, ctx.author.id))
			cursor.execute("UPDATE users SET bank = cash - {} WHERE id = {}".format(commission, ctx.author.id))
			await deposit_message(ctx, local_bank - commission, commission, 'Обналичивание', 'Снял')
		else:
			amount = int(amount)
			if amount <= 0:
				await false_message(ctx, 'Указанная сумма должна быть больше нуля')
			else:
				local_bank = f"""{cursor.execute("SELECT bank FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
				local_bank = int(local_bank)
				commission = amount / 100 * 5
				commission = int(commission)
				if amount  > local_bank:
					await false_message(ctx, 'На балансе недостаточно денег')
				else:
					cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, ctx.author.id))
					cursor.execute("UPDATE users SET bank = bank - {} WHERE id = {}".format(amount, ctx.author.id))
					cursor.execute("UPDATE users SET bank = cash - {} WHERE id = {}".format(commission, ctx.author.id))
					await deposit_message(ctx, amount - commission, commission, 'Обналичивание', 'Снял')

@client.command()
@commands.has_permissions( administrator = True)
async def give(ctx, member: discord.Member = None, amount: int = None):
	if member is None:
		await false_message(ctx, 'Пользователь не был указан')
	else:
		if amount is None:
			await false_message(ctx, 'Сумма не была указана')
		elif amount < 1:
			await false_message(ctx, 'Указанная сумма должна быть больше нуля')
		else:
			cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))
			local_cash = cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id))
			await true_message(ctx, 'Добавил к балансу', member, amount)

@client.command()
@commands.has_permissions( administrator = True)
async def take(ctx, member: discord.Member = None, amount: int = None):
	if member is None:
		await false_message(ctx, 'Пользователь не был указан')
	else:
		if amount is None:
			await false_message(ctx, 'Сумма не была указана')
		elif amount < 1:
			await false_message(ctx, 'Указанная сумма должна быть больше нуля')
		else:
			cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(amount, member.id))
			local_cash = cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id))
			await true_message(ctx, 'Cнял с баланса', member, amount)

@client.command()
@commands.has_permissions( administrator = True)
async def set(ctx, member: discord.Member = None, amount: int = None):
	if member is None:
		await false_message(ctx, 'Пользователь не был указан')
	else:
		if amount is None:
			await false_message(ctx, 'Сумма не была указана')
		elif amount < 0:
			await false_message(ctx, 'Указанная сумма должна быть больше нуля')
		else:
			cursor.execute("UPDATE users SET cash = {} WHERE id = {}".format(amount, member.id))
			local_cash = f"""{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]}"""
			await true_message(ctx, 'Установил баланс', member, local_cash)

@client.command()
async def pay(ctx, member: discord.Member = None, amount: str = None):
	if member is None:
		await false_message(ctx, 'Пользователь не был указан')
	else:
		if amount is None:
			await false_message(ctx, 'Сумма не была указана')
		else:
			if amount == "all":
				local_cash = f"""{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
				local_cash = int(local_cash)
				commission = local_cash / 100 * 5
				commission = int(commission)
				cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(local_cash, ctx.author.id))
				cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(local_cash, member.id))
				cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(commission, member.id))
				emb = discord.Embed(title = 'Заплатил', color = 0xB9FFA8)
				emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
				emb.add_field(name = 'Кому', value =f"**{member.mention}**")
				emb.add_field(name = 'Сколько', value = f"**{local_cash - commission}** :coin:")
				emb.add_field(name = 'Комиссия 5%', value = f"**{commission}** :coin:")
				emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
				await ctx.send(embed = emb)
				await ctx.message.delete()
				connection.commit()
			else:
				amount = int(amount)
				if amount < 1:
					await false_message(ctx, 'Указанная сумма должна быть больше нуля')
				else:
					local_cash = f"""{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
					local_cash = int(local_cash)
					if amount > local_cash:
						await false_message(ctx, 'На балансе недостаточно денег')
					else:
						commission = amount / 100 * 5
						commission = int(commission)
						cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(amount, ctx.author.id))
						cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))
						cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(commission, member.id))
						emb = discord.Embed(title = 'Заплатил', color = 0xB9FFA8)
						emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
						emb.add_field(name = 'Кому', value =f"**{member.mention}**")
						emb.add_field(name = 'Сколько', value = f"**{amount - commission}** :coin:")
						emb.add_field(name = 'Комиссия 5%', value = f"**{commission}** :coin:")
						emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
						await ctx.send(embed = emb)
						await ctx.message.delete()
						connection.commit()

@client.command()
async def leaderboard(ctx):
	emb = discord.Embed(title = 'Список лидеров', color = 0xB9FFA8)
	emb.set_author(name = ctx.guild.name, icon_url = ctx.guild.icon.url)
	emb.add_field(name = 'Место', value ='', inline = True)
	emb.add_field(name = 'Пользователи', value ='', inline = True)
	emb.add_field(name = 'Баланс', value ='', inline = True)
	emb.add_field(name = '', value ='', inline = False)
	counter = 0
	for row in cursor.execute("SELECT id, cash, bank FROM users ORDER BY cash DESC LIMIT 10"):
		counter += 1
		emb.add_field(name = '', value = f'**#{counter}**', inline = True)
		emb.add_field(name = '', value = f"<@{row[0]}>", inline = True)
		local_cash = row[1]
		local_bank = row[2]
		emb.add_field(name = '', value = f'**{local_cash + local_bank}** :coin:', inline = True)
		emb.add_field(name = '', value ='', inline = False)
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()

async def coin_message(ctx, value, value1):
	emb = discord.Embed(title = f'{value}', color = 0xFF7575)
	emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
	emb.add_field(name = 'Сколько', value = f'**{value1}** :coin:')
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()

@client.command()
async def coin(ctx, side: str = None, amount: int = None):
	choice = ['орёл', 'решка']
	random.shuffle(choice)
	local_cash = f"""{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
	local_cash = int(local_cash)
	if amount >= local_cash:
		await false_message(ctx, 'На балансе недостаточно денег')
	elif amount <= 0:
		await false_message(ctx, 'Указанная сумма должна быть больше нуля')
	else:
		print(choice[0], side)
		if choice[0] == side:
			await coin_message(ctx, 'Выиграл', amount)
			cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, ctx.author.id))
		else:
			await coin_message(ctx, 'Проиграл', amount)
			cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(amount, ctx.author.id))

async def time_message(ctx, value, value1):
	emb = discord.Embed(title = value, color = 0xFF7575)
	emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
	emb.add_field(name = 'Заработал', value = f'**{value1}** :coin:')
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()

@client.command()
async def work(ctx):
	cursor.execute("SELECT * FROM jobs ORDER BY amount")
	local_name = cursor.execute("SELECT salary FROM jobs ORDER BY salary LIMIT 1")
	await ctx.send(local_name)
	local_work = f"""{cursor.execute("SELECT work FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
	local_work = float(local_work)
	if local_work == 0:
		realtime = time.time()
		cursor.execute("UPDATE users SET work = {} WHERE id = {}".format(realtime, ctx.author.id))
	else:
		realtime = time.time()
		if realtime - local_work > 1:
			pass
		else:
			await false_message(ctx, 'Прошло недостаточно времени с прошлой работы')


client.run('MTA5MTI5MTcwMjM5ODAyNTc1OQ.GxR3SB.PWy0P8Vp1nsoVnaVfbQrtI66Zx2hg-vVmSxjrA')