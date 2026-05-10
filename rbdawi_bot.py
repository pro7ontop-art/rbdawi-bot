import discord
from discord.ext import commands
import json
import os
import random
from datetime import datetime

# ═══════════════════════════════════════════
#           RBDAWI LEVEL BOT ★
# ═══════════════════════════════════════════

TOKEN              = "MTUwMjg4OTc4MTkzNDI5NzIxNA.GE-sw4.JgUUnj-Oay2uFb0FD-4BNhdlOEUc7FxaeOY9GE"   # ← توكن البوت
LEVELUP_CHANNEL_ID = 1502815683069874256      # ← ID روم اللفلات (غيّره!)
COOLDOWN_SECONDS   = 60                      # ثواني الانتظار بين رسالة ورسالة
XP_MIN             = 15                      # أقل XP
XP_MAX             = 25                      # أكثر XP
LOGO_FILE          = "logo.png"              # اسم ملف الشعار (حطه بنفس المجلد)

# ───────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

DB_FILE = "levels.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user(db, guild_id, user_id):
    gid, uid = str(guild_id), str(user_id)
    if gid not in db:
        db[gid] = {}
    if uid not in db[gid]:
        db[gid][uid] = {"xp": 0, "level": 0, "messages": 0, "last_msg": 0}
    return db[gid][uid]

def xp_needed(level):
    return int(100 * (level + 1) ** 1.5)

def get_level_from_xp(xp):
    level = 0
    while xp >= xp_needed(level):
        xp -= xp_needed(level)
        level += 1
    return level

def xp_in_current_level(total_xp, level):
    for l in range(level):
        total_xp -= xp_needed(l)
    return total_xp

def progress_bar(current, total, length=14):
    filled  = int(length * current / total) if total > 0 else 0
    bar     = "█" * filled + "░" * (length - filled)
    percent = int(100 * current / total) if total > 0 else 0
    return f"`{bar}` {percent}%"

# ════════════════════════════════════════════

@bot.event
async def on_ready():
    print(f"✦ RBDAWI BOT — {bot.user} — ONLINE")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🌌 RBDAWI | !rank"
        )
    )

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    db   = load_db()
    user = get_user(db, message.guild.id, message.author.id)
    now  = int(datetime.utcnow().timestamp())

    if now - user["last_msg"] < COOLDOWN_SECONDS:
        await bot.process_commands(message)
        return

    old_level         = user["level"]
    user["xp"]       += random.randint(XP_MIN, XP_MAX)
    user["messages"] += 1
    user["last_msg"]  = now
    user["level"]     = get_level_from_xp(user["xp"])
    save_db(db)

    if user["level"] > old_level:
        channel = bot.get_channel(LEVELUP_CHANNEL_ID)
        if channel:
            await send_levelup_embed(channel, message.author, user)

    await bot.process_commands(message)

# ════════════════════════════════════════════
#           LEVEL UP EMBED
# ════════════════════════════════════════════

async def send_levelup_embed(channel, member, user):
    level   = user["level"]
    total   = user["xp"]
    needed  = xp_needed(level)
    current = xp_in_current_level(total, level)
    bar     = progress_bar(current, needed)

    embed = discord.Embed(color=0x7B2FFF)

    embed.set_author(
        name=f"{member.display_name}  •  RBDAWI",
        icon_url=member.display_avatar.url
    )

    embed.description = (
        f"## 🌌  تهانينا {member.mention}!\n"
        f"وصلت للمستوى **`{level}`** 🎉\n"
        f"```\n"
        f"  ✦  R B D A W I   S Y S T E M  ✦\n"
        f"```"
    )

    embed.add_field(
        name="📊 التقدم للمستوى القادم",
        value=f"{bar}\n`{current:,}` / `{needed:,}` XP",
        inline=False
    )

    embed.add_field(
        name="💎 إجمالي XP",
        value=f"```yaml\n{total:,} XP\n```",
        inline=True
    )

    embed.add_field(
        name="📨 الرسائل",
        value=f"```yaml\n{user['messages']:,}\n```",
        inline=True
    )

    embed.add_field(
        name="🎯 المستوى",
        value=f"```fix\nLVL {level}\n```",
        inline=True
    )

    embed.set_footer(text=f"★ RBDAWI System  •  {datetime.utcnow().strftime('%Y/%m/%d  %H:%M')}")
    embed.timestamp = datetime.utcnow()

    if os.path.exists(LOGO_FILE):
        file = discord.File(LOGO_FILE, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")
        await channel.send(content=f"<@{member.id}>", embed=embed, file=file)
    else:
        await channel.send(content=f"<@{member.id}>", embed=embed)

# ════════════════════════════════════════════
#               COMMANDS
# ════════════════════════════════════════════

@bot.command(name="rank", aliases=["r", "لفل"])
async def rank_cmd(ctx, member: discord.Member = None):
    member  = member or ctx.author
    db      = load_db()
    user    = get_user(db, ctx.guild.id, member.id)
    level   = user["level"]
    total   = user["xp"]
    needed  = xp_needed(level)
    current = xp_in_current_level(total, level)
    bar     = progress_bar(current, needed)

    embed = discord.Embed(color=0x7B2FFF)
    embed.set_author(
        name=f"{member.display_name}  •  RBDAWI",
        icon_url=member.display_avatar.url
    )
    embed.description = (
        f"```\n"
        f"  ✦  R B D A W I   S Y S T E M  ✦\n"
        f"```"
    )
    embed.add_field(
        name=f"📊 تقدمك — المستوى `{level}`",
        value=f"{bar}\n`{current:,}` / `{needed:,}` XP",
        inline=False
    )
    embed.add_field(name="💎 إجمالي XP", value=f"`{total:,}`",           inline=True)
    embed.add_field(name="📨 الرسائل",   value=f"`{user['messages']:,}`", inline=True)
    embed.add_field(name="🎯 المستوى",   value=f"`{level}`",              inline=True)
    embed.set_footer(text=f"★ RBDAWI System  •  {datetime.utcnow().strftime('%Y/%m/%d')}")
    embed.timestamp = datetime.utcnow()

    if os.path.exists(LOGO_FILE):
        file = discord.File(LOGO_FILE, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")
        await ctx.send(embed=embed, file=file)
    else:
        await ctx.send(embed=embed)


@bot.command(name="top", aliases=["lb", "ليدر"])
async def top_cmd(ctx):
    db  = load_db()
    gid = str(ctx.guild.id)
    if gid not in db:
        return await ctx.send("❌ لا يوجد بيانات بعد!")

    users  = sorted(db[gid].items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
    medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    board  = ""
    for i, (uid, data) in enumerate(users):
        m    = ctx.guild.get_member(int(uid))
        name = m.display_name if m else f"User#{uid[-4:]}"
        board += f"{medals[i]} **{name}** — LVL `{data['level']}` — `{data['xp']:,}` XP\n"

    embed = discord.Embed(
        title="🌌 لوحة الأبطال",
        description=f"```\n  ✦  R B D A W I  •  TOP 10  ✦\n```\n{board}",
        color=0x7B2FFF
    )
    embed.set_footer(text=f"★ RBDAWI System  •  {datetime.utcnow().strftime('%Y/%m/%d')}")
    embed.timestamp = datetime.utcnow()

    if os.path.exists(LOGO_FILE):
        file = discord.File(LOGO_FILE, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")
        await ctx.send(embed=embed, file=file)
    else:
        await ctx.send(embed=embed)


@bot.command(name="addxp")
@commands.has_permissions(administrator=True)
async def addxp_cmd(ctx, member: discord.Member, amount: int):
    db   = load_db()
    user = get_user(db, ctx.guild.id, member.id)
    old  = user["level"]
    user["xp"]   += amount
    user["level"] = get_level_from_xp(user["xp"])
    save_db(db)
    embed = discord.Embed(
        description=f"✅ أُضيف **{amount:,} XP** لـ {member.mention} | LV `{old}` → `{user['level']}`",
        color=0x7B2FFF
    )
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ ما عندك صلاحية!")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ ما لقيت هالمستخدم!")

# ════════════════════════════════════════════
bot.run(TOKEN)
