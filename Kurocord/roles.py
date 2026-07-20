# cogs/timed_roles.py
import discord
from discord.ext import commands, tasks
from config import roleConnection, MainServerID
from Kurocord.roleDB import getAllRoleTimer, insertUser
from datetime import datetime, timedelta, timezone

inactivityLimit = timedelta(days=90)  # anpassen nach Bedarf
removeRoleId = 1320822518185197683      # Rolle, die bei Inaktivität entfernt wird
removeRoleMensch = 542073219516071936
removeRoleHalbAlien = 750710293826371614
removeRoleAlien = 774358624851984394
addRoleId = 713128357151375390          # Rolle, die bei Inaktivität hinzugefügt wird


class TimedRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.checkLoop.start()

    def cog_unload(self):
        self.checkLoop.cancel()

    # --- Wird bei jeder Nachricht aufgerufen, um Timer zu resetten ---
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild is None or message.guild.id != MainServerID:
            return
        now = datetime.now(timezone.utc).isoformat()
        insertUser(roleConnection, str(message.author.id), now)

    # --- Loop, der Inaktivität prüft ---
    @tasks.loop(minutes=5)
    async def checkLoop(self):
        now = datetime.now(timezone.utc)
        rows = getAllRoleTimer(roleConnection)

        for discordId, lastMsgStr in rows:
            lastMsg = datetime.fromisoformat(lastMsgStr)
            if now - lastMsg >= inactivityLimit:
                await self.removeRole(int(discordId), removeRoleMensch)
                await self.removeRole(int(discordId), removeRoleHalbAlien)
                await self.removeRole(int(discordId), removeRoleAlien)
                await self.addRole(int(discordId))

    async def removeRole(self, userId: int, roleID: int):
        guild = self.bot.get_guild(MainServerID)
        if guild is None:
            return
        member = guild.get_member(userId)
        role = guild.get_role(roleID)
        if member and role and role in member.roles:
            try:
                await member.remove_roles(role, reason="Inaktivität")
            except discord.Forbidden:
                print(f"[RoleSystem] Fehler beim Entfernen der Rolle für {member.name}")

    async def addRole(self, userId: int):
        guild = self.bot.get_guild(MainServerID)
        if guild is None:
            return
        member = guild.get_member(userId)
        role = guild.get_role(addRoleId)
        if member and role and role not in member.roles:
            try:
                await member.add_roles(role, reason="Inaktivität")
            except discord.Forbidden:
                print(f"[RoleSystem] Fehler beim Hinzufügen der Rolle für {member.name}")

    @checkLoop.before_loop
    async def beforeCheckLoop(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(TimedRoles(bot))
    print("TimedRoles geladen ✅")