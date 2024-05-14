from time import sleep, strftime
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re


class WebScraper:
    def __init__(self, origin, destination, date):
        self.driver = webdriver.Chrome()
        self.origin = origin
        self.destination = destination
        self.date = date
        self.driver.get(f'https://www.kayak.com/flights/{origin}-{destination}/{date}?sort=price_a')

    def __parse_item(self, result_list):
        parsed_result = []
        #Gets the necessary data from the html component oassed
        for i in result_list:
            price = i.find_next('div', class_=re.compile(r'^.{4}-price-text$')).text
            time_list = i.find_next('div', class_=re.compile(r'^.{9}-mod-variant-large$')).find_all('span')
            time = ' '.join([j.text for j in time_list])
            airline = i.find_next('div', class_=re.compile(r'^.{11}-mod-variant-default$')).text
            origin_airport = i.find_all('div', class_=re.compile(r'^.{11}-mod-variant-default$'))[2].find_all('span')[1].text
            destination_airport = i.find_all('div', class_=re.compile(r'^.{11}-mod-variant-default$'))[2].find_all('span')[-2].text
            parsed_result.append({
                'Origin': origin_airport,
                'Destination': destination_airport,
                'Departure Date': self.date,
                'Time': time,
                'Airline': airline,
                'Price(USD)': round(float(''.join([x for x in price if x.isdigit()])), 2),
            })
        self.driver.close()
        return parsed_result

    def load_data(self):
        sleep(randint(2,6))
        try:
            path = '//*[@id="listWrapper"]'
            #opens url using webdriver
            results = WebDriverWait(self.driver, timeout=randint(1, 4)).until(
                EC.presence_of_element_located((By.XPATH, path))).get_attribute(
                'innerHTML')
            #Gets the necessary HTML component from the page
            soup = BeautifulSoup(results, "html.parser")
            result_list = soup.find_all('div', {'data-resultid': re.compile(r'^[0-9A-Fa-f]{32}$')})
            return self.__parse_item(result_list)
        except:
            #In some cases the first method fails
            try:
                path = 'resultsContainer'
                results = WebDriverWait(self.driver, timeout=randint(1, 4)).until(
                    EC.presence_of_element_located((By.CLASS_NAME, path))).get_attribute(
                    'innerHTML')
                soup = BeautifulSoup(results, "html.parser")
                result_list = soup.find_all('div', {'data-resultid': re.compile(r'^[0-9A-Fa-f]{32}$')})
                return self.__parse_item(result_list)
            except:
                print('Unspecified Error!')