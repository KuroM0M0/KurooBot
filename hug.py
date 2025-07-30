import discord
import asyncio
import random
from datetime import datetime, timedelta
from dataBase import *
import sqlite3

connection = createConnection()
cooldownDurationHugPat = 2       #für vote bleibt gleich
cooldownDurationHugPatPremium = 1
maxUses = 1
maxUsesVote = 2
maxUsesPremium = 3

async def sendHug(interaction, person):
    await interaction.response.defer(ephemeral=True)
    links = [
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384130571206656/Hug2.gif?ex=6888cd88&is=68877c08&hm=79bc45cb2ba34c1ddf32c239414651fe8b746768673b15d0e4733bdd565dd25d&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384136472330250/Hug3.gif?ex=6888cd89&is=68877c09&hm=6a0240fe77c52e14890782d9f40b09613146257ffce4185c11dbad8917cc5d7b&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384137005010964/Hug4.gif?ex=6888cd89&is=68877c09&hm=78a8be918ef205c01169c3c6542e00cb88929ecde7fa780d91a3a50b0b5d2908&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384137500201020/Hug5.gif?ex=6888cd89&is=68877c09&hm=f15662fcaee906ea3d9d3ebba46b033181f52b0e8340b68aa9ba1a2829e479ff&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384137839808635/Hug6.gif?ex=6888cd89&is=68877c09&hm=2b067f50ee36694e7500f88b56c134f9af08a68f5ba01aeb588ba8b0a5d91fcb&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384138183872522/Hug7.gif?ex=6888cd89&is=68877c09&hm=a2c2c64c3395f22c2a6656e2e2897fd6ba0395140f6af6bdbd425ab515dd7c07&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384138632400968/Hug8.gif?ex=6888cd89&is=68877c09&hm=4ee2170795600df71aed1fe66e00c3e43be6e001617f5646f49ac8c17cb23011&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1399384139173724210/Hug9.gif?ex=6888cd8a&is=68877c0a&hm=e91ad02bc639f8d95b7ae98624c13213d65c010ae82fa304cd8ab14cf5ec13be&",
        "https://cdn.discordapp.com/attachments/1354078227903283251/1354080746158952499/Umarmung.gif?ex=67e3fd77&is=67e2abf7&hm=1b0839cc4b333d9c3010ab9b3ac571812b279f67ef836be029f62df87b39e450&"
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

    if not checkHugPatCooldown(connection, userID, cooldownDurationHugPat):
        await interaction.followup.send(
            f"Du kannst den Hug-Befehl erst wieder <t:{int(now.timestamp()) + cooldownDurationHugPat * 3600}:R> verwenden.",
            ephemeral=True
        )
        return

    Premium = getPremium(connection, userID)
    if Premium:
        if not updateHugPatUses(connection, userID, maxUsesPremium):
            await interaction.followup.send(
                f"Du hast den Hug-Befehl heute bereits {maxUsesPremium}x verwendet. Bitte warte bis morgen.",
                ephemeral=True
            )
            return
    else:
        if not updateHugPatUses(connection, userID, maxUses):
            await interaction.followup.send(
                f"Du hast den Hug-Befehl heute bereits {maxUses}x verwendet. Bitte warte bis morgen.",
                ephemeral=True
            )
            return

    updateHugPatCooldown(connection, userID)

    # Aktualisiere die Kompliment-Statistiken
    targetCompliments = getCompliments(connection, targetID)
    meh = "Umarmung 🫂"
    key = meh .encode('utf-8')

    if key in targetCompliments: 
        updateCompliment(connection, targetID, "Umarmung 🫂")
    else:
        insertCompliment(connection, targetID, "Umarmung 🫂")

    
    insertLogs(connection, now.isoformat(), userID, userName, targetID, targetName, "Umarmung 🫂", "Hug", guildID, guildName)

    embed = discord.Embed(
        title="Umarmung <a:PepeHugEggplant:1310769251115728936>",
        description=f"{person.mention}, jemand würde dich jetzt sehr gerne umarmen, aber du bist nicht da </3",
        color=0x005b96
    )
    embed.set_image(url=random.choice(links))
    await interaction.followup.send("Erfolgreich gesendet", ephemeral=True)
    await channel.send(embed=embed)

    if getGhostpingSetting(connection, userID) == True:
        ghostping = await channel.send(f"{person.mention}")
        await ghostping.delete()




async def sendPat(interaction, person):
    await interaction.response.defer(ephemeral=True)
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

    if not checkHugPatCooldown(connection, userID, cooldownDurationHugPat):
        await interaction.followup.send(
            f"Du kannst den Pat-Befehl erst wieder <t:{int(now.timestamp()) + cooldownDurationHugPat * 3600}:R> verwenden.",
            ephemeral=True
        )
        return

    Premium = getPremium(connection, userID)
    if Premium:
        if not updateHugPatUses(connection, userID, maxUsesPremium):
            await interaction.followup.send(
                f"Du hast den Pat-Befehl heute bereits {maxUsesPremium}x verwendet. Bitte warte bis morgen.",
                ephemeral=True
            )
            return
    else:
        if not updateHugPatUses(connection, userID, maxUses):
            await interaction.followup.send(
                f"Du hast den Pat-Befehl heute bereits {maxUses}x verwendet. Bitte warte bis morgen.",
                ephemeral=True
            )
            return

    updateHugPatCooldown(connection, userID)
    insertLogs(connection, now.isoformat(), userID, userName, targetID, targetName, "Pat 🥰", "Pat", guildID, guildName)

    targetCompliments = getCompliments(connection, targetID)
    
    targetCompliments = getCompliments(connection, targetID)
    meh = "Pat 🥰"
    key = meh .encode('utf-8')

    if key in targetCompliments: 
        updateCompliment(connection, targetID, "Pat 🥰")
    else:
        insertCompliment(connection, targetID, "Pat 🥰")


    embed = discord.Embed(
        title="Pat <a:neko_pat:1309638933658865744>",
        description=f"{person.mention}, du bekommst anonyme pat pats <3",
        color=0x005b96
    )
    embed.set_image(url=random.choice(links))
    await interaction.followup.send("Erfolgreich gesendet", ephemeral=True)
    await channel.send(embed=embed)

    if getGhostpingSetting(connection, userID) == True:
        ghostping = await channel.send(f"{person.mention}")
        await ghostping.delete()