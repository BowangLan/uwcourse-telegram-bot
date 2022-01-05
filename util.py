import httpx
import sqlite3
import time
from config import *
from db import item_exist

def create_connection():
    try:
        conn = sqlite3.connect('data.db')
        return conn
    except e as Exception:
        print(e)
        return False

def db_init():
    conn = create_connection()
    cursor = conn.cursor()
    for t in create_tables:
        cursor.execute(t)
    cursor.close()
    conn.close()

def init_client(cookie=None):
    c = httpx.Client()
    c.headers.update({
        'cookie': cookie,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        })
    return c

def with_client(func):
    def wrapper(*args, **kwargs):
        client = httpx.Client()
        client.headers.update({
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            })
        res = func(*args, client=client, **kwargs)
        client.close()
        return res
    return wrapper


def with_db(func):
    def wrapper(*args, **kwargs):
        conn = create_connection()
        cursor = conn.cursor()
        res = func(*args, conn=conn, cursor=cursor, **kwargs)
        cursor.close()
        conn.close()
        return res
    return wrapper

# def with_user(func):
    # def wrapper():

def escape_text(text):
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for ec in escape_chars:
        text = text.replace(ec, '\\'+ec)
    return text

@with_client
@with_db
def get_courses(conn=None, cursor=None, client=None):
    url = "https://prereqmap.uw.edu/api/course_typeahead"
    res = client.get(url)
    data = res.json()
    insert_count = 0
    tic = time.time()
    for c in data[:]:
        temp = c.split(': ')
        code = temp[0]
        title = ': '.join(temp)
        temp = item_exist(cursor, 'courses', c)
        if temp:
            print(f'{c} already exists')
            print(temp)
            continue
        cursor.execute(
            'insert into courses (id, code, title) values (?, ?, ?)',
            (c, code, title)
        )
        conn.commit() 
        print('Course inserted:', c)
        insert_count += 1
    duration = round(time.time() - tic, 2)
    print(f'{insert_count} course inserted in {duration} seconds')


@with_client
@with_db
def get_course_details(conn=None, cursor=None, client: httpx.Client=None):
    def update(code):
        url = "https://prereqmap.uw.edu/api/course/" + code
        res = client.get(url)
        data = res.json()
        description = data.get('course_description') or ''
        cursor.execute(
            'update courses set description = ? where code = ?;', 
            (description, code)
        )
        conn.commit()
        print(f'Course description {code} updated')
    courses = cursor.execute('select code from courses where description is null;').fetchall()
    # print('Course count:', len(courses))

    count = 0
    tic = time.time()
    for c in courses:
        code = c[0]
        d = cursor.execute('select description from courses where code = ?;', (code,)).fetchall()
        if d[0][0]:
            print(f'Course {code} description already exists: {d[0][0]}')
            continue
        try:
            update(code)
        except Exception as e:
            print('Error!')
            print(e)
            continue
        count += 0
    duration = round(time.time() - tic, 2)
    print(f'{count} course description added in {duration} seconds')

