
API_KEY = "2107174924:AAF9QGRVf5cfMZi0wYn4ZtVyj5rCFKb_Jvs"

db_url = "data.db"

create_tables = [
    """create table if not exists users (
    user_id integer primary key,
    cookie text
);""",
    """create table if not exists user_cookies (
    user_id integer primary key,
    cookie text not null
);""",
    """create table if not exists courses (
    id text primary key,
    code text not null,
    title text not null,
    description text
);"""
]

