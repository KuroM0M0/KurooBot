import discord
from discord.ext import commands
from config import NSFWRoleID, ServerID, ChannelID

class roleRemoved(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ServerID = ServerID

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        user = before.guild.get_member(before.id)
        guild = before.guild
        beforeRoles = set(before.roles)
        afterRoles = set(after.roles)

        addedRoles = afterRoles - beforeRoles
        removedRoles = beforeRoles - afterRoles

        channel = after.guild.get_channel(ChannelID)  # oder eine andere Channel-ID verwenden
        
        if addedRoles == set([guild.get_role(NSFWRoleID)]):
            for role in addedRoles:
                await channel.send(embed=createEmbed(after, role, "added"))
        if removedRoles == set([guild.get_role(NSFWRoleID)]):
            for role in removedRoles:
               await channel.send(embed=createEmbed(after, role, "removed"))

        
        
def createEmbed(user, role, update):
    if update == "added":
        embed = discord.Embed(
            title="",
            description=f"{user.mention} hat die Rolle `{role.name}` erhalten.",
            color=discord.Color.green()
        )
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)
        return embed
    elif update == "removed":
        embed = discord.Embed(
            title="",
            description=f"{user.mention} hat die Rolle `{role.name}` verloren.",
            color=discord.Color.red()
        )
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)
        return embed


async def setup(bot):
    await bot.add_cog(roleRemoved(bot))
    #await bot.add_cog(Reaction(bot))
    print("Duftende Listener geladen ✅")
