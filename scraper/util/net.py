import urllib3
import urllib.request

def download_file(url: str, out_folder: str) -> bool:
    opener = urllib.request.build_opener()
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46')
    ]
    urllib.request.install_opener(opener)

    try:
        urllib.request.urlretrieve(url, out_folder + url.split('/')[-1])
        return True

    except Exception as e:
        print("An error occured, please try again later")
        print(e)
        return False
