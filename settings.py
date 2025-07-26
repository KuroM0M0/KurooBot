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
        userID = interaction.user.id
        StreakPrivate = getStreakPrivate(connection, userID)

        if StreakPrivate == True:
            setStreakPrivate(connection, userID, False)
            await interaction.response.send_message("Deine Streak ist jetzt wieder für alle sichtbar!", ephemeral=True)

        else:
            setStreakPrivate(connection, userID, True)
            await interaction.response.send_message("Deine Streak ist nun nur für dich Sichtbar!", ephemeral=True)


    @ui.button(label="StatsPrivate", style=discord.ButtonStyle.red)
    async def StatsPrivate(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Diese Einstellung ist nur für Premium Nutzer verfugbar!", ephemeral=True)


    @ui.button(label="Newsletter", style=discord.ButtonStyle.red)
    async def Newsletter(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Diese Einstellung ist nur für Premium Nutzer verfugbar!", ephemeral=True)




class PremiumSettings(ui.View):
    @ui.button(label="StreakPrivate", style=discord.ButtonStyle.primary)
    async def StreakPrivate(self, interaction: discord.Interaction, button: ui.Button):
        userID = interaction.user.id
        StreakPrivate = getStreakPrivate(connection, userID)

        if StreakPrivate == True:
            setStreakPrivate(connection, userID, False)
            await interaction.response.send_message("Deine Streak ist jetzt wieder für alle sichtbar!", ephemeral=True)

        else:
            setStreakPrivate(connection, userID, True)
            await interaction.response.send_message("Deine Streak ist nun nur für dich Sichtbar!", ephemeral=True)


    @ui.button(label="StatsPrivate", style=discord.ButtonStyle.primary)
    async def StatsPrivate(self, interaction: discord.Interaction, button: ui.Button):
        userID = interaction.user.id
        StatsPrivate = getStatsPrivate(connection, userID)

        if StatsPrivate == True:
            setStatsPrivate(connection, userID, False)
            await interaction.response.send_message("Deine Stats sind jetzt wieder öffentlich sichtbar!", ephemeral=True)

        else:
            setStatsPrivate(connection, userID, True)
            await interaction.response.send_message("Deine Stats sind nun Privat!", ephemeral=True)


    @ui.button(label="Newsletter", style=discord.ButtonStyle.green)
    async def Newsletter(self, interaction: discord.Interaction, button: ui.Button):
        userID = interaction.user.id
        Newsletter = getNewsletter(connection, userID)

        if Newsletter == True:
            button.label = "Newsletter: deaktiv❌"
            await interaction.response.edit_message(view=self)
            setNewsletter(connection, userID, False)
            await interaction.response.send_message("Du erhältst nun keine Updates mehr in deinen DMs!", ephemeral=True)

        else:
            button.label = "Newsletter: aktiv✅"
            await interaction.response.edit_message(view=self)
            setNewsletter(connection, userID, True)
            await interaction.response.send_message("Du erhältst nun Updates in deine DMs!", ephemeral=True)

    @ui.button(label="SparkDM", style=discord.ButtonStyle.primary)
    async def SparkDM(self, interaction: discord.Interaction, button: ui.Button):
        userID = interaction.user.id
        SparkDM = getSparkDM(connection, userID)

        if SparkDM == True:
            button.label = "Sparks per DM: deaktiv❌"
            await interaction.response.edit_message(view=self)
            setSparkDM(connection, userID, False)
            await interaction.response.send_message("Du erhaltet nun keine private Nachricht mehr, wenn du gesparkt wurdest!", ephemeral=True)

        else:
            button.label = "Sparks per DM: aktiv✅"
            await interaction.response.edit_message(view=self)
            setSparkDM(connection, userID, True)
            await interaction.response.send_message("Du erhaltet nun private Nachrichten, wenn du gesparkt wurdest!", ephemeral=True)

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


def settingStuff(userID):
    """Prüft ob User in der Datenbank Settings hat, wenn nicht wird er hinzugefügt"""
    userHaveSettings = checkUserSetting(connection, userID)
    
    if not userHaveSettings:
        insertUserSetting(connection, userID)

    