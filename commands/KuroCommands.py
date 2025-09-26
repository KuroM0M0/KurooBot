import asyncio
import discord
from discord.ext import commands
from datetime import datetime
from dataBase import *
from Methoden import *

connection = createConnection()
KuroID = 308660164137844736


class KuroCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="PremiumAktivieren")
    async def PremiumAktivieren(self, ctx, member: discord.Member):
        targetID = member.id
        userID = ctx.author.id
        if userID == KuroID:
            UserExists(connection, targetID)
            await ctx.send(f"{member} hat nun Premium!")
            setPremium(connection, targetID)
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
            UserExists(connection, targetID)
            await ctx.send(f"{member} hat nun {uses} Reveals!")
            setRevealUses(connection, targetID, uses)
        else:
            await ctx.send("Du bist nicht berechtigt dies zu tun!")

    @commands.command(name="addReveals")
    async def addReveals(self, ctx, member: discord.Member, addUses: int):
        targetID = member.id
        userID = ctx.author.id
        if userID == KuroID:
            UserExists(connection, targetID)
            uses = getRevealUses(connection, targetID) + addUses
            await ctx.send(f"{member} hat nun {uses} Reveals!")
            setRevealUses(connection, targetID, uses)
        else:
            await ctx.send("Du bist nicht berechtigt dies zu tun!")

    @commands.command(name="insertItem")
    async def insertItem(self, ctx, Name, Beschreibung, Preis, PreisTyp, ItemURL):
        userID = ctx.author.id
        if userID == KuroID:
            insertItem(connection, Name, Beschreibung, Preis, PreisTyp, ItemURL)
            await ctx.send(f"{Name} wurde hinzugefügt!")
        else:
            await ctx.send("Du bist nicht berechtigt dies zu tun!")


    @commands.command(name="setVotePunkte")
    async def setVotePunkte(self, ctx, member: discord.Member, Punkte: int):
        targetID = member.id
        userID = ctx.author.id
        if userID == KuroID:
            await ctx.send(f"{member} hat nun {Punkte} Vote Punkte!")
            setVotePunkte(connection, targetID, Punkte)
        else:
            await ctx.send("Du bist nicht berechtigt dies zu tun!")


    @commands.command(name="setStreakPunkte")
    async def setStreakPunkte(self, ctx, member: discord.Member, Punkte: int):
        targetID = member.id
        userID = ctx.author.id
        if userID == KuroID:
            await ctx.send(f"{member} hat nun {Punkte} Vote Punkte!")
            updateStreakPunkte(connection, targetID, Punkte)
        else:
            await ctx.send("Du bist nicht berechtigt dies zu tun!")


    @commands.command(name="leaveServer")
    @commands.is_owner()  # Nur der Bot-Owner darf
    async def leave_small_servers(self, ctx, min_members: int):
        # Liste der Server, die kleiner als min_members sind
        target_guilds = [guild for guild in self.bot.guilds if guild.member_count < min_members]

        if not target_guilds:
            await ctx.send(f"Keine Server mit weniger als {min_members} Mitgliedern gefunden.")
            return

        # Anzeige der Server
        server_list = "\n".join(f"{guild.name} ({guild.member_count})" for guild in target_guilds)
        await ctx.send(f"Ich würde folgende Server verlassen:\n{server_list}\nSchreib `ja` zum Bestätigen oder `nein` zum Abbrechen.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ("ja", "nein")

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30.0)  # 30 Sekunden warten
        except asyncio.TimeoutError:
            await ctx.send("Zeitüberschreitung – Vorgang abgebrochen.")
            return

        if msg.content.lower() == "nein":
            await ctx.send("Vorgang abgebrochen.")
            return

        # Server verlassen
        for guild in target_guilds:
            await guild.leave()

        await ctx.send(f"Erledigt! Ich habe {len(target_guilds)} Server verlassen.")


async def setup(bot):
    await bot.add_cog(KuroCommands(bot))
    print("KuroCommands geladen ✅")