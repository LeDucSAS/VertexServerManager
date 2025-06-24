import logging
from urllib.request import urlopen


logger = logging.getLogger("VertexServerDownloader")


class VertexServerDownloader():
    def __init__(self):
        ...


    def download_file_to_cache(self, url_to_download):
        logger.debug("download_file_to_cache()...")
        filename = url_to_download.split("/")[-1:][0]
        cache_file_path = f"cache/{filename}"
        # Download from URL
        with urlopen(url_to_download) as file:
            content = file.read()
        # Save to file
        with open(cache_file_path, 'wb') as download:
            download.write(content)
        logger.debug("download_file_to_cache() done")
        return cache_file_path