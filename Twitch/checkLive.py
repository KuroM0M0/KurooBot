import discord
from discord.ext import tasks
from config import CheckInterval, TwitchUsername, TwitchMessageChannel, TwitchPingID
from Twitch.Twitch import checkStreamStatus

Bot = None
isLive = False  # Speichert den aktuellen Live-Status

def startCheckStream(bot):
    @tasks.loop(minutes=CheckInterval)
    async def checkStream():
        '''Prüft regelmäßig, ob der Stream live geht'''
        global isLive
        
        # Hole den aktuellen Stream-Status
        stream_data = checkStreamStatus(TwitchUsername)
        
        if stream_data is None:
            print('[StreamChecker] Konnte Stream-Status nicht abrufen')
            return
        
        # Wenn der Stream live ist und vorher offline war
        if stream_data['isLive'] and not isLive:
            isLive = True
            
            # Hole den Discord Channel
            channel = bot.get_channel(TwitchMessageChannel)
            if not channel:
                print(f"[StreamChecker] Channel {TwitchMessageChannel} nicht gefunden.")
                return
            
            # Erstelle eine Embed-Nachricht
            embed = discord.Embed(
                title=f"🔴 {stream_data['title']}",
                description=f"{TwitchUsername} ist jetzt **live!**",
                color=discord.Color.purple(),
                url=f"https://twitch.tv/{TwitchUsername}"
            )
            embed.add_field(name='🎮 Spiel', value=stream_data['game_name'], inline=True)
            embed.add_field(name='👥 Zuschauer', value=str(stream_data['viewer_count']), inline=True)
                
            if stream_data["thumbnail_url"]:
                embed.set_image(url=stream_data["thumbnail_url"])
            
            embed.set_footer(text='Twitch Benachrichtigung')
            
            # Sende die Nachricht
            roleMention = f'<@&{TwitchPingID}>'
            await channel.send(f'{roleMention} Ich bin jetzt live! Schau gern vorbei c:', embed=embed)
            print(f'[StreamChecker] Benachrichtigung gesendet: {TwitchUsername} ist live!')
        
        # Wenn der Stream offline ist
        elif not stream_data["isLive"] and isLive:
            isLive = False
            print(f"[StreamChecker] {TwitchUsername} ist jetzt offline.")
    checkStream.start()