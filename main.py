from multiprocessing import Value
from time import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


#nie biore pod uwage ofert z urzedow pracy
driver = webdriver.Chrome('./chromedriver')
company_data_array = []

def log_to_file(file_name, text, variable ):
        with open(file_name, 'a') as f:
            f.write(f"{text}+{variable}")
            f.write('\n')

def login(username: str, password: str) -> None:
    driver.get("https://login.pracuj.pl/")
    email_input = driver.find_element(by=By.CSS_SELECTOR, value="[data-test='input-email']")
    password_input = driver.find_element(by=By.CSS_SELECTOR, value="[data-test='input-password'")
    login_button = driver.find_element(by=By.CSS_SELECTOR, value="[data-test='button-login']")

    email_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()
    driver.implicitly_wait(20)

def cookies_handler():
    cookies_button = driver.find_element(by=By.CSS_SELECTOR, value="[data-test='button-accept-all-in-general']")
    cookies_button.click()

def parse_html(driver: webdriver.Chrome):
    html = driver.page_source
    subsite_html = BeautifulSoup(html, "lxml")
    return subsite_html

def parse_tiles(subsite_html: BeautifulSoup) -> list:
    # list view
    job_tiles = subsite_html('div', {'class': "offer__info"})
    for job_tile in job_tiles:
        tile_link = job_tile.select(".offer-details__title-link")
        if tile_link[0].name == "a":
            job_offer_url = tile_link[0].get('href')
            time.sleep(1)
            driver.get(job_offer_url)
            WebDriverWait(driver=driver, timeout=10).until(EC.url_to_be((job_offer_url)))
            #sprawdzic czy przeszlo na konkretna ofercie jak nie to sprawdzic czy data-test='list-item-offer-location'
            #job offer view
            WebDriverWait(driver=driver, timeout=10).until(EC.any_of(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='anchor-apply']")),EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='offer-archived']"))))
            subsite_html = parse_html(driver=driver)
            driver.implicitly_wait(10)
            try:
                apply_button = subsite_html.select_one("[data-test='anchor-apply']")
            except:
                log_to_file('logs.txt', 'No button anchor-apply found on: ',apply_button)
                # with open('logs.txt', 'a') as f:
                #     f.write(f"'No button anchor-apply found on: ', {apply_button}")
                #     f.write('\n')
            try:
                driver.get(apply_button.get('href'))
            except:
                log_to_file('logs.txt', 'No button href found on: ',apply_button)
                # with open('logs.txt', 'a') as f:
                #     f.write(f"'No button href found on: ', {apply_button}")
                #     f.write('\n')
            driver.implicitly_wait(10)
            #apply form view
            if "system.erecruiter.pl" in driver.current_url:
                #job offer view
                # print("Oferta erekrutera", driver.current_url)
                driver.get(job_offer_url)
                try:
                    #najpierw kliknac u gory w O firmie
                    view_company = driver.find_element(by=By.CSS_SELECTOR, value="[data-test='anchor-view-company']")
                    view_company.click() 
                    #potem kliknac w Zobacz pelny profil albo inne ... 

                    ##Pierwszy rodzaj linkow company
                    try:
                        employer_profile = driver.find_element(by=By.CSS_SELECTOR, value="[data-test='button-employer-link']") 
                        employer_profile.click()
                    ##drugi rodzaj linkow company
                    except:
                        try:
                            print(employer_profile)
                            employer_profile2 = driver.find_element(by=By.CSS_SELECTOR, value="a.ep-profile-link")
                            employer_profile2.click()
                        except:
                            try:
                                employer_profile3 = driver.find_element(by=By.CSS_SELECTOR, value="a.employers-MuiButtonBase-root")
                                employer_profile3.click()
                            except:
                                log_to_file('logs.txt', 'HEYYYYYYY',job_offer_url)
                        

                except:
                    log_to_file('logs.txt', 'No button found on: ',job_offer_url)
                    # with open('logs.txt', 'a') as f:
                    #     f.write(f"'No button found on: ', {job_offer_url}")
                    #     f.write('\n')
                #company details view
                aa_subsite_html = parse_html(driver=driver)
                
                try:
                    company_data = aa_subsite_html.select(".sidebar > .contact-details > div > div.text")
                except:
                    company_data = aa_subsite_html.select("ep-profile-link")
                
                #nazwa-#div.default-box.contact-details > div > div.text > h3
                #addres-#div.default-box.contact-details > div > div.text > [itemprop='address']
                #nip-div.default-box.contact-details > div > div.text > [itemprop='taxID']
                #itp-itd   
                company_data_array.insert(len(company_data_array), company_data)
                # print(company_data_array)
        
        #jak istnieje ('button', {'class': "offer-details__title-link"}) to trzeba wybrac pierwszy offer-regions__label i wbic w jego link ahref
        elif tile_link[0].name == "button":
            tile_button = driver.find_element(by=By.CSS_SELECTOR, value='a')
            tile_button.click()
            tile_link_multiple_cities = job_tile('a', {'class': "offer-regions__label"})[0]
            driver.get(tile_link_multiple_cities.get('href'))
            print("Przebiłem się przez button :)", tile_link_multiple_cities.get('href'))
    return starting_page

login("organ108@o2.pl", "Swierku123!")
cookies_handler()

try:
    WebDriverWait(driver=driver, timeout=10).until(EC.title_contains(("Oferty pracy")))
except:
    driver.get("https://www.pracuj.pl/praca?pn=1")


subsite_html = parse_html(driver=driver)
#czytamy liczbe stron
temp_nr = subsite_html.select("#pagination-under-recommended-offers > div > ul > li:nth-child(6) > a")
page_nr = int(temp_nr[0].next_element.replace('\n', ''))
for starting_page in range(1,page_nr,1):
    print("strona nr: ", starting_page)
    start = time.time()
    parse_tiles(subsite_html)
    end = time.time()
    print(f"dla strony nr {starting_page} wyszło:", (end - start)/60)
