from dataBase import *;


def UserExists(connection, userID): 
    """
    Checks if a user exists in the database and inserts a new user if not.
    
    Parameters
    ----------
    connection : sqlite3.Connection
        The database connection to use.
    userID : str
        The ID of the user to check.
    """
    exists = checkUserExists(connection, userID)
    if exists is None:
        insertUser(connection, userID)
        

def ResetPremium(connection, userID):
    """
    Checks if a user's premium has expired and resets it if so.
    
    Parameters
    ----------
    connection : sqlite3.Connection
        The database connection to use.
    userID : str
        The ID of the user to check.
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

    Parameters
    ----------
    connection : sqlite3.Connection
        The database connection to use.
    userID : str
        The ID of the user to check and update.
    """
    streak = getStreak(connection, userID)
    if getSparkUses(connection, userID) < 2:
        if streak % 3 == 0:
            updateStreakPoints(connection, userID)

def ResetStreak(connection, userID):
    today = datetime.now().date()
    lastSparkStr = getCooldown(connection, userID)

    if lastSparkStr == "0":
        return

    lastSpark = datetime.fromisoformat(lastSparkStr).date()
    delta = (today - lastSpark).days
    if delta > 1:
        resetStreak(connection, userID)
