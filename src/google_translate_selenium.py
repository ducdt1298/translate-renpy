import threading
import time
from sys import platform

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import database
import monitoring_selenium

XPATH_OF_INPUT_TEXTBOX = '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[3]/c-wiz[1]/span/span/div/textarea'
XPATH_OF_OUTPUT_TEXTBOX = '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[3]/c-wiz[2]/div[8]/div/div[1]/span[1]/span/span'
XPATH_OF_OUTPUT_TEXTBOX_CASE_GENDER_SPECIFIC = '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[3]/c-wiz[2]/div[8]/div[1]/div[1]/span[1]'
XPATCH_OF_DELETE_BUTTON = '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[3]/c-wiz[1]/div[1]/div/div/span/button'
XPATCH_AGREE_TERMS_BUTTON = '/html/body/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button'

PHRASE_ON_THREAD = 50
MAX_TIME_WAIT_ELEMENT = 10
NUMBER_OF_RETRIES = 5
DRIVER_PATH_WIN = 'Driver/Win/chromedriver.exe'
DRIVER_PATH_LINUX = 'Driver/Linux/chromedriver'
DRIVER_PATH_MAC = 'Driver/Mac/chromedriver'

WEB_DRIVER_OPTIONS = webdriver.ChromeOptions()

lock = threading.Lock()
_is_running = True
_is_error = False
original_language = None
into_language = None


def set_is_running(value):
    global _is_running
    monitoring_selenium.set_is_running(value)


def set_is_error(value):
    global _is_error
    monitoring_selenium.set_is_error(value)


def build_web_driver_options(show_browser):
    if not show_browser:
        WEB_DRIVER_OPTIONS.add_argument('--headless')
    # WEB_DRIVER_OPTIONS.add_argument('--no-sandbox')
    WEB_DRIVER_OPTIONS.add_argument('--disable-gpu')
    WEB_DRIVER_OPTIONS.add_argument('--log-level=3')
    WEB_DRIVER_OPTIONS.add_argument('--disable-extensions')
    WEB_DRIVER_OPTIONS.add_argument('disable-infobars')
    WEB_DRIVER_OPTIONS.add_argument('--window-size=500,420')


def get_input_text_area(driver):
    for x in range(0, NUMBER_OF_RETRIES):
        try:
            return driver.find_element(By.XPATH, XPATH_OF_INPUT_TEXTBOX)
        except:
            time.sleep(MAX_TIME_WAIT_ELEMENT)


def clear_input(input_text_area, driver):
    for x in range(0, NUMBER_OF_RETRIES):
        try:
            input_text_area.clear()
            return
        except:
            input_text_area = get_input_text_area(driver)


def send_keys_to_input(text, input_text_area, driver):
    for x in range(0, NUMBER_OF_RETRIES):
        try:
            input_text_area.send_keys(text)
            return
        except:
            input_text_area = get_input_text_area(driver)


def translate(phrase, input_text_area, wait, driver):
    result = ''

    is_translate_ok = False
    clear_input(input_text_area, driver)
    send_keys_to_input(phrase.text, input_text_area, driver)
    for x in range(0, NUMBER_OF_RETRIES):
        try:
            # wait text availible
            result = wait.until(
                EC.element_to_be_clickable((By.XPATH, XPATH_OF_OUTPUT_TEXTBOX))
            ).text
            is_translate_ok = True
        except:
            pass

        # case gender-specific
        if not is_translate_ok:
            try:
                # wait text availible
                result = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, XPATH_OF_OUTPUT_TEXTBOX_CASE_GENDER_SPECIFIC))
                ).text
                is_translate_ok = True
            except:
                send_keys_to_input('.', input_text_area, driver)

        if is_translate_ok:
            break
    if not is_translate_ok:
        # print('Error: Cannot translate text')
        set_is_running(False)
        set_is_error(True)
        return phrase

    is_clear_ok = False
    for x in range(0, NUMBER_OF_RETRIES):
        try:
            wait.until(
                EC.element_to_be_clickable((By.XPATH, XPATCH_OF_DELETE_BUTTON))
            ).click()
            is_clear_ok = True
        except:
            try:
                clear_input(input_text_area, driver)
                is_clear_ok = True
            except:
                is_clear_ok = False
        if is_clear_ok:
            break
    if not is_clear_ok:
        print('Error: Cannot clear text area')
    phrase.text = result.replace('<span title class>', '').replace(
        '</span>', '').replace('"', "'")
    if is_translate_ok:
        phrase.status = 2
    return phrase


def agree_google_terms(wait):
    try:
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, XPATCH_AGREE_TERMS_BUTTON))
        ).click()
    except:
        pass


def runner(thread_index, driver_path):
    global _is_running
    global _is_error
    global original_language
    global into_language
    with webdriver.Chrome(executable_path=driver_path, options=WEB_DRIVER_OPTIONS) as driver:
        driver.get(
            'https://translate.google.com/?hl=en&sl={original_language}&tl={into_language}&op=translate/'.format(
                original_language=original_language,
                into_language=into_language
            )
        )
        driver.execute_script(
            'document.title = "Thread {}"'.format(thread_index + 1))
        wait = WebDriverWait(driver, MAX_TIME_WAIT_ELEMENT)
        agree_google_terms(wait)
        input_text_area = get_input_text_area(driver)
        if input_text_area is None:
            set_is_running(False)
            set_is_error(True)
            return
        while True:
            with lock:
                phrases = database.get_phrases(PHRASE_ON_THREAD)
            if len(phrases) == 0:
                break
            for phrase in phrases:
                if not _is_running or _is_error:
                    with lock:
                        for p in phrases:
                            if p.status != 2:
                                database.update_phrase_not_translated(p.id)
                        database.commit_transtion()
                    return
                phrase = translate(phrase, input_text_area, wait, driver)
                if phrase.status == 2:
                    with lock:
                        monitoring_selenium.add_count_to_thread(thread_index)
            with lock:
                for phrase in phrases:
                    if phrase.status == 2:
                        database.update_phrase_translated(
                            phrase.id, phrase.text)
                database.commit_transtion()


def get_driver():
    if platform == 'linux' or platform == 'linux2':
        return DRIVER_PATH_LINUX
    elif platform == 'darwin':
        return DRIVER_PATH_MAC
    elif platform == 'win32':
        return DRIVER_PATH_WIN


def google_translate_selenium(run_info):
    global _is_error
    global original_language
    global into_language
    original_language = run_info.get('original_language')
    into_language = run_info.get('into_language')
    set_is_running(True)
    set_is_error(False)
    total_phrase = database.count_phrase()
    total_done_done = database.count_phrase_done()
    if total_phrase == total_done_done:
        return False
    thread_display = monitoring_selenium.monitoring_process()
    driver_path = get_driver()
    build_web_driver_options(run_info.get('show_browser') == 'y')
    threads = []
    number_of_thread = int(run_info.get('number_of_thread'))
    monitoring_selenium.init_thread_count_array(number_of_thread)
    for i in range(number_of_thread):
        threads.append(threading.Thread(
            target=runner, args=(i, driver_path)))
        threads[i].start()
    while True:
        is_all_stopped = True
        for i in range(number_of_thread):
            if threads[i].is_alive():
                is_all_stopped = False
            else:
                monitoring_selenium.thread_stopped(i)
        if is_all_stopped:
            break
        time.sleep(1)
    total_phrase = database.count_phrase()
    total_done_done = database.count_phrase_done()
    if not _is_error and total_done_done < total_phrase:
        WEB_DRIVER_OPTIONS.add_argument('--headless')
        secondary_thread = threading.Thread(
            target=runner, args=(0, driver_path))
        secondary_thread.start()
        secondary_thread.join()
    set_is_running(False)
    thread_display.join()
    return _is_error
