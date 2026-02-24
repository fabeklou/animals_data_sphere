"""
This module contain utility functions for the streamlit app
"""

from typing import List, Tuple, Dict
import subprocess
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import sqlite3


# ---- Setups ---- #

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# ---- Constants ---- #

BASE_URL = "https://sn.coinafrique.com"
ROOT_PAGE_LIST = [
    {
        "title": "chiens",
        "url": "https://sn.coinafrique.com/categorie/chiens?page=",
        "keys": ("nom", "prix", "adresse", "image_lien")
    },
    {
        "title": "moutons",
        "url": " https://sn.coinafrique.com/categorie/moutons?page=",
        "keys": ("nom", "prix", "adresse", "image_lien")
    },
    {
        "title": "poules_lapins_et_pigeons",
        "url": "https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons?page=",
        "keys": ("details", "prix", "adresse", "image_lien"),
    },
    {
        "title": "autres_animaux",
        "url": "https://sn.coinafrique.com/categorie/autres-animaux?page=",
        "keys": ("nom", "prix", "adresse", "image_lien"),
    }
]
DB_URL = "./data/Animals.db"
RAW_DATA_PATH = "data/raw_data/"
CLEANED_DATA_PATH = "data/clean_data/"

# ---- Utility Functions ---- #


def scrap_simple(container):
    v1 = container.find("p", class_="ad__card-description")
    v2 = container.find("p", class_="ad__card-price")
    v3 = container.find("p", class_="ad__card-location")
    v4 = container.find("img", class_="ad__card-img")

    return {
        "nom": v1.a.text if v1 is not None else np.nan,
        "prix": v2.a.text if v2 is not None else "",
        "adresse": v3.span.text if v3 is not None else np.nan,
        "image_lien": v4["src"] if v4 is not None else np.nan
    }


def scrap_nested(path, base_url=None):
    url = BASE_URL + path if base_url is None else base_url + path

    driver.get(url)
    time.sleep(1)
    soup = bs(driver.page_source, "html.parser")

    v1 = soup.find("div", class_="ad__info__box ad__info__box-descriptions")
    v2 = soup.find("p", class_="price")

    v3 = soup.find("div", class_="row valign-wrapper extra-info-ad-detail")
    v3 = v3 if (v3 is None) else v3.find_all("span")
    v3 = v3 if (v3 is None) else v3[2]

    v4 = soup.find(id="slider")
    v4 = v4 if (v4 is None) else v4.find_all("div")[0]

    return {
        "details": v1.find_all("p")[-1].text if (v1 is not None) else np.nan,
        "prix": v2.text if (v1 is not None) else "",
        "adresse": v3.text if (v3 is not None) else np.nan,
        "image_lien": v4["style"].split('(')[1].split(')')[0].strip('"') if (v4 is not None) else np.nan,
    }


def clean_scraped_data(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    df = df.drop_duplicates()

    if df.shape[0] > 0:
        df["prix"] = pd.to_numeric(df["prix"].str.replace(
            " ", "").str.rstrip("CFA"), errors="coerce")
        df["prix"] = df["prix"].fillna(df["prix"].median())

        df['adresse'] = df['adresse'].fillna('Adresse Inconnue')
        df['image_lien'] = df['image_lien'].fillna('Lien Inconnu')

        if "nom" in df.columns:
            df["nom"] = df["nom"].fillna(df["nom"].mode())
        elif "details" in df.columns:
            df["details"] = df["details"].fillna("Details Inconnus")

    return df


def scrap_animals_data(page_to_scrap: Dict[str, str | Tuple], number_of_page: int) -> Tuple[str, pd.DataFrame]:
    animal_data_list = []
    for page_index in range(1, number_of_page + 1):
        try:
            page_url = f"{page_to_scrap["url"]}{page_index}"
            driver.get(page_url)
            time.sleep(1)

            soup = bs(driver.page_source, 'html.parser')
            containers = soup.find_all("div", class_="col s6 m4 l3")

            if page_to_scrap['title'] != "poules_lapins_et_pigeons":
                animal_data_list.extend(
                    [scrap_simple(container) for container in containers])
            else:
                path_list = [container.find(
                    "p", class_="ad__card-description").a["href"] for container in containers]
                animal_data_list.extend([scrap_nested(path)
                                        for path in path_list])
        except Exception as ex:
            raise ("No Data Scraped ERROR!")
    return page_to_scrap["title"], pd.DataFrame(animal_data_list)


def save_data_to_db(data: pd.DataFrame, table_name: str):
    conn = sqlite3.connect(DB_URL)
    data.to_sql(name=table_name, con=conn, if_exists="replace", index=False)


def scrap_clean_save_data(page_to_scrap: Dict[str, str | Tuple], number_of_page: int):
    try:
        title, data = scrap_animals_data(page_to_scrap, number_of_page)
        data = clean_scraped_data(data)
        save_data_to_db(data, table_name=title)
    except Exception as ex:
        print(ex)


def read_from_db(table_name: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_URL)
    data = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    return data


def read_raw_data():
    cmd_output = subprocess.run(
        ["ls", RAW_DATA_PATH], capture_output=True, text=True).stdout
    return [
        (
            path[17:-9].replace("_", " ").title(),
            pd.read_csv(RAW_DATA_PATH + path)
        ) for path in cmd_output.split()
    ]


def read_cleaned_data():
    cmd_output = subprocess.run(
        ["ls", CLEANED_DATA_PATH], capture_output=True, text=True).stdout
    return [
        (
            path[8:-9].replace("_", " ").title(),
            pd.read_csv(CLEANED_DATA_PATH + path)
        ) for path in cmd_output.split()
    ]


def plot_animal_data(dir_path: str) -> None:
    pass
