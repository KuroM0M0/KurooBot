import discord
from datetime import datetime
from discord import ButtonStyle, ui
from Methoden import replaceEmotes

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