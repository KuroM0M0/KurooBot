import sqlite3

def createRoleConnection():
    try:
        connection = sqlite3.connect("roleTimer.db")
        print("Datenbankverbindung erfolgreich hergestellt.")
        return connection
    except sqlite3.Error as e:
        print(f"Fehler beim Herstellen der Datenbankverbindung: {e}")
        return None
    

def getAllRoleTimer(connection):
    if connection is None:
        print("Keine Datenbankverbindung verfügbar.")
        return

    cursor = connection.cursor()
    try:
    
        cursor.execute('SELECT DiscordID, TimeSinceLastMessage FROM Timer')
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print(f"[roleDB] Fehler beim Abrufen des Rollentimers: {e}")


def insertUser(connection, userID, timestamp):
    if connection is None:
        print("Keine Datenbankverbindung verfügbar.")
        return

    cursor = connection.cursor()
    try:
        cursor.execute('''  INSERT INTO Timer (DiscordID, TimeSinceLastMessage)
                            VALUES (?, ?)
                            ON CONFLICT(DiscordID) DO UPDATE SET TimeSinceLastMessage = excluded.TimeSinceLastMessage''', 
                            (userID, timestamp))
        connection.commit()
    except sqlite3.Error as e:
        print(f"[roleDB] Fehler beim Einfügen/Aktualisieren des Benutzers: {e}")