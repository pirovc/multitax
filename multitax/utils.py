import os
import gzip
import tarfile
import urllib.request
import io

from collections import OrderedDict


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


def download_files(urls: list, output_prefix: str = None):
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
                fhs[url] = tarfile.open(fileobj=load_url_mem(url), mode='r:gz')
            elif url.endswith(".gz"):
                fhs[url] = gzip.open(urllib.request.urlopen(url), mode="rb")
            else:
                fhs[url] = urllib.request.urlopen(url)
        return fhs


def close_files(fhs: dict):
    """
    Parameters:
    * **fhs** *[dict]*: {file: file handler}

    Returns: Nothing
    """
    for fh in fhs.values():
        fh.close()


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


def load_url_mem(url: str):
    """
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


def check_file(file: str):
    if not os.path.isfile(file):
        raise FileNotFoundError(file + " file do not exist")
    if os.path.getsize(file) == 0:
        raise FileNotFoundError(file + " file is empty")


def check_no_file(file: str):
    if os.path.isfile(file):
        raise FileExistsError(file)


def check_dir(prefix: str):
    abs_path = os.path.dirname(os.path.abspath(prefix))
    if not os.path.exists(abs_path):
        raise NotADirectoryError(abs_path)


def reverse_dict(d: dict):
    rd = {}
    for k, v in d.items():
        if v not in rd:
            rd[v] = []
        rd[v].append(k)
    return rd


def join_check(elements, sep: str):
    if elements:
        return sep.join(map(str, elements))
    else:
        return ""


def filter_function(elements, function, value):
    return [elements[i] for i, v in enumerate(map(function, elements)) if v == value]


def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)
