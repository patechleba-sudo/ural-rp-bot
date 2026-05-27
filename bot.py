import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import random
import asyncio

# ——— SETUP ———
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ——— EKONOMIKA (ukládání dat) ———
def load_economy():
    if os.path.exists("economy.json"):
        with open("economy.json", "r") as f:
            return json.load(f)
    return {}

def save_economy(data):
    with open("economy.json", "w") as f:
        json.dump(data, f)

def get_balance(user_id):
    data = load_economy()
    return data.get(str(user_id), 0)

def add_balance(user_id, amount):
    data = load_economy()
    data[str(user_id)] = data.get(str(user_id), 0) + amount
    save_economy(data)

# ——— BOT READY ———
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot je online jako {bot.user}")

# ═══════════════════════════════════════
#           MODERACE (15 příkazů)
# ═══════════════════════════════════════

@tree.command(name="ban", description="Banuje uživatele")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Bez důvodu"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"🔨 {user.mention} byl zabanován. Důvod: {reason}")

@tree.command(name="unban", description="Odbanuje uživatele podle ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    await interaction.response.send_message(f"✅ {user.name} byl odbanován.")

@tree.command(name="kick", description="Vykopne uživatele")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Bez důvodu"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"👢 {user.mention} byl vykopnut. Důvod: {reason}")

@tree.command(name="mute", description="Umlčí uživatele na X minut")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, user: discord.Member, minutes: int):
    import datetime
    duration = datetime.timedelta(minutes=minutes)
    await user.timeout(duration)
    await interaction.response.send_message(f"🔇 {user.mention} byl umlčen na {minutes} minut.")

@tree.command(name="unmute", description="Odmlčí uživatele")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, user: discord.Member):
    await user.timeout(None)
    await interaction.response.send_message(f"🔊 {user.mention} byl odmlčen.")

@tree.command(name="clear", description="Smaže X zpráv")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer()
    await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🗑️ Smazáno {amount} zpráv.", ephemeral=True)

@tree.command(name="warn", description="Varuje uživatele")
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    await interaction.response.send_message(f"⚠️ {user.mention} dostal varování! Důvod: {reason}")

@tree.command(name="slowmode", description="Nastaví slowmode v kanálu (sekundy)")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏱️ Slowmode nastaven na {seconds} sekund.")

@tree.command(name="lock", description="Zamkne kanál")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("🔒 Kanál byl zamčen.")

@tree.command(name="unlock", description="Odemkne kanál")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = True
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("🔓 Kanál byl odemčen.")

@tree.command(name="serverinfo", description="Informace o serveru")
async def serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    embed = discord.Embed(title=g.name, color=discord.Color.blue())
    embed.add_field(name="Členů", value=g.member_count)
    embed.add_field(name="Kanálů", value=len(g.channels))
    embed.add_field(name="Vytvořen", value=g.created_at.strftime("%d.%m.%Y"))
    await interaction.response.send_message(embed=embed)

@tree.command(name="userinfo", description="Informace o uživateli")
async def userinfo(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(title=str(user), color=discord.Color.green())
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Na serveru od", value=user.joined_at.strftime("%d.%m.%Y"))
    embed.add_field(name="Účet vytvořen", value=user.created_at.strftime("%d.%m.%Y"))
    embed.set_thumbnail(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@tree.command(name="ping", description="Zobrazí ping bota")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

@tree.command(name="role", description="Přidá roli uživateli")
@app_commands.checks.has_permissions(manage_roles=True)
async def role(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    await user.add_roles(role)
    await interaction.response.send_message(f"✅ {user.mention} dostal roli {role.name}.")

@tree.command(name="removerole", description="Odebere roli uživateli")
@app_commands.checks.has_permissions(manage_roles=True)
async def removerole(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    await user.remove_roles(role)
    await interaction.response.send_message(f"✅ {user.mention} ztratil roli {role.name}.")

# ═══════════════════════════════════════
#           EKONOMIKA (20 příkazů)
# ═══════════════════════════════════════

@tree.command(name="balance", description="Zobrazí tvůj zůstatek")
async def balance(interaction: discord.Interaction):
    bal = get_balance(interaction.user.id)
    await interaction.response.send_message(f"💰 Máš **{bal} coinů**.")

@tree.command(name="daily", description="Vezmi si denní odměnu")
async def daily(interaction: discord.Interaction):
    amount = random.randint(50, 150)
    add_balance(interaction.user.id, amount)
    await interaction.response.send_message(f"🎁 Dostal jsi **{amount} coinů**!")

@tree.command(name="work", description="Vydělej si coiny prací")
async def work(interaction: discord.Interaction):
    amount = random.randint(20, 80)
    add_balance(interaction.user.id, amount)
    jobs = ["programátor", "kuchař", "řidič", "učitel", "zahradník"]
    await interaction.response.send_message(f"💼 Pracoval jsi jako {random.choice(jobs)} a vydělal **{amount} coinů**!")

@tree.command(name="give", description="Daruj coiny jinému hráči")
async def give(interaction: discord.Interaction, user: discord.Member, amount: int):
    if get_balance(interaction.user.id) < amount:
        await interaction.response.send_message("❌ Nemáš dost coinů!")
        return
    add_balance(interaction.user.id, -amount)
    add_balance(user.id, amount)
    await interaction.response.send_message(f"✅ Dal jsi **{amount} coinů** hráči {user.mention}.")

@tree.command(name="leaderboard", description="Top 10 nejbohatších hráčů")
async def leaderboard(interaction: discord.Interaction):
    data = load_economy()
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)[:10]
    embed = discord.Embed(title="🏆 Žebříček bohatství", color=discord.Color.gold())
    for i, (uid, bal) in enumerate(sorted_data, 1):
        try:
            user = await bot.fetch_user(int(uid))
            embed.add_field(name=f"#{i} {user.name}", value=f"{bal} coinů", inline=False)
        except:
            pass
    await interaction.response.send_message(embed=embed)

@tree.command(name="coinflip", description="Vsaď coiny na hod mincí")
async def coinflip(interaction: discord.Interaction, amount: int, choice: str):
    if get_balance(interaction.user.id) < amount:
        await interaction.response.send_message("❌ Nemáš dost coinů!")
        return
    result = random.choice(["orla", "písmo"])
    if choice.lower() == result:
        add_balance(interaction.user.id, amount)
        await interaction.response.send_message(f"🪙 Padlo **{result}** — vyhrál jsi **{amount} coinů**!")
    else:
        add_balance(interaction.user.id, -amount)
        await interaction.response.send_message(f"🪙 Padlo **{result}** — prohrál jsi **{amount} coinů**!")

@tree.command(name="slots", description="Zahraj si automaty")
async def slots(interaction: discord.Interaction, amount: int):
    if get_balance(interaction.user.id) < amount:
        await interaction.response.send_message("❌ Nemáš dost coinů!")
        return
    emojis = ["🍒", "🍋", "🍊", "💎", "7️⃣"]
    result = [random.choice(emojis) for _ in range(3)]
    display = " | ".join(result)
    if result[0] == result[1] == result[2]:
        win = amount * 5
        add_balance(interaction.user.id, win)
        await interaction.response.send_message(f"🎰 {display}\n🎉 JACKPOT! Vyhrál jsi **{win} coinů**!")
    elif result[0] == result[1] or result[1] == result[2]:
        win = amount
        add_balance(interaction.user.id, win)
        await interaction.response.send_message(f"🎰 {display}\n✅ Pár! Vyhrál jsi **{win} coinů**!")
    else:
        add_balance(interaction.user.id, -amount)
        await interaction.response.send_message(f"🎰 {display}\n❌ Prohrál jsi **{amount} coinů**.")

@tree.command(name="rob", description="Zkus okrást jiného hráče")
async def rob(interaction: discord.Interaction, user: discord.Member):
    if random.random() > 0.4:
        fine = random.randint(10, 50)
        add_balance(interaction.user.id, -fine)
        await interaction.response.send_message(f"👮 Byl jsi chycen! Zaplatil jsi pokutu **{fine} coinů**.")
    else:
        stolen = random.randint(10, min(100, get_balance(user.id)))
        add_balance(interaction.user.id, stolen)
        add_balance(user.id, -stolen)
        await interaction.response.send_message(f"🥷 Ukradl jsi **{stolen} coinů** od {user.mention}!")

@tree.command(name="deposit", description="Ulož coiny do banky")
async def deposit(interaction: discord.Interaction, amount: int):
    data = load_economy()
    uid = str(interaction.user.id)
    if data.get(uid, 0) < amount:
        await interaction.response.send_message("❌ Nemáš dost coinů!")
        return
    bank_key = f"bank_{uid}"
    data[uid] = data.get(uid, 0) - amount
    data[bank_key] = data.get(bank_key, 0) + amount
    save_economy(data)
    await interaction.response.send_message(f"🏦 Uložil jsi **{amount} coinů** do banky.")

@tree.command(name="withdraw", description="Vyber coiny z banky")
async def withdraw(interaction: discord.Interaction, amount: int):
    data = load_economy()
    uid = str(interaction.user.id)
    bank_key = f"bank_{uid}"
    if data.get(bank_key, 0) < amount:
        await interaction.response.send_message("❌ Nemáš dost coinů v bance!")
        return
    data[bank_key] = data.get(bank_key, 0) - amount
    data[uid] = data.get(uid, 0) + amount
    save_economy(data)
    await interaction.response.send_message(f"💵 Vybral jsi **{amount} coinů** z banky.")

@tree.command(name="bankbalance", description="Zobrazí zůstatek v bance")
async def bankbalance(interaction: discord.Interaction):
    data = load_economy()
    bank_key = f"bank_{str(interaction.user.id)}"
    bal = data.get(bank_key, 0)
    await interaction.response.send_message(f"🏦 Máš v bance **{bal} coinů**.")

@tree.command(name="dice", description="Vsaď na hod kostkou (1-6)")
async def dice(interaction: discord.Interaction, amount: int, number: int):
    if not 1 <= number <= 6:
        await interaction.response.send_message("❌ Číslo musí být 1-6!")
        return
    if get_balance(interaction.user.id) < amount:
        await interaction.response.send_message("❌ Nemáš dost coinů!")
        return
    roll = random.randint(1, 6)
    if roll == number:
        win = amount * 5
        add_balance(interaction.user.id, win)
        await interaction.response.send_message(f"🎲 Padlo **{roll}** — vyhrál jsi **{win} coinů**!")
    else:
        add_balance(interaction.user.id, -amount)
        await interaction.response.send_message(f"🎲 Padlo **{roll}** — prohrál jsi **{amount} coinů**.")

@tree.command(name="shop", description="Zobrazí obchod")
async def shop(interaction: discord.Interaction):
    embed = discord.Embed(title="🛒 Obchod", color=discord.Color.purple())
    embed.add_field(name="1. VIP Role — 500 coinů", value="Speciální role na serveru", inline=False)
    embed.add_field(name="2. Změna přezdívky — 100 coinů", value="Změn si přezdívku", inline=False)
    embed.add_field(name="3. Emoji boost — 200 coinů", value="Přidej custom emoji", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="buy", description="Kup si položku z obchodu")
async def buy(interaction: discord.Interaction, item: str):
    prices = {"vip": 500, "prezdivka": 100, "emoji": 200}
    item = item.lower()
    if item not in prices:
        await interaction.response.send_message("❌ Taková položka neexistuje!")
        return
    price = prices[item]
    if get_balance(interaction.user.id) < price:
        await interaction.response.send_message(f"❌ Potřebuješ **{price} coinů**, ale nemáš dost.")
        return
    add_balance(interaction.user.id, -price)
    await interaction.response.send_message(f"✅ Koupil jsi **{item}** za {price} coinů!")

@tree.command(name="inventory", description="Zobrazí tvůj inventář")
async def inventory(interaction: discord.Interaction):
    await interaction.response.send_message("🎒 Tvůj inventář je zatím prázdný. Nakup v `/shop`!")

@tree.command(name="pay", description="Pošli coiny")
async def pay(interaction: discord.Interaction, user: discord.Member, amount: int):
    if get_balance(interaction.user.id) < amount:
        await interaction.response.send_message("❌ Nemáš dost coinů!")
        return
    add_balance(interaction.user.id, -amount)
    add_balance(user.id, amount)
    await interaction.response.send_message(f"💸 Poslal jsi **{amount} coinů** uživateli {user.mention}.")

@tree.command(name="weekly", description="Týdenní odměna coinů")
async def weekly(interaction: discord.Interaction):
    amount = random.randint(300, 600)
    add_balance(interaction.user.id, amount)
    await interaction.response.send_message(f"📅 Dostal jsi týdenní odměnu: **{amount} coinů**!")

@tree.command(name="crime", description="Zkus spáchat zločin pro coiny")
async def crime(interaction: discord.Interaction):
    if random.random() > 0.5:
        fine = random.randint(30, 100)
        add_balance(interaction.user.id, -fine)
        await interaction.response.send_message(f"👮 Byl jsi chycen! Pokuta **{fine} coinów**.")
    else:
        earn = random.randint(50, 200)
        add_balance(interaction.user.id, earn)
        await interaction.response.send_message(f"🦹 Podařilo se! Získal jsi **{earn} coinů**.")

@tree.command(name="gamble", description="Vsaď všechny coiny (double or nothing)")
async def gamble(interaction: discord.Interaction):
    bal = get_balance(interaction.user.id)
    if bal <= 0:
        await interaction.response.send_message("❌ Nemáš žádné coiny!")
        return
    if random.random() > 0.5:
        add_balance(interaction.user.id, bal)
        await interaction.response.send_message(f"🎰 Vyhrál jsi! Zdvojnásobil jsi na **{bal*2} coinů**!")
    else:
        add_balance(interaction.user.id, -bal)
        await interaction.response.send_message(f"💀 Prohrál jsi všechno! Přišel jsi o **{bal} coinů**.")

@tree.command(name="setbalance", description="Nastav coiny hráči (admin)")
@app_commands.checks.has_permissions(administrator=True)
async def setbalance(interaction: discord.Interaction, user: discord.Member, amount: int):
    data = load_economy()
    data[str(user.id)] = amount
    save_economy(data)
    await interaction.response.send_message(f"✅ Nastavil jsi **{amount} coinů** hráči {user.mention}.")

# ═══════════════════════════════════════
#           HUDBA (20 příkazů)
# ═══════════════════════════════════════

music_queue = []
is_playing = False

@tree.command(name="join", description="Bot vstoupí do hlasového kanálu")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f"🎵 Připojil jsem se do **{channel.name}**.")
    else:
        await interaction.response.send_message("❌ Nejsi v žádném hlasovém kanálu!")

@tree.command(name="leave", description="Bot opustí hlasový kanál")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 Odpojil jsem se.")
    else:
        await interaction.response.send_message("❌ Nejsem v žádném kanálu!")

@tree.command(name="play", description="Přehraje píseň z YouTube")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    if not interaction.user.voice:
        await interaction.followup.send("❌ Nejsi v hlasovém kanálu!")
        return
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()

    import yt_dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        url = info['entries'][0]['url']
        title = info['entries'][0]['title']

    vc = interaction.guild.voice_client
    if vc.is_playing():
        music_queue.append((url, title))
        await interaction.followup.send(f"➕ Přidáno do fronty: **{title}**")
    else:
        source = discord.FFmpegPCMAudio(url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn")
        vc.play(source)
        await interaction.followup.send(f"▶️ Přehrávám: **{title}**")

@tree.command(name="stop", description="Zastaví přehrávání")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        music_queue.clear()
        await interaction.response.send_message("⏹️ Přehrávání zastaveno.")
    else:
        await interaction.response.send_message("❌ Nic nehraje!")

@tree.command(name="pause", description="Pozastaví přehrávání")
async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("⏸️ Pozastaveno.")
    else:
        await interaction.response.send_message("❌ Nic nehraje!")

@tree.command(name="resume", description="Obnoví přehrávání")
async def resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_pau
