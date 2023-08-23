import asyncio
import aiohttp
import time


async def download(url, start_time):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            filename = 'asyncio_' + url.replace('https://', '').replace('.', '_').replace('/', '') + '.jpg'
            with open(filename, "wb") as f:
                while True:
                    chunk = await response.content.readany()
                    if not chunk:
                        break
                    f.write(chunk)
            print(f"Downloaded  async {url} in {time.time() - start_time:.2f} seconds")


async def main(urls, start_time):
    tasks = []
    for url in urls:
        task = asyncio.ensure_future(download(url, start_time))
        tasks.append(task)
        await asyncio.gather(*tasks)
    print(f"Downloaded  async finished in {time.time() - start_time:.2f} seconds")


def async_download(urls):
    start_time = time.time()
    asyncio.run(main(urls, start_time))
