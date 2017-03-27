# coding=utf-8
import requests
from bs4 import BeautifulSoup


def get():
    s = requests.Session()
    s.headers = {'user-agent': 'Chrome/56.0.2924.87'}
    URL = "http://anhsangsoiduong.vn/danh-sach-thi-sinh.html?page="
    lst_name = []
    for i in range(10):
        res = s.get(URL + str(i + 1))
        bsObj = BeautifulSoup(res.content, 'lxml')
        names_a = bsObj.find('tbody').find_all(
            'a', class_="text-bold no-hover")
        lst_name.extend([name_a.get_text() for name_a in names_a])
    return lst_name
