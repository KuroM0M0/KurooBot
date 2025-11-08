import discord
from dataBase import *

connection = createConnection()

class disableCustomSparkModal(discord.ui.Modal, title="Disable Custom Spark"):
    SparkID = discord.ui.TextInput(label="SparkID", style=discord.TextStyle.short, required=True)

    async def on_submit(self, interaction):
        await interaction.response.defer(ephemeral=True)
        SparkID = self.SparkID.value
        userID = str(interaction.user.id)
        await checkStatCanBeDisabled(SparkID, userID, interaction)

        
        
async def checkStatCanBeDisabled(SparkID, userID, interaction):
    disabledStat = getStatDisabled(connection, SparkID)
    if disabledStat is None:
        await interaction.followup.send("Gib eine gültige Zahl ein!", ephemeral=True)
        return
    elif disabledStat[1] == userID and disabledStat[0] == 0:
        setStatDisabled(connection, SparkID, 1)
        await interaction.followup.send(f"Spark mit der ID {SparkID} wurde deaktiviert.", ephemeral=True)
        return
    elif disabledStat[1] == userID and disabledStat[0] == 1:
        setStatDisabled(connection, SparkID, 0)
        await interaction.followup.send(f"Spark mit der ID {SparkID} wurde aktiviert.", ephemeral=True)
        return
    elif disabledStat[1] != userID:
        await interaction.followup.send("Du kannst nur deine eigenen Sparks deaktivieren.", ephemeral=True)
        return
    elif disabledStat[0] == 1:
        await interaction.followup.send("Dieser Spark ist bereits deaktiviert.", ephemeral=True)
        return