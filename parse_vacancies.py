import json
import re

import requests
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from tqdm import tqdm


REQUEST = 'data scientist'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                         'AppleWebKit/537.36 (KHTML, like Gecko)' 
                         'Chrome/79.0.3945.79 Safari/537.36'}

URL = 'https://hh.ru/search/vacancy'

MONGO_URL = 'mongodb://root:password@mongo:27017/'

PARAMS = {
    "area": "1", 
    "L_is_autosearch": "false", 
    "clusters": "true", 
    "enable_snippets": "true", 
    "text": REQUEST
}


def getNumberOfPages():
    request = requests.get(URL, params=PARAMS, headers=HEADERS)
    parsed_html = bs(request.text, 'lxml')
    page_numbers = parsed_html.findAll('a', {'data-qa': 'pager-page'})
    last_page_number = int(str(page_numbers[-1].text)) if page_numbers else 0
    
    return last_page_number


def parseHHPage(data, page_num=0):  
    params = PARAMS
    params.update(page=str(page_num))
    request = requests.get(URL, params=params, headers=HEADERS)
    
    parsed_html = bs(request.text, 'lxml')
    
    vacancy_list = parsed_html.findAll('div', {'class': 'vacancy-serp-item'})
    
    for vacancy in vacancy_list:
        d = {}
        title = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        d['Title'] = title.text
        
        salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        d['Salary from'], d['Salary to'], d['Currency'] = parseSalary(salary)
        
        d['Link'] = re.sub(r'\?.*$', '', title['href'])
        
        location = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-address'})
        d['Location'] = location.text if location else None
        
        company = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
        d['Company'] = company.text if company else None
        
        data.append(d)
        
    return parsed_html


def parseSalary(salary):
    sal_from = None
    sal_to = None
    currency = None 
    if salary:
        salary = re.sub(r'[^\w\-–]', '', salary.text, re.UNICODE).replace('руб', 'RUR')
        if not salary.find('от'):
            re_search = re.search(r'(\d+)(.+)', salary)
            if re_search:
                sal_from = int(re_search.group(1))
                currency = re_search.group(2)
        elif not salary.find('до'):
            re_search = re.search(r'(\d+)(.+)', salary)
            if re_search:
                sal_to = int(re_search.group(1))
                currency = re_search.group(2)
        else:
            re_search = re.search(r'(\d+)[^d](\d+)(.+)', salary)
            if re_search:
                sal_from = int(re_search.group(1))
                sal_to = int(re_search.group(2))
                currency = re_search.group(3)
    return sal_from,  sal_to, currency


def db_insert(data):
    for vacancy in data:
        vacancies.update_one({'_id': vacancy['Link']},
                             {'$set': vacancy},
                             upsert=True)


if __name__ == '__main__':
	data = []
	last_page = getNumberOfPages()
	for i in range(1, last_page + 1):
	    parseHHPage(data, i)
	    print(f'Parsing page {i}.')
	print('Parsing is done.')

	client = MongoClient(MONGO_URL)
	db = client['db']
	vacancies = db.vacancies

	db_insert(data)
	print('Vacancies saved to MongoDB db.vacancies')
