import discord
import asyncio
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
        await interaction.response.send_message("Eigenlob stinkt :^)")
        return

    if not checkHugPatCooldown(connection, userID, cooldownDurationHugPat):
        await interaction.response.send_message(
            f"Du kannst den Hug-Befehl erst wieder <t:{int(now.timestamp()) + cooldownDurationHugPat * 3600}:R> verwenden.",
            ephemeral=True
        )
        return

    Premium = getPremium(connection, userID)
    if Premium:
        if not updateHugPatUses(connection, userID, maxUsesPremium):
            await interaction.response.send_message(
                f"Du hast den Hug-Befehl heute bereits {maxUsesPremium}x verwendet. Bitte warte bis morgen.",
                ephemeral=True
            )
            return
    else:
        if not updateHugPatUses(connection, userID, maxUses):
            await interaction.response.send_message(
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
    embed.set_image(url="https://cdn.discordapp.com/attachments/1354078227903283251/1354080746158952499/Umarmung.gif?ex=67e3fd77&is=67e2abf7&hm=1b0839cc4b333d9c3010ab9b3ac571812b279f67ef836be029f62df87b39e450&")
    await interaction.response.send_message("Erfolgreich gesendet", ephemeral=True)
    await channel.send(embed=embed)

    ghostping = await channel.send(f"{person.mention}")
    await ghostping.delete()




async def sendPat(interaction, person):
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
        await interaction.response.send_message("Eigenlob stinkt :^)")
        return

    if not checkHugPatCooldown(connection, userID, cooldownDurationHugPat):
        await interaction.response.send_message(
            f"Du kannst den Pat-Befehl erst wieder <t:{int(now.timestamp()) + cooldownDurationHugPat * 3600}:R> verwenden.",
            ephemeral=True
        )
        return

    Premium = getPremium(connection, userID)
    if Premium:
        if not updateHugPatUses(connection, userID, maxUsesPremium):
            await interaction.response.send_message(
                f"Du hast den Pat-Befehl heute bereits {maxUsesPremium}x verwendet. Bitte warte bis morgen.",
                ephemeral=True
            )
            return
    else:
        if not updateHugPatUses(connection, userID, maxUses):
            await interaction.response.send_message(
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
    embed.set_image(url="https://cdn.discordapp.com/attachments/1354078227903283251/1354081384666370141/Pat.gif?ex=67e3fe0f&is=67e2ac8f&hm=8885bf9b82c5ed9cef4b43bc8248ba7576befc791ef0c60d55881b02a8f3408e&")
    await interaction.response.send_message("Erfolgreich gesendet", ephemeral=True)
    await channel.send(embed=embed)

    ghostping = await channel.send(f"{person.mention}")
    await ghostping.delete()