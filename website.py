import json
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.options import Options


class TrainingPeaks:
    def __init__(self, username, password, download_dir=None):
        self.username = username
        self.password = password
        self.download_dir = download_dir
        self.logged_in = False
        self._init_browser()

    def _init_browser(self):
        self.chrome_options = ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.binary_location = "/usr/bin/chromium"
        self.chrome_options.add_argument("--no-sandbox")
        if self.download_dir is not None:
            prefs = {'download.default_directory' : str(self.download_dir)}
            self.chrome_options.add_experimental_option('prefs', prefs)

    def __enter__(self):
        self.browser = Chrome(
            executable_path="/usr/bin/chromedriver",
            chrome_options=self.chrome_options
        )
        return self

    def __exit__(self, type, value, traceback):
        self.browser.quit()

    def requires_login(func):
        def f(self, *args, **kwargs) :
            if not self.logged_in:
                print('Logging into TrainingPeaks...')


                self.browser.get('https://home.trainingpeaks.com/login')

                username_input = self.browser.find_element_by_id('Username')
                username_input.send_keys(self.username)

                password_input = self.browser.find_element_by_id('Password')
                password_input.send_keys(self.password)

                submit_button = self.browser.find_element_by_id('btnSubmit')
                submit_button.click()
                self.logged_in = True

            return func(self, *args, **kwargs)
        return f

    def _download_file(self, url, timeout=15):
        downloaded_files_before = [f for f in self.download_dir.iterdir() if f.is_file()]

        self.browser.set_page_load_timeout(timeout)
        try:
            self.browser.get(url)
        except TimeoutException:
            pass

        start_time = time.time()
        started_downloading = False
        while True:
            if not started_downloading and time.time() - start_time > 10:
                # Timeout if download is taking too long.
                break

            downloaded_files_after = [f for f in self.download_dir.iterdir() if f.is_file()]
            change = set(downloaded_files_after) - set(downloaded_files_before)

            for c in change:
                started_downloading = True
                if str(c).endswith(".zip"):
                    return c
            time.sleep(2)

        print("Error. There is probably no data available for the selected period.")
        return
    
    @requires_login
    def download_workout_files(self, athlete_id, start_date=None, end_date=None):
        print('Downloading workout files...')
        start = start_date.strftime('%Y-%m-%d')
        end = end_date.strftime('%Y-%m-%d')
        workout_file_export_url = f'https://tpapi.trainingpeaks.com/fitness/v1/export/{athlete_id}/files/{start}/{end}/raw'
        downloaded_file = self._download_file(workout_file_export_url)
        return downloaded_file

    @requires_login
    def download_workout_summaries(self, athlete_id, start_date=None, end_date=None):
        print('Downloading workout summaries...')
        start = start_date.strftime('%Y-%m-%d')
        end = end_date.strftime('%Y-%m-%d')
        workout_summary_export_url = f'https://tpapi.trainingpeaks.com/fitness/v1/export/{athlete_id}/workouts/{start}/{end}/raw'
        downloaded_file = self._download_file(workout_summary_export_url)
        return downloaded_file

    @requires_login
    def download_custom_metrics(self, athlete_id, start_date=None, end_date=None):
        print('Downloading custom metrics...')
        start = start_date.strftime('%Y-%m-%d')
        end = end_date.strftime('%Y-%m-%d')
        custom_metrics_url = f'https://tpapi.trainingpeaks.com/fitness/v1/export/{athlete_id}/metrics/{start}/{end}/raw'
        downloaded_file = self._download_file(custom_metrics_url)
        return downloaded_file

    def download_all(self, athlete_id, start_date=None, end_date=None):
        self.download_workout_files(athlete_id, start_date=start_date, end_date=end_date)
        self.download_workout_summaries(athlete_id, start_date=start_date, end_date=end_date)
        self.download_custom_metrics(athlete_id, start_date=start_date, end_date=end_date)

    @requires_login
    def get_athlete_id(self):
        time.sleep(5)
        local_storage = LocalStorage(self.browser)

        return local_storage["ajs_user_id"]


def unzip(filepath, destination, add_extension=None):
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(destination)
        
        if add_extension is not None:
            pass


class LocalStorage:
    """Source: https://stackoverflow.com/a/46361900/1339946
    """

    def __init__(self, driver) :
        self.driver = driver

    def __len__(self):
        return self.driver.execute_script("return window.localStorage.length;")

    def items(self) :
        return self.driver.execute_script( \
            "var ls = window.localStorage, items = {}; " \
            "for (var i = 0, k; i < ls.length; ++i) " \
            "  items[k = ls.key(i)] = ls.getItem(k); " \
            "return items; ")

    def keys(self) :
        return self.driver.execute_script( \
            "var ls = window.localStorage, keys = []; " \
            "for (var i = 0; i < ls.length; ++i) " \
            "  keys[i] = ls.key(i); " \
            "return keys; ")

    def get(self, key):
        return self.driver.execute_script("return window.localStorage.getItem(arguments[0]);", key)

    def set(self, key, value):
        self.driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", key, value)

    def has(self, key):
        return key in self.keys()

    def remove(self, key):
        self.driver.execute_script("window.localStorage.removeItem(arguments[0]);", key)

    def clear(self):
        self.driver.execute_script("window.localStorage.clear();")

    def __getitem__(self, key) :
        value = self.get(key)
        if value is None :
          raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        return key in self.keys()

    def __iter__(self):
        return self.items().__iter__()

    def __repr__(self):
        return self.items().__str__()
