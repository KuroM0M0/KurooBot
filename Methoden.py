from dataBase import *;
from typing import Optional
import re
import discord


def UserExists(connection, userID): 
    """
    Prüft ob User in der Datenbank existiert, wenn nicht wird er hinzugefügen
    """
    exists = checkUserExists(connection, userID)
    if exists is None:
        insertUser(connection, userID)
        

def ResetPremium(connection, userID):
    """
    Prüft ob Premium abgelaufen ist, wenn ja wird es resettet
    """
    Premium = getPremium(connection, userID)
    if Premium:
        PremiumTimestamp = datetime.fromisoformat(getPremiumTimestamp(connection, userID))
        MonatBack = datetime.now() - timedelta(days=30)
        if PremiumTimestamp < MonatBack:
            resetPremium(connection, userID)


def StreakPunkt(connection, userID):
    """
    Updates the streak points for a user if certain conditions are met.

    This function checks the user's streak and spark uses. If the user has
    less than 2 spark uses and their streak is divisible by 3, it updates
    their streak points.
    """
    streak = getStreak(connection, userID)
    if getSparkUses(connection, userID) < 2:
        if streak % 3 == 0:
            updateStreakPoints(connection, userID)



def ResetStreak(connection, userID):
    """
    Resets the streak for a user if the difference between the current date
    and the user's last spark date is greater than 1 day.

    This function is used to reset a user's streak when they miss a day of
    sparking. If the user has not sparked in more than a day, their streak is
    reset to 0.
    """
    today = datetime.now().date()
    lastSparkStr = getCooldown(connection, userID)

    if lastSparkStr == "0":
        return

    lastSpark = datetime.fromisoformat(lastSparkStr).date()
    delta = (today - lastSpark).days
    if delta > 1:
        resetStreak(connection, userID)



async def CheckTarget(targetID, userID, interaction):
    """
    Prüft ob User sich selbst auswählt
    """
    if targetID == userID:
        await interaction.followup.send("Eigenlob stinkt :^)")
        raise Exception("Eigenlob")
    



def CheckServerExists(connection, serverID):
    """
    Prüft ob Server in der Datenbank existiert, wenn nicht wird er hinzugefügen
    """
    exists = checkServerExists(connection, serverID)
    if exists == False:
        insertServer(connection, serverID)



def CheckUserIsInSettings(connection, userID):
    """
    Prüft ob User in der Datenbank existiert, wenn nicht wird er hinzugefügen
    """
    exists = checkUserSetting(connection, userID)
    if exists == False:
        insertUserSetting(connection, userID)




# :name: – aber NICHT, wenn davor "<" steht und NICHT, wenn direkt danach ":<digits>>" kommt
_COLON_NAME = re.compile(r"(?<!<):([A-Za-z0-9_]+):(?!\d+>)")

def replaceEmotes(text: str, guild: discord.Guild, bot: discord.Client) -> str:
    def pick_emoji(name: str) -> Optional[str]:
    # 1) zuerst im aktuellen Server
        for e in getattr(guild, "emojis", []):
            if e.name == name:
                return str(e)

        # 2) dann global suchen (inkl. current guild, falls oben nichts war)
        for g in bot.guilds:
            for e in g.emojis:
                if e.name == name:
                    return str(e)

        return None

    def repl(m: re.Match) -> str:
        name = m.group(1)
        chosen = pick_emoji(name)
        return chosen if chosen is not None else m.group(0)

    return _COLON_NAME.sub(repl, text)