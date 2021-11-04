import io
import os
import re

import validators

import database
from model import SpaceObject


def get_rpy_files_in_directory(directory_path):
    for f in os.listdir(directory_path):
        full_path = os.path.join(directory_path, f)
        if os.path.isfile(full_path) and f.endswith('.rpy'):
            database.add_file(full_path)
        elif os.path.isdir(full_path):
            get_rpy_files_in_directory(full_path)


def process_all_file():
    list_file = database.get_all_file()
    for file in list_file:
        break_dialogue(file)


def get_content_from_line(original_line):
    result = ''
    is_start = False
    for i in range(len(original_line), 0, -1):
        if original_line[i-1] == '"':
            if not is_start:
                is_start = True
                continue
            if original_line[i-2] != '\\':
                return result[::-1].replace('\n', '')
        result += original_line[i-1]


def check_have_old_translate_content(line):
    if get_content_from_line(line) != "":
        return True
    else:
        return False


def remove_old_translate_content(line):
    is_start = False
    start_index = 0
    for i in range(len(line), 0, -1):
        if line[i-1] == '"':
            if not is_start:
                start_index = i
                is_start = True
                continue
            if line[i-2] != '\\':
                return line[0:i] + line[start_index-1::]


def break_dialogue(file):
    order = 0
    dialogue_text = ''
    with open(file.path, 'r', encoding='utf8') as f:
        is_original_line = True
        while True:
            line = f.readline()
            if not line:
                break
            line_strip = line.strip()
            if line_strip.count('"') >= 2 and line_strip.endswith('"'):
                if is_original_line:
                    dialogue_text += line
                else:
                    if check_have_old_translate_content(line):
                        line = remove_old_translate_content(line)
                    dialogue_text += line
                    database.add_dialogue(order, dialogue_text, file.id)
                    order += 1
                    dialogue_text = ''
                is_original_line = not is_original_line
            else:
                dialogue_text += line
    if (dialogue_text != ''):
        database.add_dialogue(order, dialogue_text, file.id)


def process_all_dialogue():
    count_id = 0
    while True:
        count_id += 1
        dialogue = database.get_dialogue(count_id)
        if not dialogue:
            break
        break_phrase(dialogue)


def is_need_translate(text):
    need_translate = True
    text = text.strip()
    if len(text) <= 1 or validators.url(text):
        need_translate = False
    else:
        need_translate = False
        for i in range(len(text)):
            if text[i] != '.' and text[i] != '!' and text[i] != '?' and text[i] != ' ':
                need_translate = True
    return need_translate


def break_phrase(dialogue):
    renpy_animation_keyword = [
        'with fade', 'with dissolve', 'with pixellate', 'with move', 'with moveinright', 'with moveoutright',
        'with ease', 'with zoomin', 'with zoomout', 'with zoominout', 'with vpunch', 'with hpunch', 'with blinds',
        'with squares', 'with wipeleft', 'with slideleft', 'with slideawayleft', 'with pushright', 'with irisin',
        'with moveinleft', 'with moveintop', 'with moveinbottom', 'with moveoutleft', 'with moveouttop',
        'with moveoutbottom', 'with easeinright', 'with easeinleft', 'with easeintop', 'with easeinbottom',
        'with easeoutright', 'with easeoutleft', 'with easeouttop', 'with easeoutbottom', 'with wiperight',
        'with wipeup', 'with wipedown', 'with slideright', 'with slideup', 'with slidedown', 'with slideawayright',
        'with slideawayup', 'with slideawaydown', 'with pushleft', 'with pushup', 'with pushdown', 'with irisout',
        'with fdissolve'
    ]
    line = get_original_line(dialogue.text)
    if not line:
        return
    content = get_content_from_line(line)
    if not content:
        return
    list_position_keyword = []
    for keyword in renpy_animation_keyword:
        for match in re.finditer(keyword, content):
            list_position_keyword.append({
                'start': match.start(),
                'end': match.end()
            })
    order = 0
    temp = ''
    stop_scan_type = None
    for i in range(len(content)):
        for position in list_position_keyword:
            if i == position.get('start') and i != 0:
                space_obj = get_space_before_and_after(temp)
                database.add_phrase(
                    order=order,
                    text=temp.strip(),
                    space_before=space_obj.space_before,
                    space_after=space_obj.space_after,
                    need_translate=is_need_translate(temp),
                    dialogue_id=dialogue.id
                )
                temp = ''
                order += 1
            if i == position.get('end'):
                space_obj = get_space_before_and_after(temp)
                database.add_phrase(
                    order=order,
                    text=temp.strip(),
                    space_before=space_obj.space_before,
                    space_after=space_obj.space_after,
                    need_translate=False,
                    dialogue_id=dialogue.id
                )
                temp = ''
                order += 1
        if stop_scan_type is None:
            if content[i] == '[':
                stop_scan_type = 1
            if content[i] == '{':
                stop_scan_type = 2
            if content[i] == '\\' and content[i+1] == '"':
                stop_scan_type = 3
            if content[i] == '\\' and content[i+1] == '[':
                stop_scan_type = 4
            if content[i] == '\\' and content[i+1] == ']':
                stop_scan_type = 5
            if content[i] == '\\' and content[i+1] == '{':
                stop_scan_type = 6
            if content[i] == '\\' and content[i+1] == '}':
                stop_scan_type = 7
            if len(content) >= 2 and content[i] == '%' and content[i+1] != '.':
                stop_scan_type = 8
            if len(content) >= 4 and content[i] == '%' and content[i+1] == '.':
                stop_scan_type = 9
            if content[i] == '\\' and content[i+1] == 'n':
                stop_scan_type = 10
            if stop_scan_type is not None:
                if temp != '':
                    space_obj = get_space_before_and_after(temp)
                    database.add_phrase(
                        order=order,
                        text=temp.strip(),
                        space_before=space_obj.space_before,
                        space_after=space_obj.space_after,
                        need_translate=is_need_translate(temp),
                        dialogue_id=dialogue.id
                    )
                    temp = ''
                    order += 1
        else:
            if (stop_scan_type == 1 and content[i] == ']') or (stop_scan_type == 2 and content[i] == '}') \
                    or (stop_scan_type == 3 and content[i-1] == '\\' and content[i] == '"') \
                    or (stop_scan_type == 4 and content[i-1] == '\\' and content[i] == '[') \
                    or (stop_scan_type == 5 and content[i-1] == '\\' and content[i] == ']') \
                    or (stop_scan_type == 6 and content[i-1] == '\\' and content[i] == '{') \
                    or (stop_scan_type == 7 and content[i-1] == '\\' and content[i] == '}') \
                    or (stop_scan_type == 8 and content[i-1] == '%') \
                    or (stop_scan_type == 9 and content[i-2] == '.' and content[i-3] == '%') \
                    or (stop_scan_type == 10 and content[i-1] == '\\' and content[i] == 'n'):
                stop_scan_type = None
                if temp != '':
                    temp += content[i]
                    space_obj = get_space_before_and_after(temp)
                    database.add_phrase(
                        order=order,
                        text=temp.strip(),
                        space_before=space_obj.space_before,
                        space_after=space_obj.space_after,
                        need_translate=False,
                        dialogue_id=dialogue.id
                    )
                    temp = ''
                    order += 1
                    continue
        if stop_scan_type is None and i != 0 \
                and (content[i-1] == '.' or content[i-1] == '!' or content[i-1] == '?') \
                and content[i] != '.' and content[i] != '!' and content[i] != '?' and temp != '':
            space_obj = get_space_before_and_after(temp)
            database.add_phrase(
                order=order,
                text=temp.strip(),
                space_before=space_obj.space_before,
                space_after=space_obj.space_after,
                need_translate=is_need_translate(temp),
                dialogue_id=dialogue.id
            )
            temp = ''
            order += 1
        temp += content[i]
    if temp != '':
        space_obj = get_space_before_and_after(temp)
        database.add_phrase(
            order=order,
            text=temp.strip(),
            space_before=space_obj.space_before,
            space_after=space_obj.space_after,
            need_translate=is_need_translate(temp),
            dialogue_id=dialogue.id
        )


def get_original_line(dialogue_text):
    buf = io.StringIO(dialogue_text)
    count = 0
    while True:
        line = buf.readline()
        if not line:
            break
        line_strip = line.strip()
        if line_strip.count('"') >= 2 and line_strip.endswith('"'):
            return line


def get_space_before_and_after(text):
    if text.count(' ') == len(text):
        return SpaceObject(text, '')
    space_before = ''
    space_after = ''
    for c in text:
        if c != ' ':
            break
        space_before += c
    for c in text[::-1]:
        if c != ' ':
            break
        space_after += c
    return SpaceObject(space_before, space_after)


def preprocessing_file(folder_dir):
    print('---')
    print('Preprocessing all file...')
    get_rpy_files_in_directory(folder_dir)
    process_all_file()
    process_all_dialogue()
    database.commit_transtion()
    print("---Done---")
