import sys
import threading
import time

import database
from console import clear_console

_is_running = True
_is_error = False
total_phrase = 0
total_phrase_done = 0
phrase_thread_status = []
time_left = 0

is_thread_count_started = False
thread_count = None


def set_is_running(value):
    global _is_running
    _is_running = value


def set_is_error(value):
    global _is_error
    _is_error = value


def init_thread_count_array(number_of_thread):
    global phrase_thread_status
    for i in range(number_of_thread):
        phrase_thread_status.append({
            'total_done': 0,
            'is_stopped': False
        })


def add_count_to_thread(thread_index):
    global total_phrase_done
    global phrase_thread_status
    global is_thread_count_started
    phrase_thread_status[thread_index]['total_done'] += 1
    total_phrase_done += 1
    if not thread_count.is_alive() and not is_thread_count_started:
        is_thread_count_started = True
        thread_count.start()


def thread_stopped(thread_index):
    global phrase_thread_status
    phrase_thread_status[thread_index]['is_stopped'] = True


def format_seconds_to_display(seconds):
    hours = seconds // (60*60)
    seconds %= (60*60)
    minutes = seconds // 60
    seconds %= 60
    ret = ''
    if hours > 0:
        ret += '%02ih ' % (hours)
    if minutes > 0:
        ret += '%02im ' % (minutes)
    ret += '%02is' % (seconds)
    return ret


def runner_display():
    global _is_running
    global _is_error
    global total_phrase
    global phrase_thread_status
    global time_left
    while True:
        if not _is_running:
            time_left = 0
        clear_console()
        percent = 100
        if total_phrase != 0:
            percent = round(float(total_phrase_done) /
                            float(total_phrase) * 100, 2)
        print('Total phrase: {}'.format(total_phrase))
        print('Process: {}/{} ({}%)'.format(total_phrase_done, total_phrase, percent))
        print('Time left: {}'.format(format_seconds_to_display(time_left)))
        print('-----------------------------------------')
        for i in range(len(phrase_thread_status)):
            print('Total phrase done on thread {}: {} {}'.format(
                i + 1, phrase_thread_status[i]['total_done'], '(stopped)' if phrase_thread_status[i]['is_stopped'] else ''))
        if _is_error:
            print(' ')
            print('Translation was stopped because the issue of network')
            input('Press Enter to exit...')
            sys.exit()
        if not _is_running and not _is_error:
            print('----------Translation completed----------')
            break
        time.sleep(1)
        if time_left > 1:
            time_left -= 1


def runner_count():
    global _is_running
    global _is_error
    global total_phrase
    global total_phrase_done
    global time_left
    sleep_time = 5
    while _is_running and not _is_error:
        checkpoint = total_phrase_done
        time.sleep(sleep_time)
        total_in_time = total_phrase_done - checkpoint
        if total_in_time > 0:
            time_left = int(
                (total_phrase - total_phrase_done) / total_in_time * sleep_time)
        if sleep_time == 5:
            sleep_time = 10
        if sleep_time == 10:
            sleep_time = 30
        if sleep_time == 30:
            sleep_time = 60


def monitoring_process():
    global total_phrase
    global total_phrase_done
    global thread_count
    total_phrase = database.count_phrase()
    total_phrase_done = database.count_phrase_done()
    thread_display = threading.Thread(target=runner_display)
    thread_count = threading.Thread(target=runner_count, daemon=True)
    thread_display.start()
    return thread_display
