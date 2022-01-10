import os
import time
from unittest import skip

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

MAX_WAIT = 10


class FunctionalTest(StaticLiveServerTestCase):
    """ Функциональный тест """

    def setUp(self) -> None:
        """ Установка """
        self.browser = webdriver.Firefox()
        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            self.live_server_url = f'http:{staging_server}:8080'

    def tearDown(self) -> None:
        """ Демонтаж """
        self.browser.quit()

    def wait_for(self, function):
        """ Ожидать выполнение переданной функции (function) """
        start_time = time.time()
        while True:
            try:
                return function()
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def wait_for_row_in_list_table(self, row_text):
        """ Ожидание строки в таблице списка """
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element(by=By.ID, value='id_list_table')
                rows = table.find_elements(by=By.TAG_NAME, value='tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def get_item_input_box(self):
        """ Получить поле ввода для элемента """
        return self.browser.find_element(by=By.ID, value='id_text')

    def wait_to_be_logged_in(self, email):
        """ Ожидание входа в систему """
        self.wait_for(lambda: self.browser.find_element(by=By.LINK_TEXT, value='Log out'))
        navbar = self.browser.find_element(by=By.CSS_SELECTOR, value='.navbar')
        self.assertIn(email, navbar.text)

    def wait_to_be_logged_out(self, email):
        """ Ожидание выхода из системы """
        self.wait_for(lambda: self.browser.find_element(by=By.NAME, value='email'))
        navbar = self.browser.find_element(by=By.CSS_SELECTOR, value='.navbar')
        self.assertNotIn(email, navbar.text)
