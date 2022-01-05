
# Tutorial from: <https://www.w3schools.com/python/python_tuples.asp>
# Basics of web scraping on insertion into SQLite DB
#
# TODO: Command line options

import requests
import sqlite3
import hashlib
from bs4 import BeautifulSoup

opt_print_tuple=0
opt_print_sql=1

con = sqlite3.connect("jobs-u.db")
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS jobs (hash TEXT UNIQUE, date TEXT, title TEXT, location TEXT, company TEXT, link TEXT)''')

URL = "https://realpython.github.io/fake-jobs/"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="ResultsContainer")
job_elements = results.find_all("div", class_="card-content")

def print_job(job):
    for i in job:
        print(i)
    print()

def hash_arr(j):
    hash_object = hashlib.sha256()
    for i in j:
        hash_object.update(i.encode())
    return hash_object.digest()


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

    row = [date_data, title_data, location_data, company_data, url_data]
    unique = hash_arr(row)
    row = row.insert(0, unique)
    if opt_print_tuple:
        print_job_tuple(row)
    try:
        cur.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?)", row)
    except:
        print(f"Tuple not unique {row}")

if opt_print_sql:
    for row in cur.execute("SELECT * FROM jobs ORDER BY title"):
        print(row[1:])

con.commit()
con.close()
