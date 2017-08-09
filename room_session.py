# coding: utf-8
import re
import requests
import werobot
from werobot.replies import SuccessReply
from werobot.session.sqlitestorage import SQLiteStorage 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
import urllib.parse
import pandas as pd
session_storage = SQLiteStorage(filename='werobot_session.sqlite3')
robot = werobot.WeRoBot(token='angus', enable_session=True, session_storage=session_storage)

url = 'http://libcal.usc.edu/rooms_acc.php?gid=4490'

def text_menu():
    menu = '''Please Reply the number to use
    Function:
    1. library study room reservation
    2. library hour'''
    return menu


def valid_date_helper():
    main_page = requests.get(url)
    soup = BeautifulSoup(main_page.text,'lxml')
    valid_date = ''
    for item in soup.find_all('select')[0].stripped_strings:
        valid_date += item + '\n'
    return valid_date

def valid_room_helper(date):
    parameters = '&d='+date+'&cap=1'
    new_url = url + parameters
    # print(new_url)
    main_page = requests.get(new_url)
    soup = BeautifulSoup(main_page.text,'lxml')

    room_form = soup.find('form',id = 'roombookingform')
    room_form.find('div',id='s-lc-rm-tc-box').decompose()
    room_form.find_all('fieldset')[-1].decompose()
    for item in room_form.find_all('small'):
        item.decompose()
    for item in room_form.find_all('legend'):
        item.next_sibling.decompose()
    for item in room_form.find_all('a', class_ = "sr-only"):
        item.decompose()
    valid_room_time = ''
    pattern = re.compile('.*?3[A-Z]+.*?')
    for i in room_form.stripped_strings:
        if pattern.search(i):
            valid_room_time += i + '\n'
    return valid_room_time

    # room_form = soup.select('form[id="roombookingform"]')[0]
    # room_form_info = room_form.select('fieldset')
    # valid_room_time = ''
    # i = 0
    # for room in room_form_info:
    #     for item in room.stripped_strings:
    #         if item != 'Capacity: 1' and item != 'Group Study Room' and item != 'Skip to registration form':
    #             valid_room_time += (item + '\n')
    #             break
    # print(valid_room_time)
    # return valid_room_time

def valid_room_slot_helper(date, room):
    parameters = '&d='+date+'&cap=1'
    new_url = url + parameters
    # print(new_url)
    main_page = requests.get(new_url)
    soup = BeautifulSoup(main_page.text,'lxml')

    room_form = soup.find('form',id = 'roombookingform')
    room_form.find('div',id='s-lc-rm-tc-box').decompose()
    room_form.find_all('fieldset')[-1].decompose()
    for item in room_form.find_all('small'):
        item.decompose()
    for item in room_form.find_all('legend'):
        item.next_sibling.decompose()
    for item in room_form.find_all('a', class_ = "sr-only"):
        item.decompose()
    valid_time_slot = ''
    flag = False
    pattern = re.compile('[0-9]+:[0-9][0-9][a|p]m\s-\s[0-9]+:[0-9][0-9][a|p]m')
    pattern2 = re.compile('.*?3[A-Z]+.*?')
    for i in room_form.stripped_strings:
        if pattern2.search(i):
            flag = False
        if '3G' in i and flag==False:
            flag = True
        if flag and pattern.match(i):
            valid_time_slot += i + '\n'
    return valid_time_slot

def book_room_helper(date, room, time, fname, lname, email):

    # Parameters handle
    # Convert 24 Hour to 12 Hour
    time_list = time.split(',')
    for i in range(len(time_list)):
        if int(time_list[i]) >=0 and int(time_list[i]) <12:
            time_list[i] = time_list[i]+':00am -'
        elif  int(time_list[i]) == 12:
            time_list[i] = time_list[i]+':00pm -'
        else:
            time_list[i] = str(int(time_list[i])-12)+':00pm -'

    room = room.upper()
    token = list()
    for item in time_list:
        token.append(room + ' ' + item)



    parameters = '&d='+date+'&cap=1'
    new_url = url + parameters
    main_page = requests.get(new_url)
    soup = BeautifulSoup(main_page.text,'lxml')
    book_room_form = soup.find('form',id = 'roombookingform')

    avail_time_slots = book_room_form.find_all('input',value='60',type='hidden')

    params = list()
    for item in avail_time_slots:
        params.append((item['name'], 60))
        item_content = item.next_sibling
        params.append((item_content['name'],item_content['value']))
        
        if token[0] in item_content['value'] or token[1] in item_content['value']:
            params.append(('sid[]',int(''.join(list(filter(str.isdigit, item['name']))))))

    params.append(('gid',4490))
    params.append(('fname',fname))
    params.append(('lname',lname))
    params.append(('email',email))
    params.append(('qcount',0))
    params.append(('fid',0))

    post_data = urllib.parse.urlencode(params)
    post_url = 'http://libcal.usc.edu/process_roombookings.php?m=booking_mob'
    headers = {
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    'Host':'libcal.usc.edu',
    'Connection':'keep-alive',
    'Accept':"application/json, text/javascript, */*; q=0.01",
    'Origin':'http://libcal.usc.edu',
    'X-Requested-With':'XMLHttpRequest',
    'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36',
    'Referer':'http://libcal.usc.edu/booking/its',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'en,zh-CN;q=0.8,zh;q=0.6'     
    }

    # get_url = 'http://libcal.usc.edu/rooms_acc.php?gid=4490&d=2017-08-05&cap=0'
    rrr = requests.get(url)
    AWSALB_cookies = rrr.cookies['AWSALB']
    lc_rbv = rrr.cookies['lc_rbv']

    # AWSALB_cookies = requests.get(post_url).cookies['AWSALB']
    # cookies_part = "_vwo_uuid_v2=641003E722BA383572EB5960C60479AE|1b62e9dc5791b7d2b6bcad3650c57fac; optimizelyEndUserId=oeu1479493308140r0.28413408277979224; optimizelySegments=%7B%224150957310%22%3A%22false%22%2C%224155974626%22%3A%22search%22%2C%224163194645%22%3A%22gc%22%7D; optimizelyBuckets=%7B%7D; desktopCookie=uschomepage; __utma=185748653.185138458.1479232294.1485728281.1485735202.4; __utmz=185748653.1485735202.4.4.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __hstc=77507402.c99caa907c017d0cd093ec68a08585ce.1485740385320.1485740385320.1485740385320.1; hsfirstvisit=http%3A%2F%2Fexechealthadmin.usc.edu%2Fadmissions|http%3A%2F%2Fwww.bing.com%2Fsearch%3Fq%3Dusc%2520price%2520online%2520requirements%26qs%3Dn%26form%3DQBRE%26sp%3D-1%26pq%3Dusc%2520price%2520online%2520requirements%26sc%3D0-29%26sk%3D%26cvid%3D2AF353EB7C944C87865EBC99354240E1|1485740385314; hubspotutk=c99caa907c017d0cd093ec68a08585ce; __unam=79ac26c-1586b64794e-4522b679-162; _ga=GA1.2.185138458.1479232294; _gid=GA1.2.1893662304.1500247444"
    cookies = "AWSALB=" + AWSALB_cookies
    cookies += "; lc_rbv=" + lc_rbv 
    headers['Cookie'] = cookies
    print('here')
    print(headers['Cookie'])
    print('here2')
    response = requests.post(post_url, data=post_data,headers=headers)
    print(response.text)
    text = BeautifulSoup(response.json()['msg'],'lxml')
    return text.text

def validate_date(date):
    date_list = date.split('-')
    if len(date_list) != 3:
        error = 'The date is not valid, date format is like 2017-7-18\n'
        return (False, error)
    return (True, date)

def library_name_helper():
    html = requests.get('https://libraries.usc.edu/libraries-hours?week=')
    soup = BeautifulSoup(html.text,'lxml')
    table_list = soup.find_all('table')
    lib_hour = pd.read_html(str(table_list[1]))[0]
    reply = ''
    i = 0
    for item in lib_hour['Libraries']:
        reply += 'L'+str(i) +' '+ str(item) + '\n'
        i += 1
    return reply

def library_hour_helper(lib):
    html = requests.get('https://libraries.usc.edu/libraries-hours?week=')
    soup = BeautifulSoup(html.text,'lxml')
    table_list = soup.find_all('table')
    lib_hour = pd.read_html(str(table_list[1]))[0]
    lib_num = int(''.join(list(filter(str.isdigit, lib))))
    reply = ''
    required_lib = lib_hour[lib_num:(lib_num+1)]
    for col in required_lib:
        reply += required_lib[col].name + '  ' + required_lib[col].values[0] + '\n'

    return reply

@robot.subscribe
def subscribe(message):
    return text_menu()

@robot.filter('menu')
def show_menu(message):
    return text_menu()

@robot.filter('1')
def valid_date(message):
    reply = 'The followings are the valid date for room reservation\n'
    reply += 'Reply format is\n'
    reply += '2017-7-20\n'
    reply += valid_date_helper()
    return reply

@robot.filter('2')
def library_name(message):
    return library_name_helper()

@robot.filter(re.compile('[L|l][0-9]+'))
def library_hour(message):
    return library_hour_helper(message.content)

@robot.filter(re.compile('[a-zA-Z]+.*?[a-zA-Z]+.*?[a-zA-Z0-9]+@.*?usc.edu.*?',re.S))
def book_room(message,session):
    # reply = SuccessReply(message=message, content='success')
    message_list = message.content.split(' ')
    # date = message_list[2]
    # room = message_list[4]
    # time = message_list[6]
    fname = message_list[0]
    lname = message_list[1]
    email = message_list[-1]
    date = session.get('date','please input date')
    room = session.get('room_num','please input room number')
    time = session.get('start_time1','please input time slot') + ',' + session.get('start_time2','please input time slot')

    return book_room_helper(date, room, time, fname, lname, email)

@robot.filter(re.compile('.*?3[a-zA-Z]+.*?'))
def valid_room_slot(message,session):
    # date_room = message.content.split(',')
    room_num = message.content
    reply = 'The followings are valid time slot of corresponding room\n'
    reply += 'Reply format is\n'
    reply += '12 15(24Hour Format)\n'
    date = session.get('date','Please input date first')
    session['room_num'] = room_num
    # reply += valid_room_slot_helper(date_room[0],date_room[1])
    reply += valid_room_slot_helper(date, room_num)
    return reply


# Input valid date, format year-month-day, 2017-7-18
@robot.filter(re.compile('[0-9]+-[0-9]+-[0-9]+'))
def valid_room(message,session):
    valid, date = validate_date(message.content)
    if not valid:
        return date
    reply = 'The followings are all the valid room number\n'
    reply += 'Reply format is\n'
    reply += 'eg: 3F\n'
    # reply += 'You can copy this and modify the detail\n'
    reply += valid_room_helper(date)
    session['date'] = message.content   
    return reply 

# @robot.filter(re.compile('.*?book.*?date.*?room.*?time.*?fname.*?lname.*?email.*?',re.S))
@robot.filter(re.compile('[0-9]+.*?[0-9]+',re.S))
def time_slot(message, session):
    times = message.content.split(' ')
    session['start_time1'] = times[0]
    session['start_time2'] = times[-1]
    print(times[0])
    print(times[-1])
    reply = 'Now you want to book room for\n'
    reply += 'Date: ' + session.get('date','please input date first') + '\n'
    reply += 'Room: ' + session.get('room_num','please input room number first') + '\n'
    reply += 'Start_Time_Slot: ' + session.get('start_time1','please input time slot') + ' ' + session.get('start_time2','please input time slot') + '\n'
    reply += 'If you confirm the info, please reply your name and email\n'
    reply += 'The reply format is(seperator is space)\n'
    reply += 'firstname lastname test@usc.edu\n'
    reply += 'If you want to change info, please input the correct info accroding to the format\n'
    return reply


@robot.text
def other(message):
    return 'unknown'

robot.run(port=80)