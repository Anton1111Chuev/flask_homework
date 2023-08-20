from sys import argv
from multipross_down import multiproc_download
from thread_down import thread_download
from async_down import async_download

if len(argv) > 1:
    urls = argv[1:]
else:
    urls = [
        'https://iphoneroot.com/wp-content/uploads/2011/07/Mac-OS-X-Lion-Galaxy-500x312.jpg',
        'https://iphoneroot.com/wp-content/uploads/2018/02/iphone-notch-smaller.jpg',
        'https://iphoneroot.com/wp-content/uploads/2018/01/ipad-apps-on-mac.jpg'
    ]
if __name__ == '__main__':
    multiproc_download(urls)
    thread_download(urls)
    async_download(urls)
