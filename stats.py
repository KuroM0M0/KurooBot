from dataBase import *
from Methoden import replaceEmotes
import discord

connection = createConnection()

async def StatsSelf(user, interaction, scope="global"):
    if scope == "server":
        complimentStats = getServerCompliments(connection, user.id, str(interaction.guild.id))
    else:
        complimentStats = getCompliments(connection, user.id)

    if complimentStats["Normal"] or complimentStats["Custom"]:
        def format_stats(data, show_x=True):
            return "\n".join([
                replaceEmotes(f"{compliment} {count}{'x' if show_x else ''}", interaction.guild, interaction.client)
                for compliment, count in data.items()
            ])

        normal_text = format_stats(complimentStats["Normal"], show_x=True)
        custom_text = format_stats(complimentStats["Custom"], show_x=False)

        full_text = ""
        if normal_text:
            full_text += "**🌟 Sparks**\n" + normal_text
        if custom_text:
            if full_text:
                full_text += "\n\n────────────────────────────\n\n"
            full_text += "**✨ Custom Sparks**\n" + custom_text

        embedSelf = discord.Embed(
            title=f"📊 Stats von {user.display_name}",
            description=full_text,
            color=0x005b96
        )
        embedSelf.set_thumbnail(url=user.display_avatar.url)

        # Spark-Counts auch splitten
        if scope == "server":
            sparkCountSelf = getSparkCountSelfServer(connection, user.id, str(interaction.guild.id))
            sparkCountDisabled = getSparkCountDisabledServer(connection, user.id, str(interaction.guild.id))
        else:
            sparkCountSelf = getSparkCountSelf(connection, user.id)
            sparkCountDisabled = getSparkCountDisabled(connection, user.id)

        if sparkCountDisabled:
            embedSelf.set_footer(
                text=f"Hat {sparkCountSelf} Sparks erhalten und {sparkCountDisabled} davon ausgeblendet"
            )
        else:
            embedSelf.set_footer(text=f"Hat {sparkCountSelf} Sparks erhalten")
        return embedSelf
    return None


async def StatsTarget(target, interaction, scope="global"):
    if scope == "server":
        complimentStats = getServerCompliments(connection, target.id, str(interaction.guild.id))
    else:
        complimentStats = getCompliments(connection, target.id)

    if complimentStats["Normal"] or complimentStats["Custom"]:
        def format_stats(data, show_x=True):
            return "\n".join([
                replaceEmotes(f"{compliment} {count}{'x' if show_x else ''}", interaction.guild, interaction.client)
                for compliment, count in data.items()
            ])

        normal_text = format_stats(complimentStats["Normal"], show_x=True)
        custom_text = format_stats(complimentStats["Custom"], show_x=False)

        full_text = ""
        if normal_text:
            full_text += "**🌟 Sparks**\n" + normal_text
        if custom_text:
            if full_text:
                full_text += "\n\n────────────────────────────\n\n"
            full_text += "**✨ Custom Sparks**\n" + custom_text

        embedTarget = discord.Embed(
            title=f"📊 Stats von {target.display_name}",
            description=full_text,
            color=0x005b96
        )
        embedTarget.set_thumbnail(url=target.display_avatar.url)

        # Spark-Counts auch splitten
        if scope == "server":
            sparkCountSelf = getSparkCountSelfServer(connection, target.id, str(interaction.guild.id))
            sparkCountDisabled = getSparkCountDisabledServer(connection, target.id, str(interaction.guild.id))
        else:
            sparkCountSelf = getSparkCountSelf(connection, target.id)
            sparkCountDisabled = getSparkCountDisabled(connection, target.id)

        if sparkCountDisabled:
            embedTarget.set_footer(
                text=f"Hat {sparkCountSelf} Sparks erhalten und {sparkCountDisabled} davon ausgeblendet"
            )
        else:
            embedTarget.set_footer(text=f"Hat {sparkCountSelf} Sparks erhalten")
        return embedTarget
    return None


class StatSelect(discord.ui.Select):
    def __init__(self, user, person, interaction):
        options = [
            discord.SelectOption(label="🌐 Global", description="Stats von allen Servern zusammen", value="global"),
            discord.SelectOption(label="🖥️ Serverweit", description="Stats nur auf diesem Server", value="server")
        ]
        super().__init__(placeholder="Wähle eine Kategorie", min_values=1, max_values=1, options=options)
        self.user = user
        self.person = person
        self.interaction = interaction

    async def callback(self, interaction: discord.Interaction):
        scope = self.values[0]

        if self.person is None:
            embed = await StatsSelf(self.user, interaction, scope)
        else:
            embed = await StatsTarget(self.person, interaction, scope)

        if embed:
            await interaction.response.edit_message(embed=embed, view=self.view)
        else:
            await interaction.response.edit_message(content="Keine Stats vorhanden.", embed=None, view=None)


class StatView(discord.ui.View):
    def __init__(self, user, person, interaction):
        super().__init__(timeout=60)
        self.add_item(StatSelect(user, person, interaction))