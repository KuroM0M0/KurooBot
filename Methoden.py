from dataBase import *;


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