import os
import gzip
import tarfile
import urllib.request
import io

from collections import OrderedDict


def open_files(files, max: int=1):
    if isinstance(files, str):
        files = [files]

    fhs = OrderedDict()
    for file in files:
        if not os.path.isfile(file):
            raise FileNotFoundError(file + " file do not exist")
        if os.path.getsize(file) == 0:
            raise FileNotFoundError(file + " file is empty")

        if file.endswith(".tar.gz") or file.endswith(".tgz"):
            fhs[file] = tarfile.open(file, mode='r:gz')
        elif file.endswith(".gz"):
            fhs[file] = gzip.open(file, "rt")
        else:
            fhs[file] = open(file, "r")

    return fhs


def write_close_files(fhs, output_prefix: str=None):
    # Check if output prefix was specified
    if output_prefix:
        if not os.path.exists(output_prefix):
            raise NotADirectoryError(output_prefix + " directory does not exist")
        else:
            for file, fh in fhs.items():
                print(file, fh)
                # file = output_prefix + "/" + os.path.basename(url)
                # if os.path.isfile(file):
                #     raise FileExistsError(file + " already exists")
                # with open(file, "w") as outf:
                #     outf.write(fhs[-1].read().decode())
                #     #fhs[-1].seek(0)

    for fh in fhs.values():
        fh.close()


def download_files(default_urls, custom_ulrs: list=None):
    # Check default or custom urls
    urls = custom_ulrs if custom_ulrs else default_urls

    if isinstance(urls, str):
        urls = [urls]

    fhs = OrderedDict()
    for url in urls:
        if url.endswith(".tar.gz") or url.endswith(".tgz"):         
            # tar files have mixed headers and content
            # whole file should be loaded in memory first
            fhs[url] = tarfile.open(fileobj=load_file_mem(url), mode='r:gz')
        elif url.endswith(".gz"):
            fhs[url] = gzip.open(urllib.request.urlopen(url), mode="rb")
        else:
            fhs[url] = urllib.request.urlopen(url)

    return fhs


def load_file_mem(url):
    filestream = urllib.request.urlopen(url)
    # From https://stackoverflow.com/questions/18623842/read-contents-tarfile-into-python-seeking-backwards-is-not-allowed
    tmpfile = io.BytesIO()
    while True:
        s = filestream.read(io.DEFAULT_BUFFER_SIZE)
        if not s:
            break
        tmpfile.write(s)
    filestream.close()
    tmpfile.seek(0)
    return tmpfile