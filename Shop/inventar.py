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
    items = shop.loadItems()
    userID = interaction.user.id
    userItems = getUserItems(connection, userID)
    

    for item in userItems:
        itemID = item[0]
        count = item[1]

#TODO: Tedten obs geht
    
    embed = discord.Embed(title="Inventar", color=0x005b96)
    for item in items:
        inventory = Inventory(item, getUserItemCount(connection, userID, item.itemID))
        embed.add_field(name=item.name, value=inventory, inline=False)
    return embed