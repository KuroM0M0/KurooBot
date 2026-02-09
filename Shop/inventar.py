import discord
from discord import ui, app_commands
from discord.ext import commands
from dataclasses import dataclass
from Shop.shop import Shop
from dataBase import *
from slashCommands.spark import CheckSparkChannel
from config import connection


class Inventar(commands.Cog):
    @app_commands.command(name="inventar", description="Hier siehst du welche Items du hast c:")
    async def inventar(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = InventarEmbed(interaction, connection)
        serverID = str(interaction.guild.id)
        userID = str(interaction.user.id)

        if getBan(connection, serverID, userID) == True:
            await interaction.followup.send("Du wurdest von der Nutzung vom Bot ausgeschlossen!", ephemeral=True)
            return

        if serverID is not None:
            channelID = str(interaction.channel.id)
            await CheckSparkChannel(connection, serverID, channelID, interaction)
        try:
            await interaction.followup.send(embed=embed, view=InventarButtons(connection))
        except Exception as e:
            print("Fehler beim Senden des Inventars:", e)
            await interaction.followup.send(f"Fehler: {e}", ephemeral=True)


class InventarButtons(ui.View):
    def __init__(self, connection):
        super().__init__(timeout=None)
        self.connection = connection


def InventarEmbed(interaction, connection):
    shop = Shop(connection)
    userID = interaction.user.id
    userItems = getUserItems(connection, userID)
    hatItems = False

    embed = discord.Embed(title="Inventar", color=0x005b96)
    embed.set_footer(text="Nutze /use (item) um dein Item zu verwenden!")

    if not userItems:
        embed.add_field(name="Leer", value="Du hast noch keine Items.", inline=False)
        return embed

    for itemID, count in userItems:
        if count > 0:
            hatItems = True
            shopItem = shop.getItemByID(itemID)
            if shopItem:
                embed.add_field(
                    name=shopItem.name,
                    value=f"Anzahl: {count}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"Unbekanntes Item (ID: {itemID})",
                    value=f"Anzahl: {count}",
                    inline=False
                )

    if not hatItems:
        embed.add_field(name="Leer", value="Du hast noch keine Items.", inline=False)

    return embed


async def setup(bot: commands.Bot):
    await bot.add_cog(Inventar(bot))
    print("Inventar geladen ✅")