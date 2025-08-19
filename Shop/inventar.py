import discord
from discord import ui
from Shop.shop import Shop
from dataBase import *

class InventarButtons(ui.View):
    def __init__(self, connection):
        super().__init__(timeout=None)
        self.connection = connection


def InventarEmbed(interaction, connection):
    shop = Shop(connection)
    items = shop.loadItems()
    userID = interaction.user.id
    userItems = getUserItems(connection, userID)

    
    embed = discord.Embed(title="Inventar", color=0x005b96)
    for item in items:
        embed.add_field(name=item.name, value=item.description, inline=False)
    return embed