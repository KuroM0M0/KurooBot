import json
import discord
import asyncio
import logging
from discord.ext import commands
from discord import app_commands
from discord import ui
from datetime import datetime, timedelta
from dotenv import load_dotenv
#eigene Imports
import paypal
import emotes as E
from dataBase import *
from Methoden import *
from user.settings import *
from slashCommands.disableCustomSpark import disableCustomSparkModal
from slashCommands.stats import *
from slashCommands.spark import WhatIsSparkButton
from Shop.shop import ShopButtons, Shop, ShopEmbed
from Shop.inventar import *
from user.premiumDM import startPremiumChecker
from Shop.items import *
from duftenServer.NSFW import *
from config import BotToken, MainServerID, connection, KuroID
from Twitch.checkLive import startCheckStream


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
cooldownDuration = 24

logging.basicConfig(level=logging.WARN) #AKTIVIEREN FÜR LOGGING

load_dotenv()

try:
    with open("compliments.json", "r", encoding="utf8") as f:
        compliments = json.load(f)
        for key, data in compliments.items():
            link = data.get("link")
except FileNotFoundError:
    compliments = {}

    
async def setBotActivity():
    await asyncio.sleep(10)  # Warte 10 Sekunden, um sicherzustellen, dass der Bot vollständig verbunden ist
    activity = discord.Streaming(
        name=f"{len(bot.guilds)} von 100 Server",
        url="https://www.twitch.tv/kurom0m0"
    )
    await bot.change_presence(activity=activity)


#wird beim Start vom Bot ausgeführt
@bot.event
async def on_ready():
    print(f"Bot ist eingeloggt als {bot.user.name}")
    try:
        #Global synchronisieren (alle globalen Commands)
        synced_global = await bot.tree.sync()
        print(f"Global synchronisierte Commands: {len(synced_global)}")

         #Guild-spezifisch synchronisieren (nur ausgewählter Server)
        #duftGuild = await bot.tree.sync(guild=discord.Object(id=duftendeID))
        kuroGuild = await bot.tree.sync(guild=discord.Object(id=MainServerID))
        HugGuild = await syncHugCommands(bot, connection)
        #print(f"Duften-spezifisch synchronisierte Commands: {len(duftGuild)}")
        print(f"Kuro-spezifisch synchronisierte Commands: {len(kuroGuild)}")
        print(f"Hug-spezifisch synchronisierte Commands: {len(HugGuild)}")

        bot.add_view(WhatIsSparkButton())
        bot.add_view(interactionView())
    except Exception as e:
        print(f"Fehler beim Synchronisieren: {e}")

    #zeigt in Konsole an, auf welchen Servern der Bot ist
    for guild in bot.guilds:
        print(f'- {guild.name} (ID: {guild.id}) | {len(guild.members)} Mitglieder')
    await setBotActivity()
    #bot.loop.create_task(paypal.checkPaymentsLoop(bot, connection))
    startPremiumChecker(bot, connection)
    startCheckStream(bot)

@bot.event
async def on_guild_join(guild):
    await setBotActivity()

@bot.event
async def on_guild_remove(guild):
    await setBotActivity()

async def loadCommands():
    await bot.load_extension("commands.AdminCommands")
    await bot.load_extension("commands.SecretCommands")
    await bot.load_extension("commands.KuroCommands")
    await bot.load_extension("commands.error")
    await bot.load_extension("duftenServer.NSFW")
    await bot.load_extension("duftenServer.roleRemoved")
    await bot.load_extension("slashCommands.hug")
    await bot.load_extension("slashCommands.timeout")
    await bot.load_extension("slashCommands.reveal")
    await bot.load_extension("slashCommands.help")
    await bot.load_extension("Shop.inventar")
    await bot.load_extension("slashCommands.stats")
    await bot.load_extension("slashCommands.birthday")
    await bot.load_extension("slashCommands.settings")
    await bot.load_extension("slashCommands.newsletter")
    await bot.load_extension("slashCommands.spark")
    await bot.load_extension("slashCommands.profil")
    await bot.load_extension("slashCommands.vote")
    await bot.load_extension("slashCommands.use")
    await bot.load_extension("slashCommands.shop")
    await bot.load_extension("slashCommands.feedback")
    await bot.load_extension("Kurocord.roles")


    

async def main():
    await loadCommands()
    await bot.start(BotToken)
    
        


@bot.tree.command(name="topserver", description="Zeigt an auf welchem Server am meisten gesparkt wird.")
async def topserver(interaction: discord.Interaction):
    rows = getTopServerSparks(connection)
    serverID = str(interaction.guild.id)
    channelID = str(interaction.channel.id)

    CheckServerExists(connection, serverID)
    if serverID is not None:
        await CheckSparkChannel(connection, serverID, channelID, interaction)

    if rows:
        embed = discord.Embed(
            title="Top Server Sparks",
            color=0x005b96
        )
        description = ""
        for serverID, serverName, Count in rows:
            description += f"{serverName}: {Count} \n"
            embed.description = description
        
        
        await interaction.response.send_message(embed=embed, view=TopServerButton())
    else:
        await interaction.response.send_message("Es gibt noch keine Logs.")




@bot.tree.command(name="cooldown", description="Zeigt dir deinen aktuellen Cooldown an")
async def cooldown(interaction: discord.Interaction):
    userID = str(interaction.user.id)
    userName = interaction.user.display_name

    result = getCooldown(connection, userID)
    if result:
        last_used = datetime.fromisoformat(result)
        now = datetime.now()
        cooldownDurationSec = cooldownDuration * 3600
        cooldownNow = int(last_used.timestamp()) + cooldownDurationSec
        if int(now.timestamp()) < cooldownNow:
            await interaction.response.send_message(f"Du kannst den Befehl /spark wieder <t:{cooldownNow}:R> verwenden.", ephemeral=True)
        else:
            await interaction.response.send_message("Du hast keinen Cooldown mehr.", ephemeral=True)
    else:
        await interaction.response.send_message("Du hast keinen Cooldown mehr.", ephemeral=True)



@bot.tree.command(name="streak", description="Schaue dir alle Streak relevanten Dinge an")
async def streak(interaction: discord.Interaction):
    userID = str(interaction.user.id)
    userName = interaction.user.display_name
    streak = getStreak(connection, userID)
    streakPunkte = getStreakPoints(connection, userID)
    streakPrivate = getStreakPrivate(connection, userID)
    serverID = str(interaction.guild.id)
    channelID = str(interaction.channel.id)

    if getBan(connection, serverID, userID) == True:
        await interaction.followup.send("Du wurdest von der Nutzung des Bots ausgeschlossen!", ephemeral=True)
        return

    CheckServerExists(connection, serverID)
    if serverID is not None:
        await CheckSparkChannel(connection, serverID, channelID, interaction)

    embed = discord.Embed(
            title=f"Streak von {userName}",
            description=f"Streak: {streak} Tage\nStreak Punkte: {streakPunkte} {E.StreakPoint}",
            color=0x005b96
        )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text="3 Tage Streak = 1 Punkt")

    if streakPrivate == True:
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="premium", description="Hole dir Premium")
async def premium(interaction: discord.Interaction):
    await interaction.response.send_message("[Sende über **Freunde&Familie** 1€](https://paypal.me/KuroPixel?country.x=DE&locale.x=de_DE). In die Nachricht bitte deine Discord ID, damit dir Premium zugewiesen werden kann.\n-# Discord ID = Rechtsklick auf dich -> Nutzer-ID Kopieren", ephemeral=True)




class TopServerButton(ui.View):
    @ui.button(label="Sparks", style=discord.ButtonStyle.primary)
    async def SparkButton(self, interaction: discord.Interaction, button: ui.Button):
        rows = getTopServerSparks(connection)
        embed = discord.Embed(
            title="Top Server Sparks",
            color=0x005b96
        )

        description = ""
        for serverID, serverName, Count in rows:
            description += f"{serverName}: {Count} \n"
            embed.description = description
        await interaction.response.edit_message(embed=embed)


    @ui.button(label="Hug/Pat", style=discord.ButtonStyle.primary)
    async def HugPatButton(self, interaction: discord.Interaction, button: ui.Button):
        rows = getTopServerHugs(connection)
        embed = discord.Embed(
            title="Top Server Hug/Pat",
            color=0x005b96
        )

        description = ""
        for serverID, serverName, Count in rows:
            description += f"{serverName}: {Count} \n"
            embed.description = description
        await interaction.response.edit_message(embed=embed)



@bot.tree.command(name="spark_ausblenden", description="Verberge bestimmte Custom Sparks in deinen Stats (Premium)")
async def sparkDisable(interaction: discord.Interaction):
    userID = str(interaction.user.id)
    premium = getPremium(connection, userID)
    if premium:
        await interaction.response.send_modal(disableCustomSparkModal())
    else:
        await interaction.response.send_message("Dieser Befehl ist nur für Premium Nutzer verfügbar.", ephemeral=True)




@bot.command()
async def testembed(ctx):
    embed = discord.Embed(
        title="Test",
        description="Funktioniert das?",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

asyncio.run(main())