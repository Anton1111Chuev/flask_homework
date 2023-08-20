import urllib
import threading
import time


def download(url, start_time):
    filename = 'threading_' + url.replace('https://', '').replace('.', '_').replace('/', '') + '.jpg'
    urllib.request.urlretrieve(url, filename)
    print(f"Downloaded  thread {url} in {time.time() - start_time:.2f} seconds")


def thread_download(urls):
    threads = []
    start_time = time.time()
    for url in urls:
        thread = threading.Thread(target=download, args=[url, start_time])
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    print(f"Downloaded  thread finished in {time.time() - start_time:.2f} seconds")
