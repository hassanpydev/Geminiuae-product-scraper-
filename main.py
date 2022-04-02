import json
import os
import sqlite3

import requests
import fuzzywuzzy
from bs4 import BeautifulSoup
import threading

lock = threading.RLock()
DATA = {"Ceiling System": []}


def write_json(
        path: os.path = os.getcwd(), name: str = "Undefined", data_file=None
) -> None:
    """Write results into JSON file
    Args:
        name ([str]): [The name of the file]
        data_file ([dict]): The data to be written
        :param data_file: dictionary object to be saved into json file
        :param name:  file name
        :param path: a path refers to current keyword path
    """
    if data_file is None:
        data_file = {}
    try:

        with open(os.path.join(path, f"{name}.json"), "+w") as fp:
            json.dump(data_file, fp, indent=3, sort_keys=True)
            fn = os.path.join(path, f"{name}.json")
    except BaseException as e:
        print(e)


def CallAPI(
        category_name: str, page_number: int, brand_name: str, calculated_page_number=False
) -> dict:
    url = "https://geminiuae.com/{}?page={}&q=Categories-{}&from-xhr".format(
        category_name, page_number, brand_name
    )
    print(url)
    payload = {}
    headers = {
        "Connection": "keep-alive",
        "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://geminiuae.com/12-ceiling-system",
        "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        if calculated_page_number:
            return response.json()
        else:
            print("Request was successful")
            product = response.json()["products"]
            return product
    else:
        print(response.raise_for_status())


def scrapCategories(source):
    soup = BeautifulSoup(source, "html.parser")
    categories = soup.find_all("li", {"class": "level-1 parent"})
    if categories:
        return categories
    else:
        print("No categories found")
        return []


def getAllCategories():
    main_url = "https://geminiuae.com/"

    response = requests.get(main_url)
    if response.status_code == 200:
        categories = scrapCategories(response.text)
        return categories
    else:
        print(response.raise_for_status())
        return None


def getTotalItemsPerCategory(category_data: dict) -> int:
    if isinstance(category_data, dict):
        return int(category_data["pagination"].get("total_items"))
    else:
        raise ValueError("Category must be a dict not a {}".format(type(category_data)))


def connectSqlLite() -> tuple:
    connection = sqlite3.connect("test.sqlite3")
    return connection, connection.cursor()


def productImage(product_url):
    """

    :param product_url:
    :return:
    """
    request = requests.get(product_url)
    if request.status_code == 200:
        soup = BeautifulSoup(request.text, "html.parser")
        img = soup.find_all("ul", {"class": "product-images js-qv-product-images"})
        if img:
            return [src.li.img["src"] for src in img]


def insertProduct(
        product_name, product_desc, product_image, product_url, parent, brand
) -> None:
    """

    :param product_name:
    :param product_desc:
    :param product_image:
    :param product_url:
    :param parent:
    :param brand:
    :return:
    """
    sql_str = f"""
    insert into products (product_name,product_image,product_url,parent,brand) VALUES (
    '{product_name.strip("'")}','{product_image[0].split('/')[-1]}','{product_url.split('/')[-1]}','{parent}','{brand}'
    );"""
    print("Adding product to database")
    connection, cur = connectSqlLite()
    cur.execute(sql_str)
    last_id = cur.lastrowid
    connection.commit()
    return last_id
 

def insertSubCategory(category_id: int, subcategory_name: str) -> str:
    """

    :rtype: str
    """
    # todo check if subcategory exists
    # todo insert subcategory and return id
    # todo insert brands
    # todo insert with parent id
    print(subcategory_name.strip())
    sql_str = f"""
        INSERT INTO sub_category (category_name,parent) VALUES ('{subcategory_name.strip()}', {category_id});
        """
    print("Adding data to database")
    connection, cur = connectSqlLite()
    cur.execute(sql_str)
    last_id = cur.lastrowid
    connection.commit()
    print("Data stored successfully")
    return last_id


def getBrands(url: str):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    brands = [
        "-".join(brand["href"].split("/")[-1].split("-")[1::])
        for brand in soup.select(".category-sub-menu a")
    ]

    return brands


def scrapSubCategories(subcategories, parent):
    for subcategory in subcategories:
        category_name = subcategory["href"].split("/")[-1]
        print(subcategory.span.text)
        current_id = insertSubCategory(
            subcategory_name=subcategory.span.text, category_id=parent
        )
        brands = getBrands(subcategory["href"])
        for brand in brands:
            if brand != 'all-brands':
                print(brand)
                total_items = CallAPI(
                    category_name=category_name,
                    brand_name=brand,
                    calculated_page_number=True,
                    page_number=1,
                )
                print(getTotalItemsPerCategory(total_items))
                for page_number in range(1, getTotalItemsPerCategory(total_items)):
                    products = CallAPI(
                        category_name=category_name, page_number=page_number, brand_name=brand
                    )
                    for product in products:
                        print(product.get("name"))
                        insertProduct(
                            product_name=product.get("name"),
                            product_desc=product.get("description_short"),
                            product_image=productImage(product.get("link")),
                            parent=current_id,
                            product_url=product.get("link"),
                            brand=brand,
                        )


def ScarpAndInsertMainCategory(category_name: str, category_selector) -> None:
    # todo check if category exists
    # todo insert category and return id
    sql_str = f"""
    INSERT INTO maincat (category_name) VALUES ('{category_name}');
    """
    connection, cur = connectSqlLite()
    cur.execute(sql_str)
    print(cur.lastrowid)
    connection.commit()
    scrapSubCategories(category_selector, cur.lastrowid)
    connection.close()


def insertProductPhoto(url: str, product_id):
    """

    :param url:
    :param product_id:
    :return:
    """
    sql_str = f"""
    insert into product_images (url, product_id) values (url,product_id)
    
    """
    connection, cur = connectSqlLite()
    cur.execute(sql_str)
    connection.commit()


t = getAllCategories()
for i in t:
    cleaned_data = i.span.text
    print(cleaned_data)
    ScarpAndInsertMainCategory(cleaned_data, i.select(".level-2 > a"))
    print(len(i.select(".level-2 > a")))

# print(
#     getTotalItemsPerCategory(
#         CallAPI(
#             category_name="13-gypsum-boards",
#             page_number=0,
#             brand_name="all-brands",
#             calculated_page_number=True,
#         )
#     )
# )
