import aiohttp
import asyncio
import async_timeout
from minghu6.http.request import headers

async def fetch(session, url):
    with async_timeout.timeout(20):
        async with session.get(url) as response:
            return await response.read()

async def main(loop):
    async with aiohttp.ClientSession(loop=loop, headers=headers) as session:
        html = await fetch(session, 'http://blog.csdn.net/minghu9/article')
        print(html)

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))