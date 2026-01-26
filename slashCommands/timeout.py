from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from config import MainServerID, RoleID
import discord

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.guilds(discord.Object(id=MainServerID))
    @app_commands.default_permissions(mention_everyone=True)
    @app_commands.command(name="timeout", description="Timeoute eine Person")
    async def timeout(self, interaction: discord.Interaction, target: discord.User):
        await interaction.response.send_modal(TimeoutModal(target))


class TimeoutModal(discord.ui.Modal):
    def __init__(self, target: discord.User):
        super().__init__(title="Timeout " + target.name)
        self.target = target

        self.durationSelect = discord.ui.Select(
            placeholder="Dauer",
            options=[
                discord.SelectOption(label="1min", value="1min"),
                discord.SelectOption(label="30min", value="30min"),
                discord.SelectOption(label="1h", value="1h"),
                discord.SelectOption(label="2h", value="2h"),
                discord.SelectOption(label="3h", value="3h"),
                discord.SelectOption(label="4h", value="4h"),
                discord.SelectOption(label="5h", value="5h"),
                discord.SelectOption(label="6h", value="6h"),
                discord.SelectOption(label="8h", value="8h"),
                discord.SelectOption(label="10h", value="10h"),
                discord.SelectOption(label="12h", value="12h"),
                discord.SelectOption(label="15h", value="15h"),
                discord.SelectOption(label="20h", value="20h"),
            ])

        duration = discord.ui.Label(
            text="Dauer des Timeouts",
            component=self.durationSelect
        )

        self.reason = discord.ui.TextInput(label="Grund", placeholder="zb. Trolling", style=discord.TextStyle.long)

        self.add_item(duration)
        self.add_item(self.reason)
        #discord.ui.TextInput(label="Dauer", placeholder="Dauer", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        selectedDuration = self.durationSelect.values[0]
        reason = self.reason.value or "Kein Grund angegeben"

        minutes = 0
        if "min" in selectedDuration:
            minutes = int(selectedDuration.replace("min", ""))
        elif "h" in selectedDuration:
            minutes = int(selectedDuration.replace("h", "")) * 60
            
        duration = timedelta(minutes=minutes)

        try:
            # 4. Timeout anwenden
            # Hinweis: target muss ein discord.Member sein, damit .timeout() existiert
            #await self.target.timeout(duration, reason=reason)
            
            await interaction.response.send_message(
                f"✅ **{self.target.name}** wurde für **{selectedDuration}** stummgeschaltet.\n"
                f"**Grund:** {reason}", 
                ephemeral=True
            )
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Ich habe keine Berechtigung, diesen User zu timeouten (vielleicht ist seine Rolle höher als meine?).", 
                ephemeral=True
            )










async def setup(bot):
    await bot.add_cog(Timeout(bot))
    print("timeout geladen ✅")