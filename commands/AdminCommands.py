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


    @commands.command(name="ban")
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member: discord.Member, reason):
        serverID = str(ctx.guild.id)
        userID = str(member.id)
        insertBan(connection, userID, serverID, ctx.author.id, reason)
        await ctx.send(f"{member} ist nun vom Bot ausgeschlossen!")


    @commands.command(name="unban")
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, member: discord.Member):
        serverID = str(ctx.guild.id)
        userID = str(member.id)
        updateBan(connection, serverID, userID)
        await ctx.send(f"{member} kann den Bot nun wieder nutzen!")




async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
    print("AdminCommands geladen ✅")