import discord
from discord.ext import tasks
from datetime import datetime, timedelta
from dataBase import *

def checkPremiumStatus(connection, userID):
    """
    Prüft, ob Premium in 5 Tagen abläuft, und gibt Reminder zurück (nur einmal)
    """
    if not getPremium(connection, userID):
        return None

    start_ts = datetime.fromisoformat(getPremiumTimestamp(connection, userID))
    months = int(getPremiumInMonths(connection, userID) or 0)

    expire_date = start_ts + timedelta(days=30 * months)
    remind_date = expire_date - timedelta(days=5)
    now = datetime.now()

    # Nur Datum vergleichen, damit es ganztägig gilt
    if now.date() == remind_date.date():
        unix = int(expire_date.timestamp())
        return f"Dein Premium läuft bald ab! Es endet am <t:{unix}:F> (<t:{unix}:R>)."

    # Premium abgelaufen?
    if now >= expire_date:
        resetPremium(connection, userID)
        return None

    return None


def startPremiumChecker(bot, connection):
    """
    Startet den Premium-Checker Task, der alle 12 Stunden läuft.
    """

    @tasks.loop(hours=12)
    async def premiumChecker():
        allUsers = getAllPremiumUser(connection)
        for userID in allUsers:
            reminder = checkPremiumStatus(connection, userID[0])
            if reminder:
                user = await bot.fetch_user(userID[0])
                try:
                    await user.send(reminder)
                except discord.Forbidden:
                    print(f"Kann {userID} keine DM schicken (vermutlich blockiert).")

    premiumChecker.start()