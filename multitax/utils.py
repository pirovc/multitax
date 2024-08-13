import gzip
import io
import os
import tarfile
import urllib.request
import urllib.parse
import zlib
import warnings
import re
from collections import OrderedDict
from urllib.error import HTTPError
from bs4 import BeautifulSoup


def check_dir(prefix: str):
    abs_path = os.path.dirname(os.path.abspath(prefix))
    if not os.path.exists(abs_path):
        raise NotADirectoryError(abs_path)


def check_file(file: str):
    if not os.path.isfile(file):
        raise FileNotFoundError(file + " file do not exist")
    if os.path.getsize(file) == 0:
        raise FileNotFoundError(file + " file is empty")


def check_no_file(file: str):
    if os.path.isfile(file):
        raise FileExistsError(file)


def close_files(fhs: dict):
    """
    Parameters:
    * **fhs** *[dict]*: {file: file handler}

    Returns: Nothing
    """
    for fh in fhs.values():
        fh.close()


def download_files(urls: list, output_prefix: str = None, retry_attempts: int = 1):
    """
    Download and open files (memory/stream) or write to disk (multitax.utils.save_urls)

    Parameters:
    * **urls** *[list]*: List of files to download (text, ".gz", ".tar.gz", ".tgz")
    * **output_prefix** *[str]*: Output directory to save files

    Returns:
    * OrderedDict {file: file handler} (same order as input)
    """
    if isinstance(urls, str):
        urls = [urls]

    att = 0
    while att < retry_attempts:
        att += 1
        try:
            # If output is provided, save files and parse from disc
            if output_prefix:
                files = save_urls(urls, output_prefix)
                return open_files(files)
            else:
                # stream contents from url
                fhs = OrderedDict()
                for url in urls:
                    if url.endswith(".tar.gz") or url.endswith(".tgz"):
                        # tar files have mixed headers and content
                        # whole file should be loaded in memory first and not streamed
                        fhs[url] = tarfile.open(
                            fileobj=load_url_mem(url), mode='r:gz')
                    elif url.endswith(".gz"):
                        fhs[url] = gzip.open(
                            urllib.request.urlopen(url), mode="rb")
                        fhs[url].peek(1)  # peek into file to check if is valid
                    else:
                        fhs[url] = urllib.request.urlopen(url)

                return fhs
        except (HTTPError, zlib.error, tarfile.TarError):
            warnings.warn(
                "Download failed, trying again (" + str(att) + "/" + str(retry_attempts) + ")", UserWarning)

    raise Exception("One or more files could not be downloaded: " +
                    ", ".join(urls))


def filter_function(elements, function, value):
    return [elements[i] for i, v in enumerate(map(function, elements)) if v == value]


def join_check(elements, sep: str):
    if elements:
        return sep.join(map(str, elements))
    else:
        return ""


def load_url_mem(url: str):
    """import
    Parameters:
    * **url** *[str]*: URL to load into memory

    Returns:
    * io.BytesIO of the requested url
    """
    urlstream = urllib.request.urlopen(url)
    # From https://stackoverflow.com/questions/18623842/read-contents-tarfile-into-python-seeking-backwards-is-not-allowed
    tmpfile = io.BytesIO()
    while True:
        s = urlstream.read(io.DEFAULT_BUFFER_SIZE)
        if not s:
            break
        tmpfile.write(s)
    urlstream.close()
    tmpfile.seek(0)
    return tmpfile


def open_files(files: list):
    """
    Parameters:
    * **files** *[list]*: List of files to open (text, ".gz", ".tar.gz", ".tgz")

    Returns:
    * OrderedDict {file: file handler} (same order as input)
    """

    fhs = OrderedDict()
    for file in files:
        if file.endswith(".tar.gz") or file.endswith(".tgz"):
            fhs[file] = tarfile.open(file, mode='r:gz')
        elif file.endswith(".gz"):
            fhs[file] = gzip.open(file, "rt")
        else:
            fhs[file] = open(file, "r")
    return fhs


def reverse_dict(d: dict):
    rd = {}
    for k, v in d.items():
        if v not in rd:
            rd[v] = []
        rd[v].append(k)
    return rd


def save_urls(urls: list, output_prefix: str):
    """
    Parameters:
    * **urls** *[list]*: List of urls to download
    * **output_prefix** *[str]*: Output directory to save files

    Returns:
    * list of files saved
    """
    files = []
    for url in urls:
        outfile = output_prefix + os.path.basename(url)
        check_no_file(outfile)
        urlstream = urllib.request.urlopen(url)
        with open(outfile, 'b+w') as f:
            f.write(urlstream.read())
        urlstream.close()
        files.append(outfile)
    return files


def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)


def fuzzy_find_download_links(url: str, regex_pattern: str, page=None):
    """
    Parameters:
    * **url** *[str]*: URL to load into memory
    * **pattern** *[str]*: Link pattern to search for in the page
    * **page** *[str]*: Optional page content to parse, primarily for unit testing
    """
    if page is None:
        page = urllib.request.urlopen(url)
    o = urllib.parse.urlparse(url)
    soup = BeautifulSoup(page, 'html.parser')
    domain = url.split('/')
    return [f'{o.scheme}://{o.netloc}/{a.attrs['href']}' for a in soup.find_all('a', attrs={'href' : re.compile(regex_pattern)})]

warnings.formatwarning = warning_on_one_line


if __name__ == "__main__":
    links = fuzzy_find_download_links("https://www.arb-silva.de/no_cache/download/archive/current/Exports/taxonomy/", ".*tax_slv_ssu_.*.txt.gz$")
    print(links)