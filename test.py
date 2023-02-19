import requests
from bs4 import BeautifulSoup as bs


page = requests.get("https://habr.com/ru/companies/page1/")
soup = bs(page.text, "html.parser")
companiesBlock = soup.find("div", {"class": "tm-companies"})
companies = companiesBlock.find_all("div", {"class": "tm-companies__company-wrapper"})
for company in companies:
    name = company.find("a", {"class": "tm-company-snippet__title"}).text
    description = company.find("div", {"class": "tm-company-snippet__description"}).text
    hubsBlock = company.find("div", {"class": "tm-companies__company-hubs"})
    print(hubsBlock)
    # hubs = [hub.text for hub in hubsBlock.find_all("span", {"class": "tm-companies__hubs-item"})]
    # print(f"{name} | {description} | {hubs}")
    print()
