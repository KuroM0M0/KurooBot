import discord
import asyncio
from dataBase import *

connection = createConnection()



class NewsletterModal(discord.ui.Modal, title="Newsletter"):
    new = discord.ui.TextInput(label="Was ist neu?", style=discord.TextStyle.paragraph, required=True)
    updateNr = discord.ui.TextInput(label="Nummer/Name des Updates", style=discord.TextStyle.short, required=True)
    fazit = discord.ui.TextInput(label="Zusammenfassung", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Update {self.updateNr.value}", color=discord.Color.green())
        embed.add_field(name="Was ist neu?", value=self.new.value, inline=False)
        embed.add_field(name="Zusammenfassung", value=self.fazit.value, inline=False)

        NewsletterSubs = getNewsletterSubs(connection)
        for subscriber in NewsletterSubs:
            Subs = await interaction.client.fetch_user(subscriber)
            await Subs.send(embed=embed)
            await asyncio.sleep(1)