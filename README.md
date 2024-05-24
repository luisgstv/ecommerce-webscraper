# E-Commerce Price Comparison Webscraper

This project is a comprehensive webscraper for three different e-commerce websites: Amazon, Kabum, and Pichau. It allows you to quickly search for a product and compare prices across these sites. Kabum and Pichau are Brazilian e-commerce platforms specializing in selling computer parts and electronics, with Kabum offering a broader range of electronic goods. Amazon, being a global platform, can be scraped for different country-specific sites by simply changing the URL suffix.

With an intuitive GUI, you can search for a product and select which websites to scrape based on your preference. You are not required to scrape all three sites; you can choose any combination of them. Additionally, the project supports exporting the scraped data in two formats, CSV and Excel, allowing you to save the results in your preferred format.

## Tools and Modules

- **Selenium**: Used for scraping Amazon and Kabum websites.
- **Playwright**: Used for scraping the Pichau website because Selenium could not access it.
- **BeautifulSoup4**: Employed to parse HTML pages and quickly locate the desired elements for all scrapers.
- **Pandas**: Utilized for creating DataFrames to manipulate and export data to CSV and Excel files, ensuring the results are sorted in ascending order.
- **Locale**: Used to format the price values in the DataFrame to the Brazilian format, ensuring the data is clean and sorted correctly.
- **Time**: Introduced delays in the scraping process to avoid sending too many requests in a short period, reducing the risk of getting banned.
- **Re**: Used to create patterns to verify if the product name matches the search query by analyzing each word in the title and to securely find prices within the page.
- **CustomTkinter**: Utilized to build the graphical user interface (GUI) with all the necessary functionalities for user interaction.
- **Threading**: Used to create separate threads for each scraper, allowing them to run concurrently and improve the scraping speed.

## How it Works

When you run the program, you'll see a field to enter the product you want to search for, switches to enable or disable the websites, and checkboxes to select export formats. After entering the product, selecting the websites to scrape, and choosing the export formats, you click the search button. This action starts separate threads for each scraper, passing the relevant information to each one. Each scraper follows a similar process: accessing the site, performing the search, determining the number of pages, scraping the data, parsing the HTML with BeautifulSoup4, and finding the desired elements. The data is then exported in the chosen formats. Despite following the same general approach, each scraper has its unique aspects.

Additionally, each scraper can be run independently from the command line by executing its respective script, allowing you to enter the product name directly in the terminal and receive progress updates.

### Webscrapers Workflow

1. **Amazon Scraper**:

   - Access the Amazon website and bypass the captcha by refreshing the page.
   - Perform the search for the specified product and apply the 4-star filter.
   - Determine the number of result pages.
   - Parse the HTML using BeautifulSoup4.
   - Find the title and check if it matches the search query. Then, check for specific unwanted words in the title and remove those products from the data if the words are present. This step ensures that only relevant products are included (for example, some products might include a processor and a motherboard in the title, but you only want the processor, so the script filters out such results).
   - Find the price. If it is not visible, open the product page to check. If it remains hidden, attempt to open the options and get the first available price. If no options are accessible, remove the product from the data.
   - Find the URL and extract the ASIN from it, then create a new URL with the ASIN.
   - Go to the next page and repeat the process until the last page.
   - If at any point no products are found on a specific page, stop the scraping process as the subsequent pages are unlikely to have relevant results.
   - Export the data to the selected formats, including the product name, price, ASIN, and URL.

2. **Kabum Scraper**:

   - Access the Kabum website.
   - Perform the search for the specified product.
   - Determine the number of result pages.
   - Parse the HTML using BeautifulSoup4.
   - Find the title and check if it matches the search query. Then, check for specific unwanted words in the title and remove those products from the data if the words are present. This step ensures that only relevant products are included (for example, some products might include a processor and a motherboard in the title, but you only want the processor, so the script filters out such results).
   - Find the price. If the price field does not contain a numerical value, remove the product from the data.
   - Find the product ID and create a URL with it.
   - Go to the next page and repeat the process until the last page.
   - If at any point no products are found on a specific page, stop the scraping process as the subsequent pages are unlikely to have relevant results.
   - Export the data to the selected formats, including the product name, price, ID, and URL.

3. **Pichau Scraper**:

   - Access the Pichau website.
   - Perform the search for the specified product.
   - Determine the number of result pages.
   - Parse the HTML using BeautifulSoup4.
   - Check if the product is in stock. If not, stop the scraping process as the subsequent products are also unlikely to be in stock.
   - Find the title and check if it matches the search query. Then, check for specific unwanted words in the title and remove those products from the data if the words are present. This step ensures that only relevant products are included (for example, some products might include a processor and a motherboard in the title, but you only want the processor, so the script filters out such results).
   - Find the price using regular expressions (re) because there are no reliable tags to find this value.
   - Find the product URL.
   - Go to the next page and repeat the process until the last page.
   - If at any point no products are found on a specific page, stop the scraping process as the subsequent pages are unlikely to have relevant results.
   - Export the data to the selected formats, including the product name, price and URL.

### GUI Explanation

The GUI is built using CustomTkinter and provides an intuitive interface for users to interact with the scrapers:

- **Product Search Field**: Enter the name of the product you want to search for.
- **Search Button**: Initiates the scraping process using threads for each selected scraper.
- **Website Switches**: Toggle switches to enable or disable scraping from Amazon, Kabum, or Pichau. All scrapers are enabled by default.
- **Export Options**: Checkboxes to select the export formats (CSV, Excel). The CSV option is checked by default.

Each scraper will run concurrently in its own thread, fetching data and updating the GUI with progress information. Once the scraping is complete, the data will be exported to the selected formats.

## How to Use

To use this project, you will need to follow these steps:

1. **Clone this repository**:

```bash
git clone repository
```

2. Install the required modules using the following command:

```bash
pip install -r requirements.txt
```

3. Install the playwright drivers:

```bash
playwright install
```

4. Enter the product name, select the websites to scrape, and choose the export formats.

5. Click the search button to start the scraping process. The progress will be displayed in the GUI, and the data will be exported in the selected formats once scraping is complete.

## Additional Notes

Feel free to contribute to this project by submitting pull requests or opening issues for any bugs or feature requests.
