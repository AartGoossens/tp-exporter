import time
from getpass import getpass

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.options import Options


class TrainingPeaks:
    def __init__(self, download_dir):
        self.download_dir = download_dir
        self.logged_in = False

        self.chrome_options = ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.binary_location = "/usr/bin/chromium"
        self.chrome_options.add_argument("--no-sandbox")
        #self.chrome_options.add_argument(f"download.default_directory={download_dir}")
        prefs = {'download.default_directory' : str(download_dir)}
        self.chrome_options.add_experimental_option('prefs', prefs)

    def __enter__(self):
        print(f'Starting browser...')
        self.browser = Chrome(
            executable_path="/usr/bin/chromedriver",
            chrome_options=self.chrome_options
        )
        print('Done.\n')
        return self

    def __exit__(self, type, value, traceback):
        print('Quitting browser...')
        self.browser.quit()
        print('Done.\n')

    def requires_login(func):
        def f(self, *args, **kwargs) :
            if not self.logged_in:
                print('Logging into TrainingPeaks...')

                print('TrainingPeaks credentials:')
                username = input('Username: ')
                password = getpass(prompt='Password: ')

                self.browser.get('https://home.trainingpeaks.com/login')

                username_input = self.browser.find_element_by_id('Username')
                username_input.send_keys(username)

                password_input = self.browser.find_element_by_id('Password')
                password_input.send_keys(password)

                submit_button = self.browser.find_element_by_id('btnSubmit')
                submit_button.click()
                self.logged_in = True
                print('Done.\n')
            else:
                print('Already logged in. Skipping.')

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
        while True:
            if time.time() - start_time > 10:
                # Timeout if download is taking too long.
                break

            downloaded_files_after = [f for f in self.download_dir.iterdir() if f.is_file()]
            change = set(downloaded_files_after) - set(downloaded_files_before)

            for c in change:
                if str(c).endswith(".zip"):
                    break

        return change.pop()
    
    @requires_login
    def download_workout_files(self, athlete_id, start_date=None, end_date=None):
        print('Downloading workout files...')
        start = start_date.strftime('%Y-%m-%d')
        end = end_date.strftime('%Y-%m-%d')
        workout_file_export_url = f'https://tpapi.trainingpeaks.com/fitness/v1/export/{athlete_id}/files/{start}/{end}/raw'
        downloaded_file = self._download_file(workout_file_export_url)
        print('Done.\n')
        return downloaded_file

    @requires_login
    def download_workout_summaries(self, athlete_id, start_date=None, end_date=None):
        print('Downloading workout summaries...')
        start = start_date.strftime('%Y-%m-%d')
        end = end_date.strftime('%Y-%m-%d')
        workout_summary_export_url = f'https://tpapi.trainingpeaks.com/fitness/v1/export/{athlete_id}/workouts/{start}/{end}/raw'
        downloaded_file = self._download_file(workout_summary_export_url)
        print('Done.\n')
        return downloaded_file

    @requires_login
    def download_custom_metrics(self, athlete_id, start_date=None, end_date=None):
        print('Downloading custom metrics...')
        start = start_date.strftime('%Y-%m-%d')
        end = end_date.strftime('%Y-%m-%d')
        custom_metrics_url = f'https://tpapi.trainingpeaks.com/fitness/v1/export/{athlete_id}/metrics/{start}/{end}/raw'
        downloaded_file = self._download_file(custom_metrics_url)
        print('Done.\n')
        return downloaded_file

    def download_all(self, athlete_id, start_date=None, end_date=None):
        self.download_workout_files(athlete_id, start_date=start_date, end_date=end_date)
        self.download_workout_summaries(athlete_id, start_date=start_date, end_date=end_date)
        self.download_custom_metrics(athlete_id, start_date=start_date, end_date=end_date)


def unzip(filepath, destination, add_extension=None):
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(destination)
        
        if add_extension is not None:
            pass
