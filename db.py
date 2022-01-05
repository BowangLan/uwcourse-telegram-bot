def item_exist(cursor, table, item_id, id_col='id', fields='*'):
    return cursor.execute(f'select {fields} from {table} where {id_col} = ?;', (item_id,)).fetchall()

def get_user_cookie(cursor, user_id):
    return cursor.execute('select cookie from user_cookies where user_id = ?;', (user_id,)).fetchall()

def update_user_cookie(cursor, user_id, cookie):
    return cursor.execute('update user_cookies set cookie = ? where user_id = ?;', (cookie, user_id))

def add_user_cookie(cursor, user_id, cookie):
    return cursor.execute('insert into user_cookies (user_id, cookie) values (?, ?)', (user_id, cookie))

