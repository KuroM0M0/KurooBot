import discord
from discord.ext import commands
from datetime import datetime
from dataBase import *
from Methoden import *

connection = createConnection()

class AdminCommands(commands.Cog):
    @commands.command(name="setSparkChannel")
    @commands.has_permissions(administrator=True)
    async def setSparkChannel(self, ctx):
        channel = ctx.channel
        serverID = ctx.guild.id
        CheckServerExists(connection, serverID)
        await ctx.send(f"{channel} ist nun der Spark Channel!")
        setChannelSparkID(connection, serverID, channel.id)


    @commands.command(name="setNewsletterChannel")
    @commands.has_permissions(administrator=True)
    async def setNewsletterChannel(self, ctx):
        channel = ctx.channel
        serverID = ctx.guild.id
        CheckServerExists(connection, serverID)
        await ctx.send(f"{channel} ist nun der Newsletter Channel!")
        setChannelNewsletterID(connection, serverID, channel.id)





    @setSparkChannel.error
    async def setSparkChannel_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Du brauchst Administrator-Rechte, um diesen Befehl zu benutzen!", delete_after=10)

    @setNewsletterChannel.error
    async def setNewsletterChannel_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Du brauchst Administrator-Rechte, um diesen Befehl zu benutzen!", delete_after=10)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
    print("AdminCommands geladen ✅")