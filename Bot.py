import time
import discord
import sqlite3
import random
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True
intents.presences = True

client = commands.Bot(command_prefix='!', intents=intents, help_command=None, activity = discord.Game('!help', status = discord.Status.online))

connection = sqlite3.connect('server.db')
cursor = connection.cursor()

@client.event
async def on_ready():
	for guild in client.guilds:
		for member in guild.members:
			if cursor.execute(f"SELECT id FROM member WHERE id = {member.id}").fetchone() is None:
				cursor.execute(f"INSERT INTO member VALUES ({member.id}, 0, 0, 0, 0, 0, 0, 0, 0)")
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
	local_cash = f"""{cursor.execute("SELECT cash FROM member WHERE id = {}".format(value)).fetchone()[0]}"""
	local_bank = f"""{cursor.execute("SELECT bank FROM member WHERE id = {}".format(value)).fetchone()[0]}"""
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
			local_cash = f"""{cursor.execute("SELECT cash FROM member WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
			local_cash = int(local_cash)
			commission = local_cash / 100 * 5
			commission = int(commission)
			cursor.execute("UPDATE member SET cash = cash - {} WHERE id = {}".format(local_cash, ctx.author.id))
			cursor.execute("UPDATE member SET bank = bank + {} WHERE id = {}".format(local_cash, ctx.author.id))
			cursor.execute("UPDATE member SET bank = bank - {} WHERE id = {}".format(commission, ctx.author.id))
			cursor.execute("UPDATE server SET commission = commission + {} WHERE id = {}".format(commission, 0))
			await deposit_message(ctx, local_cash - commission, commission, 'Депозит', 'Положил')
		else:
			amount = int(amount)
			if amount <= 0:
				await false_message(ctx, 'Указанная сумма должна быть больше нуля')
			else:
				local_cash = f"""{cursor.execute("SELECT cash FROM member WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
				local_cash = int(local_cash)
				commission = amount / 100 * 5
				commission = int(commission)
				if amount  > local_cash:
					await false_message(ctx, 'На балансе недостаточно денег')
				else:
					cursor.execute("UPDATE member SET cash = cash - {} WHERE id = {}".format(amount, ctx.author.id))
					cursor.execute("UPDATE member SET bank = bank + {} WHERE id = {}".format(amount, ctx.author.id))
					cursor.execute("UPDATE member SET bank = bank - {} WHERE id = {}".format(commission, ctx.author.id))
					cursor.execute("UPDATE server SET commission = commission + {} WHERE id = {}".format(commission, 0))
					await deposit_message(ctx, amount- commission, commission, 'Депозит', 'Положил')

@client.command()
async def withdraw(ctx, amount: str = None):
	if amount is None:
		await false_message(ctx, 'Сумма не была указана')
	else:
		if amount == "all":
			local_bank = f"""{cursor.execute("SELECT bank FROM member WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
			local_bank = int(local_bank)
			commission = local_bank / 100 * 5
			commission = int(commission)
			cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(local_bank, ctx.author.id))
			cursor.execute("UPDATE member SET bank = bank - {} WHERE id = {}".format(local_bank, ctx.author.id))
			cursor.execute("UPDATE member SET bank = cash - {} WHERE id = {}".format(commission, ctx.author.id))
			cursor.execute("UPDATE server SET commission = commission + {} WHERE id = {}".format(commission, 0))
			await deposit_message(ctx, local_bank - commission, commission, 'Обналичивание', 'Снял')
		else:
			amount = int(amount)
			if amount <= 0:
				await false_message(ctx, 'Указанная сумма должна быть больше нуля')
			else:
				local_bank = f"""{cursor.execute("SELECT bank FROM member WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
				local_bank = int(local_bank)
				commission = amount / 100 * 5
				commission = int(commission)
				if amount  > local_bank:
					await false_message(ctx, 'На балансе недостаточно денег')
				else:
					cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(amount, ctx.author.id))
					cursor.execute("UPDATE member SET bank = bank - {} WHERE id = {}".format(amount, ctx.author.id))
					cursor.execute("UPDATE member SET bank = cash - {} WHERE id = {}".format(commission, ctx.author.id))
					cursor.execute("UPDATE server SET commission = commission + {} WHERE id = {}".format(commission, 0))
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
			cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(amount, member.id))
			local_cash = cursor.execute("SELECT cash FROM member WHERE id = {}".format(member.id))
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
			cursor.execute("UPDATE member SET cash = cash - {} WHERE id = {}".format(amount, member.id))
			local_cash = cursor.execute("SELECT cash FROM member WHERE id = {}".format(member.id))
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
			cursor.execute("UPDATE member SET cash = {} WHERE id = {}".format(amount, member.id))
			local_cash = f"""{cursor.execute("SELECT cash FROM member WHERE id = {}".format(member.id)).fetchone()[0]}"""
			await true_message(ctx, 'Установил баланс', member, local_cash)

@client.command()
async def pay(ctx, member: discord.Member = None, amount: str = 0):
	if member is None:
		await false_message(ctx, 'Пользователь не был указан')
	else:
		if amount is None:
			await false_message(ctx, 'Сумма не была указана')
		else:
			if amount == "all":
				local_cash = f"""{cursor.execute("SELECT cash FROM member WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
				local_cash = int(local_cash)
				commission = local_cash / 100 * 5
				commission = int(commission)
				cursor.execute("UPDATE member SET cash = cash - {} WHERE id = {}".format(local_cash, ctx.author.id))
				cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(local_cash, member.id))
				cursor.execute("UPDATE member SET cash = cash - {} WHERE id = {}".format(commission, member.id))
				cursor.execute("UPDATE server SET commission = commission + {} WHERE id = {}".format(commission, 0))
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
					local_cash = f"""{cursor.execute("SELECT cash FROM member WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
					local_cash = int(local_cash)
					if amount > local_cash:
						await false_message(ctx, 'На балансе недостаточно денег')
					else:
						commission = amount / 100 * 5
						commission = int(commission)
						cursor.execute("UPDATE member SET cash = cash - {} WHERE id = {}".format(amount, ctx.author.id))
						cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(amount, member.id))
						cursor.execute("UPDATE member SET cash = cash - {} WHERE id = {}".format(commission, member.id))
						cursor.execute("UPDATE server SET commission = commission + {} WHERE id = {}".format(commission, 0))
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
	for row in cursor.execute("SELECT id, cash, bank FROM member ORDER BY cash DESC LIMIT 5"):
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

async def coin_message(ctx, value, value1, color2):
	emb = discord.Embed(title = 'Монетка', color = color2)
	emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
	emb.add_field(name = 'Результат', value = f'**{value}**')
	emb.add_field(name = 'Сколько', value = f'**{value1}** :coin:')
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()
	connection.commit()

@client.command()
async def coin(ctx, side: str = None, amount: int = 0):
	choice = ['орёл', 'решка']
	random.shuffle(choice)
	local_cash = f"""{cursor.execute("SELECT cash FROM member WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
	local_cash = int(local_cash)
	if amount >= local_cash:
		await false_message(ctx, 'На балансе недостаточно денег')
	elif amount <= 0:
		await false_message(ctx, 'Указанная сумма должна быть больше нуля')
	else:
		if choice[0] == side:
			cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(amount, ctx.author.id))
			cursor.execute("UPDATE server SET gameprofit = gameprofit + {} WHERE id = {}".format(amount, 0))
			cursor.execute("UPDATE server SET gameamount = gameamount + {} WHERE id = {}".format(1, 0))
			await coin_message(ctx, 'Выиграл', amount * 2, 0xB9FFA8)
		else:
			cursor.execute("UPDATE member SET cash = cash - {} WHERE id = {}".format(amount, ctx.author.id))
			cursor.execute("UPDATE server SET gamelossprofit = gamelossprofit + {} WHERE id = {}".format(amount, 0))
			cursor.execute("UPDATE server SET gameamount = gameamount + {} WHERE id = {}".format(1, 0))
			await coin_message(ctx, 'Проиграл', amount, 0xFF7575)

#-------------------------------------------
#      | Работа с библиотекой TIME | 
#-------------------------------------------

async def true_bonus_message(ctx, value, day, hour, min, value2):
	emb = discord.Embed(title = value, color = 0xB9FFA8)
	emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
	emb.add_field(name = 'Следующая', value = f'**через {day}дн {hour}ч {min}м.**')
	emb.add_field(name = 'Заработал', value = f'**{value2}** :coin:')
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()
	connection.commit()

async def false_bonus_message(ctx, day, hour, min):
	emb = discord.Embed(title = '', color = 0xFF7575)
	emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
	emb.add_field(name = f'Этот бонус ещё недоступен, возвращайся **через {day}дн {hour}ч {min}м**.', value = '')
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()

async def time_algorithm(ctx, amount, excerpt, name, abama):
	local_timely = f"""{cursor.execute("SELECT {} FROM member WHERE id = {}".format(abama, ctx.author.id)).fetchone()[0]}"""
	local_timely = float(local_timely)
	realtime = time.time()
	if local_timely == 0:
		localgm_time = time.gmtime(abs(excerpt))
		cursor.execute("UPDATE member SET {} = {} WHERE id = {}".format(abama, realtime, ctx.author.id))
		cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(amount, ctx.author.id))
		cursor.execute("UPDATE server SET bonusamount = bonusamount + {} WHERE id = {}".format(amount, 0))
		await true_bonus_message(ctx, name, localgm_time.tm_mday - 1, localgm_time.tm_hour, localgm_time.tm_min, amount)
	else:
		localgm_time = time.gmtime(abs(excerpt - (realtime - local_timely)))
		if realtime - local_timely > excerpt:
			cursor.execute("UPDATE member SET {} = {} WHERE id = {}".format(abama, realtime, ctx.author.id))
			cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(amount, ctx.author.id))
			cursor.execute("UPDATE server SET bonusamount = bonusamount + {} WHERE id = {}".format(amount, 0))
			await true_bonus_message(ctx, name, localgm_time.tm_mday - 1, localgm_time.tm_hour, localgm_time.tm_min, amount)
		else:
			await false_bonus_message(ctx, localgm_time.tm_mday - 1, localgm_time.tm_hour, localgm_time.tm_min)

@client.command()
async def timely(ctx):
	await time_algorithm(ctx, 500, 21600, 'Почасовой бонус', 'timely')

@client.command()
async def daily(ctx):
	await time_algorithm(ctx, 1250, 86400, 'Ежедневный бонус', 'daily')

@client.command()
async def weekly(ctx):
	await time_algorithm(ctx, 4750, 604800, 'Еженедельный бонус', 'weekly')

@client.command()
async def monthly(ctx):
	await time_algorithm(ctx, 11000, 2592000, 'Ежемесячный бонус', 'monthly')

@client.command()
async def work(ctx):
	rand = random.randrange(0, 19)
	local_work = f"""{cursor.execute("SELECT work FROM member WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
	local_jobs = f"""{cursor.execute("SELECT name FROM ability WHERE id = {}".format(rand)).fetchone()[0]}"""
	local_salary = f"""{cursor.execute("SELECT salary FROM ability WHERE id = {}".format(rand)).fetchone()[0]}"""
	local_work = float(local_work)
	local_salary = int(local_salary)
	realtime = time.time()
	if local_work == 0:
		localgm_time = time.gmtime(abs(14400))
		cursor.execute("UPDATE member SET work = {} WHERE id = {}".format(realtime, ctx.author.id))
		cursor.execute("UPDATE server SET workamount = workamount + {} WHERE id = {}".format(local_salary, 0))
		cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(local_salary, ctx.author.id))
		emb = discord.Embed(title = 'Работа', color = 0xB9FFA8)
		emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
		emb.add_field(name = 'Следующая', value = f'**через {localgm_time.tm_mday - 1}дн {localgm_time.tm_hour}ч {localgm_time.tm_min}м.**')
		emb.add_field(name = 'Профессия', value = f'**{local_jobs}**')
		emb.add_field(name = 'Заработал', value = f'**{local_salary}** :coin:')
		emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
		await ctx.send(embed = emb)
		await ctx.message.delete()
		connection.commit()
	else:
		localgm_time = time.gmtime(abs(14400 - (realtime - local_work)))
		if realtime - local_work > 14400:
			cursor.execute("UPDATE member SET work = {} WHERE id = {}".format(realtime, ctx.author.id))
			cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(local_salary, ctx.author.id))
			emb = discord.Embed(title = 'Работа', color = 0xB9FFA8)
			emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
			emb.add_field(name = 'Следующая', value = f'**через {localgm_time.tm_mday - 1}дн {localgm_time.tm_hour}ч {localgm_time.tm_min}м.**')
			emb.add_field(name = 'Профессия', value = f'**{local_jobs}**')
			emb.add_field(name = 'Заработал', value = f'**{local_salary}** :coin:')
			emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
			await ctx.send(embed = emb)
			await ctx.message.delete()
			connection.commit()
		else:
			await false_bonus_message(ctx, localgm_time.tm_mday - 1, localgm_time.tm_hour, localgm_time.tm_min)

async def wardengardenspraheng(ctx, number, gardenwarden, color2):
	wardengarder = f"""{cursor.execute("SELECT cause FROM ability WHERE id = {}".format(gardenwarden)).fetchone()[0]}"""
	emb = discord.Embed(title = ' ', color = color2)
	emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
	emb.add_field(name = f'{wardengarder} {number} :coin:', value = ' ')
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()
	connection.commit()

@client.command()
async def event(ctx):
	number = random.randrange(-75, 150)
	local_cash = f"""{cursor.execute("SELECT cash FROM member WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
	local_cash = float(local_cash)
	if number >= 0:
		gardenwarden = random.randrange(0, 10)
		cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(number, ctx.author.id))
		cursor.execute("UPDATE server SET bonusamount = bonusamount + {} WHERE id = {}".format(number, 0))
		await wardengardenspraheng(ctx, number, gardenwarden, 0xB9FFA8)
	else:
		number = abs(number)
		gardenwarden = random.randrange(11, 20)
		if local_cash < number:
			cursor.execute("UPDATE member SET cash = {} WHERE id = {}".format(0, ctx.author.id))
		else:
			cursor.execute("UPDATE member SET cash = cash - {} WHERE id = {}".format(number, ctx.author.id))
		await wardengardenspraheng(ctx, number, gardenwarden, 0xFF7575)
	
async def darbumverde(ctx, color2, gardenwarden, commission, coin):
	emb = discord.Embed(title = 'Ограбление', color = color2)
	emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
	emb.add_field(name = f'{gardenwarden} {commission} {coin}', value = ' ')
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()
	connection.commit()
	
@client.command()
async def rob(ctx, member: discord.Member = None):
	realtime = time.time()
	if member is None:
		await false_message(ctx, 'Пользователь не был указан')
	else:
		local_rob = f"""{cursor.execute("SELECT rob FROM member WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
		local_cash = f"""{cursor.execute("SELECT cash FROM member WHERE id = {}".format(member.id)).fetchone()[0]}"""
		local_rob = float(local_rob)
		local_cash = int(local_cash)
		commission = random.randint(int(local_cash * 0.5), local_cash)
		localgm_time = time.gmtime(abs(43200 - (realtime - local_rob)))
		if local_rob == 0:
			gardenwarden = random.randint(0, 10)
			local_trash = f"""{cursor.execute("SELECT robtext FROM ability WHERE id = {}".format(gardenwarden)).fetchone()[0]}"""
			cursor.execute("UPDATE member SET rob = {} WHERE id = {}".format(realtime, ctx.author.id))
			cursor.execute("UPDATE server SET robamount = robamount + {} WHERE id = {}".format(commission, 0))
			cursor.execute("UPDATE member SET cash = cash - {} WHERE id = {}".format(commission, member.id))
			cursor.execute("UPDATE server SET commission = commission + {} WHERE id = {}".format(commission, 0))
			await darbumverde(ctx, 0xB9FFA8, local_trash, commission, ':coin:')
		else:
			if realtime - local_rob > 43200:
				randoma = random.randint(0, 100)
				if randoma > 60:
					gardenwarden = random.randint(0, 10)
					cursor.execute("UPDATE member SET rob = {} WHERE id = {}".format(realtime, ctx.author.id))
					local_trash = f"""{cursor.execute("SELECT robtext FROM ability WHERE id = {}".format(gardenwarden)).fetchone()[0]}"""
					await darbumverde(ctx, 0xB9FFA8, local_trash, commission, ':coin:')
				else:
					gardenwarden = random.randint(11, 20)
					cursor.execute("UPDATE member SET rob = {} WHERE id = {}".format(realtime, ctx.author.id))
					cursor.execute("UPDATE member SET cash = cash - {} WHERE id = {}".format(commission, member.id))
					local_trash = f"""{cursor.execute("SELECT robtext FROM ability WHERE id = {}".format(gardenwarden)).fetchone()[0]}"""
					await darbumverde(ctx, 0xFF7575, local_trash, ' ', ' ')
			else:
				await false_bonus_message(ctx, localgm_time.tm_mday - 1, localgm_time.tm_hour, localgm_time.tm_min)

async def slots_message(ctx, tcolor, ffieldtext, sfieldtext, fdfieldtext):
	emb = discord.Embed(title = 'Слоты', color = tcolor)
	emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
	emb.add_field(name = 'Результат', value = f'{ffieldtext}')
	emb.add_field(name = fdfieldtext, value = f'**{sfieldtext} **:coin:')
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()
	connection.commit()

@client.command()
async def slots(ctx, amount: int = 0):
	local_cash = f"""{cursor.execute("SELECT cash FROM member WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
	local_cash = int(local_cash)
	if amount >= local_cash:
		await false_message(ctx, 'На балансе недостаточно денег')
	elif amount <= 0:
		await false_message(ctx, 'Указанная сумма должна быть больше нуля')
	else:
		choice = [':dollar:', ':euro:', ':pound:'] * 3
		random.shuffle(choice)
		if choice[0] == choice[1] == choice[2]:
			local_amount = int(amount * 20)
			cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(local_amount, ctx.author.id))
			cursor.execute("UPDATE server SET gameprofit = gameprofit + {} WHERE id = {}".format(local_amount, 0))
			cursor.execute("UPDATE server SET gameamount = gameamount + {} WHERE id = {}".format(1, 0))
			await slots_message(ctx, 0xB9FFA8, choice[0] + " " + choice[1] + " " + choice[2], local_amount, 'Выигрыш')
		elif choice[0] == choice[1] or choice[1] == choice[2]:
			local_amount = int(amount * 1.5)
			cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(local_amount, ctx.author.id))
			cursor.execute("UPDATE server SET gameprofit = gameprofit + {} WHERE id = {}".format(local_amount, 0))
			cursor.execute("UPDATE server SET gameamount = gameamount + {} WHERE id = {}".format(1, 0))
			await slots_message(ctx, 0xB9FFA8, choice[0] + " " + choice[1] + " " + choice[2], local_amount, 'Выигрыш')
		else:
			cursor.execute("UPDATE member SET cash = cash - {} WHERE id = {}".format(amount, ctx.author.id))
			cursor.execute("UPDATE server SET gamelossprofit = gamelossprofit + {} WHERE id = {}".format(amount, 0))
			await slots_message(ctx, 0xFF7575, choice[0] + " " + choice[1] + " " + choice[2], amount, 'Проигрышы')

async def revolver_message(ctx, tcolor, ffieldtext, sfieldtext, fdfieldtext):
	emb = discord.Embed(title = 'Револьвер', color = tcolor)
	emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar)
	emb.add_field(name = 'Результат', value = f'{ffieldtext}')
	emb.add_field(name = fdfieldtext, value = f'**{sfieldtext} **:coin:')
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()
	connection.commit()

@client.command()
async def revolver(ctx, amount: int = 0):
	local_cash = f"""{cursor.execute("SELECT cash FROM member WHERE id = {}".format(ctx.author.id)).fetchone()[0]}"""
	local_cash = int(local_cash)
	choice = [':cd:', ':dvd:', ':dvd:', ':dvd:', ':dvd:']
	random.shuffle(choice)
	if amount >= local_cash:
		await false_message(ctx, 'На балансе недостаточно денег')
	elif amount <= 0:
		await false_message(ctx, 'Указанная сумма должна быть больше нуля')
	else:
		if choice[0] == ':cd:':
			local_amount = int(amount * 5)
			cursor.execute("UPDATE member SET cash = cash + {} WHERE id = {}".format(local_amount, ctx.author.id))
			cursor.execute("UPDATE server SET gameprofit = gameprofit + {} WHERE id = {}".format(local_amount, 0))
			cursor.execute("UPDATE server SET gameamount = gameamount + {} WHERE id = {}".format(1, 0))
			await revolver_message(ctx, 0xB9FFA8, choice[0] + " " + choice[1] + " " + choice[2] + " " + choice[3] + " " + choice[4], local_amount, 'Выигрыш')
		else:
			cursor.execute("UPDATE member SET cash = cash - {} WHERE id = {}".format(amount, ctx.author.id))
			cursor.execute("UPDATE server SET gamelossprofit = gamelossprofit + {} WHERE id = {}".format(amount, 0))
			cursor.execute("UPDATE server SET gameamount = gameamount + {} WHERE id = {}".format(1, 0))
			await revolver_message(ctx, 0xFF7575, choice[0] + " " + choice[1] + " " + choice[2] + " " + choice[3] + " " + choice[4], amount, 'Проигрышы')

@client.command()
async def help(ctx):
	emb = discord.Embed(title = 'Команды', color = 0xB9FFA8)
	emb.set_author(name = ctx.guild.name, icon_url = ctx.guild.icon.url)
	emb.add_field(name = 'Экономические', value = '`balance` `deposit` `withdraw` `pay` `give` `take` `set` `leaderboard` `coin` `revolver` `work` `timely` `daily` `weekly` `monthly` `slots` `rob` `event`', inline = False)
	emb.add_field(name = 'Административные', value = '`ban` `kick` `mute`', inline = False)
	emb.set_image(url = "https://cdn.discordapp.com/attachments/1093147291327668335/1093250649338167296/unknown_11.png")
	await ctx.send(embed = emb)
	await ctx.message.delete()

client.run('MTA5MTI5MTcwMjM5ODAyNTc1OQ.GL9Tgc.QLVH-UPlVi901JCn0c-pMg0SyHu19ItWpUoAWM')