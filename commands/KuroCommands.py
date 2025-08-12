import discord
from discord.ext import commands
from datetime import datetime
from dataBase import *
from Methoden import *

connection = createConnection()
KuroID = 308660164137844736


class KuroCommands(commands.Cog):
    @commands.command(name="PremiumAktivieren")
    async def PremiumAktivieren(self, ctx, member: discord.Member):
        targetID = member.id
        userID = ctx.author.id
        if userID == KuroID:
            await ctx.send(f"{member} hat nun Premium!")
            setPremium(connection, datetime.now().isoformat(), targetID)
        else:
            await ctx.send("Du bist nicht berechtigt dies zu tun!")

    @commands.command(name="PremiumDeaktivieren")
    async def PremiumDeaktivieren(self, ctx, member: discord.Member):
        targetID = member.id
        userID = ctx.author.id
        if userID == KuroID:
            await ctx.send(f"{member} hat nun kein Premium mehr!")
            resetPremium(connection, targetID)
        else:
            await ctx.send("Du bist nicht berechtigt dies zu tun!")

    @commands.command(name="setReveals")
    async def setReveals(self, ctx, member: discord.Member, uses: int):
        targetID = member.id
        userID = ctx.author.id
        if userID == KuroID:
            await ctx.send(f"{member} hat nun {uses} Reveals!")
            setRevealUses(connection, targetID, uses)
        else:
            await ctx.send("Du bist nicht berechtigt dies zu tun!")

    @commands.command(name="addReveals")
    async def addReveals(self, ctx, member: discord.Member, addUses: int):
        targetID = member.id
        userID = ctx.author.id
        if userID == KuroID:
            uses = getRevealUses(connection, targetID) + addUses
            await ctx.send(f"{member} hat nun {uses} Reveals!")
            setRevealUses(connection, targetID, uses)
        else:
            await ctx.send("Du bist nicht berechtigt dies zu tun!")


async def setup(bot):
    await bot.add_cog(KuroCommands(bot))
    print("KuroCommands geladen ✅")