import aiohttp

TOP_GG_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJib3QiOiJ0cnVlIiwiaWQiOiIxMzA2MjQ0ODM4NTA0NjY1MTY5IiwiaWF0IjoiMTc1MzkxMjY3NCJ9.lRf9Yg1X3oXrJhSqdNVFgXvcbubQQ8JyDObeiiZSOA4"
BOT_ID = 1306244838504665169

async def checkVote(userID) -> bool:
    url = f"https://top.gg/api/bots/{BOT_ID}/check?userId={userID}"
    headers = {"Authorization": TOP_GG_TOKEN}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            return bool(data.get("voted"))