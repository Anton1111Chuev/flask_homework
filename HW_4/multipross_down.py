import urllib

import requests
from multiprocessing import Process, Pool
import time


def download_file(url, start_time):
    filename = 'multiprocessing_' + url.replace('https://', '').replace('.', '_').replace('/', '') + '.jpg'
    urllib.request.urlretrieve(url, filename)
    print(f"Downloaded  multiproces {url} in {time.time() - start_time:.2f} seconds")


def multiproc_download(urls):
    start_time = time.time()
    processes = []
    for url in urls:
        process = Process(target=download_file, args=(url, start_time,))
        processes.append(process)
        process.start()
    for process in processes:
        process.join()

    print(f"Downloaded  multiproces finished in {time.time() - start_time:.2f} seconds")
