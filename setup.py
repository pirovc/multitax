import io
import os
import re

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

lib_folder = os.path.dirname(os.path.realpath(__file__))
install_requires = []
with open(f"{lib_folder}/requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="multitax",
    version="1.3.1",
    url="https://www.github.com/pirovc/multitax",
    license="MIT",
    author="Vitor C. Piro",
    description="Python package to obtain, parse and explore biological and custom taxonomies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["multitax"],
    install_requires=install_requires,
    python_requires=">=3.4",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
