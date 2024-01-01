from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

import time
from datetime import datetime, timedelta
from dateutil import parser
import smtplib
from email.mime.multipart import MIMEMultipart

def scrape_logic():
    def driver_setting():
        service = Service(executable_path='C:\Program Files\Google\Chrome\Application\chromedriver.exe')

        # 实例化对象
        option = ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])  # 开启实验性功能

        # 去除特征值
        option.add_argument("--disable-extensions")
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-gpu')
        option.add_argument('--disable-dev-shm-usage')
        option.add_argument("--disable-blink-features=AutomationControlled")
        # option.add_argument("--headless=new")

        # 实例化谷歌
        driver = webdriver.Chrome(service=service, options=option)

        # 修改get方法
        script = '''object.defineProperty(navigator,'webdriver',{undefinedget: () => undefined})'''
        # execute_cdp_cmd用来执行chrome开发这个工具命令
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})

        return driver


    def flight_selection():
        # Select flight
        tab_text = "Flights"
        flights_tab = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//span[text()='{tab_text}']"))
        )
        flights_tab.click()

        time.sleep(1.6)

        # Select flight type
        flights_type = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//span[text()='{flightTypeChoice}']"))
        )
        flights_type.click()

        time.sleep(1.8)


    def place_choice(choice):
        aria_label = 'Leaving from' if choice == 'departure' else 'Going to'
        id = 'origin' if choice == 'departure' else 'destination'

        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[@aria-label='{aria_label}' and @data-stid='{id}_select-menu-trigger']"))
        )
        button.click()

        time.sleep(1)

        # Send the type in departure/arrival to server
        input_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f"input[id='{id}_select']"))
        )
        input_field.send_keys(departureFrom if choice == 'departure' else arriveAt)

        # Find and output all the pop out departure
        outer_ul = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//ul[@data-stid='{id}_select-results']"))
        )
        # Wait for at least one inner <li> element with data-index attribute to be present
        places = WebDriverWait(outer_ul, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, ".//li[@data-index]"))
        )
        for index, place in enumerate(places[:-1], start=1):
            place_name = place.find_element(By.XPATH, './/span/strong').text
            print(f"{index}: {place_name}")

        choice = input(f"Choose {id} by number")

        # Click the button to confirm the departure/destination
        place_button = driver.find_element(By.XPATH,f"//li[@data-index='{int(choice) - 1}' and .//button]")
        place_button.click()

        time.sleep(2.5)


    def get_future_date():
        while True:
            today_date = datetime.now()
            max_date = today_date + timedelta(days=365)
            # Prompt the user to choose a date
            user_input = input(f"Choose a date e.g '{today_date.strftime('%Y-%m-%d')}': ")

            try:
                chosen_date = parser.parse(user_input)

                # Check if the chosen date is in the future
                if today_date < chosen_date < max_date:
                    formatted_date = chosen_date.strftime('%Y-%m-%d')
                    print(f"Chosen date: {formatted_date}")
                    return formatted_date
                else:
                    print("Please choose a date within the next 12 months.")
            except ValueError:
                print("Invalid date format. Please enter a valid date.")


    def date_choice(flightTypeChoice):
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-stid='uitk-date-selector-input1-default']"))
        )
        button.click()

        print("Type in start date:")
        startDate = get_future_date()

        #check the back date is after start date
        if flightTypeChoice == 'Roundtrip':
            print("Type in back date:")
            while True:
                backDate = get_future_date()
                if backDate > startDate:
                    break
                else:
                    print("Please type in a date after you start date")

        time.sleep(2)
        driver.execute_script(f"document.getElementsByName('EGDSSingleDatePicker-Date-date_form_field')[0].value = '{startDate}';")
        time.sleep(1.5)

        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-stid='apply-date-selector']"))
        )
        button.click()

        time.sleep(2.3)


    def search_button():
        submit_button = driver.find_element(By.XPATH, "//button[@id='search_button']")
        submit_button.click()

        time.sleep(10)

    def find_lowest_price(prices_list):
        # Extract numerical values from each element and convert to integers
        numeric_prices = [int(price.split('$')[1].replace(',', '')) for price in prices_list]

        # Find the index of the minimum value
        min_index = numeric_prices.index(min(numeric_prices))

        # Return the minimum value and its index
        return min_index

    def data_scraping():
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//span[@data-test-id='departure-time']"))
        )

        # departure times
        dep_arrival_times = driver.find_elements(By.XPATH, "//span[@data-test-id='departure-time']")[:10]
        dep_arrival_times_list = [value.text for value in dep_arrival_times]

        # airline name
        airlines = driver.find_elements(By.XPATH, "//div[@data-test-id='flight-operated']")[:10]
        airlines_list = [value.text for value in airlines]

        # durations
        durations_stops = driver.find_elements(By.XPATH, "//div[@data-test-id='journey-duration']")[:10]
        durations_list = [value.text for value in durations_stops]

        # layovers
        layovers = driver.find_elements(By.XPATH, "//div[@data-test-id='layovers']")[:10]
        layovers_list = [value.text for value in layovers]

        # prices
        prices = driver.find_elements(By.XPATH, "//span[@data-stid='' and @class='uitk-lockup-price']")[:10]
        price_list = [value.text for value in prices]

        cheapestIndex = find_lowest_price(price_list)

        #store data
        new_flight_data = {
            'dep_arrival_times': dep_arrival_times_list[cheapestIndex],
            'airlines': airlines_list[cheapestIndex],
            'durations_stops': durations_list[cheapestIndex],
            'layovers': layovers_list[cheapestIndex],
            'prices': price_list[cheapestIndex]
        }

        # Add the new row to the DataFrame
        df.loc[len(df)] = new_flight_data


        for column in df.columns:
            print(f"{column}:")
            print(df[column])
            print("\n")


    def pd_initializer():
        df_columns = ['dep_arrival_times', 'airlines', 'durations_stops', 'layovers', 'prices']
        df = pd.DataFrame(columns=df_columns)
        return df

    def connect_mail(username, password):
        global server
        server = smtplib.SMTP('smtp.outlook.com', 587)
        server.ehlo()
        server.starttls()
        server.login(username, password)

    def create_mag():
        global msg
        msg = f'\nCurrent Chpeast flight:\n\nDeparture and arrival time:{df[len(df)][0]}\nAirline:{df[len(df)][1]}\nFlight duration and stops:{df[len(df)][2]}\nlayovers:{df[len(df)][3]}\nPrice:{df[len(df)][4]}'

    def send_email(msg):
        sendMail = 'xlchen0411@gmail.com'
        toBeSendMail = '2313249827@qq.com'
        global message
        message = MIMEMultipart()
        message['Subject'] = 'Current Cheapest Flight'
        message['From'] = sendMail
        message['to'] = toBeSendMail

        server.sendmail(sendMail,toBeSendMail,msg)


    driver = driver_setting()
    df = pd_initializer()

    try:
        flightTypeChoice = "One-way"
        departureFrom = "toronto"
        arriveAt = "guangzhou"

        driver.get('https://www.expedia.ca/')

        flight_selection()
        place_choice('departure')
        place_choice('destination')

        date_choice(flightTypeChoice)
        search_button()

        time.sleep(15)

        time.sleep(15)

        data_scraping()

        print('end')
        #change date to next 7 days and scraping

        return df

    finally:
        driver.quit()


