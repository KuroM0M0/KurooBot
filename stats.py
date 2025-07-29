from dataBase import *
import discord

connection = createConnection()

async def StatsSelf(user):
    complimentStats = getCompliments(connection, user.id)

    if complimentStats["Normal"] or complimentStats["Custom"]:
        def format_stats(data, show_x=True):
            return "\n".join([
                f"{compliment} {count}{'x' if show_x else ''}"
                for compliment, count in data.items()
            ])

        normal_text = format_stats(complimentStats["Normal"], show_x=True)
        custom_text = format_stats(complimentStats["Custom"], show_x=False)

        full_text = ""

        if normal_text:
            full_text += "**🌟 Sparks**\n" + normal_text

        if custom_text:
            if full_text:  # Nur trennen, wenn beide vorhanden sind
                full_text += "\n\n────────────────────────────\n\n"
            full_text += "**✨ Custom Sparks**\n" + custom_text

        embedSelf = discord.Embed(
            title=f"📊 Stats von {user.display_name}",
            description=full_text,
            color=0x005b96
        )
        embedSelf.set_thumbnail(url=user.display_avatar.url)

        sparkCountSelf = getSparkCountSelf(connection, user.id)
        sparkCountDisabled = getSparkCountDisabled(connection, user.id)
        if sparkCountDisabled is not None and sparkCountDisabled != 0:
            embedSelf.set_footer(text=f"Hat {sparkCountSelf} Sparks erhalten und {sparkCountDisabled} davon ausgeblendet")
        else:
            embedSelf.set_footer(text=f"Hat {sparkCountSelf} Sparks erhalten")
        return embedSelf
    return None


async def StatsTarget(target):
    complimentStats = getCompliments(connection, target.id)

    if complimentStats["Normal"] or complimentStats["Custom"]:
        def format_stats(data, show_x=True):
            return "\n".join([
                f"{compliment} {count}{'x' if show_x else ''}"
                for compliment, count in data.items()
            ])

        normal_text = format_stats(complimentStats["Normal"], show_x=True)
        custom_text = format_stats(complimentStats["Custom"], show_x=False)

        full_text = ""

        if normal_text:
            full_text += "**🌟 Sparks**\n" + normal_text

        if custom_text:
            if full_text:  # Nur trennen, wenn beide vorhanden sind
                full_text += "\n\n────────────────────────────\n\n"
            full_text += "**✨ Custom Sparks**\n" + custom_text

        embedTarget = discord.Embed(
            title=f"📊 Stats von {target.display_name}",
            description=full_text,
            color=0x005b96
        )
        embedTarget.set_thumbnail(url=target.display_avatar.url)

        sparkCountSelf = getSparkCountSelf(connection, target.id)
        sparkCountDisabled = getSparkCountDisabled(connection, target.id)
        if sparkCountDisabled is not None and sparkCountDisabled != 0:
            embedTarget.set_footer(text=f"Hat {sparkCountSelf} Sparks erhalten und {sparkCountDisabled} davon ausgeblendet")
        else:
            embedTarget.set_footer(text=f"Hat {sparkCountSelf} Sparks erhalten")
        return embedTarget
    return None