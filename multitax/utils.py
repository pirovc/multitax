import os
import gzip
import tarfile
import urllib.request
import io

from collections import OrderedDict


def open_files(files):
    fhs = OrderedDict()
    for file in files:
        if file.endswith(".tar.gz") or file.endswith(".tgz"):
            fhs[file] = tarfile.open(file, mode='r:gz')
        elif file.endswith(".gz"):
            fhs[file] = gzip.open(file, "rt")
        else:
            fhs[file] = open(file, "r")
    return fhs


def close_files(fhs):
    for fh in fhs.values():
        fh.close()


def download_files(default_urls, custom_ulrs: list=None, output_prefix: str=None):
    # Check default or custom urls
    urls = custom_ulrs if custom_ulrs else default_urls

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


def save_urls(urls, output_prefix):
    files = []
    for url in urls:
        outfile = output_prefix + "/" + os.path.basename(url)
        check_no_file(outfile)
        urlstream = urllib.request.urlopen(url)
        with open(outfile, 'b+w') as f:
            f.write(urlstream.read())
        urlstream.close()
        files.append(outfile)
    return files


def load_url_mem(url):
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


def check_file(file):
    if not os.path.isfile(file):
        raise FileNotFoundError(file + " file do not exist")
    if os.path.getsize(file) == 0:
        raise FileNotFoundError(file + " file is empty")


def check_no_file(file):
    if os.path.isfile(file):
        raise FileExistsError(file)


def check_dir(d):
    if not os.path.exists(d):
        raise NotADirectoryError(d)
