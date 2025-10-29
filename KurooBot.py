import json
import discord
import asyncio
import random
import logging
from discord.ext import commands
from discord import app_commands
from discord import ButtonStyle, ui
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
#eigene Imports
import paypal
from dataBase import *
from Methoden import *
from help import *
from hug import sendHug, sendPat
from spark import *
from user.settings import *
from newsletter import NewsletterModal
from disableCustomSpark import disableCustomSparkModal
from stats import *
from user.vote import *
from reveal import RevealMainView, RevealCustomView, revealEmbed
from Shop.shop import ShopButtons, Shop, ShopEmbed
from Shop.inventar import *
from user.birthday import *
from user.premiumDM import startPremiumChecker
from Shop.items import *
from duftenServer.NSFW import *


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
KuroID = 308660164137844736
cooldownDuration = 24
VoteCooldown = 12 #in Stunden
duftendeID = 1185618335950438500

logging.basicConfig(level=logging.WARN) #AKTIVIEREN FÜR LOGGING

load_dotenv()
BotToken = os.getenv("BotToken")
#BotToken = os.getenv("TestBotToken") #Testbot

connection = createConnection()

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
        synced_guild = await bot.tree.sync(guild=discord.Object(id=duftendeID))
        print(f"Guild-spezifisch synchronisierte Commands: {len(synced_guild)}")

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
    

async def main():
    await loadCommands()
    await bot.start(BotToken)




@bot.tree.command(name="spark", description="Mache einer Person ein anonymes Kompliment")
@app_commands.describe(person="Wähle eine Person aus", kompliment="Wähle ein Kompliment aus der Liste")
async def spark(interaction: discord.Interaction, person: discord.Member, kompliment: str, reveal: bool):
    await interaction.response.defer(ephemeral=True)
    userID = str(interaction.user.id)
    userName = interaction.user.display_name
    targetID = str(person.id)
    targetName = person.display_name
    guildID = str(interaction.guild.id)
    guildName = interaction.guild.name
    now = datetime.now()
    channel = interaction.channel
    channelID = str(channel.id)
    
    UserExists(connection, userID)
    if getBan(connection, guildID, targetID) == True:
        await interaction.followup.send("Dieser Nutzer wurde vom Bot ausgeschlossen!", ephemeral=True)
        return
    if getBan(connection, guildID, userID) == True:
        await interaction.followup.send("Du wurdest von der Nutzung des Bots ausgeschlossen!", ephemeral=True)
        return

    Premium = getPremium(connection, userID)
    cooldown = getCooldown(connection, userID)
    date = datetime.now().date().isoformat()
    SparkUses = getSparkUses(connection, userID)

    ResetStreak(connection, userID)
    CheckServerExists(connection, guildID)

    #resettet SparkUses
    if cooldown != date:
        resetSparkUses(connection, userID)
        SparkUses = 0

    #await SparkCheck(cooldown, SparkUses, Premium, date, interaction)
    #await CheckTarget(targetID, userID, interaction)
    await CheckSparkChannel(connection, guildID, channelID, interaction)

    if SparkUses < 1:
        updateStreak(connection, userID)
        StreakPunkt(connection, userID)

    if reveal == None:
        reveal = False

    if kompliment in compliments:
        updateCooldown(connection, userID)
        updateSparkUses(connection, userID)
        targetCompliments = getCompliments(connection, targetID)

        #seit 25.07.25 wird Compliments Table nicht mehr verwendet sondern die Logs
        #überprüft ob das ausgewählte (kompliment) in der Datenbank ist
        if kompliment in targetCompliments: 
            #nimmt das Kompliment aus der Datenbank (also i guess, weil nur das ausgewählte verändert wird)
            updateCompliment(connection, targetID, kompliment)
        else:
            insertCompliment(connection, targetID, kompliment)

        insertLogs(connection, now.isoformat(), userID, userName, targetID, targetName, kompliment, "Compliment", guildID, guildName, reveal)

        embed = discord.Embed(
        title=f"{compliments[kompliment]['name']}",
        description=f"{person.mention} {compliments[kompliment]['text']}",
        color=0x00FF00)

        embed.set_image(url=random.choice(compliments[kompliment].get("link")))
        embed.set_thumbnail(url=person.display_avatar.url)
        embed.set_footer(text=f"Spark ID: {getSparkID(connection)}")

        if getGhostpingSetting(connection, targetID) == True:
            await channel.send(embed=embed, content=f"||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​|| {person.mention}")
        else:
            await channel.send(embed=embed)

        if getSparkDM(connection, targetID) == True:
            await asyncio.sleep(2)
            await sendSparkDM(targetID, interaction)
        await interaction.followup.send("Dein Kompliment war erfolgreich :D", ephemeral=True)


    else:
        if Premium:
            CustomSpark = getCustomSparkSetting(connection, targetID)
            if CustomSpark == False:
                await interaction.followup.send("Diese Person hat ausgestellt, dass man ihr einen custom Spark schicken kann!", ephemeral=True)
                return
            insertCompliment(connection, targetID, kompliment)
            insertLogs(connection, now.isoformat(), userID, userName, targetID, targetName, kompliment, "Custom", guildID, guildName, reveal)
            updateCooldown(connection, userID)
            updateSparkUses(connection, userID)

            kompliment = replaceEmotes(kompliment, interaction.guild, interaction.client)

            embed = discord.Embed(
                title=f"{targetName} hier eine Persönliche Nachricht für dich!",
                description=f"{person.mention} ||| {kompliment}",
                color=0x008B00
            )
        
            embed.set_footer(text=f"Spark ID: {getSparkID(connection)}")

            await interaction.followup.send("Dein anonymer Text war erfolgreich :D", ephemeral=True)

            if getGhostpingSetting(connection, targetID) == True:
                await channel.send(embed=embed, content=f"||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​|| {person.mention}")
            else:
                await channel.send(embed=embed)


            if getSparkDM(connection, targetID) == True:
                await asyncio.sleep(2)
                await sendSparkDM(targetID, interaction)

        #Wenn nutzer kein Premium hat
        else:
            await interaction.followup.send("Du hast kein Premium! Bitte wähle ein vorhandenes Kompliment aus.", ephemeral=True)

    


@spark.autocomplete("kompliment")
async def kompliment_autocomplete(interaction: discord.Interaction, current: str):
    choices = []
    for compliment in compliments:
        choices.append(app_commands.Choice(name=compliment, value=compliment))
    return [choice for choice in choices if current.lower() in choice.name.lower()]




@bot.tree.command(name="stats", description="Zeigt dir die Statistiken einer Person an.")
@app_commands.describe(person="Wähle die Person aus, von der du die Stats sehen möchtest.")
async def stats(interaction: discord.Interaction, person: discord.Member = None):
    await interaction.response.defer(ephemeral=True)
    user = interaction.user
    userID = str(interaction.user.id)
    channel = interaction.channel
    serverID = str(interaction.guild.id)
    channelID = str(interaction.channel.id)

    if getBan(connection, serverID, userID) == True:
        await interaction.followup.send("Du wurdest von der Nutzung vom Bot ausgeschlossen!", ephemeral=True)
        return

    CheckServerExists(connection, serverID)
    await CheckSparkChannel(connection, serverID, channelID, interaction)

    if person is None:
        StatsPrivateSelf = getStatsPrivate(connection, userID)
        embedSelf = await StatsSelf(user, interaction, "global")
        if not embedSelf:
            await interaction.followup.send(
                f"{user.display_name} hat noch keine Stats. Mach ihr doch eine Freude mit /spark c:"
            )
            return
        if StatsPrivateSelf == 1:
            await interaction.followup.send(embed=embedSelf, view=StatView(user, None, interaction))
        else:
            await interaction.delete_original_response()
            await channel.send(embed=embedSelf, view=StatView(user, None, interaction))
    else:
        targetID = str(person.id)

        if getBan(connection, serverID, targetID) == True:
            await interaction.followup.send("Dieser Nutzer wurde vom Bot ausgeschlossen!", ephemeral=True)
            return
    
        targetName = person.display_name
        embedTarget = await StatsTarget(person, interaction, "global")
        StatsPrivateTarget = getStatsPrivate(connection, targetID)
        if not embedTarget:
            await interaction.delete_original_response()
            await channel.send(
                f"{person.display_name} hat noch keine Stats. Mach ihr doch eine Freude mit /spark c:"
            )
            return
        if StatsPrivateTarget == 1:
            await interaction.followup.send(f"{targetName} hat seine Stats versteckt.", ephemeral=True)
        else:
            await interaction.delete_original_response()
            await channel.send(embed=embedTarget, view=StatView(user, person, interaction))
    
        




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




@bot.tree.command(name="hug", description="Umarme eine andere Person Anonym")
@app_commands.describe(person="Wähle eine Person aus, die du Umarmen möchtest.")
async def hug(interaction: discord.Interaction, person: discord.Member):
    await interaction.response.defer(ephemeral=True)
    serverID = str(interaction.guild.id)
    channelID = str(interaction.channel.id)
    userID = str(interaction.user.id)
    targetID = str(person.id)

    if getBan(connection, serverID, targetID) == True:
        await interaction.followup.send("Dieser Nutzer wurde vom Bot ausgeschlossen!", ephemeral=True)
        return

    if getBan(connection, serverID, userID) == True:
        await interaction.followup.send("Du wurdest von der Nutzung vom Bot ausgeschlossen!", ephemeral=True)
        return

    CheckServerExists(connection, serverID)
    await CheckSparkChannel(connection, serverID, channelID, interaction)
    await sendHug(interaction, person)




@bot.tree.command(name="pat", description="Gib einer anderen Person anonym ein Patpat c:")
@app_commands.describe(person="Wähle eine Person aus, der du ein Patpat geben möchtest.")
async def pat(interaction: discord.Interaction, person: discord.Member):
    await interaction.response.defer(ephemeral=True)
    serverID = str(interaction.guild.id)
    channelID = str(interaction.channel.id)
    userID = str(interaction.user.id)
    targetID = str(person.id)

    if getBan(connection, serverID, targetID) == True:
        await interaction.followup.send("Dieser Nutzer wurde vom Bot ausgeschlossen!", ephemeral=True)
        return

    if getBan(connection, serverID, userID) == True:
        await interaction.followup.send("Du wurdest von der Nutzung vom Bot ausgeschlossen!", ephemeral=True)
        return
    
    CheckServerExists(connection, serverID)
    await CheckSparkChannel(connection, serverID, channelID, interaction)
    await sendPat(interaction, person)




@bot.tree.command(name="help", description="Zeigt dir alle Befehle an")
async def help(interaction: discord.Interaction, command: str = None):
    if interaction.guild is not None:
        serverID = str(interaction.guild.id)
        channelID = str(interaction.channel.id)
        CheckServerExists(connection, serverID)
        if serverID is not None:
            await CheckSparkChannel(connection, serverID, channelID, interaction)

    if command is None:
        embed = discord.Embed(
            color=0x005b96
        )

        embed.add_field(
            name="ℹ️ Befehle: ",
            value=cmdDescription,
            inline=False
        )
        await interaction.response.send_message(embed=embed)
    elif command == "spark":
        await helpSpark(interaction)
    elif command == "stats":
        await helpStats(interaction)
    elif command == "hug":
        await helpHug(interaction)
    elif command == "pat":
        await helpPat(interaction)
    elif command == "settings":
        await helpSettings(interaction)
    elif command == "streak":
        await helpStreak(interaction)
    elif command == "reveal":
        await helpReveal(interaction)
    elif command == "admin":
        await helpAdmin(interaction)
    elif command == "vote":
        await helpVote(interaction)
    elif command == "shop":
        await helpShop(interaction)

@help.autocomplete("command")
async def helpAutocomplete(interaction: discord.Interaction, current: str):
    befehle = ["admin", "spark", "stats", "hug", "pat", "settings", "streak", "reveal", "vote", "shop"]
    return [
        app_commands.Choice(name=b, value=b)
        for b in befehle
        if current.lower() in b.lower()
    ]




@bot.tree.command(name="settings", description="Stelle zB. SparkDMs ein/aus")
async def settings(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    userID = str(interaction.user.id)
    premium = getPremium(connection, userID)

    if checkUserSetting(connection, userID) == None:
        insertUserSetting(connection, userID)

    settingsObj = newSettings(premium, userID)
    view = SettingsView(premium, userID)
    embed = settingsObj.getEmbed()
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)




class FeedbackModal(discord.ui.Modal, title="Feedback Formular"):
    feedback = discord.ui.TextInput(label="Dein Feedback", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        bot_owner = await interaction.client.fetch_user(KuroID)
        embed = discord.Embed(title="Neues Feedback erhalten!", description=self.feedback.value, color=discord.Color.blue())
        embed.set_footer(text=f"Von {interaction.user} ({interaction.user.id})")
        
        await bot_owner.send(embed=embed)
        await interaction.response.send_message("Danke für dein Feedback :D", ephemeral=True)

@bot.tree.command(name="feedback", description="Sende über ein Formular Feedback an den Bot-Entwickler")
async def feedback(interaction: discord.Interaction):
        await interaction.response.send_modal(FeedbackModal())




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
            description=f"Streak: {streak} Tage\nStreak Punkte: {streakPunkte} <:Streakpunkt:1406583255934963823>",
            color=0x005b96
        )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text="3 Tage Streak = 1 Punkt")

    if streakPrivate == True:
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="sendnewsletter", description="Newsletter an alle Abonnenten schicken")
#@app_commands.guilds(discord.Object(id=475295112453423125)) funktioniert nicht, testen worans liegt
async def sendNewsletter(interaction: discord.Interaction):
    if interaction.user.id != KuroID:
        await interaction.response.send_message("Du darfst diesen Befehl nicht verwenden.", ephemeral=True)
        return
    await interaction.response.send_modal(NewsletterModal())


@bot.tree.command(name="premium", description="Hole dir Premium")
async def premium(interaction: discord.Interaction):
    await interaction.response.send_message("[Sende über **Freunde&Familie** 1€](https://paypal.me/KuroPixel?country.x=DE&locale.x=de_DE). In die Nachricht bitte deine Discord ID, damit dir Premium zugewiesen werden kann.\n-# Discord ID = Rechtsklick auf dich -> Nutzer-ID Kopieren", ephemeral=True)


@bot.tree.command(name="vote", description="Wenn du den Bot kostenlos unterstützen möchtest :)")
async def vote(interaction: discord.Interaction):
    userID = str(interaction.user.id)
    now = datetime.now()
    Vote = await checkVote(userID)
    LastVote = getVoteTimestamp(connection, userID)
    votePoints = getVotePoints(connection, userID)

    if LastVote:
        lastVoteDt = datetime.fromisoformat(LastVote)
    else:
        lastVoteDt = datetime.min

    if Vote:
        if now - lastVoteDt >= timedelta(hours=VoteCooldown):
            setVotePoints(connection, userID)
            setVoteTimestamp(connection, userID, now.isoformat())
            votePoints = getVotePoints(connection, userID)
            await interaction.response.send_message(
                f"✅ Dein Vote wurde erkannt und deine Belohnung gutgeschrieben!\n"
                f"Du hast jetzt **{votePoints} VotePunkte**. ❤️",
                ephemeral=True)
        else:
            await interaction.response.send_message(
                f"⚠️ Dein letzter Vote ist noch nicht lange genug her.\n"
                f"⏳ Du kannst alle **{VoteCooldown} Stunden** Punkte abholen.\n"
                f"Aktuell hast du **{votePoints} VotePunkte**.",
                ephemeral=True)
    else:
        await interaction.response.send_message(
            f"ℹ️ Du hast noch keinen Vote abgeholt.\n"
            f"👉 Bitte stimme zuerst hier ab: https://top.gg/bot/1306244838504665169/vote\n\n"
            f"⚡ Danach kannst du **diesen Befehl erneut ausführen**, "
            f"um deine Punkte zu erhalten.\n"
            f"Aktuell hast du **{votePoints} VotePunkte**.",
            ephemeral=True)




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



@bot.tree.command(name="profil", description="Zeige dein Profil an")
async def profil(interaction: discord.Interaction, user: discord.User = None):
    if user is None:
        user = interaction.user
    userID = user.id
    privacy = getProfilPrivateSetting(connection, userID)
    await interaction.response.defer(ephemeral=privacy)
    
    userName = user.display_name
    sparkCount = getSparkCount(connection, userID)
    Premium = getPremium(connection, userID)
    PremiumTimestamp = getPremiumTimestamp(connection, userID)
    serverID = str(interaction.guild.id)
    channelID = str(interaction.channel.id)
    Birthday = getBirthday(connection, userID)

    if getBan(connection, serverID, interaction.user.id) == True:
            await interaction.followup.send("Du wurdest von der Nutzung des Bots ausgeschlossen!", ephemeral=True)
            return
    if getBan(connection, serverID, userID) == True:
        await interaction.followup.send("Dieser Nutzer wurde vom Bot ausgeschlossen!", ephemeral=True)
        return

    CheckServerExists(connection, serverID)
    if serverID is not None:
        await CheckSparkChannel(connection, serverID, channelID, interaction)

    embed = discord.Embed(
        title=f"Profil von {userName}",
        color=0x005b96)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="🗓️Beigetreten am", value=user.joined_at.strftime("%d.%m.%Y"), inline=True)

    if Birthday is not None and Birthday != '0':
        embed.add_field(name="🎂Geburtstag", value=getBirthday(connection, userID), inline=True)

    if Premium == True:
        dt = datetime.fromisoformat(PremiumTimestamp)
        unix_timestamp = int(dt.timestamp())
        embed.add_field(name="💎 Premium seit", value=f"<t:{unix_timestamp}:f>", inline=False)

    embed.add_field(name="\u200b", value="\u200b", inline=False) #leerzeile
    embed.add_field(name="👀 Reveals", value=getRevealUses(connection, userID), inline=True)
    embed.add_field(name=" |", value=" |", inline=True)
    embed.add_field(name="📨 Versendete Sparks", value=f"{sparkCount} Sparks", inline=True)

    if privacy == True:
        if userID != interaction.user.id:
            await interaction.followup.send("Diese Person hat ihr Profil auf Privat.", ephemeral=True)
            return
        else:
            await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        await interaction.followup.send(embed=embed)




@bot.tree.command(name="reveal", description="Lasse dir anzeigen von wem ein Spark gesendet wurde!")
async def reveal(interaction: discord.Interaction, sparkid: int = None):
    await interaction.response.defer(ephemeral=True)
    userID = str(interaction.user.id)
    revealUses = getRevealUses(connection, userID)
    reveals = getReveals(connection, userID) #noch nicht revealed
    customReveals = getRevealsCustom(connection, userID) #noch nicht revealede custom sparks
    revealed = getRevealedSparks(connection, userID) #schon revealed
    revealedCustom = getRevealedSparksCustom(connection, userID)
    if sparkid is not None:
        isRevealed = getIsRevealed(connection, sparkid)
        if revealUses < 1:
            await interaction.followup.send("Du hast keine Reveals mehr. Um dir neue zu holen, gib '/help reveal' ein.", ephemeral=True)
            return

        if userID != getSparkTargetID(connection, sparkid):
            await interaction.followup.send("Du kannst nur Sparks revealen, die du selbst erhalten hast!", ephemeral=True)
            return

        result = getSparkReveal(connection, sparkid)
        if result is None:
            await interaction.followup.send("Dieser Spark existiert nicht oder der Sender möchte Anonym bleiben.", ephemeral=True)
            return
        elif isRevealed == True:
            await interaction.followup.send(f"Dieser Spark wurde bereits von dir aufgedeckt!", ephemeral=True)
            return
        else:
            await interaction.followup.send(f"Dieser Spark wurde von {result} gesendet.", ephemeral=True)
            setRevealUses(connection, userID, revealUses - 1)
            setIsRevealed(connection, sparkid)
    else:
        description_lines = []
        if not reveals and not customReveals:
            embed = discord.Embed(
                title="✨ Revealbare Sparks:",
                description="Du hast aktuell keine revealbaren Sparks.",
                color=0x00ff00)
            
        else:
            if revealed or revealedCustom:
                description_lines.append("**Bereits revealed:**")
            if revealed:
                description_lines.extend(revealEmbed(revealed))

            # 2️⃣ Noch nicht revealed Sparks
            if reveals:
                if description_lines:
                    description_lines.append("")  # Leerzeile zur Trennung
                description_lines.append("**Noch revealbar:**")
                for spark_id, timestamp, compliment in reveals:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        unix_ts = int(dt.timestamp())
                    except ValueError:
                        unix_ts = 0
                    line = f"{compliment} — <t:{unix_ts}:R> — ID `{spark_id}`"
                    description_lines.append(line)

            # Falls gar nichts vorhanden ist
            if not description_lines:
                description_lines.append("Du hast aktuell keine revealbaren Sparks.")

            # Embed erstellen
            embed = discord.Embed(
                title="✨ Revealbare Sparks:",
                description="\n".join(description_lines),
                color=0x005b96
            )
        await interaction.followup.send(embed=embed, view=RevealMainView(reveals, revealed, customReveals, revealedCustom), ephemeral=True)


@bot.tree.command(name="shop", description="Hier kannst du dir unterschiedliche Items mit Vote/Streakpunkten kaufen :)")
async def shop(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = ShopEmbed(1, interaction, connection)
    try:
        await interaction.followup.send(embed=embed, view=ShopButtons(connection))
    except Exception as e:
        print("Fehler beim Senden des Shops:", e)
        await interaction.followup.send(f"Fehler: {e}", ephemeral=True)



@bot.tree.command(name="inventar", description="Hier siehst du welche Items du hast c:")
async def inventar(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = InventarEmbed(interaction, connection)
    serverID = str(interaction.guild.id)
    userID = str(interaction.user.id)

    if getBan(connection, serverID, userID) == True:
        await interaction.followup.send("Du wurdest von der Nutzung vom Bot ausgeschlossen!", ephemeral=True)
        return

    if serverID is not None:
        channelID = str(interaction.channel.id)
        await CheckSparkChannel(connection, serverID, channelID, interaction)
    try:
        await interaction.followup.send(embed=embed, view=InventarButtons(connection))
    except Exception as e:
        print("Fehler beim Senden des Inventars:", e)
        await interaction.followup.send(f"Fehler: {e}", ephemeral=True)



@bot.tree.command(name="setbirthday", description="Setze deinen Geburtstag")
async def Birthday(interaction: discord.Interaction):
    serverID = str(interaction.guild.id)
    userID = str(interaction.user.id)

    if getBan(connection, serverID, userID) == True:
        await interaction.followup.send("Du wurdest von der Nutzung des Bots ausgeschlossen!", ephemeral=True)
        return

    if serverID is not None:
        channelID = str(interaction.channel.id)
        await CheckSparkChannel(connection, serverID, channelID, interaction)
        
    # Wrapper für save_callback, da die View nur (user_id, year, month, day) übergibt
    def save_cb(user_id: int, year: Optional[int], month: int, day: int):
        # Wenn Jahr optional, erstelle ein date-Objekt
        if year:
            date_str = f"{day:02d}-{month:02d}-{year:04d}"
        else:
            # nur Monat+Tag: setze Jahr auf 2000 oder NULL-String (je nach DB)
            date_str = f"{day:02d}-{month:02d}-2000"  # Beispiel: Jahres-Platzhalter
        setBirthday(connection, user_id, date_str)

    # View erstellen, owner_id = wer den Command aufruft
    view = BirthdayView(owner_id=interaction.user.id, save_callback=save_cb, default_month=None)

    embed = view.build_embed()
    # Nachricht senden
    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
    sent = await interaction.original_response()
    view.message = sent


@bot.tree.command(name="use", description="Nutze deine Items aus dem /Inventar")
async def use(interaction: discord.Interaction, item: str):
    actionData = ITEM_ACTIONS.get(item)
    hasItem = checkUserHasItem(connection, interaction.user.id, getItemIDByName(connection, item))
    if hasItem == False:
        await interaction.response.send_message(f"❌ Du hast keine **{item}**!", ephemeral=True)
        return
    if not actionData:
        await interaction.response.send_message(f"❌ Für **{item}** gibt es noch keine Funktion.", ephemeral=True)
        return

    func = actionData["func"]
    needSparkID = actionData["needSparkID"]

    if needSparkID:
        # Modal öffnen
        await interaction.response.send_modal(SparkIDModal(func, item))
    else:
        await interaction.response.defer(ephemeral=True)
        # Direkt ausführen
        await func(interaction)
    

@use.autocomplete("item")
async def itemName_autocomplete(interaction: discord.Interaction, current: str):
    shop = Shop(connection)
    userItems = getUserItems(connection, interaction.user.id)  # [(itemID, count), ...]
    allItems = shop.loadItems()

    itemNameList = []
    for item in allItems:
        for userItem in userItems:
            if item.itemID == userItem[0] and userItem[1] > 0:  # Anzahl > 0
                itemNameList.append(item.name)

    # Erstelle Choice-Objekte
    choices = [
        app_commands.Choice(name=name, value=name)
        for name in itemNameList
    ]

    # Filtere nach Suchbegriff
    return [
        choice for choice in choices
        if current.lower() in choice.name.lower()
    ]

asyncio.run(main())
