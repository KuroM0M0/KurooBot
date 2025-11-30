import requests
from config import TwitchID, TwitchSecret

twitchOauthToken = None

def getTwitchOauthToken():
    """Holt einen OAuth Token von Twitch mit Client Credentials Flow"""
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': TwitchID,
        'client_secret': TwitchSecret,
        'grant_type': 'client_credentials'
    }

    try:
        # Twitch erwartet x-www-form-urlencoded → data statt params
        response = requests.post(url, data=params)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token")
    except Exception as e:
        print(f"[Twitch] Fehler beim Token holen: {e}")
        return None


def _format_thumbnail(url: str, width: int = 1920, height: int = 1080) -> str:
    """Ersetzt die Twitch-Template-Parameter in der Thumbnail-URL."""
    if not url:
        return None
    return (
        url
        .replace("{width}", str(width))
        .replace("{height}", str(height))
    )


def checkStreamStatus(username: str):
    """Prüft, ob der Twitch-Stream live ist und gibt strukturierte Daten zurück."""
    global twitchOauthToken

    # Token holen, falls nicht vorhanden
    if not twitchOauthToken:
        twitchOauthToken = getTwitchOauthToken()
        if not twitchOauthToken:
            return None

    url = f'https://api.twitch.tv/helix/streams?user_login={username}'
    headers = {
        'Client-ID': TwitchID,
        'Authorization': f'Bearer {twitchOauthToken}'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Stream ist live?
        if data.get('data'):
            stream_info = data['data'][0]

            title = stream_info.get("title") or "Kein Titel"
            game_name = stream_info.get("game_name") or "Unbekannt"
            viewer_count = stream_info.get("viewer_count") or 0
            thumbnail = stream_info.get("thumbnail_url")

            # **Thumbnail jetzt hier zentral ersetzen**
            thumbnail = _format_thumbnail(thumbnail, width=1280, height=720)

            return {
                "isLive": True,
                "title": title,
                "game_name": game_name,
                "viewer_count": viewer_count,
                "thumbnail_url": thumbnail
            }
        else:
            return {"isLive": False}

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            # Token abgelaufen → neu holen → einmal erneut versuchen
            print("[Twitch] OAuth Token abgelaufen. Hole neuen Token…")
            twitchOauthToken = getTwitchOauthToken()
            if twitchOauthToken:
                return checkStreamStatus(username)
            return None

        print(f"[Twitch] HTTP Fehler: {e}")
        return None

    except Exception as e:
        print(f"[Twitch] Unerwarteter Fehler: {e}")
        return None