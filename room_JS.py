# coding: utf-8
import re
import requests
import werobot
from werobot.replies import SuccessReply
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
robot = werobot.WeRoBot(token='angus', enable_session=False)

url = 'http://libcal.usc.edu/rooms_acc.php?gid=4490'

def text_menu():
    menu = '''
    Function:
    1. library study room reservation
    '''
    return menu


def valid_date_helper():
    main_page = requests.get(url)
    soup = BeautifulSoup(main_page.text,'lxml')
    valid_date = ''
    for item in soup.findAll('select')[0].stripped_strings:
        valid_date += item + '\n'
    return valid_date

def valid_room_helper(date):
    parameters = '&d='+date+'&cap=1'
    new_url = url + parameters
    print(new_url)
    main_page = requests.get(new_url)
    soup = BeautifulSoup(main_page.text,'lxml')
    room_form = soup.select('form[id="roombookingform"]')[0]
    room_form_info = room_form.select('fieldset')
    valid_room_time = ''
    i = 0
    for room in room_form_info:
        for item in room.stripped_strings:
            if item != 'Capacity: 1' and item != 'Group Study Room' and item != 'Skip to registration form':
                valid_room_time += (item + '\n')
                break
    print(valid_room_time)
    return valid_room_time

def book_room_helper(date, room, time, fname, lname, email):
    # driver = webdriver.PhantomJS()
    driver = webdriver.Chrome('E:\chromedriver_win32\chromedriver.exe')
    parameters = '&d='+date+'&cap=1'
    new_url = url + parameters
    driver.get(new_url)
    room = room.upper()
    time_list = time.split(',')
    period = 2
    if time_list[0] == time_list[-1]:
        period = 1
    for i in range(len(time_list)):
        if int(time_list[i]) >=0 and int(time_list[i]) <12:
            time_list[i] = time_list[i]+':00am -'
        elif  int(time_list[i]) == 12:
            time_list[i] = time_list[i]+':00pm -'
        else:
            time_list[i] = str(int(time_list[i])-12)+':00pm -'

    while period >0:
        option = driver.find_element_by_xpath("//h2[contains(text(), '%s')]/parent::*/parent::*/*[contains(@class,'checkbox')]/self::*[contains(.,'%s')]/child::label" %(room, time_list[2-period]))
        option.click()
        period -= 1

    first_name = driver.find_element_by_id('fname')
    first_name.send_keys(fname)
    last_name = driver.find_element_by_id('lname')
    last_name.send_keys(lname)
    email_field = driver.find_element_by_id('email')
    email_field.send_keys(email)
    submit = driver.find_element_by_id('s-lc-rm-ac-but')
    submit.click()
    return 'successful, plz check your email'

def validate_date(date):
    date_list = date.split('-')
    if len(date_list) != 3:
        error = 'The date is not valid, date format is like 2017-7-18\n'
        return (False, error)
    return (True, date)

@robot.subscribe
def subscribe(message):
    return text_menu()

@robot.filter('menu')
def show_menu(message):
    return text_menu()

@robot.filter('1')
def valid_date(message):
    return valid_date_helper()


@robot.filter(re.compile('.*?book.*?date.*?room.*?time.*?fname.*?lname.*?email.*?'))
def book_room(message):
    reply = SuccessReply(message=message, content='success')
    message_list = message.content.split(' ')
    date = message_list[2]
    room = message_list[4]
    time = message_list[6]
    fname = message_list[8]
    lname = message_list[10]
    email = message_list[-1]
    print(date)
    print(room)
    print(time)
    print(fname)
    print(lname)
    print(email)
    # valid, date = validate_date(date)
    # if not valid:
    #     return date
    # year = date[0]
    # month = date[1]
    # day = date[-1]

    book_room_helper(date, room, time, fname, lname, email)

# Input valid date, format year-month-day, 2017-7-18
@robot.filter(re.compile('.*?-*?-.*?'))
def valid_room(message):
    valid, date = validate_date(message.content)
    if not valid:
        return date
    return valid_room_helper(date)    


@robot.text
def other(message):
    return 'unknown'

robot.run(port=80)