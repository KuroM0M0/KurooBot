import discord
import asyncio
import random
import emotes as E
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from dataBase import *
from Methoden import *
from slashCommands.spark import CheckSparkChannel
from config import connection


cooldownDurationHugPat = 1#2       #für vote bleibt gleich
cooldownDurationHugPatPremium = 1
maxUses = 1
maxUsesVote = 2
maxUsesPremium = 3

async def sendHug(interaction, person, anonym):
    CheckUserIsInSettings(connection, interaction.user.id)

    links = [
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384130571206656/Hug2.gif",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384136472330250/Hug3.gif",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384137005010964/Hug4.gif",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384137500201020/Hug5.gif",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384137839808635/Hug6.gif",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384138183872522/Hug7.gif",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384138632400968/Hug8.gif",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384139173724210/Hug9.gif",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1354080746158952499/Umarmung.gif"
    ]

    userID = str(interaction.user.id)
    userName = interaction.user.display_name
    targetID = str(person.id)
    targetName = person.display_name
    guildID = str(interaction.guild.id) if interaction.guild else None
    guildName = interaction.guild.name if interaction.guild else None
    channel = interaction.channel
    now = datetime.now()

    # Ensure user exists
    if not checkUserExists(connection, userID):
        insertUser(connection, userID)

    # Self-hug verhindern
    if targetID == userID:
        await interaction.followup.send("Eigenlob stinkt :^)", ephemeral=True)
        return

    # 1. Cooldown prüfen
    next_available = getNextHugAvailable(connection, userID, cooldownDurationHugPat)
    if next_available:
        await interaction.followup.send(
            f"Du kannst den Befehl erst wieder <t:{int(next_available.timestamp())}:R> verwenden.",
            ephemeral=True
        )
        return

    # 2. Tageslimit prüfen
    isPremium = getPremium(connection, userID)
    allowed = updateHugPatUses(connection, userID, maxUsesPremium if isPremium else maxUses)
    if not allowed:
        await interaction.followup.send(
            f"Du hast den Befehl heute bereits "
            f"{maxUsesPremium if isPremium else maxUses}x verwendet. Bitte warte bis morgen.",
            ephemeral=True
        )
        return

    # 3. Cooldown + Log setzen
    updateHugPatCooldown(connection, userID)
    insertLogs(connection, now.isoformat(), userID, userName, targetID, targetName, "Umarmung 🫂", "Hug", guildID, guildName)

    # --- Komplimente aktualisieren, Embed senden, Ping ---

    if anonym == False:
        embed = discord.Embed(
            title=f"Umarmung {E.Hug}",
            description=f"{person.mention}, {interaction.user.mention} würde dich jetzt sehr gerne umarmen, aber du bist nicht da </3",
            color=0x005b96
        )
    else:
        embed = discord.Embed(
            title=f"Umarmung {E.Hug}",
            description=f"{person.mention}, jemand würde dich jetzt sehr gerne umarmen, aber du bist nicht da </3",
            color=0x005b96
        )

    embed.set_image(url=random.choice(links))
    await interaction.followup.send("Erfolgreich gesendet", ephemeral=True)
    if getGhostpingSetting(connection, targetID) == True:
        ghostping = await channel.send(f"{person.mention}")
        await ghostping.delete()

    await channel.send(embed=embed)





async def sendPat(interaction, person, anonym):
    checkUserSetting(connection, interaction.user.id)
    links = [
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384607237083249/Pat7.gif?ex=6888cdf9&is=68877c79&hm=4371fb99a5fda1edc3441be7fd3a1ebe23f6f4ad6de4d6f001d34a3132c956a7&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384607752851606/Pat2.gif?ex=6888cdf9&is=68877c79&hm=9aa055276b6bf43688a1fe04f34148b51fe1fcfb5c89f0b44406d91250b72309&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384608377933925/Pat3.gif?ex=6888cdf9&is=68877c79&hm=bb311e2d673d3eb5b38a80df2b8f0aabb1450b2ec5fa7c48efc67497432ab495&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384609170522112/Pat4.gif?ex=6888cdfa&is=68877c7a&hm=79f42dff28f0be01b09a73cf9794797d2f520bf91e79f712b1be9a7b9c5dc537&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384609589825536/Pat5.gif?ex=6888cdfa&is=68877c7a&hm=aa39103d7e55b55919c6d34fe4a7d222f8d5d78aa6f9b02b4440b53e501be634&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384610194063381/Pat6.gif?ex=6888cdfa&is=68877c7a&hm=76cc5983bd0fe79c38059ec16b2c476d2629efbbf9cc6a745893b41befe6d32d&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1354081384666370141/Pat.gif?ex=67e3fe0f&is=67e2ac8f&hm=8885bf9b82c5ed9cef4b43bc8248ba7576befc791ef0c60d55881b02a8f3408e&"
    ]
    userID = str(interaction.user.id)
    userName = interaction.user.display_name
    targetID = str(person.id)
    targetName = person.display_name
    guildID = str(interaction.guild.id)
    guildName = interaction.guild.name
    channel = interaction.channel
    now = datetime.now()

    exists = checkUserExists(connection, userID)
    if exists is None:
        insertUser(connection, userID)

    if targetID == userID:
        await interaction.followup.send("Eigenlob stinkt :^)")
        return

    # 1. Cooldown prüfen
    next_available = getNextHugAvailable(connection, userID, cooldownDurationHugPat)
    if next_available:
        await interaction.followup.send(
            f"Du kannst den Befehl erst wieder <t:{int(next_available.timestamp())}:R> verwenden.",
            ephemeral=True
        )
        return

    # 2. Tageslimit prüfen
    isPremium = getPremium(connection, userID)
    allowed = updateHugPatUses(connection, userID, maxUsesPremium if isPremium else maxUses)
    if not allowed:
        await interaction.followup.send(
            f"Du hast den Befehl heute bereits "
            f"{maxUsesPremium if isPremium else maxUses}x verwendet. Bitte warte bis morgen.",
            ephemeral=True
        )
        return

    # 3. Cooldown + Log setzen
    updateHugPatCooldown(connection, userID)
    insertLogs(connection, now.isoformat(), userID, userName, targetID, targetName, "Pat 🥰", "Pat", guildID, guildName)
    
    targetCompliments = getCompliments(connection, targetID)
    meh = "Pat 🥰"
    key = meh .encode('utf-8')

    if key in targetCompliments: 
        updateCompliment(connection, targetID, "Pat 🥰")
    else:
        insertCompliment(connection, targetID, "Pat 🥰")

    if anonym == False:
        embed = discord.Embed(
            title=f"Pat {E.Pat}",
            description=f"{person.mention}, du bekommst pat pats von {interaction.user.mention} <3",
            color=0x005b96
        )
    else:
        embed = discord.Embed(
            title=f"Pat {E.Pat}",
            description=f"{person.mention}, du bekommst anonyme pat pats <3",
            color=0x005b96
        )
    embed.set_image(url=random.choice(links))
    await interaction.followup.send("Erfolgreich gesendet", ephemeral=True)
    if getGhostpingSetting(connection, targetID) == True:
        ghostping = await channel.send(f"{person.mention}")
        await ghostping.delete()

    await channel.send(embed=embed)


class HugCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hug", description="Umarme eine andere Person Anonym")
    @app_commands.describe(person="Wähle eine Person aus, die du Umarmen möchtest.")
    async def hug(self, interaction: discord.Interaction, person: discord.Member, anonym: bool = True):
        await interaction.response.defer(ephemeral=True)
        serverID = str(interaction.guild.id)
        channelID = str(interaction.channel.id)
        userID = str(interaction.user.id)
        targetID = str(person.id)


        await BanStuff(connection, serverID, targetID, userID, interaction)
        CheckServerExists(connection, serverID)
        await CheckSparkChannel(connection, serverID, channelID, interaction)
        await sendHug(interaction, person, anonym)




    @app_commands.command(name="pat", description="Gib einer anderen Person anonym ein Patpat c:")
    @app_commands.describe(person="Wähle eine Person aus, der du ein Patpat geben möchtest.")
    async def pat(self, interaction: discord.Interaction, person: discord.Member, anonym: bool = True):
        await interaction.response.defer(ephemeral=True)
        serverID = str(interaction.guild.id)
        channelID = str(interaction.channel.id)
        userID = str(interaction.user.id)
        targetID = str(person.id)


        await BanStuff(connection, serverID, targetID, userID, interaction)
        CheckServerExists(connection, serverID)
        await CheckSparkChannel(connection, serverID, channelID, interaction)
        await sendPat(interaction, person, anonym)



async def setup(bot: commands.Bot):
    await bot.add_cog(HugCommand(bot))
    print("Hug/Pat geladen ✅")