from httpx import Client
import random

user_agent = "Mozilla/5.0 Win(dows NT 10.0; Win64; x64 AppleW)ebKit/537.36 KH(TML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"

def get_year_course(c: Client, year: str):
    return c.get(f'https://myplan.uw.edu/plan/api/plan/terms?year={year}')

def make_session(c: Client, referrer='course/#/'): 
    # old_cookie = c.headers['cookie'] 
    res = c.get(f'https://myplan.uw.edu/plan/api/session?referrer={referrer}') 
    return res.headers.get('set-cookie') is not None

def make_session_2(c: Client, referrer='course/#/'):
    res = c.get(f'https://myplan.uw.edu/course/api/session?referrer={referrer}') 
    return res.headers.get('set-cookie') is not None

def get_history_years(c: Client):
    return c.get('https://myplan.uw.edu/plan/api/academicHistory/years')

def search_course(client: Client, query: str):
    def generate_request_id():
        string = '1234567890abcdef'
        random.choice(string)
        output = ''
        output += ''.join([random.choice(string) for i in range(8)])
        output += '-'
        output += ''.join([random.choice(string) for i in range(4)])
        output += '-'
        output += ''.join([random.choice(string) for i in range(4)])
        output += '-'
        output += ''.join([random.choice(string) for i in range(4)])
        output += '-'
        output += ''.join([random.choice(string) for i in range(12)])
        return output
    make_session_2(client, referrer='course/#/courses')

    params = {
        "campus": "seattle",
        "consumerLevel": "UNDERGRADUATE",
        "days": [],
        "endTime": "2230",
        "instructorSearch": False,
        "queryString": query,
        "requestId": generate_request_id(),
        "sectionSearch": True,
        "startTime": "0630",
        "username": "blan2",
    }

    res = client.post('https://myplan.uw.edu/course/api/courses', json=params)
    data = res.json()
    return data


def get_myplan_course_detail(client, code, cousre_id=None):
    # url = "course/api/courses/{code}/details"
    # url = f"https://myplan.uw.edu/" + url
    # url = "course/api/courses/{code}/details?courseId={course_id}"
    make_session_2(client)
    url = f"https://myplan.uw.edu/course/api/courses/{code}/details"
    res = client.get(url)
    return res.json()
