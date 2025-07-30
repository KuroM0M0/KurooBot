import json
import discord
import asyncio
import random
from discord.ext import commands
from discord import app_commands
from discord import ButtonStyle, ui
from datetime import datetime, timedelta
from collections import Counter
#für Paypal
#import requests
#from flask import Flask, request, jsonify
#import threading
#eigene Imports
from dataBase import *
from Methoden import *
from help import *
from hug import sendHug, sendPat
from spark import *
from settings import Settings, PremiumSettings, settingStuff
from newsletter import NewsletterModal
from disableCustomSpark import disableCustomSparkModal
from stats import *
from vote import *
import sqlite3

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
KuroID = 308660164137844736
cooldownDuration = 24
VoteCooldown = 12 #in Stunden

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
        synced = await bot.tree.sync()
        print(f"Slash-Commands synchronisiert: {len(synced)} Befehle")
    except Exception as e:
        print(f"Fehler beim Synchronisieren: {e}")
    #zeigt in Konsole an, auf welchen Servern der Bot ist
    for guild in bot.guilds:
        print(f'- {guild.name} (ID: {guild.id})')
    bot.loop.create_task(setBotActivity())




@bot.command(name="PremiumAktivieren")
async def PremiumAktivieren(ctx, member: discord.Member):
    targetID = member.id
    userID = ctx.author.id
    if userID == KuroID:
        await ctx.send(f"{member} hat nun Premium!")
        setPremium(connection, datetime.now().isoformat(), targetID)
    else:
        await ctx.send("Du bist nicht berechtigt dies zu tun!")

@bot.command(name="PremiumDeaktivieren")
async def PremiumDeaktivieren(ctx, member: discord.Member):
    targetID = member.id
    userID = ctx.author.id
    if userID == KuroID:
        await ctx.send(f"{member} hat nun kein Premium mehr!")
        resetPremium(connection, targetID)
    else:
        await ctx.send("Du bist nicht berechtigt dies zu tun!")

@bot.command(name="setReveals")
async def setReveals(ctx, member: discord.Member, uses: int):
    targetID = member.id
    userID = ctx.author.id
    if userID == KuroID:
        await ctx.send(f"{member} hat nun {uses} Reveals!")
        setRevealUses(connection, targetID, uses)
    else:
        await ctx.send("Du bist nicht berechtigt dies zu tun!")

@bot.command(name="setSparkChannel")
@commands.has_permissions(administrator=True)
async def setSparkChannel(ctx):
    channel = ctx.channel
    serverID = ctx.guild.id
    CheckServerExists(connection, serverID)
    await ctx.send(f"{channel} ist nun der Spark Channel!")
    setChannelSparkID(connection, serverID, channel.id)

@setSparkChannel.error
async def setSparkChannel_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du brauchst Administrator-Rechte, um diesen Befehl zu benutzen!", delete_after=10)

@bot.command(name="setNewsletterChannel")
@commands.has_permissions(administrator=True)
async def setNewsletterChannel(ctx):
    channel = ctx.channel
    serverID = ctx.guild.id
    CheckServerExists(connection, serverID)
    await ctx.send(f"{channel} ist nun der Newsletter Channel!")
    setChannelNewsletterID(connection, serverID, channel.id)



@bot.tree.command(name="spark", description="Mache einer Person ein anonymes Kompliment")
@app_commands.describe(person="Wähle eine Person aus", kompliment="Wähle ein Kompliment aus der Liste")
async def spark(interaction: discord.Interaction, person: discord.Member, kompliment: str, reveal: bool = None):
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

    Premium = getPremium(connection, userID)
    cooldown = getCooldown(connection, userID)
    date = datetime.now().date().isoformat()
    SparkUses = getSparkUses(connection, userID)

    ResetPremium(connection, userID)
    ResetStreak(connection, userID)
    CheckServerExists(connection, guildID)

    #resettet SparkUses
    if cooldown != date:
        resetSparkUses(connection, userID)
        SparkUses = 0

    await SparkCheck(cooldown, SparkUses, Premium, date, interaction)
    await CheckTarget(targetID, userID, interaction)
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
        await channel.send(embed=embed)

        if getGhostpingSetting(connection, targetID) == True:
            ghostping = await channel.send(f"{person.mention}")
            await ghostping.delete()

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

            embed = discord.Embed(
                title=f"{targetName} hier eine Persönliche Nachricht für dich!",
                description=f"{person.mention} ||| {kompliment}",
                color=0x008B00)
        
            embed.set_footer(text=f"Spark ID: {getSparkID(connection)}")
            await channel.send(embed=embed)

            await interaction.followup.send("Dein anonymer Text war erfolgreich :D", ephemeral=True)

            if getGhostpingSetting(connection, targetID) == True:
                ghostping = await channel.send(f"{person.mention}")
                await ghostping.delete()


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
    user = (interaction.user)
    userID = str(interaction.user.id)
    channel = interaction.channel
    serverID = str(interaction.guild.id)
    channelID = str(interaction.channel.id)

    CheckServerExists(connection, serverID)
    await CheckSparkChannel(connection, serverID, channelID, interaction)

    if person == None:
        StatsPrivateSelf = getStatsPrivate(connection, userID)
        embedSelf = await StatsSelf(user)
        if embedSelf == None:
            await interaction.followup.send(f"{user.display_name} hat noch keine Stats. Mach ihr doch eine Freude mit /spark c:")
            return
        if StatsPrivateSelf == 1:
            await interaction.followup.send(embed=embedSelf)
            return
        else:
            await interaction.delete_original_response()
            await channel.send(embed=embedSelf)
            return

    else:
        targetID = str(person.id)
        targetName = person.display_name
        embedTarget = await StatsTarget(person)
        StatsPrivateTarget = getStatsPrivate(connection, targetID)
        if embedTarget == None:
            await interaction.delete_original_response()
            await channel.send(f"{person.display_name} hat noch keine Stats. Mach ihr doch eine Freude mit /spark c:")
            return
        if StatsPrivateTarget == 1:
            await interaction.followup.send(f"{targetName} hat seine Stats versteckt.", ephemeral=True)
            return
        else:
            await StatsTarget(person)
            await interaction.delete_original_response()
            await channel.send(embed=embedTarget)
            return
    
        




@bot.tree.command(name="topserver", description="Zeigt an auf welchem Server am meisten gesparkt wird.")
async def topserver(interaction: discord.Interaction):
    rows = getTopServerSparks(connection)
    guildID = str(interaction.guild.id)
    channelID = str(interaction.channel.id)

    CheckServerExists(connection, guildID)
    await CheckSparkChannel(connection, guildID, channelID, interaction)

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
    serverID = str(interaction.guild.id)
    channelID = str(interaction.channel.id)
    CheckServerExists(connection, serverID)
    await CheckSparkChannel(connection, serverID, channelID, interaction)
    await sendHug(interaction, person)




@bot.tree.command(name="pat", description="Gib einer anderen Person anonym ein Patpat c:")
@app_commands.describe(person="Wähle eine Person aus, der du ein Patpat geben möchtest.")
async def pat(interaction: discord.Interaction, person: discord.Member):
    serverID = str(interaction.guild.id)
    channelID = str(interaction.channel.id)
    CheckServerExists(connection, serverID)
    await CheckSparkChannel(connection, serverID, channelID, interaction)
    await sendPat(interaction, person)




@bot.tree.command(name="help", description="Zeigt dir alle Befehle an")
async def help(interaction: discord.Interaction, command: str = None):
    serverID = str(interaction.guild.id)
    channelID = str(interaction.channel.id)
    CheckServerExists(connection, serverID)
    await CheckSparkChannel(connection, serverID, channelID, interaction)

    if command is None:
        embed = discord.Embed(
            color=0x005b96
        )

        embed.add_field(
            name="ℹ️ Befehle: ",
            value="\n".join(cmdDescription),
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

@help.autocomplete("command")
async def helpAutocomplete(interaction: discord.Interaction, current: str):
    befehle = ["spark", "stats", "hug", "pat", "settings", "streak", "reveal", "admin"]
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

    settingStuff(userID)
    await interaction.followup.send(embed=settingStuff(userID), ephemeral=True)
    if premium == True:
        await interaction.followup.send(view=PremiumSettings(), ephemeral=True)
        return
    else:
        await interaction.followup.send(view=Settings(), ephemeral=True)
        await interaction.followup.send("Folgende Settings sind nur für Premium Nutzer einstellbar: \nStatsPrivate \nSparkDM \nNewsletter \nHug/Pat DM", ephemeral=True)
        return




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

    CheckServerExists(connection, serverID)
    await CheckSparkChannel(connection, serverID, channelID, interaction)

    embed = discord.Embed(
            title=f"Streak von {userName}",
            description=f"Streak: {streak} Tage\nStreak Punkte: {streakPunkte}",
            color=0x005b96
        )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text="3 Tage Streak = 1 Punkt")

    if streakPrivate == True:
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="sendnewsletter", description="Newsletter an alle Abonnenten schicken")
async def sendNewsletter(interaction: discord.Interaction):
    if interaction.user.id != KuroID:
        await interaction.response.send_message("Du darfst diesen Befehl nicht verwenden.", ephemeral=True)
        return
    await interaction.response.send_modal(NewsletterModal())


@bot.tree.command(name="premium", description="Hole dir Premium")
async def premium(interaction: discord.Interaction):
    await interaction.response.send_message("[Sende hier hin 1€ um Premium zu erhalten](https://paypal.me/KuroPixel?country.x=DE&locale.x=de_DE). In die Nachricht bitte deine Discord ID, damit dir Premium zugewiesen werden kann.", ephemeral=True)


@bot.tree.command(name="vote", description="Wenn du den Bot kostenlos unterstützen möchtest :)")
async def vote(interaction: discord.Interaction):
    userID = str(interaction.user.id)
    now = datetime.now()
    Vote = await checkVote(userID)
    LastVote = getVoteTimestamp(connection, userID)

    if LastVote:
        lastVoteDt = datetime.fromisoformat(LastVote)
    else:
        lastVoteDt = datetime.min

    if Vote:
        if now - lastVoteDt >= timedelta(hours=VoteCooldown):
            setVotePoints(connection, userID)
            setVoteTimestamp(connection, userID, now.isoformat())
            await interaction.response.send_message(
                "✅ Danke für deinen Vote! Du hast einen VotePunkt erhalten. ❤️", 
                ephemeral=True)
        else:
            await interaction.response.send_message(
                "⚠️ Du hast schon vor Kurzem gevotet! Bitte warte, bis du erneut voten kannst.",
                ephemeral=True)
    else:
        await interaction.response.send_message(
            "ℹ️ Du hast noch nicht gevotet. Bitte stimme hier ab: https://top.gg/bot/1306244838504665169/vote",
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
    userName = user.display_name
    sparkCount = getSparkCount(connection, userID)
    Premium = getPremium(connection, userID)
    PremiumTimestamp = getPremiumTimestamp(connection, userID)
    privacy = getProfilPrivateSetting(connection, userID)
    serverID = str(interaction.guild.id)
    channelID = str(interaction.channel.id)

    CheckServerExists(connection, serverID)
    await CheckSparkChannel(connection, serverID, channelID, interaction)

    embed = discord.Embed(
        title=f"Profil von {userName}",
        color=0x005b96)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="🗓️Beigetreten am", value=user.joined_at.strftime("%d.%m.%Y"), inline=True)

    if getBirthday(connection, userID) is not None:
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
            await interaction.response.send_message("Diese Person hat ihr Profil auf Privat.", ephemeral=True)
            return
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="reveal", description="Lasse dir anzeigen von wem ein Spark gesendet wurde!")
async def reveal(interaction: discord.Interaction, sparkid: int):
    await interaction.response.defer(ephemeral=True)
    userID = str(interaction.user.id)
    revealUses = getRevealUses(connection, userID)

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
    else:
        await interaction.followup.send(f"Dieser Spark wurde von {result} gesendet.", ephemeral=True)
        setRevealUses(connection, userID, revealUses - 1)

        


#bot.run('MTMxMDc0NDM3OTIyODQyNjI5MA.GbLQRE.J0BWbSEs22F6cEiqzrUBwMgjrWYr6dqbIn49N8')
bot.run('MTMwNjI0NDgzODUwNDY2NTE2OQ.Gh_inc.Ys9Pc1_L89uRQ1fPm1wsqbDvcD32SEzHivkSUg') #richtiger Bot