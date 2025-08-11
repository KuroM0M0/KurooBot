import discord
from discord.ext import commands
from datetime import datetime
from dataBase import *
from Methoden import *

class SecretCommands(commands.Cog):
    @commands.command(name="verkraben")
    async def verkraben(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        if member == None:
            await ctx.send(f"{target.mention} hat sich verkraben!")
        else:
            await ctx.send(f"{target.mention} geh dich verkraben!")

    @commands.command(name="bremium")
    async def bremium(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        if member == None:
            await ctx.send(f"{target.mention} hat sich bremium geholt!")
        else:
            await ctx.send(f"{target.mention} hol dir auch bremium! c:")






async def setup(bot):
    await bot.add_cog(SecretCommands(bot))