import re
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

usr_agent = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
}

def main():
    url = input("Enter you imdb link: ").strip()
    if not is_valid_imdb_link(url):
        print("Incorrect IMDb link, please try again")
        return

    print("Searching...", flush=True)
    link_array = get_movie_links(url)

    if len(link_array) == 0:
        print("No movie links found")
        return

    print("Extracting...", flush=True)
    movie_data = get_movie_data(link_array)

    if movie_data is None:
        return

    print("Saving ...", flush=True)
    convert_to_csv(movie_data)

    print("Done")

def is_valid_imdb_link(url):
    """URL validation"""
    pattern = r"https://www.imdb.com.+"
    return bool(re.match(pattern, url))

def get_movie_links(url):
    """Parse, find and store all movie urls in array"""
    if re.search(r"https://www.imdb.com/title/tt\d+/", url):
        return [url]
    
    try:
        with requests.Session() as session:
            response = session.get(url, headers=usr_agent)
            soup = BeautifulSoup(response.content, "html.parser")
            movie_link_list = soup.find_all("a", href=re.compile(r"/title/tt\d+/"))
            link_array = []

            for link in movie_link_list:
                title_link = link["href"].split("?")[0]
                movie_link = f"https://www.imdb.com{title_link}"

                if movie_link in link_array:
                    continue
                else:
                    link_array.append(movie_link)
            
            return link_array
        
    except requests.exceptions.RequestException as error:
        print(f"Error occurred while accesing url: {error}", flush=True)
        return []

def extract_title(soup, pattern):
    movie_title_tag = str(soup.find("span", attrs={"class": "sc-afe43def-1 fDTGTb"}))
    movie_title = re.sub(pattern, "", movie_title_tag)

    if "&amp;" in movie_title:
        movie_title = movie_title.replace("&amp;", "&")

    return movie_title

def extract_year(soup, pattern):
    movie_year_tag = str(soup.find("a", href=re.compile(r"/title/tt\d+/releaseinfo.+")))
    movie_year = re.sub(pattern, "", movie_year_tag)
    return movie_year

def extract_rating(soup, pattern):
    imdb_rating_tag = str(soup.find("span", attrs={"class": "sc-bde20123-1 iZlgcd"}))
    imdb_rating = re.sub(pattern, "", imdb_rating_tag)
    return imdb_rating

def extract_genres(soup, pattern):
    movie_genres_array = []
    movie_genres_tags = soup.find_all("a", attrs={"class": "ipc-chip ipc-chip--on-baseAlt"})

    for genre in movie_genres_tags:
        movie_genres_array.append(re.sub(pattern, "", str(genre)))

    movie_genres = ", ".join(movie_genres_array)
    return movie_genres

def get_movie_data(link_array):
    """Extract and store movie data"""
    try:
        with requests.Session() as session:
            movie_data = {
                "title":  [],
                "year":   [],
                "rating": [],
                "genre":  [],
            }

            for link in link_array:
                response = session.get(link, headers=usr_agent)
                soup = BeautifulSoup(response.content, "html.parser")
                pattern = "<.+?>"

                movie_data["title"].append(extract_title(soup, pattern))
                movie_data["year"].append(extract_year(soup, pattern))
                movie_data["rating"].append(extract_rating(soup, pattern))
                movie_data["genre"].append(extract_genres(soup, pattern))

            return movie_data
        
    except requests.exceptions.RequestException as error:
        print(f"Error occurred while extracting data: {error}", flush=True)
        return None

def convert_to_csv(movie_data):
    """Convert and save data as csv file"""
    df = pd.DataFrame(movie_data)
    df.replace(to_replace="None", value=np.nan, inplace=True)
    # Drop rows with absent movie title
    df.dropna(subset=["title"], inplace=True)

    df.to_csv("imdb_data.csv", index=False, header=False, mode="w")

if __name__ == "__main__":
    main()