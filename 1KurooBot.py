import json
import discord
import asyncio
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
from hug import sendHug, sendPat
from spark import SparkCheck
from settings import Settings, PremiumSettings, settingStuff
from newsletter import NewsletterModal
import sqlite3

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
KuroID = 308660164137844736
UpdateChannelID = 1310607294026747954
cooldownDuration = 24

connection = createConnection()

try:
    with open("compliments.json", "r", encoding="utf8") as f:
        compliments = json.load(f)
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




@bot.tree.command(name="spark", description="Mache einer Person ein anonymes Kompliment")
@app_commands.describe(person="Wähle eine Person aus", kompliment="Wähle ein Kompliment aus der Liste")
async def spark(interaction: discord.Interaction, person: discord.Member, kompliment: str):
    await interaction.response.defer(ephemeral=True)
    userID = str(interaction.user.id)
    userName = interaction.user.display_name
    targetID = str(person.id)
    targetName = person.display_name
    guildID = str(interaction.guild.id)
    guildName = interaction.guild.name
    now = datetime.now()
    channel = interaction.channel
    
    UserExists(connection, userID)

    Premium = getPremium(connection, userID)
    cooldown = getCooldown(connection, userID)
    date = datetime.now().date().isoformat()
    SparkUses = getSparkUses(connection, userID)

    ResetPremium(connection, userID)
    ResetStreak(connection, userID)

    #resettet SparkUses
    if cooldown != date:
        resetSparkUses(connection, userID)
        SparkUses = 0


    await SparkCheck(cooldown, SparkUses, Premium, date, interaction)
    await CheckTarget(targetID, userID, interaction)

    if SparkUses < 1:
        updateStreak(connection, userID)
        StreakPunkt(connection, userID)


    if kompliment in compliments:
        updateCooldown(connection, userID)
        updateSparkUses(connection, userID)
        targetCompliments = getCompliments(connection, targetID)
    
        #überprüft ob das ausgewählte (kompliment) in der Datenbank ist
        if kompliment in targetCompliments: 
            #nimmt das Kompliment aus der Datenbank (also i guess, weil nur das ausgewählte verändert wird)
            updateCompliment(connection, targetID, kompliment)
        else:
            insertCompliment(connection, targetID, kompliment)

        insertLogs(connection, now.isoformat(), userID, userName, targetID, targetName, kompliment, "Compliment", guildID, guildName)

        embed = discord.Embed(
        title=f"{compliments[kompliment]['name']}",
        description=f"{person.mention} {compliments[kompliment]['text']}",
        color=0x00FF00)

        embed.set_image(url=f"{compliments[kompliment]['link']}")
        embed.set_thumbnail(url=person.display_avatar.url)
        embed.set_footer(text=f"Spark ID: {getSparkID(connection)}")
        await channel.send(embed=embed)

        ghostping = await channel.send(f"{person.mention}")
        await ghostping.delete()

        await interaction.followup.send("Dein Kompliment war erfolgreich :D", ephemeral=True)


    else:
        if Premium:
            insertCompliment(connection, targetID, kompliment)
            insertLogs(connection, now.isoformat(), userID, userName, targetID, targetName, kompliment, "Custom", guildID, guildName)
            updateCooldown(connection, userID)
            updateSparkUses(connection, userID)

            embed = discord.Embed(
                title=f"{targetName} hier eine Persönliche Nachricht für dich!",
                description=f"{person.mention} ||| {kompliment}",
                color=0x008B00)
        
            embed.set_footer(text=f"Spark ID: {getSparkID(connection)}")
            await channel.send(embed=embed)

            await interaction.followup.send("Dein anonymer Text war erfolgreich :D", ephemeral=True)

            ghostping = await channel.send(f"{person.mention}")
            await ghostping.delete()

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
async def stats(interaction: discord.Interaction, person: discord.Member):
    targetID = str(person.id)
    targetName = person.display_name
    Streak = getStreak(connection, targetID)
    StatsPrivate = getStatsPrivate(connection, targetID)

    if StatsPrivate == 1:
        await interaction.response.send_message(f"{targetName} hat seine Stats versteckt.", ephemeral=True)
        return

    if Streak == None:
        Streak = 0

    complimentStats = getCompliments(connection, targetID)
    if complimentStats:
        kompliment = "\n".join([f"{k}: {v}" for k, v in complimentStats.items()])
        embed = discord.Embed(
            title=f"Stats von {person.display_name}",
            description=f"{kompliment}",
            color=0x005b96
        )
        embed.set_thumbnail(url=person.display_avatar.url)
        #embed.set_footer(text=f"Streak: {Streak} Tage")
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"{targetName} hat noch keine Stats. Mach ihr doch eine Freude mit /spark c:")




@bot.tree.command(name="topserver", description="Zeigt an auf welchem Server am meisten gesparkt wird.")
async def topserver(interaction: discord.Interaction):
    rows = getTopServerSparks(connection)

    if rows:
        embed = discord.Embed(
            title="Top Server Sparks",
            color=0x005b96
        )
        description = ""
        for serverID, serverName, Count in rows:
            print(f"{serverName} {Count}")
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
    print(f"{userName} CooldownCommand")




@bot.tree.command(name="hug", description="Umarme eine andere Person Anonym")
@app_commands.describe(person="Wähle eine Person aus, die du Umarmen möchtest.")
async def hug(interaction: discord.Interaction, person: discord.Member):
    await sendHug(interaction, person)




@bot.tree.command(name="pat", description="Gib einer anderen Person anonym ein Patpat c:")
@app_commands.describe(person="Wähle eine Person aus, der du ein Patpat geben möchtest.")
async def pat(interaction: discord.Interaction, person: discord.Member):
    await sendPat(interaction, person)




@bot.tree.command(name="help", description="Zeigt dir alle Befehle an")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        color=0x005b96
    )

    cmdDescription = [
        "**/spark (Person) (Kompliment)**\n   Damit kannst du einer Person ein Anonymes kompliment machen.\n",
        "**/stats (Person)**\n                Zeige alle Komplimente an, die diese Person bisher bekommen hat\n",
        "**/topserver**\n                     Zeigt die 2 meistgenutzten Server an\n",
        "**/hug (Person)**\n                  Umarme diese Person Anonym\n",
        "**/pat (Person)**\n                  gib der Person ein Anonymes pat\n",
        "**/cooldown**\n                      Schaue nach, wann du wieder /spark verwenden kannst\n",
        "**/feedback**\n                      Öffnet ein Formular in dem du Feedback für den Bot eingeben kannst\n",
        "**/settings**\n                      Stell einige Dinge ein, zb. ob du private Nachrichten möchtest\n",
        "**/streak**\n                        Schaue dir alle relevanten Dinge zu deiner Streak an\n"
    ]

    embed.add_field(
        name="ℹ️ Befehle: ",
        value="\n".join(cmdDescription),
        inline=False
    )
    await interaction.response.send_message(embed=embed)




@bot.tree.command(name="settings", description="Stelle zB. SparkDMs ein/aus")
async def settings(interaction: discord.Interaction):
    userID = str(interaction.user.id)
    premium = getPremium(connection, userID)

    settingStuff(userID)
    if premium == True:
        await interaction.response.send_message(view=PremiumSettings(), ephemeral=True)
        return
    else:
        await interaction.response.send_message(view=Settings(), ephemeral=True)
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

    embed = discord.Embed(
            title=f"Streak von {userName}",
            description=f"Streak: {streak} Tage\nStreak Punkte: {streakPunkte}",
            color=0x005b96
        )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

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





        


bot.run('MTMxMDc0NDM3OTIyODQyNjI5MA.GbLQRE.J0BWbSEs22F6cEiqzrUBwMgjrWYr6dqbIn49N8')
#bot.run('MTMwNjI0NDgzODUwNDY2NTE2OQ.Gh_inc.Ys9Pc1_L89uRQ1fPm1wsqbDvcD32SEzHivkSUg') #richtiger Bot