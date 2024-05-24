import pandas as pd
import locale
import re

def remove_accents(text):
    accents = str.maketrans(
        'áàãâäéèêëíìîïóòõôöúùûüç',
        'aaaaaeeeeiiiiooooouuuuc'
    )
    return text.translate(accents)
    
def verify_title(title, search):
    clear_title = remove_accents(title).lower()
    clear_search = remove_accents(search).lower()
    search_keywords = clear_search.split(' ')
    pattern = fr"\b({'|'.join(map(re.escape, search_keywords))})"
    matches = re.findall(pattern, clear_title)
    if len(set(matches)) == len(search_keywords):
        return True

def skip_words(title):
    clear_title = remove_accents(title).lower()
    keywords = ['pc', 'computador', 'kit', 'notebook', 'p/note', 'servidor', 'linux']
    for keyword in keywords:
        if keyword in clear_title:
            return True

def create_df(data, filename, website, columns, export_options):
    data_frame = pd.DataFrame(data, columns=columns)
    data_frame['Price'] = data_frame['Price'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)
    data_frame = data_frame.sort_values(by='Price', ascending=True)
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    data_frame['Price'] = data_frame['Price'].apply(lambda x: locale.currency(x, grouping=True))
    data_frame = data_frame.drop_duplicates()
    if export_options == None:
        data_frame.to_csv(f'{filename.capitalize()} - {website}.csv', index=False)
    else:
        if export_options['csv']:
            data_frame.to_csv(f'{filename.capitalize()} - {website}.csv', index=False)
        if export_options['excel']:
            data_frame.to_excel(f'{filename.capitalize()} - {website}.xlsx', index=False)