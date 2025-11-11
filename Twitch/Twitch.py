import requests
from config import TwitchID, TwitchSecret

#ersetzen falls für andere auch verfügbar sein soll
twitchOauthToken = None

def getTwitchOauthToken():
    '''Holt einen OAuth Token von Twitch mit Client Credentials Flow'''
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': TwitchID,
        'client_secret': TwitchSecret,
        'grant_type': 'client_credentials'
    }

    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data['access_token']
    except Exception as e:
        print(f'Fehler beim Abrufen des OAuth Tokens: {e}')
        return None


def checkStreamStatus(username):
    '''Prüft ob ein Twitch-Stream live ist'''
    global twitchOauthToken
    
    # Token holen, falls noch nicht vorhanden
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
        
        # Wenn das data Array nicht leer ist, ist der Stream live
        if data['data']:
            stream_info = data['data'][0]
            return {
                'isLive': True,
                'title': stream_info['title'],
                'game_name': stream_info['game_name'],
                'viewer_count': stream_info['viewer_count'],
                'thumbnail_url': stream_info['thumbnail_url']
            }
        else:
            return {'isLive': False}
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            # Token ist abgelaufen, neuen holen
            print('OAuth Token abgelaufen, hole neuen Token...')
            twitchOauthToken = getTwitchOauthToken()
            return checkStreamStatus(username)  # Nochmal versuchen
        else:
            print(f'Fehler beim Abrufen des Stream-Status: {e}')
            return None
    except Exception as e:
        print(f'Unerwarteter Fehler: {e}')
        return None