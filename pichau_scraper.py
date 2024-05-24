from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from functions import remove_accents, verify_title, skip_words, create_df
import re
    
class PichauScraper:
    def __init__(self, update_callback=None, export_options=None):
        self.update_callback = update_callback
        self.export_options = export_options

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True, slow_mo=300)
        self.page = self.browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0')

    def run(self, search):
        self.search = search

        self.search_product()

        self.page_counter = 1
        self.data = []
        print(f'Pichau: Number of pages to scrape: {self.total_pages} pages.')
        while True:
            print(f'Pichau: Scraping page {self.page_counter}.')
            if self.update_callback:
                self.update_callback(self.page_counter, self.total_pages)
            self.scrape()
            if self.page_counter < int(self.total_pages):
                self.next_page()
            else:
                break
        
        create_df(self.data, self.search, 'Pichau', columns=['Title', 'Price', 'URL'], export_options=self.export_options)
        self.playwright.stop()

    def search_product(self):
        self.page.goto('https://www.pichau.com.br/')
        self.page.wait_for_load_state()
        search_input = 'input.MuiInputBase-input'
        self.page.fill(search_input, self.search)
        self.page.press(search_input, 'Enter')
        self.total_pages = BeautifulSoup(self.page.inner_html('ul.MuiPagination-ul'), 'html.parser').find_all('button')[-2].text

    def scrape(self):
        self.page.wait_for_load_state()
        soup = BeautifulSoup(self.page.inner_html('div.MuiGrid-container div.MuiGrid-container'), 'html.parser')
        products = soup.find_all('div', class_='MuiCard-root')

        counter = 0
        for product in products:
            stock_verification = product.find('div', class_='MuiCardContent-root').find('p')
            if stock_verification:
                self.page_counter = int(self.total_pages)
                if self.update_callback:
                    self.update_callback(self.page_counter, self.total_pages)
                break

            title = product.find('div', class_='MuiCardContent-root').find('h2').text
            if not verify_title(title, self.search):
                continue
            if skip_words(title):
                continue
            title = remove_accents(title)

            price = product.find('div', class_='MuiCardContent-root').find('div', string=re.compile('$')).text
            price = price.replace('\xa0', ' ')

            url = product.parent['href']
            full_url = f'https://pichau.com.br{url}'

            counter += 1

            self.data.append([title, price, full_url])
        
        if counter < 1:
            self.page_counter = int(self.total_pages)
            if self.update_callback:
                self.update_callback(self.page_counter, self.total_pages)
            print('Pichau: No more products')

    def next_page(self):
        self.page.mouse.wheel(0, 3000)
        self.page.wait_for_timeout(2500)
        self.page.locator('ul.MuiPagination-ul button').all()[-1].click()
        self.page_counter += 1

if __name__ == '__main__':
    search = input('Product you wanna search: ')
    scraper = PichauScraper()
    scraper.run(search)