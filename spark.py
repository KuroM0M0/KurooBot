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