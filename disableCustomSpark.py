import discord
from dataBase import *

connection = createConnection()

class disableCustomSparkModal(discord.ui.Modal, title="Disable Custom Spark"):
    SparkID = discord.ui.TextInput(label="SparkID", style=discord.TextStyle.short, required=True)

    async def on_submit(self, interaction):
        SparkID = self.SparkID.value
        userID = str(interaction.user.id)
        disabledStat = getStatDisabled(connection, SparkID)

        if disabledStat is None:
            await interaction.response.send_message("Gib eine gültige Zahl ein!", ephemeral=True)
            return
        elif disabledStat[1] == userID and disabledStat[0] == 0:
            setStatDisabled(connection, SparkID, 1)
            await interaction.response.send_message(f"Spark mit der ID {SparkID} wurde deaktiviert.", ephemeral=True)
            return
        elif disabledStat[1] == userID and disabledStat[0] == 1:
            setStatDisabled(connection, SparkID, 0)
            await interaction.response.send_message(f"Spark mit der ID {SparkID} wurde aktiviert.", ephemeral=True)
            return
        elif disabledStat[1] != userID:
            await interaction.response.send_message("Du kannst nur deine eigenen Sparks deaktivieren.", ephemeral=True)
            return
        elif disabledStat[0] == 1:
            await interaction.response.send_message("Dieser Spark ist bereits deaktiviert.", ephemeral=True)
            return