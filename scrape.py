#! /usr/bin/env python3
#
# Example Script Only, not a serious program.
#
# Tutorial from: <https://realpython.com/beautiful-soup-web-scraper-python/>
# Basics of web scraping on insertion into SQLite DB.
#
# Linted with <http://pep8online.com/>
#

import os
import requests
import sqlite3
import hashlib
import sys
import argparse
from bs4 import BeautifulSoup

helps = """
Author:  Richard James Howe
Email:   howe.r.j.89@gmail.com
License: The Unlicense
Repo:    https://github.com/howerj/scrape

This program is not designed to be useful to anyone, but as a
demonstration project and learning exercise, as well as containing
useful snippets the author might find useful in the future. The
actual goal of this program is to parse and extract information
(example data from a fake job website as part of a tutorial) from a
website and store it into an sqlite database,

If you are intending to do anything serious with this project you
have taken a very wrong turn.

The tutorial on scraping is available here:

<https://realpython.com/beautiful-soup-web-scraper-python/>

Happy hacking!
"""

ap = argparse.ArgumentParser(
        description=helps,
        formatter_class=argparse.RawTextHelpFormatter
)

default_url="https://realpython.github.io/fake-jobs/"

ap.add_argument("--print_tuple", default=False, action="store_true", help="Print data as it is being collected")
ap.add_argument("--print_sql",  default=False, action="store_true", help="Print SQL db contents after collection")
ap.add_argument("--fetch_desc", default=False, action="store_true", help="Fetch the description from the link in the job description")
ap.add_argument("--file_local", default=False, action="store_true", help="Use local version of website instead of fetching it with a HTTP Get")
ap.add_argument("--clean",      default=False, action="store_true", help="Cleanup DB")
ap.add_argument("--url",        default=default_url,                help="URL (or directory if --file_local is set) to get data from")

opt = ap.parse_args()

con = sqlite3.connect("jobs.db")
cur = con.cursor()

if opt.clean:
    cur.execute('''DROP TABLE IF EXISTS jobs''')
    cur.execute('''VACUUM''')

cur.execute('''
        CREATE TABLE IF NOT EXISTS jobs
        (
            hash TEXT UNIQUE,
            date TEXT,
            title TEXT,
            location TEXT,
            company TEXT,
            link TEXT,
            description TEXT
)''')

if opt.file_local and opt.file_local == default_url:
    opt.url = "realpython.github.io/fake-jobs/"

def get_file(url):
    if not opt.file_local:
        page = requests.get(url)
        return page.content
    f = open(url)
    r = f.read()
    f.close()
    return r


content = get_file(opt.url + "/index.html")
if opt.file_local:
    os.chdir(opt.url)
soup = BeautifulSoup(content, "html.parser")
results = soup.find(id="ResultsContainer")
job_elements = results.find_all("div", class_="card-content")


def print_job_list(l):
    print(l)
    print()


def hash_arr(j):
    hash_object = hashlib.sha256()
    for i in j:
        hash_object.update(i.encode())
    return hash_object.digest()


def get_job_description(url):
    content = get_file(url)
    soup = BeautifulSoup(content, "html.parser")
    results = soup.find(id="ResultsContainer")
    content_class = results.find(class_="content")
    # print(content_class.__dict__)
    p = results.find_all("p", attrs={"id":""})
    return p[0].text.strip()

for job_element in job_elements:
    title_element = job_element.find("h2", class_="title")
    company_element = job_element.find("h3", class_="company")
    location_element = job_element.find("p", class_="location")
    date_element = job_element.find("time")
    date_data = date_element["datetime"]
    links = job_element.find_all("a")
    url_data = ""
    for link in links:
        link_url = link["href"]
        link_text = link.text.strip()
        if link_text == "Apply":
            url_data = link_url
    title_data = title_element.text.strip()
    company_data = company_element.text.strip()
    location_data = location_element.text.strip()

    description = ""
    if opt.fetch_desc:
        try:
            description = get_job_description(url_data)
        except:
            print(f"Failed to retrieve URL {url_data}")

    # Do not include optional description in hash
    row = [date_data, title_data, location_data, company_data, url_data]
    row.insert(0, hash_arr(row))
    row.append(description)
    if opt.print_tuple:
        print_job_list(row)
    try:
        cur.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?)", row)
    except:
        print(f"Not unique {row}")

if opt.print_sql:
    for row in cur.execute("SELECT * FROM jobs ORDER BY title"):
        print(row[1:])

con.commit()
con.close()

