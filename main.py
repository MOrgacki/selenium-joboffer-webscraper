from multiprocessing import Value
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#nie biore pod uwage ofert z urzedow pracy
driver = webdriver.Chrome('./chromedriver')
company_data_array = []

def parse_html(driver: webdriver.Chrome):
    html = driver.page_source
    subsite_html = BeautifulSoup(html, "html5lib")
    return subsite_html

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

def parse_tiles(subsite_html: BeautifulSoup) -> list:
    # list view
    job_tiles = subsite_html('div', {'class': "offer__info"})
    for job_tile in job_tiles:
        tile_link = job_tile('a', {'class': "offer-details__title-link"})
        tile_link_multiple_cities = job_tile('button', {'class': "offer-details__title-link"})
        wspolna_lista = []
        #jak istnieje ('button', {'class': "offer-details__title-link"}) to trzeba wybrac pierwszy offer-regions__label i wbic w jego link ahref
        # for link in tiles_link:
        job_offer_url = tile_link[0].get('href')
        driver.get(job_offer_url)
        # try:
        #     WebDriverWait(driver=driver, timeout=10).until(EC.url_to_be((job_offer_url)))
        # except:
        #     driver.get(job_offer_url)
        WebDriverWait(driver=driver, timeout=10).until(EC.url_to_be((job_offer_url)))
        if job_offer_url == driver.current_url:
            pass
        elif job_tile.find("span",string="lokalizacje"):# czy istnieje w kafelku data-test='list-item-offer-location'                pass
            pass
        else:
            print("Nie pokryty przypadek przejscia na oferte")
        #sprawdzic czy przeszlo na konkretna ofercie jak nie to sprawdzic czy data-test='list-item-offer-location'
        #job offer view
        WebDriverWait(driver=driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='anchor-apply']")))
        subsite_html = parse_html(driver=driver)
        driver.implicitly_wait(10)
        apply_button = subsite_html.select_one("[data-test='anchor-apply']")
        driver.get(apply_button.get('href'))
        driver.implicitly_wait(10)
        #apply form view
        if "system.erecruiter.pl" in driver.current_url:
            #job offer view
            print("Oferta erekrutera", driver.current_url)
            driver.get(job_offer_url)
            try:
                #najpierw kliknac u gory w O firmie
                view_company = driver.find_element(by=By.CSS_SELECTOR, value="[data-test='anchor-view-company']")
                view_company.click() 
                #potem kliknac w Zobacz pelny profil albo inne ... 
                employer_profile = driver.find_element(by=By.CSS_SELECTOR, value="[data-test='button-employer-link']") 
                employer_profile.click()
                print("clicked!")

                #nazwa-#div.default-box.contact-details > div > div.text > h3
                #addres-#div.default-box.contact-details > div > div.text > [itemprop='address']
                #nip-div.default-box.contact-details > div > div.text > [itemprop='taxID']
                #itp-itd
            except:
                print()
                with open('logs.txt', 'w') as f:
                    f.write(f"'No button found on: ', {job_offer_url}")
                    f.write('\n')
            #company details view
            aa_subsite_html = parse_html(driver=driver)
            try:
                company_data = aa_subsite_html.select(".sidebar > .contact-details > div > div.text")
            except:
                company_data = aa_subsite_html.select("ep-profile-link")
                
            company_data_array.insert(len(company_data_array), company_data)
            print(company_data_array)
    return job_tiles

login("organ108@o2.pl", "Swierku123!")
cookies_handler()


try:
    WebDriverWait(driver=driver, timeout=10).until(EC.title_contains(("Oferty pracy")))
except:
    driver.get("https://www.pracuj.pl/praca?pn=1")


subsite_html = parse_html(driver=driver)

parse_tiles(subsite_html)