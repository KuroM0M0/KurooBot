import discord
from discord.ext import tasks
from datetime import datetime, timedelta
from dataBase import *

# JSON-Datei einlesen
with open('user/Premium.json', 'r') as file:
    data = json.load(file)


def checkPremiumStatus(connection, userID: int):
    """
    Prüft, ob Premium in 5 Tagen abläuft, Reminder zurückgibt oder Premium zurücksetzt.
    """
    if not getPremium(connection, userID):
        return None

    start_ts = datetime.fromisoformat(getPremiumTimestamp(connection, userID))
    months = int(getPremiumInMonths(connection, userID) or 0)

    expire_date = start_ts + timedelta(days=30 * months)
    remind_date = expire_date - timedelta(days=5)
    now = datetime.now()

    # Reminder (nur Datum, ganztägig gültig)
    if now.date() == remind_date.date():
        unix = int(expire_date.timestamp())
        return (
            f"Dein Premium läuft bald ab! Es endet am <t:{unix}:F> (<t:{unix}:R>). "
            "\n-# Kleiner Tipp: Wenn du diese Nachricht ausblenden willst, nutze /settings"
        )

    # Premium abgelaufen
    if now >= expire_date:
        resetPremium(connection, userID)

        # Reminder-Eintrag entfernen
        uid = str(userID)
        data.pop(uid, None)

        # Datei aktualisieren
        with open('user/Premium.json', 'w') as file:
            json.dump(data, file, indent=2)

        return None

    return None



def startPremiumChecker(bot, connection):
    """
    Startet den Premium-Checker Task, der alle 20 Stunden läuft.
    """
    @tasks.loop(hours=20)
    async def premiumChecker():
        allUsers = getAllPremiumUser(connection)

        for userIDTuple in allUsers:
            userID_int = userIDTuple[0]      # DB → int
            userID = str(userID_int)         # JSON → str

            # Nutzer möchte keine DMs
            if getPremiumDMSetting(connection, userID_int) == 0:
                continue

            # Reminder bereits gesendet?
            if data.get(userID, {}).get("sent") is True:
                continue

            # Premiumstatus prüfen
            reminder = checkPremiumStatus(connection, userID_int)

            if reminder:
                # Reminder als gesendet markieren
                data[userID] = {"sent": True}

                # JSON speichern
                with open('user/Premium.json', 'w') as file:
                    json.dump(data, file, indent=2)

                # DM senden
                user = await bot.fetch_user(userID_int)
                try:
                    await user.send(reminder)
                except discord.Forbidden:
                    print(f"Kann {userID_int} keine DM schicken (vermutlich blockiert).")

    # premiumChecker.start()