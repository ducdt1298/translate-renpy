import time
from datetime import datetime

import database
from build_rpy import build_rpy_files
from console import input_info
from google_translate_selenium import google_translate_selenium
from preprocessing_file import preprocessing_file


def main():
    run_info = input_info()
    start = time.time()
    if not run_info.get('is_continue'):
        preprocessing_file(run_info.get('folder_dir'))
    is_translate_error = google_translate_selenium(run_info)
    if not is_translate_error:
        is_build_success = build_rpy_files()
        if is_build_success:
            print('---Clear temp data---')
            database.reset_database()
            end = time.time()
            print('--')
            print('All done at: {}'.format(
                datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
            print('Total time: {}'.format(time.strftime(
                '%H:%M:%S', time.gmtime(end - start))))
    input('Press Enter to exit...')


main()
