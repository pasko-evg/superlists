from django.conf import settings
from django.contrib.auth import get_user_model, BACKEND_SESSION_KEY, SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore
from selenium.webdriver.common.by import By

from functional_tests.base import FunctionalTest
from functional_tests.management.commands.create_session import create_pre_authenticated_session
from functional_tests.server_tools import create_session_on_server

User = get_user_model()


class MyListTest(FunctionalTest):
    """ Тестирование приложения Мои Списки """

    def create_pre_authenticated_session(self, email):
        """ Создать предварительно аутентифицированный сеанс """

        if self.staging_server:
            session_key = create_session_on_server(self.staging_server, self.site_name, email)
        else:
            session_key = create_pre_authenticated_session(email)

        # Установить cookie, которые нужны для первого посещения домена.
        # Страницы 404 загружаются быстрее всего!
        self.browser.get(self.live_server_url + '/404_no_such_url/')
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session_key,
            path='/',
        ))

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        """ Тест: Списки зарегистрированных пользователей сохраняются как Мои Списки """
        # Эдит является зарегистрированным пользователем
        self.create_pre_authenticated_session('testuser@evg-project.org')

        # Эдит открывает домашнюю страницу и начинает новый список
        self.browser.get(self.live_server_url)
        self.add_list_item('Reticulate splines')
        self.add_list_item('Immanentize eschaton')
        first_list_url = self.browser.current_url

        # Она замечает ссылку на Мои Списки в первый раз
        self.browser.find_element(by=By.LINK_TEXT, value='My Lists').click()

        # Она видит, что ее список находится там, и он назван на основе первого элемента списка
        self.wait_for(lambda: self.browser.find_element(by=By.LINK_TEXT, value='Reticulate splines'))
        self.browser.find_element(by=By.LINK_TEXT, value='Reticulate splines').click()
        self.wait_for(lambda: self.assertEqual(self.browser.current_url, first_list_url))

        # Она решает начать еще один список, что бы только убедится
        self.browser.get(self.live_server_url)
        self.add_list_item('Click cows')
        second_list_url = self.browser.current_url

        # Под заголовком Мои Списки появляется ее новый список
        self.wait_for(lambda: self.browser.find_element(by=By.LINK_TEXT, value='Click cows'))
        self.browser.find_element(by=By.LINK_TEXT, value='Click cows').click()
        self.wait_for(lambda: self.assertEqual(self.browser.current_url, second_list_url))

        # Она выходит из системы. Опция Мои Списки исчезает
        self.browser.find_element(by=By.LINK_TEXT, value='Log Out').click()
        self.wait_for(lambda: self.assertEqual(
            self.browser.find_element(By.LINK_TEXT, 'My lists'), []
        ))
