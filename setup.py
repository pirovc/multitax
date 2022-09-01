from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="multitax",
    version="1.2.0",
    url="https://www.github.com/pirovc/multitax",
    license='MIT',

    author="Vitor C. Piro",
    author_email="pirovc@posteo.net",

    description="Python package to obtain, parse and explore biological and custom taxonomies",
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=['multitax'],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.4",
)
