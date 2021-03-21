import shutil
import os
import gzip
import tarfile


def setup_dir(d):
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)


def uncompress_gzip(f, outf):
    with gzip.open(f, 'r') as f_in, open(outf, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


def uncompress_tar_gzip(f, outdir):
    # Extract all files ignoring internal directories to outdir
    files = []
    with tarfile.open(f) as tar_in:
        for member in tar_in.getmembers():
            if member.isreg():
                member.name = os.path.basename(member.name)
                files.append(member.name)
                tar_in.extract(member, outdir)
    return files