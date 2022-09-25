from setuptools import setup, find_packages

with open("README.md", "r") as file:
    long_description = file.read()

name = "AioPTTCrawler"
setup(
    name=name,
    version="0.0.2",
    author="DOUIF",
    author_email="a15975345678@gmail.com",
    description="PTT crawler using asyncio",
    long_description=long_description,
    long_description_content_type = "text/markdown",
    url="https://github.com/DOUIF/aio-ptt-crawler",
    packages=find_packages(),
    install_requires=[
        'aiohttp>=3.8.3',
        "lxml>=4.9.1",
        "requests>=2.28.1",
        "pandas>=1.5.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires ='>=3.10',
)