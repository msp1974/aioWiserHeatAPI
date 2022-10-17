import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aioWiserHeatAPI",
    version="0.1.0",
    author="Mark Parker",
    author_email="msparker@sky.com",
    description="An AsyncIO API for controlling the Drayton Wiser Heating system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/msp1974/aioWiserHeatAPI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["zeroconf", "aiofiles", "pyyaml"],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": ["wiser = aioWiserHeatAPI.cli:main"],
    },
)
