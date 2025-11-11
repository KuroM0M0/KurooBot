import discord
from discord.ext import tasks
from config import CheckInterval, TwitchUsername, TwitchMessageChannel, TwitchPingID
from Twitch.Twitch import checkStreamStatus

Bot = None
isLive = False  # Speichert den aktuellen Live-Status

@tasks.loop(minutes=CheckInterval)
async def checkStream(bot):
    '''Prüft regelmäßig, ob der Stream live geht'''
    global isLive
    print("Stream-Status prüfen...")
    
    # Hole den aktuellen Stream-Status
    stream_data = checkStreamStatus(TwitchUsername)
    
    if stream_data is None:
        print('Konnte Stream-Status nicht abrufen')
        return
    
    # Wenn der Stream live ist und vorher offline war
    if stream_data['isLive'] and not isLive:
        isLive = True
        
        # Hole den Discord Channel
        channel = bot.get_channel(TwitchMessageChannel)
        if channel:
            # Erstelle eine Embed-Nachricht
            embed = discord.Embed(
                title=f'🔴 {TwitchUsername} ist jetzt LIVE!',
                description=stream_data['title'],
                color=discord.Color.purple(),
                url=f'https://twitch.tv/{TwitchUsername}'
            )
            embed.add_field(name='Spiel', value=stream_data['game_name'], inline=True)
            embed.add_field(name='Zuschauer', value=stream_data['viewer_count'], inline=True)
            
            # Thumbnail hinzufügen (ersetze Platzhalter in der URL)
            thumbnail = stream_data['thumbnail_url'].replace('{width}', '440').replace('{height}', '248')
            embed.set_image(url=thumbnail)
            
            embed.set_footer(text='Twitch Benachrichtigung')
            
            # Sende die Nachricht
            roleMention = f'<@&{TwitchPingID}>'
            await channel.send(f'{roleMention} {TwitchUsername} ist live!', embed=embed)
            print(f'Benachrichtigung gesendet: {TwitchUsername} ist live!')
        else:
            print(f'Channel mit ID {TwitchMessageChannel} nicht gefunden')
    
    # Wenn der Stream offline ist
    elif not stream_data['isLive'] and isLive:
        isLive = False
        print(f'{TwitchUsername} ist jetzt offline')
