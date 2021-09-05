import sqlite3

from model import *

conn = sqlite3.connect('data/data.db', check_same_thread=False)
c = conn.cursor()


def reset_database():
    c.execute('DELETE FROM info')
    c.execute('DELETE FROM phrase')
    c.execute('DELETE FROM dialogue')
    c.execute('DELETE FROM file')
    c.execute('DELETE FROM sqlite_sequence')
    conn.commit()


def add_info(path, original_language, into_language):
    c.execute('''
        INSERT INTO info(path, original_language, into_language) 
        VALUES(?, ?, ?)
    ''', (path, original_language, into_language,))


def get_info():
    sql = '''
    SELECT path, original_language, into_language
    FROM info
    WHERE
        id = 1
    '''
    for row in c.execute(sql):
        return Info(
            row[0],
            row[1],
            row[2]
        )
    return None


def add_file(path):
    c.execute('INSERT INTO file(path, status) VALUES(?, 0)', (path,))


def get_all_file():
    list_files = []
    for row in c.execute('SELECT id, path, status FROM file'):
        list_files.append(FileObject(row[0], row[1], row[2]))
    return list_files


def add_dialogue(order, text, file_id):
    c.execute('''
        INSERT INTO dialogue(ord, text, status, file_id) 
        VALUES(?, ?, 0, ?)
    ''', (order, text, file_id,))


def get_dialogue(id):
    sql = '''
        SELECT id, ord, text, status, file_id
        FROM dialogue WHERE id = ?
    '''
    for row in c.execute(sql, (id,)):
        return DialogueObject(
            row[0],
            row[1],
            row[2],
            row[3],
            row[4]
        )
    return None


def add_phrase(order, text, space_before, space_after, need_translate, dialogue_id):
    c.execute('''
        INSERT INTO phrase(ord, text, space_before, space_after, need_translate, status, dialogue_id) 
        VALUES(?, ?, ?, ?, ?, 0, ?)
    ''', (order, text, space_before, space_after, need_translate, dialogue_id))


def get_phrases(limit):
    sql1 = '''
        SELECT id, text, status FROM phrase
        WHERE
            need_translate = 1
            AND status = 0
        ORDER BY id ASC
        LIMIT ?
    '''
    sql2 = '''
        UPDATE phrase
        SET status = 1
        WHERE id = ?
    '''
    phrases = []
    for row in c.execute(sql1, (limit,)):
        phrase = PhraseObject(
            id=row[0],
            ord=None,
            text=row[1],
            space_before=None,
            space_after=None,
            need_translate=None,
            status=row[2],
            dialogue_id=None
        )
        c.execute(sql2, (row[0],))
        phrase.status = 1
        phrases.append(phrase)
    return phrases


def update_phrase_translated(id, text):
    c.execute('''
        UPDATE phrase
        SET 
            text = ?,
            status = 2
        WHERE id = ?
    ''', (text, id,))


def update_phrase_not_translated(id):
    c.execute('''
        UPDATE phrase
        SET 
            status = 0
        WHERE id = ?
    ''', (id,))


def count_phrase():
    sql = '''
        SELECT COUNT(id)
        FROM phrase
        WHERE
            need_translate = 1
    '''
    for row in c.execute(sql):
        return row[0]
    return None


def count_phrase_done():
    sql = '''
        SELECT COUNT(id)
        FROM phrase
        WHERE
            need_translate = 1
            AND status = 2
    '''
    for row in c.execute(sql):
        return row[0]
    return None


def reset_phrase_status():
    c.execute('''
        UPDATE phrase
        SET status = 0
        WHERE status = 1
    ''')


def get_all_phrase_by_dialogue(id):
    sql = '''
        SELECT text, space_before, space_after
        FROM phrase
        WHERE
            dialogue_id = ?
        ORDER BY ord ASC
    '''
    phrases = []
    for row in c.execute(sql, (id,)):
        phrases.append(PhraseObject(
            id=None,
            ord=None,
            text=row[0],
            space_before=row[1],
            space_after=row[2],
            need_translate=None,
            status=None,
            dialogue_id=None
        ))
    return phrases


def update_dialogue_translated(id, text):
    c.execute('''
        UPDATE dialogue
        SET 
            text = ?,
            status = 1
        WHERE id = ?
    ''', (text, id,))


def get_dialogue_text_by_file(id, ord):
    sql = '''
        SELECT text FROM dialogue
        WHERE
            file_id = ?
            AND ord = ?
    '''
    for row in c.execute(sql, (id, ord,)):
        return row[0]
    return None


def update_file_status(id):
    c.execute('''
        UPDATE file
        SET status = 1
        WHERE id = ?
    ''', (id,))


def commit_transtion():
    conn.commit()
