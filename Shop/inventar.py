import discord
from discord import ui
from dataclasses import dataclass
from Shop.shop import Shop
from dataBase import *

class InventarButtons(ui.View):
    def __init__(self, connection):
        super().__init__(timeout=None)
        self.connection = connection

@dataclass
class Inventory():
    item: object
    count: int


def InventarEmbed(interaction, connection):
    shop = Shop(connection)
    userID = interaction.user.id
    userItems = getUserItems(connection, userID)

    embed = discord.Embed(title="Inventar", color=0x005b96)

    if not userItems:
        embed.add_field(name="Leer", value="Du hast noch keine Items.", inline=False)
        return embed

    for itemID, count in userItems:
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

    return embed