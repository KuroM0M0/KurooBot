import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from dataBase import *
from Methoden import *
from slashCommands.spark import CheckSparkChannel
from config import connection

class Profil(commands.Cog):
    @app_commands.command(name="profil", description="Zeige dein Profil an")
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

async def setup(bot: commands.Bot):
    await bot.add_cog(Profil(bot))
    print("Profil geladen ✅")