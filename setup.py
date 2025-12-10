"""
Setup script for Naukri Scraper
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="naukri-scraper",
    version="1.0.0",
    author="dwaithdev-ship-it",
    description="A Python utility to scrape job listings from Naukri.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dwaithdev-ship-it/NaukriScapper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "pandas>=2.0.0",
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "naukri-scraper=cli:main",
        ],
    },
    keywords="naukri scraper job web-scraping python",
    project_urls={
        "Bug Reports": "https://github.com/dwaithdev-ship-it/NaukriScapper/issues",
        "Source": "https://github.com/dwaithdev-ship-it/NaukriScapper",
    },
)
