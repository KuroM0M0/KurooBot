async def sparkCheck(cooldown, SparkUses, Premium, date, interaction):
#prüft ob User schon gesparkt hat heute
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