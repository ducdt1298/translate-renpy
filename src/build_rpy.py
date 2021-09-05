import io

import database


def check_before_merge():
    total_phrase = database.count_phrase()
    total_phrase_done = database.count_phrase_done()
    if total_phrase_done < total_phrase:
        print('Oops, found an error during translation, please relaunch the program to complete the process...')
        return False
    return True


def merge_text(phrases):
    ret = ''
    for p in phrases:
        ret += p.space_before + p.text + p.space_after
    return ret


def merge_dialogue():
    print('---')
    print('Merge all dialogue...')
    count_id = 0
    while True:
        count_id += 1
        dialogue = database.get_dialogue(count_id)
        if not dialogue:
            break
        if dialogue.status == 1:
            continue
        phrases = database.get_all_phrase_by_dialogue(dialogue.id)
        text_merged = merge_text(phrases)
        dialogue_text = ''
        buf = io.StringIO(dialogue.text)
        is_original_line = True
        while True:
            line = buf.readline()
            if not line:
                break
            line_strip = line.strip()
            if line_strip.count('"') >= 2 and line_strip.endswith('"'):
                if not is_original_line:
                    line = line.replace('""', '"{}"'.format(text_merged))
                is_original_line = not is_original_line
            dialogue_text += line
        database.update_dialogue_translated(dialogue.id, dialogue_text)
    database.commit_transtion()
    print("---Done---")


def buid_files():
    print('---')
    print('Building rpy file...')
    list_file = database.get_all_file()
    for file in list_file:
        if file.status == 1:
            continue
        order = 0
        with open(file.path, 'w', encoding='utf-8') as rpy_file:
            while True:
                dialogue_text = database.get_dialogue_text_by_file(
                    file.id, order)
                if dialogue_text is None:
                    break
                rpy_file.write(dialogue_text)
                order += 1
        database.update_file_status(file.id)
    print("---Rpy file building completed---")


def build_rpy_files():
    if not check_before_merge():
        return False
    merge_dialogue()
    buid_files()
    return True
