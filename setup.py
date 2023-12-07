import codecs
import os.path

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__VERSION__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="aioWiserHeatAPI",
    version=get_version("aioWiserHeatAPI/__init__.py"),
    author="Mark Parker",
    author_email="msparker@sky.com",
    description="An AsyncIO API for controlling the Drayton Wiser Heating system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/msp1974/aioWiserHeatAPI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "zeroconf>=0.47.1",
        "aiohttp>=3.8.1",
        "aiofiles>=0.8.0",
        "pyyaml>=6.0",
        "httpx>=0.25.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": ["wiser = aioWiserHeatAPI.cli:main"],
    },
)
