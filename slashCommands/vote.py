import discord
from discord.ext import commands
from discord import app_commands
from config import connection
from datetime import datetime, timedelta
from Methoden import *
from dataBase import *
from user.vote import *
from config import VoteCooldown

class Vote(commands.Cog):
    @app_commands.command(name="vote", description="Wenn du den Bot kostenlos unterstützen möchtest :)")
    async def vote(self, interaction: discord.Interaction):
        userID = str(interaction.user.id)
        now = datetime.now()
        Vote = await checkVote(userID)
        LastVote = getVoteTimestamp(connection, userID)
        votePoints = getVotePoints(connection, userID)

        if LastVote:
            lastVoteDt = datetime.fromisoformat(LastVote)
        else:
            lastVoteDt = datetime.min

        if Vote:
            if now - lastVoteDt >= timedelta(hours=VoteCooldown):
                setVotePoints(connection, userID)
                setVoteTimestamp(connection, userID, now.isoformat())
                votePoints = getVotePoints(connection, userID)
                await interaction.response.send_message(
                    f"✅ Dein Vote wurde erkannt und deine Belohnung gutgeschrieben!\n"
                    f"Du hast jetzt **{votePoints} VotePunkte**. ❤️",
                    ephemeral=True)
            else:
                await interaction.response.send_message(
                    f"⚠️ Dein letzter Vote ist noch nicht lange genug her.\n"
                    f"⏳ Du kannst alle **{VoteCooldown} Stunden** Punkte abholen.\n"
                    f"Aktuell hast du **{votePoints} VotePunkte**.",
                    ephemeral=True)
        else:
            await interaction.response.send_message(
                f"ℹ️ Du hast noch keinen Vote abgeholt.\n"
                f"👉 Bitte stimme zuerst hier ab: https://top.gg/bot/1306244838504665169/vote\n\n"
                f"⚡ Danach kannst du **diesen Befehl erneut ausführen**, "
                f"um deine Punkte zu erhalten.\n"
                f"Aktuell hast du **{votePoints} VotePunkte**.",
                ephemeral=True)
            

async def setup(bot: commands.Bot):
    await bot.add_cog(Vote(bot))
    print("Vote geladen ✅")