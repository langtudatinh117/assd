#!/usr/bin/python
# coding=utf-8
import requests
import string
import random
from bs4 import BeautifulSoup
from pymongo import MongoClient
import name
import re
import json
from collections import Counter
import ast
import time

lst_name = name.get()
###########################################
client = MongoClient("ds023408.mlab.com", 23408)
db = client['anhsang']
db.authenticate('daoan', '0903293343')
account = db['acc']
vong1_2 = db['vong1_2']
vong3 = db['vong3_2']
##########################################

s = requests.Session()
s.headers = {'user-agent': 'Chrome/56.0.2924.87'}


def id_generator(size=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_token():
    URL = "http://anhsangsoiduong.vn"
    res = s.get(URL)
    bsObj = BeautifulSoup(res.content, 'lxml')
    token = bsObj.find('input', attrs={"name": "_csrf"})['value']
    return token


def reg(token=get_token()):
    logout()
    URL = "http://anhsangsoiduong.vn/dang-ky.html"
    id_user_pass = id_generator()
    body = {
        "_csrf": token, "RegisterForm[username]": id_user_pass,
        "RegisterForm[password]": id_user_pass,
        "RegisterForm[passwordReType]": id_user_pass,
        "RegisterForm[phone]": ""
    }
    res = s.post(URL, data=body)
    if res.status_code == 200:
        return id_user_pass
    else:
        return False


def logout(token=get_token()):
    URL = "http://anhsangsoiduong.vn/dang-xuat.html"
    res = s.post(URL, data={"_csrf": token})
    if res.status_code == 200:
        return True
    else:
        return False


def login(user, password, token=get_token()):
    logout()
    URL = "http://anhsangsoiduong.vn/dang-nhap.html"
    body = {
        "_csrf": token, "LoginForm[username]": user,
        "LoginForm[password]:": password,
        "LoginForm[rememberMe]": "0",
        "LoginForm[rememberMe]": "1"
    }
    res = s.post(URL, data=body)
    if res.status_code == 200:
        return True
    else:
        return False


def get_all_city_id():
    URL = "http://anhsangsoiduong.vn/danh-sach-ket-qua.html?round_id=1"
    try:
        res = s.get(URL)
    except:
        get_all_city_id()
    if res.status_code == 200:
        bsObj = BeautifulSoup(res.content, 'lxml')
        city_id_ops = bsObj.find(
            'select', attrs={
                "id": "city_id"
            }).find_all('option')
        lst_city_id = [city_id_op['value'] for city_id_op in city_id_ops]
        del lst_city_id[0]
        return lst_city_id
    else:
        return False


def get_school(city_id):
    URL = "http://anhsangsoiduong.vn/danh-sach-ket-qua.html?round_id=1&city_id=" + city_id
    try:
        res = s.get(URL)
    except:
        get_school(city_id)
    if res.status_code == 200:
        bsObj = BeautifulSoup(res.content, 'lxml')
        school_id_ops = bsObj.find(
            'select', attrs={
                "id": "school_id"
            }).find_all('option')
        lst_school_id = [school_id_op['value']
                         for school_id_op in school_id_ops]
        del lst_school_id[0]
        return lst_school_id
    else:
        return False


def update_info(token=get_token()):
    URL = "http://anhsangsoiduong.vn/user/user/update-profile-assd"
    hoten = random.choice(lst_name)
    gioitinh = 'male'
    ngaysinh = "-".join(
        str(e) for e in [random.randrange(1994, 1999, 1), random.randrange(1, 12, 1), random.randrange(1, 28, 1)])
    cmt = ''.join(random.choice(string.digits) for _ in range(10))
    phone = '09' + ''.join(random.choice(string.digits) for _ in range(8))
    email = id_generator(8) + '@gmail.com'
    city = random.choice(get_all_city_id())
    school_id = random.choice(get_school(city))
    ma_sv = ''.join(random.choice(string.digits) for _ in range(6))
    body = {"_csrf": token, "UpdateInfoFormASSD[full_name]": hoten, "UpdateInfoFormASSD[gender]": gioitinh,
            "UpdateInfoFormASSD[birthday]": ngaysinh,
            "UpdateInfoFormASSD[cmt]": cmt, "UpdateInfoFormASSD[phone]": phone,
            "UpdateInfoFormASSD[email]": email, "UpdateInfoFormASSD[city_id]": city,
            "UpdateInfoFormASSD[school_id]": school_id, "UpdateInfoFormASSD[ma_sv]": ma_sv,
            "UpdateInfoFormASSD[khoa]": school_id, "UpdateInfoFormASSD[lop]": ma_sv}
    res = s.post(URL, data=body)
    if res.status_code == 200:
        return True
    else:
        return False


def save_acc():
    try:
        user_and_pass = reg()
        if (update_info() and user_and_pass):
            account.insert_one({'acc': user_and_pass})
            logout()
    except:
        save_acc()
    else:
        return True


def get_list_acc():
    return [acc['acc'] for acc in account.find()]


def get_game_token(user, password):
    URL = "http://anhsangsoiduong.vn/assd/exam/play-exam"
    logout()
    login(user, password)
    res = s.get(URL)
    bsObj = BeautifulSoup(res.content, 'lxml')
    token = bsObj.find('iframe').attrs['src']
    p = re.compile("token=(.*)&link")
    return "".join(p.findall(token))


def get_port_game(game_token):
    URL = "http://anhsangsoiduong.vn/files/game_assd/html5/index.php?game_token=" + game_token
    res = s.get(URL)
    bsObj = BeautifulSoup(res.content, 'lxml')
    port = bsObj.find('input', attrs={"id": "ip_port"}).attrs['value']
    return port + "?method="


def startGame(URL, game_token):
    return s.get(URL + 'start&token=' + game_token + '&type=2').content


def getQues(URL, game_token):
    ques = s.get(URL + 'get_ques&token=' + game_token)
    ans = json.loads(ques.content)['data']['ans']
    data = {"ques": json.loads(ques.content)['data']['ques'], "ans": [
        ans[0], ans[1], ans[2], ans[3]]}
    return data


def getAns(URL, game_token, ans_=0):
    ans = s.get(URL + 'ans_ques&token=' + game_token + '&ans=' + str(ans_))
    return json.loads(ans.content)['data']


def getQAndA(URL, game_token):
    Quiz = getQues(URL, game_token)
    Quiz['ans'] = Quiz['ans'][int(getAns(URL, game_token)['ans'])]
    return Quiz


def continueGame(URL, game_token):
    s.get(URL + 'continue&token=' + game_token)


def saveDB(q):
    doc = vong1_2.find_one({'ques': q['ques']})
    if doc is None:
        vong1_2.insert_one(q)
        return True


def get_q_vong3(URL, game_token):
    return s.get(URL + 'get_ques&token=' + game_token)


def post_ans_12(URL, game_token):
    for num in range(0, 20):
        ques_and_ans = json.loads(s.get(URL + 'get_ques&token=' + game_token).content)['data']
        ## find in database
        doc = vong1_2.find_one({'ques': ques_and_ans['ques']})
        # time.sleep(5)
        if doc is not None:
            ans_ = ques_and_ans['ans'].index(doc['ans'])
            print getAns(URL, game_token, ans_)
        else:
            print getAns(URL, game_token)


def findAns_and_save(user):
    game_token = get_game_token(user, user)
    print (game_token)
    URL = get_port_game(game_token)
    print (URL)
    isWork = startGame(URL, game_token)
    if json.loads(isWork)['code'] == 9:
        return False
    new = 0
    for num in range(0, 20):
        try:
            quiz = getQAndA(URL, game_token)
            if saveDB(quiz):
                new += 1
        except:
            continue

    continueGame(URL, game_token)
    for num1 in range(0, 20):
        try:
            quiz = getQAndA(URL, game_token)
            if saveDB(quiz):
                new += 1
        except:
            continue
    print(new)
    continueGame(URL, game_token)
    ques = get_q_vong3(URL, game_token)
    try:
        aList = json.loads(ques.content)['data']['a']
        bList = json.loads(ques.content)['data']['b']
        for item in aList:
            doc = vong3.find_one({"a": item})
            if doc is None:
                vong3.insert_one({"a": item, "b": str(dict(Counter(bList)))})
            else:
                bTrongDB = ast.literal_eval(doc['b'])
                for bItem in bList:
                    if bItem in bTrongDB:
                        bTrongDB[bItem] = int(bTrongDB[bItem]) + 1
                vong3.update({"a": item}, {'$set': {'b': str(bTrongDB)}})
    except:
        print ("loi")
    finally:
        s = requests.Session()
        s.headers = {'user-agent': 'Chrome/56.0.2924.87'}


def do_it(user, password):
    game_token = get_game_token(user, password)
    URL = get_port_game(game_token)
    isWork = startGame(URL, game_token)
    print isWork
    if json.loads(isWork)['code'] == 9:
        return False
    post_ans_12(URL, game_token)
    continueGame(URL, game_token)
    post_ans_12(URL, game_token)
    continueGame(URL, game_token)
    ques = s.get(URL + 'get_ques&token=' + game_token)
    aList = json.loads(ques.content)['data']['a'][:15]
    bList = json.loads(ques.content)['data']['b']
    result_vong_3 = []
    for item in aList:
        doc = vong3.find_one({"a": item})
        if doc is not None:
            bTrongDB = ast.literal_eval(doc['b'])
            result = list(filter(lambda x: bTrongDB[x] == max(bTrongDB.values()), bTrongDB))
            for item_b in bList:
                if item_b in result:
                    result_vong_3.append(str(bList.index(item_b)))
    print result_vong_3
    time.sleep(60)
    post_vong_3 = s.get(URL + 'ans_v3&token=' + game_token + '&ans=' + ",".join(result_vong_3))
    print post_vong_3.content


list_acc = get_list_acc()

for acc_ne in list_acc:
    try:
        findAns_and_save(acc_ne)
    except:
        continue

# number_acc = 0
# while True:
#     if save_acc():
#         number_acc += 1
#         print number_acc

# findAns_and_save("yl288vw2")
#
# print reg()
# update_info()


# do_it('tienanhduong94', 'tienanhduong94')
