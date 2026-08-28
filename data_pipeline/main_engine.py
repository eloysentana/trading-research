from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SYMBOLS_FOLDER = BASE_DIR / 'symbols folder'
DRIVERS_DIR = BASE_DIR / 'drivers'
TEMP_DIR = BASE_DIR / 'Temp_files'
DATASETS_DIR = BASE_DIR.parent / 'datasets' / 'yearly2'


def initiate_data_collector(year1, year2):
    import os
    os.system('cls')

    def update_symbols_files():
        '''
        Creates a csv file with 'Symbol,Name,Last Sale,Net Change,% Change,Market Cap,Country,IPO Year,Volume,Sector,Industry'
        Then it sorts it in descendent order by Market Cap, and stores the ordered file in 'symbols folder/sorted_symbols',
        while leaving the original one in 'symbols folder/nasdaq_screener_nnnnnnnnnnnnn.csv' (the exact filename
        changes because of nasdaq's naming system).
        Each time this function is called, it deletes both previous csv files and updates them by downloading a new one and sorting it

        Example of Raw (unordered) csv file from nasdaq.com:
            Symbol,Name,Last Sale,Net Change,% Change,Market Cap,Country,IPO Year,Volume,Sector,Industry
            A,Agilent Technologies Inc. Common Stock,$149.25,0.24,0.161%,44188751970.00,United States,1999,111202,Industrials,Electrical Products
            AA,Alcoa Corporation Common Stock ,$43.96,0.11,0.251%,7778157773.00,,2016,362857,Industrials,Metal Fabrications
            AAC,Ares Acquisition Corporation Class A Ordinary Shares,$10.07,-0.01,-0.099%,1258750000.00,,2021,57312,Finance,Business Services
            AACG,ATA Creativity Global American Depositary Shares,$1.47,0.02,1.379%,46124072.00,China,2008,1263,Consumer Discretionary,Service to the Health Industry

        Example of Sorted (by Market Cap) csv file in 'symbols folder/sorted_symbols':
            Symbol,Name,Last Sale,Net Change,% Change,Market Cap,Country,IPO Year,Volume,Sector,Industry
            AAPL,Apple Inc. Common Stock,$131.20,-1.03,-0.779%,2274659008000.0,United States,1980.0,18784603,Technology,Computer Manufacturing
            MSFT,Microsoft Corporation Common Stock,$237.22,-0.97,-0.407%,1768350119220.0,United States,1986.0,6783853,Technology,Computer Software: Prepackaged Software
            GOOG,Alphabet Inc. Class C Capital Stock,$89.464,1.204,1.364%,1157932552000.0,United States,2004.0,4752243,Technology,Internet and Information Services
            GOOGL,Alphabet Inc. Class A Common Stock,$88.98,1.22,1.39%,1151668140000.0,United States,2004.0,6047038,Technology,Internet and Information Services
            AMZN,Amazon.com Inc. Common Stock,$84.18,0.39,0.465%,856690448676.0,United States,1997.0,14765237,Consumer Discretionary,Catalog/Specialty Distribution

        '''
        import shutil
        from time import sleep
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from webdriver_manager.chrome import ChromeDriverManager  # library to automatically download the newest version of chromedriver.exe

        try:  # first we get the list of all US tickers
            chrome_options = webdriver.ChromeOptions()  # setting up the browser
            SYMBOLS_FOLDER.mkdir(parents=True, exist_ok=True)
            prefs = {'download.default_directory': str(SYMBOLS_FOLDER)}  # where we are going to store the downloaded data file (csv file)
            chrome_options.add_experimental_option('prefs', prefs)
            browser = webdriver.Chrome(
                ChromeDriverManager(path=str(DRIVERS_DIR)).install(),
                chrome_options=chrome_options)

            symbols_link = 'https://www.nasdaq.com/market-activity/stocks/screener'  # getting to the nasdaq's webpage

            while True:  # find the 'accept cookies' element no matter what
                try:
                    browser.get(symbols_link)
                    sleep(3)  # giving chrome some time to load the page...
                    browser.implicitly_wait(5)
                    accept_cookies = browser.find_element(By.XPATH, '/html/body/div[10]/div[2]/div/div/div[2]/div/div/button')
                    accept_cookies.click()
                except Exception as unable_to_find_elem:
                    print(f'\n\t*ERROR: {unable_to_find_elem}')
                    print('Trying with alternative buttons...')
                    try:
                        show_purpose = browser.find_element(By.XPATH, '/html/body/div[10]/div[2]/div/div/div[2]/div/button')
                        show_purpose.click()
                        sleep(1)
                        allow_all = browser.find_element(By.XPATH, '/html/body/div[10]/div[3]/div[2]/button')
                        allow_all.click()
                    except Exception as second_try:
                        print(f'*ERROR RETRYING: {second_try}')
                    else:
                        break
                    sleep(3)  # giving chrome some time to load the page...
                else:
                    print('Cookie button detected')
                    print('Cookie button clicked')
                    break

            sleep(1)
            download_csv = browser.find_element(By.XPATH, '/html/body/div[2]/div/main/div[2]/article/div[3]/div[1]/div/div/div[3]/div[2]/div[2]/div/button')
            print('CSV Button detected')
            shutil.rmtree(SYMBOLS_FOLDER)  # remove the previous folder containing the old symbols file
            print('Old folder deleted')
            SYMBOLS_FOLDER.mkdir(parents=True)
            print('New folder created')
            download_csv.click()  # download the csv file
            print('CSV Button Clicked')
            sleep(3)
            browser.quit()  # close browser

        except Exception as exc:
            print(f'\n\t**ERROR IN SYMBOLS LINK: {exc}')
            quit()

        def sort_symbols(folder_path, name):
            '''
            folder_path: parent directory
            name: name of the new sorted file
            '''
            from os import listdir
            unsorted_file = folder_path / listdir(folder_path)[0]
            import pandas as pd
            reader = pd.read_csv(unsorted_file)
            sorted_df = reader.sort_values(by=["Market Cap"], ascending=False)
            sorted_df.to_csv(folder_path / name, index=False)

        sort_symbols(SYMBOLS_FOLDER, 'sorted_symbols')

    def get_symbols(sorted_symbols_path=None):
        '''
        Returns a list with the n top symbols by market cap, being n=row_limit
        Example of outcome: ['AAPL', 'MSFT', 'GOOG', 'GOOGL', 'AMZN']
        '''
        import csv

        sorted_symbols_path = sorted_symbols_path or (SYMBOLS_FOLDER / 'sorted_symbols')
        while True:
            try:
                # row_limit = int(input('Introduce the number of companies you want to download (-1 for all): '))
                row_limit = 150
                break
            except:
                print('An ERROR occurred setting row_limit, TRY AGAIN (Ctrl+C to stop the script)')

        with open(sorted_symbols_path, 'r') as fsorted:
            reader = csv.reader(fsorted)
            next(reader)
            data = list(reader)
            final = [row[0] for row in data[0:row_limit]]
            print(final)
            return final

    def download_files_to_temp(symbols, temp_path=None, period1='1356220800', period2='1664726516'):
        '''
        symbols: Something like ['AAPL', 'MSFT', 'GOOG', 'GOOGL', 'AMZN']
        period1: First bar date in epoch format
        period2: Last bar date in epoch format
        '''
        import os
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager  # library to automatically download the newest version of chromedriver.exe
        from time import sleep
        from os.path import isfile, join

        temp_path = temp_path or TEMP_DIR
        chrome_options = webdriver.ChromeOptions()  # setting up the browser
        temp_path.mkdir(parents=True, exist_ok=True)
        prefs = {'download.default_directory': str(temp_path)}  # where we are going to store the downloaded data files (csv files)
        chrome_options.add_experimental_option('prefs', prefs)
        browser = webdriver.Chrome(
            ChromeDriverManager(path=str(DRIVERS_DIR)).install(),
            chrome_options=chrome_options)
        prev_len = 0
        unsuccessful = []
        idx = 0
        for ticker in symbols:
            idx += 1
            ticker = ticker.replace('/', '-')
            n = 4
            while n != 1:
                n -= 1
                browser.get(f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval=1d&events=history')
                sleep(0.5)
                new_len = len([f for f in os.listdir(temp_path) if isfile(join(temp_path, f))])
                if prev_len < new_len:
                    prev_len = new_len
                    print(f'{idx}: {ticker} DOWNLOADED')
                    break
                else:
                    print(f'COULD NOT DOWNLOAD {ticker}, {4-n}')
            else:
                print(f'{idx}: {ticker} COULD NOT BE DOWNLOADED')
                unsuccessful.append(ticker)
        if len(unsuccessful) > 0:
            print(f'\n{unsuccessful} COULD NOT BE DOWNLOADED')

    def copy_files_to_def(src_dir=None):
        '''
        To be able to copy the files independently of downloading them,
        we set this function aside from the download step
        '''
        import shutil

        src_dir = src_dir or TEMP_DIR
        def_path = DATASETS_DIR / f'{year1}to{year2}'  # where the final files end up
        try:
            shutil.rmtree(def_path)
        except OSError:
            print('No preexistent path - nice!')

        shutil.copytree(src_dir, def_path)  # creates a new directory def_path and copies all the files
        if len(os.listdir(src_dir)) == len(os.listdir(def_path)):
            shutil.rmtree(src_dir)  # remove the temporary directory after its files have been copied to the final folder
        else:
            print('ERROR WHILE COPYING FILES')

    # update_symbols_files()

    symbols = get_symbols()

    def date_to_epoch(num):
        import datetime
        import calendar
        if num == 1:
            year = year1
        if num == 2:
            year = year2
        t = datetime.datetime(year, 1, 1, 0, 0, 0)
        return calendar.timegm(t.timetuple())

    period1 = date_to_epoch(1)
    period2 = date_to_epoch(2)

    download_files_to_temp(symbols=symbols, period1=period1, period2=period2)  # first we download the files and store them in a temporary folder
    copy_files_to_def()  # then we copy them to their final location, to avoid deleting old files before newer ones are safely downloaded


if __name__ == '__main__':
    for y in range(2011, 2021):
        initiate_data_collector(y, y + 2)
