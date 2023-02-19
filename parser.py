import json
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By


FILE_SUFFIX = ".json"
DATA_DIRECTORY = Path("data")


class Parser:
    def __init__(self, url=None):
        self._url = url
        self._soup = None
        self._data = {}
        self._lastPage = None
        self._browser = webdriver.Chrome()
        self._browser.maximize_window()

    def _generateSoup(self):
        page = requests.get(self._url)
        self._soup = bs(page.text, 'html.parser')

    def _getCompanies(self):
        companiesBlock = self._soup.find('div', {'class': 'tm-companies'})
        return companiesBlock.find_all('div', {'class': 'tm-companies__item tm-companies__item_inlined'})

    def _addCompany(self, companyData):
        self._data[companyData.pop('Name')] = companyData

    def _writeFileSummaryOfCompanies(self):
        path = DATA_DIRECTORY / "summary of companies"
        with path.with_suffix(FILE_SUFFIX).open('w', encoding='utf-8') as file:
            json.dump(self._data, file, indent=4, ensure_ascii=False)

    def _generateNextPageUrl(self, page):
        if page < self._lastPage:
            url = self._url.split('/')
            url[-2] = f"page{page + 1}"
            return "/".join(url)

    def _getInfoAboutCompany(self, browser, companyID):
        companyShortInfoBlock = browser.find_element(By.XPATH, f"//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[{companyID}]/div[1]/div[1]/div[1]")
        companyName = companyShortInfoBlock.find_element(By.CLASS_NAME, "tm-company-snippet__title").text
        companyDescription = companyShortInfoBlock.find_element(By.CLASS_NAME, "tm-company-snippet__description").text
        companyProfile = companyShortInfoBlock.find_element(By.CLASS_NAME, "tm-company-snippet__title").get_attribute("href")
        companyCountersBlock = browser.find_element(By.XPATH, f"//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[{companyID}]/div[2]")
        companyRating = float(companyCountersBlock.find_element(By.XPATH, f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[{companyID}]/div[2]/span[1]").text)
        companySubscribers = int(companyCountersBlock.find_element(By.XPATH, f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[{companyID}]/div[2]/span[2]").text.replace("К", ""))
        try:
            companyHubsBlock = browser.find_element(By.XPATH, f"//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[{companyID}]/div[1]/div[2]")
            companyHubs = [hub.text for hub in companyHubsBlock.find_elements(By.CLASS_NAME, "tm-companies__hubs-item")]
        except:
            companyHubs = []
        browser.get(companyProfile)
        industriesBlock = browser.find_element(By.CLASS_NAME, "tm-company-profile__categories")
        industries = [industry.text for industry in industriesBlock.find_elements(By.CLASS_NAME, "tm-company-profile__categories-wrapper")]
        try:
            companyAbout = browser.find_element(By.XPATH, "//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/section[1]/div[1]/div[1]/dl[2]/dd[1]/span[1]").text
        except:
            companyAbout = browser.find_element(By.XPATH, "//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/section[1]/div[1]/div[1]/dl[3]/dd[1]/span[1]").text

        return {
            "Name": companyName,
            "Description": companyDescription,
            "About": companyAbout,
            "Industries": industries,
            "Rating": companyRating,
            "Subscribers": companySubscribers,
            "Hubs": companyHubs,
            "Profile": companyProfile
        }

    def start(self):
        self._generateSoup()
        self._browser.get(self._url)
        self._lastPage = int([el.text for el in self._browser.find_elements(By.CLASS_NAME, "tm-pagination__page")][-1])
        for page in range(16, self._lastPage + 1):
            try:
                for companyID, company in enumerate(self._getCompanies(), start=1):
                    self._addCompany(self._getInfoAboutCompany(self._browser, companyID))
                    self._browser.get(self._url)
                self._browser.get(self._url)
                self._browser.find_element(By.XPATH, "//a[@id='pagination-next-page']").click()
                self._url = self._generateNextPageUrl(page)
                time.sleep(2)
            except Exception as e:
                print('complete last page')
                self._browser.close()
                break
        self._writeFileSummaryOfCompanies()


parser = Parser("https://habr.com/ru/companies/page16/")
parser.start()
