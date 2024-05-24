from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
from functions import remove_accents, verify_title, skip_words, create_df

class AmazonScraper:
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

        self.page_counter = 1
        self.data = []
        print(f'Amazon: Number of pages to scrape: {self.total_pages} pages.')
        while True:
            print(f'Amazon: Scraping page {self.page_counter}.')
            if self.update_callback:
                self.update_callback(self.page_counter, self.total_pages)
            self.scrape()
            if self.page_counter < int(self.total_pages):
                self.next_page()
            else:
                break
        
        create_df(self.data, self.search, 'Amazon', columns=['Title', 'Price', 'ASIN', 'URL'], export_options=self.export_options)

    def search_product(self):
        self.driver = webdriver.Chrome(options=self.options)

        self.driver.get('https://www.amazon.com.br/')

        time.sleep(1.5)
        self.driver.refresh()

        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input#twotabsearchtextbox'))
        )

        search_input.send_keys(self.search + Keys.ENTER)

        four_stars = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.a-star-medium-4'))
        )

        four_stars.click()
        
        try:
            self.total_pages = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.s-pagination-item'))
            )[-2].text
        except TimeoutException:
            print('Amazon: Error, trying again.')
            self.driver.close()
            self.search_product()

        
        time.sleep(1.5)

    def scrape(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        products = soup.find_all('div', attrs={'data-component-type': 's-search-result'})

        counter = 0
        for index, product in enumerate(products): 
            title = product.find('div', attrs={'data-cy': 'title-recipe'}).find('h2').find('span').text
            if not verify_title(title, self.search):
                continue
            if skip_words(title):
                continue
            title = remove_accents(title)

            price = product.find('span', class_='a-price')
            
            if price is not None:
                price = price.find('span').text
            else:
                print('Amazon: Getting product without visible price.')
                self.driver.find_element(By.XPATH, f'//*[@data-component-type="s-search-result"][{index+1}]//h2/a["href"]').click()
                
                try:
                    price = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.aok-offscreen'))
                    ).text
                except TimeoutException:
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, '#buybox-see-all-buying-choices a').click()
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.aok-align-center span.a-offscreen'))
                        )
                        price_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                        price = price_soup.find('div', class_='aok-align-center').find('span', class_='a-offscreen').text
                        time.sleep(1.5)
                        self.driver.back()
                    except NoSuchElementException:
                        self.driver.back()
                        continue

                time.sleep(1.5)
                self.driver.back()
            
            price = price.replace('\xa0', ' ')

            url = product.find('h2').find('a', class_='a-link-normal')['href']
            if 'sspa' in url:
                asin = url.split(r'%2F')[3]
            else:
                asin = url.split('/')[3]
            full_url = f'https://amazon.com.br/dp/{asin}'

            counter += 1

            self.data.append([title, price, asin, full_url])

        if counter < 1:
            self.page_counter = int(self.total_pages)
            if self.update_callback:
                self.update_callback(self.page_counter, self.total_pages)
            print('Amazon: No more products')

    def next_page(self):
        self.driver.find_element(By.CSS_SELECTOR, '.s-pagination-next').click()

        time.sleep(5)

        self.page_counter += 1

if __name__ == '__main__':
    search = input('Product you wanna search: ')
    webscraper = AmazonScraper()
    webscraper.run(search)