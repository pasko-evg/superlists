import os
import time
from unittest import skip

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from functional_tests.server_tools import reset_database

MAX_WAIT = 10


def wait(function):
    def modified_function(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return function(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    return modified_function


class FunctionalTest(StaticLiveServerTestCase):
    """ Функциональный тест """

    def setUp(self) -> None:
        """ Установка """
        self.browser = webdriver.Firefox()
        self.staging_server = os.environ.get('STAGING_SERVER')
        self.site_name = os.environ.get('SITE_NAME')
        if self.staging_server:
            self.live_server_url = f'http://{self.staging_server}:8080'
            reset_database(self.staging_server, self.site_name)

    def tearDown(self) -> None:
        """ Демонтаж """
        self.browser.quit()

    @wait
    def wait_for(self, function):
        """ Ожидать выполнение переданной функции (function) """
        return function()

    def get_item_input_box(self):
        """ Получить поле ввода для элемента """
        return self.browser.find_element(by=By.ID, value='id_text')

    @wait
    def wait_for_row_in_list_table(self, row_text):
        """ Ожидание строки в таблице списка """
        table = self.browser.find_element(by=By.ID, value='id_list_table')
        rows = table.find_elements(by=By.TAG_NAME, value='tr')
        self.assertIn(row_text, [row.text for row in rows])

    @wait
    def wait_to_be_logged_in(self, email):
        """ Ожидание входа в систему """
        self.browser.find_element(by=By.LINK_TEXT, value='Log out')
        navbar = self.browser.find_element(by=By.CSS_SELECTOR, value='.navbar')
        self.assertIn(email, navbar.text)

    @wait
    def wait_to_be_logged_out(self, email):
        """ Ожидание выхода из системы """
        self.browser.find_element(by=By.NAME, value='email')
        navbar = self.browser.find_element(by=By.CSS_SELECTOR, value='.navbar')
        self.assertNotIn(email, navbar.text)

    def add_list_item(self, item_text):
        """ Добавить элемент списка """
        num_rows = len(self.browser.find_elements(By.CSS_SELECTOR, '#id_list_table tr'))
        self.get_item_input_box().send_keys(item_text)
        self.get_item_input_box().send_keys(Keys.ENTER)
        item_number = num_rows + 1
        self.wait_for_row_in_list_table(f'{item_number}: {item_text}')
