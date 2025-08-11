import discord
from discord.ext import commands
from datetime import datetime
from dataBase import *
from Methoden import *

KuroID = 308660164137844736
connection = createConnection()


class KuroCommands(commands.Cog):
    @commands.command(name="PremiumAktivieren")
    async def PremiumAktivieren(ctx, member: discord.Member):
        targetID = member.id
        userID = ctx.author.id
        if userID == KuroID:
            await ctx.send(f"{member} hat nun Premium!")
            setPremium(connection, datetime.now().isoformat(), targetID)
        else:
            await ctx.send("Du bist nicht berechtigt dies zu tun!")

    @commands.command(name="PremiumDeaktivieren")
    async def PremiumDeaktivieren(ctx, member: discord.Member):
        targetID = member.id
        userID = ctx.author.id
        if userID == KuroID:
            await ctx.send(f"{member} hat nun kein Premium mehr!")
            resetPremium(connection, targetID)
        else:
            await ctx.send("Du bist nicht berechtigt dies zu tun!")

    @commands.command(name="setReveals")
    async def setReveals(ctx, member: discord.Member, uses: int):
        targetID = member.id
        userID = ctx.author.id
        if userID == KuroID:
            await ctx.send(f"{member} hat nun {uses} Reveals!")
            setRevealUses(connection, targetID, uses)
        else:
            await ctx.send("Du bist nicht berechtigt dies zu tun!")


async def setup(bot):
    await bot.add_cog(KuroCommands(bot))