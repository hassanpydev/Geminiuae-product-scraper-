import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional

duplicateFilter = []


class CompanyDetails(BaseModel):
    company_phone: Optional[str]
    company_tele: Optional[str]
    company_email: Optional[str]
    company_category: Optional[str]
    company_name: Optional[str]


def make_request(url):
    req = requests.get(url)
    if req.status_code == 200:
        return req.text


def extractConsultation(html):
    source = BeautifulSoup(html, 'html.parser')
    companies = source.find_all('div', {'class': "row"})
    for attempt in companies:
        if attempt.find_all('a', {'class': "facListItem"}):
            for companies_information in attempt.find_all('div', {'class': "col-md-4 col-sm-12"}):
                try:
                    company_information = companies_information['onclick'][26::].split(',')
                    company_phone = company_information[0].strip("'").replace(' ', '')
                    company_tele = company_information[1].strip("'").replace(' ', '')
                    company_email = company_information[2].strip("'").replace(' ', '')
                    company_category = company_information[3].strip("'").replace(' ', '')
                    company_name = company_information[4].strip("'").replace(' ', '')
                    print(CompanyDetails(company_phone=company_phone.strip(), company_tele=company_tele.strip(),
                                         company_email=company_email.strip(), company_category=company_category.strip(),
                                         company_name=company_name.strip().replace("');", '')).json())
                except KeyError:
                    continue
            print(len(duplicateFilter))
            # print(company_phone, company_tele, company_email, company_category, company_name)


responses = make_request('https://modon.gov.sa/ar/Partners/PrequalifiedConsultancyFirms/Pages/default.aspx')
print(extractConsultation(responses))
