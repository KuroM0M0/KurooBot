from dataBase import *
import discord

connection = createConnection()

async def StatsSelf(user):
    complimentStats = getCompliments(connection, user.id)

    if complimentStats:
        kompliment = "\n".join([f"{k}: {v}" for k, v in complimentStats.items()])
        embedSelf = discord.Embed(
            title=f"Stats von {user.display_name}",
            description=f"{kompliment}",
            color=0x005b96
        )
        embedSelf.set_thumbnail(url=user.display_avatar.url)
        return embedSelf
    return None

async def StatsTarget(target):
    complimentStats = getCompliments(connection, target.id)
    if complimentStats:
        kompliment = "\n".join([f"{k}: {v}" for k, v in complimentStats.items()])
        embedTarget = discord.Embed(
            title=f"Stats von {target.display_name}",
            description=f"{kompliment}",
            color=0x005b96
        )
        embedTarget.set_thumbnail(url=target.display_avatar.url)
        return embedTarget
    return None