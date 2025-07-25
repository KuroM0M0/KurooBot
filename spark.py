import discord

async def sparkCheck(cooldown, SparkUses, Premium, date, interaction):
    """prüft ob User heute schon gesparkt hat"""
    if cooldown:
        if Premium:
            #Wenn User Premium hat, dann prüft ob mehr als 2 mal gesparkt wurde
            if SparkUses == 2:
                await interaction.response.send_message(f"Du hast Heute bereits 2x gesparkt! Versuchs morgen nochmal.", ephemeral=True)
                return
        else:
            if cooldown == date:
                await interaction.response.send_message(f"Du kannst den Befehl /spark morgen wieder verwenden.", ephemeral=True)
                return
            


async def sendSparkDM(targetID, interaction):
    BotID = 1306244838504665169#TestbotID#1310744379228426290
    channel = interaction.channel

    messages = [msg async for msg in channel.history(limit=1)]
    if messages and messages[0].author.id == BotID:
        target = await interaction.client.fetch_user(int(targetID))
        embed = discord.Embed(title="Du wurdest gesparkt!", description=messages[0].jump_url, color=0x005b96)
        await target.send(embed=embed)