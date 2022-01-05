import requests
import sqlite3
from bs4 import BeautifulSoup


#con = sqlite3.connect("jobs.db")


URL = "https://realpython.github.io/fake-jobs/"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

results = soup.find(id="ResultsContainer")

job_elements = results.find_all("div", class_="card-content")

for job_element in job_elements:
    title_element = job_element.find("h2", class_="title")
    company_element = job_element.find("h3", class_="company")
    location_element = job_element.find("p", class_="location")
    print(title_element.text.strip())
    print(company_element.text.strip())
    print(location_element.text.strip())
    date_element = job_element.find("time")
    date = date_element["datetime"]
    print(date)

    links = job_element.find_all("a")
    for link in links:
        link_url = link["href"]
        link_text = link.text.strip()
        if link_text == "Apply":
            print(f"Link = {link_url}")
    print()


