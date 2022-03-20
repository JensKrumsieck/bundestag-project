import os
import time
import typing
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.request
from util.progress import progress
from util.net import download_file
from util.io import ensure_path, remove_duplicates

baseUrl = "https://www.bundestag.de"
reqUrl = f"{baseUrl}/ajax/filterlist/de/parlament/plenum/abstimmung/liste/462112-462112?limit=20&noFilterSet=true&offset="
baseDir = os.getcwd() + '/scraper/'
rootDir = os.getcwd()
urllist = f'{baseDir}out/polls_urls.txt'

####
# 1. get_links() to get links to all poll files
# 2. get_files() to download individual excel files
# 3. check_files() to ensure files matching all list items
# 4. merge_data() to build a big csv file
# 5. process_data() to build individual csv files
####


def ensure_out():
    path = os.getcwd() + "/scraper/out"
    ensure_path(path)
    ensure_path(f"{path}/files")


def get_links():
    polls = []
    for i in range(0, 1000, 20):
        print(f"sending request with offset {i}")
        try:
            url = reqUrl + str(i)
            req = requests.get(url, timeout=5)
            if req.status_code > 400:
                print(req.status_code)
                break
            res = req.content
            soup = BeautifulSoup(res, 'lxml')
            items = soup.find_all(class_="bt-link-dokument")
            if len(items) == 0:
                print("end reached")
                break
            for item in items:
                href: str = item.get('href')
                if href.endswith(".xlsx") or href.endswith(".xls"):  # get excel files
                    polls.append(f"{baseUrl}{href}")
        except:
            print("Request failed, try again")

        # send request every sec
        time.sleep(1)
    ensure_out()
    with open(f'{baseDir}out/polls_urls.txt', 'a') as file:
        file.write('\n'.join(polls))


def get_files():
    ensure_out()
    # ensure links are loaded
    if not os.path.exists(urllist):
        get_links()

    opener = urllib.request.build_opener()
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46')
    ]
    urllib.request.install_opener(opener)
    # execute get_links to get all links beforehand
    with open(urllist, 'r') as file:
        urls = [url.strip() for url in file.readlines()]
        urls = remove_duplicates(urls)
        for idx, url in enumerate(urls):
            progress(idx, len(urls), f"({idx}/{len(urls)})")
            try:
                urllib.request.urlretrieve(url, f'{baseDir}out/files/' + url.split('/')[-1])
            except Exception as e:
                print("An error occured, please try again later")
                print(e)
                break
            # send request every 1 sec
            time.sleep(1)


def check_files():
    folder = f'{baseDir}out/files/'
    i = 0
    with open(urllist, 'r') as list:
        urls = remove_duplicates(list.readlines())
        files = os.listdir(folder)
        for url in urls:
            if url.split("/")[-1].strip() not in files:
                download_file(url)


def merge_data():
    # this takes some time^^
    folder = f'{baseDir}out/files/'
    files = os.listdir(folder)
    dfs = []
    for idx, file in enumerate(files):
        progress(idx, len(files), f"({idx}/{len(files)})")
        dfs.append(pd.read_excel(folder+file))
    df = pd.concat(dfs)
    df.to_csv(f'{baseDir}out/data.csv', sep=";", encoding='utf-8-sig')
    print("merge completed!")


def evaluate_vote(row: pd.Series):
    yes = row["ja"]  # 1
    no = row["nein"]  # 0
    abstention = row["Enthaltung"]  # 2
    invalid = row["ungültig"]  # 2
    not_voted = row["nichtabgegeben"]  # 2
    if yes == 1:
        return 1
    elif no == 1:
        return 0
    elif abstention == 1 or invalid == 1 or not_voted == 1:
        return 2
    else:
        return np.NaN  # should not happen


def process_data():
    # data reduction, takes some minutes
    file = f'{baseDir}out/data.csv'
    df = pd.read_csv(file, sep=";")
    unique = df.drop_duplicates(subset=["Name", "Vorname", "Fraktion/Gruppe"])
    names = pd.DataFrame([unique["Name"], unique["Vorname"], unique["Fraktion/Gruppe"]]).transpose().reset_index().drop("index", axis=1)
    results = dict()
    for idx, row in df.iterrows():
        progress(idx, len(df.index), f"({idx}/{len(df.index)})")
        if row["Wahlperiode"] not in results:
            results[row["Wahlperiode"]] = names  # instantiate df for "Wahlperiode"
        cur = results[row["Wahlperiode"]]
        poll_name = f'{row["Wahlperiode"]:02d}-{row["Sitzungnr"]:03d}-{row["Abstimmnr"]:02d}'
        if poll_name not in cur:
            cur[poll_name] = np.nan

        vote = evaluate_vote(row)
        name_index = names[(names["Vorname"] == row["Vorname"]) & (names["Name"] == row["Name"]) & (names["Fraktion/Gruppe"] == row["Fraktion/Gruppe"])].index
        cur.at[name_index, poll_name] = vote
        results[row["Wahlperiode"]] = cur  # reassign

    ensure_path(rootDir + "/data")
    # save individual periods
    for period in results:
        cur: pd.DataFrame = results[period]  # to get intellisense
        # drop cols from other periods
        cols = [c for c in cur.columns if not c.startswith(str(period)) and "-" in c]
        cur = cur.drop(list(cols), axis=1)
        vote_cols = [c for c in cur.columns if "-" in c]
        cur = cur.dropna(axis=0, how="all", subset=vote_cols)
        cur.to_csv(f'{rootDir}/data/{period}_data.csv', sep=";", encoding='utf-8-sig')
    # merge and save all
    all: pd.DataFrame = pd.concat(results.values())
    all.to_csv(f'{rootDir}/data/all_data.csv', sep=";", encoding='utf-8-sig')
