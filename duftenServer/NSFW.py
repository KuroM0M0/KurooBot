import discord
import json
from discord import app_commands, ui
from discord.ext import commands

NSFWRoleID = 1186568822879170600 
ServerID = 1185618335950438500

# JSON-Datei einlesen
with open('duftenServer/NSFW_ID.json', 'r') as file:
    data = json.load(file)

class NSFWRevoke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @app_commands.guilds(discord.Object(id=ServerID))
    @commands.has_permissions(administrator=True)
    @app_commands.command(name="nsfwrevoke", description="NSFW Revoke")
    async def nsfwrevoke(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel

        Nachricht = await channel.send("Drücke auf Bye, um die NSFW-Rechte entzogen zu bekommen.", view=interactionView())
        #await Nachricht.add_reaction("🔞")
        self.message_id = Nachricht.id
        data['NSFW_MSG_ID'] = Nachricht.id

        #NachrichtID in JSON speichern | indent=2 steuert einrückung in der Datei
        with open('duftenServer/NSFW_ID.json', 'w') as file:
            json.dump(data, file, indent=2)

        await interaction.delete_original_response()

#unnötig, dient nurnoch als Vorlage falls mal irgendwas mit reaktionen gemacht werden soll
class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_id = data.get('NSFW_MSG_ID')
        print("init geladen")

    #on_reaction_add ist von discord.py und gibt automatisch reaction und user mit
    #on_raw_reaction_add ist die richtige Lösung wenn der Bot auch nach nem Neustart reagieren soll
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = self.bot.get_user(payload.user_id)

        if message.id == self.message_id:
            await channel.send(f"{user.mention} möchtest du wirklich den Zugang zum NSFW Bereich verlieren?", view=confirmView())


class interactionView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Bye", style=discord.ButtonStyle.green, custom_id="confirm")
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Möchtest du wirklich den Zugang zum NSFW Bereich verlieren?", view=confirmView(), ephemeral=True)



class confirmView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Ja", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        user = interaction.user
        guild = interaction.guild
        role = guild.get_role(NSFWRoleID)
        await user.remove_roles(role)
        await interaction.response.send_message(f"{user.mention} du hast den Zugang zum NSFW Bereich verloren.", ephemeral=True)

    @ui.button(label="Nein", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(content="Aktion abgebrochen.", view=None)





async def setup(bot):
    await bot.add_cog(NSFWRevoke(bot))
    #await bot.add_cog(Reaction(bot))
    print("Duftende Commands geladen ✅")