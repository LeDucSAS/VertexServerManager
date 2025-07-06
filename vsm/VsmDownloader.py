import logging
import requests
from urllib.request import urlopen


logger = logging.getLogger("VsmDownloader")


class VsmDownloader():
    
    def __init__(self):
        ...


    def download_file_to_cache_basic(self, url_to_download:str) -> str:
        logger.debug("download_file_to_cache_basic()...")
        filename = url_to_download.split("/")[-1:][0]
        cache_file_path = f"cache/{filename}"
        # Download from URL
        with urlopen(url_to_download) as file:
            content = file.read()
        # Save to file
        with open(cache_file_path, 'wb') as download:
            download.write(content)
        logger.debug("download_file_to_cache_basic() done")
        return cache_file_path


    def download_to_cache(self, url_to_download:str, download_step:int = 10) -> str:
        logger.debug("download_to_cache() ...")
        # Getting the file data
        response = requests.get(url_to_download, stream=True, allow_redirects=True)

        archive_name = response.url.split("?")[0].split("/")[-1]
        downloaded_file_path = f"cache/{archive_name}"

        with open(downloaded_file_path, 'wb') as fd:
            logger.info(f'Downloading {downloaded_file_path}')
            total_length = response.headers.get('content-length')
            if total_length is None: # no content length header
                fd.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                nextdone = download_step
                logger.info("Download 0%")
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    fd.write(data)
                    done = int(100 * dl / total_length)
                    if(done == nextdone):
                        logger.info(f"Download {done}%")
                        nextdone = nextdone + download_step
            logger.info(f'Downloaded {downloaded_file_path}')
        logger.debug("download_to_cache() => done")
        return archive_name