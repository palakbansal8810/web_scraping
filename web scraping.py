from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
import re


term_to_search = input("Name of the medicine to search:-")
tata1mg_products = {}
apollo_products = {}
pharmeasy_products = {}


def get_webdriver(options=None):
    browsers = [
        (webdriver.Edge, EdgeOptions),
        (webdriver.Chrome, ChromeOptions),
        (webdriver.Firefox, FirefoxOptions),
        (webdriver.Safari, None),  # Safari does not require additional options
        (webdriver.Ie, None),  # Internet Explorer does not require additional options
    ]

    for browser, options_class in browsers:
        try:
            options = options_class()
            options.add_argument("--headless")

            if browser == webdriver.Chrome:
                options.use_chromium = True

            driver = browser(options=options)
            return driver, options
        except WebDriverException:
            continue
    raise WebDriverException("No suitable web browser found")


def parse_tata1mg_products():
    global tata1mg_products
    driver,options=get_webdriver()
    url = f"https://www.1mg.com/search/all?name={term_to_search}"

    driver.get(url)

    wait = WebDriverWait(driver, 10)
    price_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='style__price-tag___']")))

    product_name_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='style__product-description___']")))

    product_description = []
    for product_name_element in product_name_elements:
        try:
            text = (product_name_element.text.splitlines()[1]).replace('\n',' ')
            product_description.append(text)
        except IndexError:
            product_description.append("No description available")

    product_links=[]
    try:
        product_boxes =WebDriverWait(driver,5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='col-xs-12 style__container___cTDz0']")))
        for product_box in product_boxes:
            product_link_element = product_box.find_element(By.CSS_SELECTOR, "a")
            product_link = product_link_element.get_attribute("href") if product_link_element else ""
            product_links.append(product_link)
    except:
        for product_name_element in product_name_elements:
            product_links.append(f"https://www.1mg.com/search/all?name={term_to_search}")


    counter=0
    tata1mg_products = {}
    for price_element, product_name_element, description,product_link in zip(price_elements, product_name_elements, product_description,product_links):
        split = product_name_element.text.splitlines()
        product_name = split[0]

        tata1mg_products[product_name.strip()] = {
            "description": description,
            "price": price_element.text.strip("MRP₹").strip("₹"),
            "link": product_link,
        }
        counter += 1


def parse_apollo_products():
    global apollo_products
    driver, options = get_webdriver()
    url = f"https://www.apollopharmacy.in/search-medicines/{term_to_search}"

    driver.get(url)

    wait = WebDriverWait(driver, 5)
    price_elements = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div[class*='ProductCard_priceGroup__4D4k0']")
        )
    )

    product_name_elements = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "p[class*='ProductCard_productName__vXoqs']")
        )
    )

    product_boxes = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div[class*='ProductCard_pdHeader__ANDKh']")
        )
    )

    product_links = []
    for product_box in product_boxes:
        product_link_element = product_box.find_element(
            By.CSS_SELECTOR, "a[class*='ProductCard_proDesMain__4D8VV']"
        )
        product_link = (
            product_link_element.get_attribute("href") if product_link_element else ""
        )
        product_links.append(product_link)

    product_description = []
    for product_name_element in product_name_elements:
        try:
            text = (product_name_element.text.splitlines()[0]).replace("\n", " ")
            product_description.append(text)
        except IndexError:
            product_description.append("No description available")

    counter = 0
    apollo_products = {}
    for price_element, product_name_element, description, product_link in zip(
        price_elements, product_name_elements, product_description, product_links
    ):
        split = product_name_element.text.splitlines()
        product_name = split[0]

        apollo_products[product_name.strip()] = {
            "description": description,
            "price": re.search("₹([\d.]+)", price_element.text).group(1),
            "link": product_link,
        }
        counter += 1


def parse_pharmeasy_products():
    global pharmeasy_products
    driver, options = get_webdriver()
    url = f"https://pharmeasy.in/search/all?name={term_to_search}"

    driver.get(url)

    wait = WebDriverWait(driver, 5)
    price_elements = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div[class*='ProductCard_ourPrice__yDytt']")
        )
    )

    product_name_elements = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "h1[class*='ProductCard_medicineName__8Ydfq']")
        )
    )

    product_boxes = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div[class*='ProductCard_medicineUnitContainer__cBkHl']")
        )
    )

    product_links = []
    for product_box in product_boxes:
        try:
            product_link_element = product_box.find_element(By.CSS_SELECTOR, "a")
            product_link = (
                product_link_element.get_attribute("href")
                if product_link_element
                else ""
            )
            product_links.append(product_link)
        except:
            product_links.append(
                f"https://pharmeasy.in/search/all?name={term_to_search}"
            )

    product_description = []
    for product_name_element in product_name_elements:
        try:
            text = (product_name_element.text.splitlines()[0]).replace("\n", " ")
            product_description.append(text)
        except IndexError:
            product_description.append("No description available")

    counter = 0
    pharmeasy_products = {}
    for price_element, product_name_element, description, product_link in zip(
        price_elements, product_name_elements, product_description, product_links
    ):
        split = product_name_element.text.splitlines()
        product_name = split[0]

        pharmeasy_products[product_name.strip()] = {
            "description": description,
            "price": price_element.text.strip("MRP₹").strip("₹").strip("*"),
            "link": product_link,
        }
        counter += 1


if __name__ == "__main__":
    parse_apollo_products()
    parse_tata1mg_products()
    parse_pharmeasy_products()
    # print(f"\n\n\nAPOLLO PRODUCTS:{apollo_products},\n\n\nTATA 1MG PRODUCTS:\n\n\n{tata1mg_products},\n\n\n PHARMEASY PRODUCTS:\n\n\n{pharmeasy_products}")
    print(
        f"\n\n\nAPOLLO PRODUCTS:{apollo_products},\n\n\nPHARMEASY PRODUCTS:\n\n\n{pharmeasy_products}"
    )
