from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import json
import sqlite3
from typing import List

from soupsieve import match
def connectSqlLite() -> tuple:
    connection = sqlite3.connect("test.sqlite3")
    return connection, connection.cursor()
categories = json.loads(open("sm_categories_id.json").read()).keys()
categories_id = json.loads(open("sm_categories_id.json").read())

def readCategory() -> List[str]:
    """
    read category from sqlite db
    :return:
    """
    sql_str = "select category_name from maincat"
    connection, cur = connectSqlLite()
    cur.execute(sql_str)
    result = cur.fetchall()
    connection.close()
    return [i[0] for i in result]
def readSubCategory() -> List[str]:
    """
    read sub category from sqlite db
    :return:
    """
    sql_str = "select category_name from sub_category"
    connection, cur = connectSqlLite()
    cur.execute(sql_str)
    result = cur.fetchall()
    connection.close()
    return [i[0] for i in result]   
def updateCategory_By_name(category_name: str) -> None:
    """
    update category name
    :param category_name:
    :return:
    """
    sql_str = f"""
    UPDATE maincat SET cat_match = '{category_name}' WHERE category_name = '{category_name}';
    """
    connection, cur = connectSqlLite()
    cur.execute(sql_str)
    connection.commit()
    connection.close()
def findMatch(category_name: str) -> str:
    """
    find match for category name
    :param category_name:
    :return:
    """
    best_match = process.extractOne(category_name, categories)
    return best_match
for category in readCategory():
    print(category)
    best_match = findMatch(category)
    if best_match[1] > 80:
        updateCategory_By_name(categories_id.get(best_match[0]))
        print(best_match)
    else:
        print("No match found")
