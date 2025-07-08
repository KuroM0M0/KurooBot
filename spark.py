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
    BotID = 1310744379228426290
    channel = interaction.channel

    messages = [msg async for msg in channel.history(limit=2)]
    if messages and messages[1].author.id == BotID:
        target = await interaction.client.fetch_user(int(targetID))
        await target.send(messages[0].jump_url)
