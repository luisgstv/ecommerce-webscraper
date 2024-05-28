from amazon_scraper import AmazonScraper
from pichau_scraper import PichauScraper
from kabum_scraper import KabumScraper
import customtkinter as ctk
import threading
import pandas as pd
import queue
from functions import sort_df

class ProductPriceFinder(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Setup Price Finder')
        self.geometry('500x500')

        # Search
        self.search_label = ctk.CTkLabel(self, text='Search')
        self.search_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text='Search a product')
        self.search_button = ctk.CTkButton(self.search_frame, text='Search', command=self.search)

        self.search_label.pack(pady=5)
        self.search_frame.pack(fill='x', padx=35, pady=5)
        self.search_entry.pack(side='left', expand=True, fill='x')
        self.search_button.pack(side='left')

        # Status
        self.status_label = ctk.CTkLabel(self, text='Status')
        self.status_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.status_label.pack(pady=5)
        self.status_frame.pack(pady=5)
        
        self.amazon_switch_var = ctk.StringVar(value='Amazon: On')
        self.amazon_switch = ctk.CTkSwitch(self.status_frame, onvalue='Amazon: On', offvalue='Amazon: Off', textvariable=self.amazon_switch_var, variable=self.amazon_switch_var)
        self.amazon_status = ctk.CTkLabel(self.status_frame, text='Amazon: Waiting')
        self.amazon_progress = ctk.CTkProgressBar(self.status_frame)
        self.amazon_progress.set(0)
        self.amazon_switch.pack(pady=5)
        self.amazon_status.pack(pady=5)
        self.amazon_progress.pack(pady=5)

        self.kabum_switch_var = ctk.StringVar(value='Kabum: On')
        self.kabum_switch = ctk.CTkSwitch(self.status_frame, onvalue='Kabum: On', offvalue='Kabum: Off', textvariable=self.kabum_switch_var, variable=self.kabum_switch_var)
        self.kabum_status = ctk.CTkLabel(self.status_frame, text='Kabum: Waiting')
        self.kabum_progress = ctk.CTkProgressBar(self.status_frame)
        self.kabum_progress.set(0)
        self.kabum_switch.pack(pady=5)
        self.kabum_status.pack(pady=5)
        self.kabum_progress.pack(pady=5)

        self.pichau_switch_var = ctk.StringVar(value='Pichau: On')
        self.pichau_switch = ctk.CTkSwitch(self.status_frame, onvalue='Pichau: On', offvalue='Pichau: Off', textvariable=self.pichau_switch_var, variable=self.pichau_switch_var)
        self.pichau_status = ctk.CTkLabel(self.status_frame, text='Pichau: Waiting')
        self.pichau_progress = ctk.CTkProgressBar(self.status_frame)
        self.pichau_progress.set(0)
        self.pichau_switch.pack(pady=5)
        self.pichau_status.pack(pady=5)
        self.pichau_progress.pack(pady=5)

        # Output
        self.output_label = ctk.CTkLabel(self, text='Output')
        self.output_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.output_label.pack(pady=5)
        self.output_frame.pack(pady=5)

        self.csv_var = ctk.IntVar(value=1)
        self.excel_var = ctk.IntVar(value=0)
        self.sheets_var = ctk.IntVar(value=0)

        self.csv_checkbox = ctk.CTkCheckBox(self.output_frame, text='CSV', variable=self.csv_var)
        self.excel_checkbox = ctk.CTkCheckBox(self.output_frame, text='Excel', variable=self.excel_var)
        self.csv_checkbox.pack(side='left')
        self.excel_checkbox.pack(side='left')

    def search(self):
        search = self.search_entry.get()
        if search != '':
            self.amazon_progress.set(0)
            self.kabum_progress.set(0)
            self.pichau_progress.set(0)

            self.results_queue = queue.Queue()
            self.results = {}
            self.active_scrapers = 0

            self.export_options = {
                'csv': self.csv_var.get(),
                'excel': self.excel_var.get()
            }

            if 'Amazon: On' in self.amazon_switch_var.get():
                self.active_scrapers += 1
                self.amazon = threading.Thread(target=lambda: self.run_scraper(AmazonScraper, 'Amazon', search, self.amazon_progress, self.export_options), daemon=True)
                self.amazon.start()
                self.update_status('Amazon', 'Running')
            if 'Kabum: On' in self.kabum_switch_var.get():
                self.active_scrapers += 1
                self.kabum = threading.Thread(target=lambda: self.run_scraper(KabumScraper, 'Kabum', search, self.kabum_progress, self.export_options), daemon=True)
                self.kabum.start()
                self.update_status('Kabum', 'Running')
            if 'Pichau: On' in self.pichau_switch_var.get():
                self.active_scrapers += 1
                self.pichau = threading.Thread(target=lambda: self.run_scraper(PichauScraper, 'Pichau', search, self.pichau_progress, self.export_options), daemon=True)
                self.pichau.start()
                self.update_status('Pichau', 'Running')

            self.check_queue()

    def run_scraper(self, scraper_class, name, search, progress_bar, export_options):
        scraper = scraper_class(update_callback=lambda page, total: self.update_progress(name, page, total, progress_bar), export_options=export_options)
        data = scraper.run(search)
        self.results_queue.put((name, data))
        self.update_status(name, 'Completed')

    def check_queue(self):
        try:
            while True:
                name, data = self.results_queue.get_nowait()
                self.results[name] = data

                if len(self.results) == self.active_scrapers: 
                    lower_prices_df = self.compare_prices()
                    if self.export_options['csv']:
                        lower_prices_df.to_csv(f'{self.search_entry.get().capitalize()} - Lowest Prices.csv', index=False)
                    if self.export_options['excel']:
                        lower_prices_df.to_excel(f'{self.search_entry.get().capitalize()} - Lowest Prices.xlsx', index=False)
                    break
        except queue.Empty:
            self.after(1000, self.check_queue)

    def update_status(self, scraper_name, status):
        if scraper_name == 'Amazon':
            self.amazon_status.configure(text=f'Amazon: {status}')
        elif scraper_name == 'Kabum':
            self.kabum_status.configure(text=f'Kabum: {status}')
        elif scraper_name == 'Pichau':
            self.pichau_status.configure(text=f'Pichau: {status}')

    def update_progress(self, scraper_name, page, total_pages, progress_bar):
        progress = int(page) / int(total_pages)
        progress_bar.set(progress)
        if scraper_name == 'Amazon':
            self.amazon_status.configure(text=f'Amazon: Running (Page {page}/{total_pages})')
        elif scraper_name == 'Kabum':
            self.kabum_status.configure(text=f'Kabum: Running (Page {page}/{total_pages})')
        elif scraper_name == 'Pichau':
            self.pichau_status.configure(text=f'Pichau: Running (Page {page}/{total_pages})')

    def compare_prices(self):
        lower_prices = []
        for name, df in self.results.items():
            df['Site'] = name
            df = df[['Title', 'Price', 'Site', 'URL']].iloc[0]
            lower_prices.append(df)
        lower_prices_df = pd.DataFrame(lower_prices)
        lower_prices_df = sort_df(lower_prices_df)
        return lower_prices_df

if __name__ == '__main__':
    app = ProductPriceFinder()
    app.mainloop()