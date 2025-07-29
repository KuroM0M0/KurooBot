from dataBase import *
import discord
from discord import ButtonStyle, ui

connection = createConnection()

#secondary, grey, gray = grau
#primary, blurple = blau
#danger, red = rot
#green, success = grün
#link = link benötigt
#premium = sku_id benötigt

class Settings(ui.View):
    @ui.button(label="StreakPrivate", style=discord.ButtonStyle.green)
    async def StreakPrivate(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        userID = interaction.user.id
        StreakPrivate = getStreakPrivate(connection, userID)

        if StreakPrivate == True:
            button.label = "Streak: Öffentlich🌐"
            await interaction.edit_original_response(view=self)
            setStreakPrivate(connection, userID, False)

        else:
            button.label = "Streak: Privat🔒"
            await interaction.edit_original_response(view=self)
            setStreakPrivate(connection, userID, True)

    @ui.button(label="Ghostping", style=discord.ButtonStyle.primary)
    async def Ghostping(self, interaction: discord.Interaction, button: ui.Button):
        userID = interaction.user.id
        Ghostping = getGhostpingSetting(connection, userID)

        if Ghostping == True:
            button.label = "Ghostping: deaktiv❌"
            await interaction.response.edit_message(view=self)
            setGhostpingSetting(connection, userID, False)

        else:
            button.label = "Ghostping: aktiv✅"
            await interaction.response.edit_message(view=self)
            setGhostpingSetting(connection, userID, True)

    @ui.button(label="Profil", style=discord.ButtonStyle.primary)
    async def Profil(self, interaction: discord.Interaction, button: ui.Button):
        userID = interaction.user.id
        Profil = getProfilPrivateSetting(connection, userID)

        if Profil == True:
            button.label = "Profil: Öffentlich🌐"
            await interaction.response.edit_message(view=self)
            setProfilPrivateSetting(connection, userID, False)

        else:
            button.label = "Profil: Privat🔒"
            await interaction.response.edit_message(view=self)
            setProfilPrivateSetting(connection, userID, True)




class PremiumSettings(ui.View):
    @ui.button(label="StreakPrivate", style=discord.ButtonStyle.primary)
    async def StreakPrivate(self, interaction: discord.Interaction, button: ui.Button):
        userID = interaction.user.id
        StreakPrivate = getStreakPrivate(connection, userID)

        if StreakPrivate == True:
            button.label = "Streak: Öffentlich🌐"
            await interaction.response.edit_message(view=self)
            setStreakPrivate(connection, userID, False)
            #await interaction.followup.send("Deine Streak ist jetzt wieder für alle sichtbar!", ephemeral=True)

        else:
            button.label = "Streak: Privat🔒"
            await interaction.response.edit_message(view=self)
            setStreakPrivate(connection, userID, True)
            #await interaction.followup.send("Deine Streak ist nun nur für dich Sichtbar!", ephemeral=True)


    @ui.button(label="StatsPrivate", style=discord.ButtonStyle.primary)
    async def StatsPrivate(self, interaction: discord.Interaction, button: ui.Button):
        userID = interaction.user.id
        StatsPrivate = getStatsPrivate(connection, userID)

        if StatsPrivate == True:
            button.label = "Stats: Öffentlich🌐"
            await interaction.response.edit_message(view=self)
            setStatsPrivate(connection, userID, False)
            #await interaction.response.send_message("Deine Stats sind jetzt wieder öffentlich sichtbar!", ephemeral=True)

        else:
            button.label = "Stats: Privat🔒"
            await interaction.response.edit_message(view=self)
            setStatsPrivate(connection, userID, True)
            #await interaction.response.send_message("Deine Stats sind nun Privat!", ephemeral=True)


    @ui.button(label="Newsletter", style=discord.ButtonStyle.green)
    async def Newsletter(self, interaction: discord.Interaction, button: ui.Button):
        userID = interaction.user.id
        Newsletter = getNewsletter(connection, userID)

        if Newsletter == True:
            button.label = "Newsletter: deaktiv❌"
            await interaction.response.edit_message(view=self)
            setNewsletter(connection, userID, False)
            #await interaction.response.send_message("Du erhältst nun keine Updates mehr in deinen DMs!", ephemeral=True)

        else:
            button.label = "Newsletter: aktiv✅"
            await interaction.response.edit_message(view=self)
            setNewsletter(connection, userID, True)
            #await interaction.response.send_message("Du erhältst nun Updates in deine DMs!", ephemeral=True)

    @ui.button(label="SparkDM", style=discord.ButtonStyle.primary)
    async def SparkDM(self, interaction: discord.Interaction, button: ui.Button):
        userID = interaction.user.id
        SparkDM = getSparkDM(connection, userID)

        if SparkDM == True:
            button.label = "Sparks per DM: deaktiv❌"
            await interaction.response.edit_message(view=self)
            setSparkDM(connection, userID, False)
            #await interaction.response.send_message("Du erhaltet nun keine private Nachricht mehr, wenn du gesparkt wurdest!", ephemeral=True)

        else:
            button.label = "Sparks per DM: aktiv✅"
            await interaction.response.edit_message(view=self)
            setSparkDM(connection, userID, True)
            #await interaction.response.send_message("Du erhaltet nun private Nachrichten, wenn du gesparkt wurdest!", ephemeral=True)

    @ui.button(label="CustomSparks", style=discord.ButtonStyle.primary)
    async def CustomSparks(self, interaction: discord.Interaction, button: ui.Button):
        userID = interaction.user.id
        CustomSpark = getCustomSparkSetting(connection, userID)

        if CustomSpark == True:
            button.label = "Custom Sparks: deaktiv❌"
            await interaction.response.edit_message(view=self)
            setCustomSparkSetting(connection, userID, False)
            #await interaction.response.send_message("Du erhaltet nun keine private Nachricht mehr, wenn du gesparkt wurdest!", ephemeral=True)

        else:
            button.label = "Custom Sparks: aktiv✅"
            await interaction.response.edit_message(view=self)
            setCustomSparkSetting(connection, userID, True)
            #await interaction.response.send_message("Du erhaltet nun private Nachrichten, wenn du gesparkt wurdest!", ephemeral=True)

    @ui.button(label="Ghostping", style=discord.ButtonStyle.primary)
    async def Ghostping(self, interaction: discord.Interaction, button: ui.Button):
        userID = interaction.user.id
        Ghostping = getGhostpingSetting(connection, userID)

        if Ghostping == True:
            button.label = "Ghostping: deaktiv❌"
            await interaction.response.edit_message(view=self)
            setGhostpingSetting(connection, userID, False)

        else:
            button.label = "Ghostping: aktiv✅"
            await interaction.response.edit_message(view=self)
            setGhostpingSetting(connection, userID, True)

    @ui.button(label="Profil", style=discord.ButtonStyle.primary)
    async def Profil(self, interaction: discord.Interaction, button: ui.Button):
        userID = interaction.user.id
        Profil = getProfilPrivateSetting(connection, userID)

        if Profil == True:
            button.label = "Profil: Öffentlich🌐"
            await interaction.response.edit_message(view=self)
            setProfilPrivateSetting(connection, userID, False)

        else:
            button.label = "Profil: Privat🔒"
            await interaction.response.edit_message(view=self)
            setProfilPrivateSetting(connection, userID, True)


def settingStuff(userID):
    """Prüft ob User in der Datenbank Settings hat, wenn nicht wird er hinzugefügt"""
    userHaveSettings = checkUserSetting(connection, userID)
    
    if not userHaveSettings:
        insertUserSetting(connection, userID)

    streakPrivate = getStreakPrivate(connection, userID)
    statsPrivate = getStatsPrivate(connection, userID)
    newsletter = getNewsletter(connection, userID)
    sparkDM = getSparkDM(connection, userID)
    ghostPing = getGhostpingSetting(connection, userID)
    customSpark = getCustomSparkSetting(connection, userID)
    profilPrivate = getProfilPrivateSetting(connection, userID)

    if streakPrivate == 1:
        streakPrivate = "Privat🔒"
    elif streakPrivate == 0:
        streakPrivate = "Öffentlich🌐"

    if statsPrivate == 1:
        statsPrivate = "Privat🔒"
    elif statsPrivate == 0:
        statsPrivate = "Öffentlich🌐"

    if newsletter == 1:
        newsletter = "Aktiv✅"
    elif newsletter == 0:
        newsletter = "Deaktiv❌"

    if sparkDM == 1:
        sparkDM = "Aktiv✅"
    elif sparkDM == 0:
        sparkDM = "Deaktiv❌"

    if customSpark == 1:
        customSpark = "Aktiv✅"
    elif customSpark == 0:
        customSpark = "Deaktiv❌"

    if ghostPing == 1:
        ghostPing = "Aktiv✅"
    elif ghostPing == 0:
        ghostPing = "Deaktiv❌"

    if profilPrivate == 1:
        profilPrivate = "Privat🔒"
    elif profilPrivate == 0:
        profilPrivate = "Öffentlich🌐"

    embed = discord.Embed(title="Settings", color=0x005b96)
    embed.add_field(name="Streak", value=streakPrivate, inline=False)
    embed.add_field(name="Stats", value=statsPrivate, inline=False)
    embed.add_field(name="Newsletter", value=newsletter, inline=False)
    embed.add_field(name="SparkDM", value=sparkDM, inline=False)
    embed.add_field(name="Custom Sparks", value=customSpark, inline=False)
    embed.add_field(name="Ghostping", value=ghostPing, inline=False)
    embed.add_field(name="Profil", value=profilPrivate, inline=False)
    return embed