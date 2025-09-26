import discord
import asyncio
import requests
from datetime import datetime, timedelta
import re
import os
from dotenv import load_dotenv
from dataBase import *

load_dotenv()
PaypalAPI = os.getenv("PaypalAPI")
PaypalClientID = os.getenv("PaypalClientID")
PaypalSecret = os.getenv("PaypalSecret")

# ---- DEBUG: Umgebungsvariablen prüfen ----
print(f"[DEBUG] Geladene PayPal-Konfiguration:")
print(f"  API-URL: {PaypalAPI}")
print(f"  Client-ID: {'*' * (len(PaypalClientID)-4) + PaypalClientID[-4:] if PaypalClientID else 'FEHLT!'}")
print(f"  Secret: {'Vorhanden' if PaypalSecret else 'FEHLT!'}")
print(f"  Aktuelle Zeit (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")

# ---- PAYPAL TOKEN ----
def getPaypalToken():
    print("[DEBUG] Starte Token-Abfrage...")
    try:
        resp = requests.post(
            f"{PaypalAPI}/v1/oauth2/token",
            auth=(PaypalClientID, PaypalSecret),
            data={"grant_type": "client_credentials"},
        )
        resp.raise_for_status()
        token = resp.json()["access_token"]
        print(f"[DEBUG] Token erfolgreich erhalten (erste 8 Zeichen: {token[:8]}...)")
        return token
    except Exception as e:
        print(f"[ERROR] Token-Fehler: {str(e)[:200]}")  # Kürze lange Fehlermeldungen
        raise

# ---- TRANSAKTIONEN ABRUFEN ----
def getRecentTransactions(token):
    headers = {"Authorization": f"Bearer {token}"}
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"{PaypalAPI}/v1/reporting/transactions?start_date={yesterday}&end_date={now}"

    print(f"[DEBUG] Abfrage Transaktionen von {yesterday} bis {now}")
    print(f"[DEBUG] API-URL: {url}")

    try:
        resp = requests.get(url, headers=headers)
        print(f"[DEBUG] API-Statuscode: {resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
        transactions = data.get("transaction_details", [])

        print(f"[DEBUG] Gefundene Transaktionen: {len(transactions)}")
        if len(transactions) > 0:
            print(f"[DEBUG] Erste Transaktions-ID: {transactions[0]['transaction_info']['transaction_id']}")

        return transactions
    except Exception as e:
        print(f"[ERROR] Transaktionsabfrage fehlgeschlagen: {str(e)[:300]}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"[ERROR] API-Antwort: {e.response.text[:500]}")  # Zeige Teil der Antwort
        raise

# ---- LOOP: ZAHLUNGEN PRÜFEN ----
async def checkPaymentsLoop(bot, connection):
    print("[DEBUG] Payment-Loop gestartet. Warte auf Bot-Ready...")
    await bot.wait_until_ready()
    print(f"[DEBUG] Bot ist bereit: {bot.user} (ID: {bot.user.id})")

    while not bot.is_closed():
        try:
            print("\n" + "="*50)
            print(f"[DEBUG] Neue Loop-Iteration - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

            # Token abrufen
            token = getPaypalToken()

            # Transaktionen abrufen
            transactions = getRecentTransactions(token)

            if not transactions:
                print("[DEBUG] Keine Transaktionen im Zeitfenster gefunden.")
            else:
                print(f"[DEBUG] Verarbeite {len(transactions)} Transaktion(en)...")

                for tx in transactions:
                    try:
                        info = tx["transaction_info"]
                        amount = info["transaction_amount"]["value"]
                        currency = info["transaction_amount"]["currency_code"]

                        # Debug: Zeige relevante Transaktionsdaten
                        tx_id = info.get("transaction_id", "unbekannt")
                        print(f"\n[DEBUG] Transaktion {tx_id}:")
                        print(f"  Betrag: {amount} {currency}")
                        print(f"  Typ: {tx.get('transaction_info', {}).get('transaction_type', 'unbekannt')}")

                        # Textfelder checken
                        note_fields = [
                            info.get("transaction_subject", ""),
                            info.get("invoice_id", ""),
                            info.get("custom_field", ""),
                            info.get("transaction_note", "")
                        ]
                        note = next((field for field in note_fields if field), "")
                        print(f"  Notiz/Referenz: '{note[:100]}'...")  # Zeige ersten Teil der Notiz

                        # Discord-ID suchen
                        match = re.search(r"(?:discord[: ]+)(\d{17,19})", note, re.IGNORECASE)
                        if match:
                            discord_id = match.group(1)
                            print(f"  [MATCH] Discord-ID gefunden: {discord_id}")

                            if amount == "1.00" and currency == "EUR":
                                print(f"  [CHECK] Betrag und Währung passen (1.00 EUR)")

                                # DB-Prüfung
                                tx_id = info.get("transaction_id")
                                exists = checkPaypalTransactionExists(connection, tx_id) if tx_id else False
                                print(f"  [DB] Transaktion {tx_id} existiert bereits in DB: {exists}")

                                if not exists:
                                    print(f"  [ACTION] Setze Premium für Nutzer {discord_id}...")
                                    setPremium(connection, discord_id)
                                    insertPaypalTransaction(connection, discord_id, tx_id)
                                    print(f"  [SUCCESS] Premium aktiviert und Transaktion gespeichert!")
                                else:
                                    print(f"  [SKIP] Transaktion bereits verarbeitet.")
                            else:
                                print(f"  [SKIP] Betrag ({amount} {currency}) passt nicht zu 1.00 EUR.")
                        else:
                            print("  [NO MATCH] Keine Discord-ID in den Notizfeldern gefunden.")

                    except Exception as e:
                        print(f"[ERROR] Fehler bei Transaktion {tx.get('transaction_id', 'unbekannt')}: {str(e)[:200]}")

        except Exception as e:
            print(f"[ERROR] Hauptloop-Fehler: {str(e)[:300]}")

        # Wartezeit mit Debug-Info
        next_run = datetime.utcnow() + timedelta(seconds=300)
        print(f"[DEBUG] Nächste Prüfung um {next_run.strftime('%H:%M:%S')} UTC (in ~5 Minuten)...")
        await asyncio.sleep(300)
