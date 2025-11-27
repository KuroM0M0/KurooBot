import discord
import emotes as E
from discord.ext import commands
from datetime import datetime
from dataBase import *
from Methoden import *
from config import *
from Twitch.checkLive import checkStreamStatus

class SecretCommands(commands.Cog):
    @commands.command(name="verkraben")
    async def verkraben(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        if member == None:
            await ctx.send(f"{target.mention} hat sich verkraben! {E.Schaufel}")
        else:
            await ctx.send(f"{target.mention} geh dich verkraben! {E.Schaufel}")

    @commands.command(name="bremium")
    async def bremium(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        if member == None:
            await ctx.send(f"{target.mention} hat sich bremium geholt!")
        else:
            await ctx.send(f"{target.mention} hol dir auch bremium! c:")

    @commands.command(name='status')
    async def status_command(self, ctx):
        '''Manueller Befehl um den Stream-Status zu prüfen'''
        stream_data = checkStreamStatus(TwitchUsername)
        
        if stream_data is None:
            await ctx.send('Fehler beim Abrufen des Stream-Status')
            return
        
        if stream_data['isLive']:
            await ctx.send(f'✅ {TwitchUsername} ist aktuell LIVE!')
        else:
            await ctx.send(f'❌ {TwitchUsername} ist aktuell offline')






async def setup(bot):
    await bot.add_cog(SecretCommands(bot))
    print("SecretCommands geladen ✅")