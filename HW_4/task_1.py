import os
import time
import threading
import multiprocessing
import asyncio
import argparse
import requests
import aiohttp

'''
https://onlinejpgtools.com/images/examples-onlinejpgtools/sunflower.jpg
https://jpeg.org/images/jpeg-home.jpg
https://ik.imagekit.io/ikmedia/backlit.jpg
'''

folder = 'images'


def download_image(url):
    response = requests.get(url)
    if not os.path.exists(folder):
        os.mkdir(folder)
    filename = os.path.join(folder, os.path.basename(url))
    with open(filename, 'wb') as f:
        f.write(response.content)


async def async_download_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if not os.path.exists(folder):
                os.mkdir(folder)
            filename = os.path.join(folder, os.path.basename(url))
            with open(filename, 'wb') as f:
                f.write(await response.read())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Saving image')
    parser.add_argument('urls', nargs='+', help='')
    args = parser.parse_args()

    start_time = time.time()
    for url in args.urls:
        download_image(url)
    print(f'Synchronous download in {time.time() - start_time:.2f} seconds')

    threads = []
    start_time = time.time()
    for url in args.urls:
        thread = threading.Thread(target=download_image, args=(url,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    print(f'Multithreading download in {time.time() - start_time:.2f} seconds')

    processes = []
    start_time = time.time()
    for url in args.urls:
        process = multiprocessing.Process(target=download_image, args=(url,))
        processes.append(process)
        process.start()
    for process in processes:
        process.join()
    print(f'Multiprocessing download in {time.time() - start_time:.2f} seconds')

    tasks = []
    start_time = time.time()
    if not os.path.exists(folder):
        os.mkdir(folder)
    for url in args.urls:
        task = asyncio.ensure_future(async_download_image(url))
        tasks.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    print(f'Async download in {time.time() - start_time:.2f} seconds')
