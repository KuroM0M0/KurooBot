import asyncio
import discord
from discord import ButtonStyle, ui
from dataBase import *

class WhatIsSparkButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Was ist ein Spark?", style=discord.ButtonStyle.secondary, custom_id="whatIsSpark")
    async def what_is_spark(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Ein Spark ist ein **anonymes** Kompliment an dich. Jeder kann **täglich einmal** einer Person einen Spark senden. Wenn du mehr zu bestimmten Befehlen wissen willst, kannst du einfach **/help (CommandName)** eingeben c:", ephemeral=True)

            
async def SparkCheck(cooldown, SparkUses, Premium, date, interaction):

    """prüft ob User heute schon gesparkt hat"""
    if cooldown:
        if Premium:
            #Wenn User Premium hat, dann prüft ob mehr als 2 mal gesparkt wurde
            if SparkUses == 2:
                await interaction.followup.send(f"Du hast Heute bereits 2x gesparkt! Versuchs morgen nochmal.", ephemeral=True)
                raise Exception("2 Uses Premium")
        else:
            if cooldown == date:
                await interaction.followup.send(f"Du kannst den Befehl /spark morgen wieder verwenden.", ephemeral=True)
                raise Exception("Cooldown")



async def sendSparkDM(targetID, interaction):
    #BotID = 1306244838504665169
    BotID = 1310744379228426290#TestbotID

    channel = interaction.channel

    messages = [msg async for msg in channel.history(limit=1)]
    if messages and messages[0].author.id == BotID:
        target = await interaction.client.fetch_user(int(targetID))
        embed = discord.Embed(title="Du wurdest gesparkt!", description=messages[0].jump_url, color=0x005b96)
        await target.send(embed=embed, view=WhatIsSparkButton())



async def CheckSparkChannel(connection, guildID, channelID, interaction):
    sparkChannel = getChannelSparkID(connection, guildID)
    if sparkChannel != channelID and sparkChannel != None:
        await interaction.followup.send("Du kannst hier keine Befehle nutzen! Nutze den vorgesehenen Channel dafür.", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.delete_original_response()
        raise Exception("Wrong Channel")
    