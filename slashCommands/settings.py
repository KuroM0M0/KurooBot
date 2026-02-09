from discord.ext import commands
import discord
from discord import app_commands
from config import connection
from user.settings import *


class Settings(commands.Cog):
    @app_commands.command(name="settings", description="Stelle zB. SparkDMs ein/aus")
    async def settings(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        userID = str(interaction.user.id)
        premium = getPremium(connection, userID)

        if checkUserSetting(connection, userID) == None:
            insertUserSetting(connection, userID)

        settingsObj = newSettings(premium, userID)
        view = SettingsView(premium, userID)
        embed = settingsObj.getEmbed()
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Settings(bot))
    print("Settings geladen ✅")