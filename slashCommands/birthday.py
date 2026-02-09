import discord
from config import connection    
from discord.ext import commands
from discord import app_commands
from Methoden import getBan
from slashCommands.spark import CheckSparkChannel
from dataBase import *
from typing import Optional
from user.birthday import BirthdayView

class Birthday(commands.Cog):
    @app_commands.command(name="setbirthday", description="Setze deinen Geburtstag")
    async def Birthday(self, interaction: discord.Interaction):
        serverID = str(interaction.guild.id)
        userID = str(interaction.user.id)

        if getBan(connection, serverID, userID) == True:
            await interaction.followup.send("Du wurdest von der Nutzung des Bots ausgeschlossen!", ephemeral=True)
            return

        if serverID is not None:
            channelID = str(interaction.channel.id)
            await CheckSparkChannel(connection, serverID, channelID, interaction)
            
        # Wrapper für save_callback, da die View nur (user_id, year, month, day) übergibt
        def save_cb(user_id: int, year: Optional[int], month: int, day: int):
            # Wenn Jahr optional, erstelle ein date-Objekt
            if year:
                date_str = f"{day:02d}-{month:02d}-{year:04d}"
            else:
                # nur Monat+Tag: setze Jahr auf 2000 oder NULL-String (je nach DB)
                date_str = f"{day:02d}-{month:02d}-2000"  # Beispiel: Jahres-Platzhalter
            setBirthday(connection, user_id, date_str)

        # View erstellen, owner_id = wer den Command aufruft
        view = BirthdayView(owner_id=interaction.user.id, save_callback=save_cb, default_month=None)

        embed = view.build_embed()
        # Nachricht senden
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
        sent = await interaction.original_response()
        view.message = sent


async def setup(bot: commands.Bot):
    await bot.add_cog(Birthday(bot))
    print("Stats geladen ✅")