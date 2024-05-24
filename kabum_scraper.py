from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
from functions import remove_accents, verify_title, skip_words, create_df

class KabumScraper:
    def __init__(self, update_callback=None, export_options=None):
        self.update_callback = update_callback
        self.export_options = export_options

        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0')
        self.options.add_argument('--headless')
        self.options.add_argument('--log-level=3')

    def run(self, search):
        self.search = search

        self.search_product()

        self.data = []
        self.page_counter = 1
        print(f'Kabum: Number of pages to scrape: {self.total_pages} pages.')
        while True:
            print(f'Kabum: Scraping page {self.page_counter}.')
            if self.update_callback:
                self.update_callback(self.page_counter, self.total_pages)
            self.scrape()
            if self.page_counter < int(self.total_pages):
                self.next_page()
            else:
                break
        
        create_df(self.data, self.search, 'Kabum', columns=['Title', 'Price', 'ID', 'URL'], export_options=self.export_options)

    def search_product(self):
        self.driver = webdriver.Chrome(options=self.options)

        self.driver.get('https://www.kabum.com.br/')

        search_input = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input.id_search_input'))
        )

        search_input.send_keys(self.search + Keys.ENTER)
        
        try:
            self.total_pages = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.pagination li'))
            )[-2].text
        except TimeoutException:
            print('Kabum: Product not found.')
            self.driver.close()

        time.sleep(2)

    def scrape(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        products = soup.find_all('article', class_='productCard')

        counter = 0
        for product in products: 
            title = product.find('span', class_='nameCard').text
            if not verify_title(title, self.search):
                continue
            if skip_words(title):
                continue
            title = remove_accents(title)

            price = product.find('span', class_='priceCard').text
            if '----' in price:
                continue
            price = price.replace('\xa0', ' ')

            product_id = product.find('a')['data-smarthintproductid']
            url = f'https://kabum.com.br/produto/{product_id}'

            counter += 1

            self.data.append([title, price, product_id, url])
        
        if counter < 1:
            self.page_counter = int(self.total_pages)
            if self.update_callback:
                self.update_callback(self.page_counter, self.total_pages)
            print('Kabum: No more products')

    def next_page(self):
        next_page = self.driver.find_element(By.CSS_SELECTOR, 'a.nextLink')
        self.driver.execute_script("arguments[0].scrollIntoView();", next_page)
        time.sleep(1)
        self.driver.execute_script('arguments[0].click()', next_page)

        time.sleep(2)

        self.page_counter += 1

if __name__ == '__main__':
    search = input('Product you wanna search: ')
    webscraper = KabumScraper()
    webscraper.run(search)