# IMDb Web Scraper

*Python Version 3.7+*

A Python script that extracts movie data from the IMDb website. It retrieves movie titles, release years, ratings, and genres and saves the data to a CSV file

## Usage
Install the following libraries:
```
pip install requests beautifulsoup4 pandas numpy
```

Run Command:

```
python imdb_scraper.py
```
- Enter an IMDb link when prompted.

## Notes
- The web scraper relies on the structure and layout of IMDb's website. Any changes to the website's HTML structure may cause inaccurate results
- Currently only supports English version of IMDb website
