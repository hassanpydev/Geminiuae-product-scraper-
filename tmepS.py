
from time import sleep

import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from typing import Optional
from selenium.webdriver.support.ui import WebDriverWait
import os
from pydantic import BaseModel


options = Options()
data = []


class CompanyDetails(BaseModel):
    company_phone: Optional[str]
    company_tele: Optional[str]
    company_email: Optional[str]
    company_category: Optional[str]
    company_name: Optional[str]


def extractConsultation(html):
    source = BeautifulSoup(html, "html.parser")
    companies = source.find_all("div", {"class": "row"})
    for attempt in companies:
        if attempt.find_all("a", {"class": "facListItem"}):
            for companies_information in attempt.find_all(
                "div", {"class": "col-md-4 col-sm-12"}
            ):
                try:
                    company_information = companies_information["onclick"][26::].split(
                        ","
                    )
                    company_phone = company_information[0].strip("'").replace("  ", "")
                    company_tele = company_information[1].strip("'").replace("  ", "")
                    company_email = company_information[2].strip("'").replace("  ", "")
                    company_category = (
                        company_information[3].strip("'").replace("  ", "")
                    )
                    company_name = company_information[4].strip("'").replace("  ", "")
                    comp = CompanyDetails(
                        company_phone=company_phone.strip().replace("'", ""),
                        company_tele=company_tele.strip().replace("'", ""),
                        company_email=company_email.strip().replace("'", ""),
                        company_category=company_category.strip().replace("'", ""),
                        company_name=company_name.strip().replace("');", "").replace("'", ""),
                    )
                    data.append(comp.json())
                except KeyError:
                    continue


def HeadlessBrowserHttpRequest(target: str, page=None) -> str:
    """
    create a headless browser and send a http request.
    :param target: target url
    :param page: page number
    :return: html source code

    """
    driver = webdriver.Chrome(
        options=options, executable_path=os.path.abspath("chromedriver")
    )
    driver.get(target)

    print("Headless Browser: ", driver.title)
    WebDriverWait(driver, 10).until(
        lambda driver: driver.find_element(By.CSS_SELECTOR, ".facListItem")
    )
    source = driver.page_source
    extractConsultation(source)
    print("\033[1;32m Headless Browser: Done !!!\033[1;00m")
    counter = 0
    while True:
        try:
            counter += 1
            driver.find_element(By.CSS_SELECTOR, ".fa-angle-left").click()
            sleep(8)
            extractConsultation(driver.page_source)
            print(f"\033[1;32m New Page {counter} Scrapped: Done !!!\033[1;00m")
            
        except BaseException as e:
            print(e)
            break
    driver.quit()
    # current_page = 2
    # while True:
    #     for i in range(1, 5):
    #         try:
    #             driver.find_elements(By.CSS_SELECTOR, ".pagination a")[i].click()
    #             print(len(driver.find_elements(By.CSS_SELECTOR, ".pagination a")))
                
    #             sleep(4)
    #             WebDriverWait(driver, 10).until(
    #                 lambda driver: driver.find_element(By.CSS_SELECTOR, ".facListItem")
    #             )

    #             extractConsultation(driver.page_source)
    #         except IndexError as e:
    #             print(e)
    #             break
    #         except Exception as e:
    #             # print(e)
    #             continue
    #     WebDriverWait(driver, 10).until(
    #                 lambda driver: driver.find_element(By.CSS_SELECTOR, ".facListItem")
    #             )
    #     driver.find_elements(By.CSS_SELECTOR, ".pagination a")[-1].click()

HeadlessBrowserHttpRequest(
    "https://modon.gov.sa/ar/Partners/Factories/Pages/default.aspx"
)

# write data into file 
with open("data.txt", "wb") as f:
    for item in data:
        f.write(str(str(item) + ',').encode("utf-8"))
        f.write("\n".encode("utf-8"))
