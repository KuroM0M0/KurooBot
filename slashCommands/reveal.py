import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from discord import ButtonStyle, ui
from Methoden import replaceEmotes
from dataBase import *
from config import connection


class Reveal(commands.Cog):
    @app_commands.command(name="reveal", description="Lasse dir anzeigen von wem ein Spark gesendet wurde!")
    async def reveal(self, interaction: discord.Interaction, sparkid: int = None):
        await interaction.response.defer(ephemeral=True)
        userID = str(interaction.user.id)
        revealUses = getRevealUses(connection, userID)
        reveals = getReveals(connection, userID) #noch nicht revealed
        customReveals = getRevealsCustom(connection, userID) #noch nicht revealede custom sparks
        revealed = getRevealedSparks(connection, userID) #schon revealed
        revealedCustom = getRevealedSparksCustom(connection, userID)
        if sparkid is not None:
            isRevealed = getIsRevealed(connection, sparkid)
            if revealUses < 1:
                await interaction.followup.send("Du hast keine Reveals mehr. Um dir neue zu holen, gib '/help reveal' ein.", ephemeral=True)
                return

            if userID != getSparkTargetID(connection, sparkid):
                await interaction.followup.send("Du kannst nur Sparks revealen, die du selbst erhalten hast!", ephemeral=True)
                return

            result = getSparkReveal(connection, sparkid)
            if result is None:
                await interaction.followup.send("Dieser Spark existiert nicht oder der Sender möchte Anonym bleiben.", ephemeral=True)
                return
            elif isRevealed == True:
                await interaction.followup.send(f"Dieser Spark wurde bereits von dir aufgedeckt!", ephemeral=True)
                return
            else:
                await interaction.followup.send(f"Dieser Spark wurde von {result} gesendet.", ephemeral=True)
                setRevealUses(connection, userID, revealUses - 1)
                setIsRevealed(connection, sparkid)
        else:
            description_lines = []
            if not reveals and not customReveals:
                embed = discord.Embed(
                    title="✨ Revealbare Sparks:",
                    description="Du hast aktuell keine revealbaren Sparks.",
                    color=0x00ff00)
                
            else:
                if revealed or revealedCustom:
                    description_lines.append("**Bereits revealed:**")
                if revealed:
                    description_lines.extend(revealEmbed(revealed))

                # 2️⃣ Noch nicht revealed Sparks
                if reveals:
                    if description_lines:
                        description_lines.append("")  # Leerzeile zur Trennung
                    description_lines.append("**Noch revealbar:**")
                    for spark_id, timestamp, compliment in reveals:
                        try:
                            dt = datetime.fromisoformat(timestamp)
                            unix_ts = int(dt.timestamp())
                        except ValueError:
                            unix_ts = 0
                        line = f"{compliment} — <t:{unix_ts}:R> — ID `{spark_id}`"
                        description_lines.append(line)

                # Falls gar nichts vorhanden ist
                if not description_lines:
                    description_lines.append("Du hast aktuell keine revealbaren Sparks.")

                # Embed erstellen
                embed = discord.Embed(
                    title="✨ Revealbare Sparks:",
                    description="\n".join(description_lines),
                    color=0x005b96
                )
            await interaction.followup.send(embed=embed, view=RevealMainView(reveals, revealed, customReveals, revealedCustom), ephemeral=True)


class RevealMainView(ui.View):
    def __init__(self, normal_reveals, revealed, custom_reveals, revealed_custom):
        super().__init__(timeout=None)
        self.normal_reveals = normal_reveals
        self.revealed = revealed
        self.custom_reveals = custom_reveals
        self.revealed_custom = revealed_custom

    @ui.button(label="Custom Sparks", style=discord.ButtonStyle.primary)
    async def show_custom(self, interaction: discord.Interaction, button: ui.Button):
        # Wechsel zu Custom-View
        custom_embed = buildCustomEmbed(self.custom_reveals, self.revealed_custom, interaction)
        await interaction.response.edit_message(embed=custom_embed, view=RevealCustomView(
            self.normal_reveals, self.revealed, self.custom_reveals, self.revealed_custom
        ))


class RevealCustomView(ui.View):
    def __init__(self, normal_reveals, revealed, custom_reveals, revealed_custom):
        super().__init__(timeout=None)
        self.normal_reveals = normal_reveals
        self.revealed = revealed
        self.custom_reveals = custom_reveals
        self.revealed_custom = revealed_custom

    @ui.button(label="Zurück", style=discord.ButtonStyle.secondary)
    async def back_to_main(self, interaction: discord.Interaction, button: ui.Button):
        # Wechsel zurück zur Haupt-View
        main_embed = buildMainEmbed(self.normal_reveals, self.revealed, interaction)
        await interaction.response.edit_message(embed=main_embed, view=RevealMainView(
            self.normal_reveals, self.revealed, self.custom_reveals, self.revealed_custom
        ))





def revealEmbed(revealed):
    descLines = []
    for spark_id, timestamp, compliment, sender_name in revealed:
        try:
            dt = datetime.fromisoformat(timestamp)
            unix_ts = int(dt.timestamp())
        except ValueError:
            unix_ts = 0
        line = f"{compliment} — <t:{unix_ts}:R> — von **{sender_name}** — ID `{spark_id}`"
        descLines.append(line)
    return descLines


def buildMainEmbed(reveals, revealed, interaction):
    description_lines = []

    if revealed:
        description_lines.append("**Bereits revealed:**")
        for spark_id, timestamp, compliment, sender_name in revealed:
            compliment = replaceEmotes(compliment, interaction.guild, interaction.client)
            try:
                dt = datetime.fromisoformat(timestamp)
                unix_ts = int(dt.timestamp())
            except ValueError:
                unix_ts = 0
            description_lines.append(f"{compliment} — <t:{unix_ts}:R> — von **{sender_name}** — ID `{spark_id}`")

    if reveals:
        if description_lines:
            description_lines.append("")  # Leerzeile
        description_lines.append("**Noch revealbar:**")
        for spark_id, timestamp, compliment in reveals:
            compliment = replaceEmotes(compliment, interaction.guild, interaction.client)
            try:
                dt = datetime.fromisoformat(timestamp)
                unix_ts = int(dt.timestamp())
            except ValueError:
                unix_ts = 0
            description_lines.append(f"{compliment} — <t:{unix_ts}:R> — ID `{spark_id}`")

    if not description_lines:
        description_lines.append("Du hast aktuell keine revealbaren Sparks.")

    return discord.Embed(
        title="✨ Revealbare Sparks:",
        description="\n".join(description_lines),
        color=0x00ff00
    )


def buildCustomEmbed(custom_reveals, revealed_custom, interaction):
    description_lines = []

    if revealed_custom:
        description_lines.append("**Bereits revealed (Custom):**")
        for spark_id, timestamp, compliment, sender_name in revealed_custom:
            compliment = replaceEmotes(compliment, interaction.guild, interaction.client)
            try:
                dt = datetime.fromisoformat(timestamp)
                unix_ts = int(dt.timestamp())
            except ValueError:
                unix_ts = 0
            description_lines.append(f"{compliment} — <t:{unix_ts}:R> — von **{sender_name}** — ID `{spark_id}`")
            description_lines.append("────────────")

    if custom_reveals:
        if description_lines:
            description_lines.append("")  # Leerzeile
        description_lines.append("**Noch revealbar (Custom):**")
        for spark_id, timestamp, compliment in custom_reveals:
            compliment = replaceEmotes(compliment, interaction.guild, interaction.client)
            try:
                dt = datetime.fromisoformat(timestamp)
                unix_ts = int(dt.timestamp())
            except ValueError:
                unix_ts = 0
            description_lines.append(f"{compliment} — <t:{unix_ts}:R> — ID `{spark_id}`")
            description_lines.append("────────────")

    if not description_lines:
        description_lines.append("Du hast aktuell keine revealbaren Custom Sparks.")

    return discord.Embed(
        title="✨ Revealbare Sparks:",
        description="\n".join(description_lines),
        color=0x00ff00
    )


async def setup(bot):
    await bot.add_cog(Reveal(bot))
    print("reveal geladen ✅")