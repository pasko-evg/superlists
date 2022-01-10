import os
import poplib
import re
import time

from django.core import mail
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from functional_tests.base import FunctionalTest

SUBJECT = 'Your login link for Superlists'


class LoginTest(FunctionalTest):
    """ Тестирование регистрации в системе """

    def wait_for_email(self, test_email, subject):
        """ Ожидать электронное сообщение """
        # TODO: Переделать метод, нужна проверка письма по дате отправки, локальная почта глючит
        if not self.staging_server:
            email = mail.outbox[0]
            self.assertIn(test_email, email.to)
            self.assertEqual(email.subject, subject)
            return email.body

        email_id = None
        start = time.time()
        inbox = poplib.POP3_SSL('mail.evg-project.org')
        try:
            inbox.user(test_email)
            inbox.pass_(os.environ['TEST_MAIL_PASSWORD'])
            while time.time() - start < 60:
                count, _ = inbox.stat()
                # print(f'{count=}')
                for i in reversed(range(max(1, count - 10), count + 1)):
                    print(f'Getting msg {i}')
                    response, lines, __ = inbox.retr(i)
                    # print(f'{response=}')
                    lines = [l.decode('utf8') for l in lines]
                    print(lines)
                    if f'Subject: {subject}' in lines:
                        email_id = i
                        body = '\n'.join(lines)
                        # print(f'{body=}')
                        return body
                time.sleep(5)
        finally:
            if email_id:
                inbox.dele(email_id)
            inbox.quit()

    def test_can_get_email_link_to_log_in(self):
        """ Тест: Можно получить ссылку по почте для регистрации """
        # Эдит заходит на офигительный сайт суперсписков и впервые замечает раздел "Войти"
        # в навигационной панели, он говорит ввести ей свой адрес электронной почты, что она и делает
        if self.staging_server:
            test_email = 'testuser@evg-project.org'
        else:
            test_email = 'testuser@example.com'
        self.browser.get(self.live_server_url)
        self.browser.find_element(by=By.NAME, value='email').send_keys(test_email)
        self.browser.find_element(by=By.NAME, value='email').send_keys(Keys.ENTER)

        # Появляется сообщение, которое говорит, что ей на почту было выслано письмо
        self.wait_for(lambda: self.assertIn(
            'Check your email',
            self.browser.find_element(by=By.TAG_NAME, value='body').text
        ))

        # Эдит проверяет свою почту и находит сообщение
        body = self.wait_for_email(test_email, SUBJECT)

        # Оно содержит ссылку на url-адрес
        self.assertIn('Use this link to log in', body)
        url_search = re.search(r'http://.+/.+$', body)
        if not url_search:
            self.fail(f'Could not find url in email body:\n{body}')
        url = url_search.group(0)
        print(f'{url=}')
        self.assertIn(self.live_server_url, url)

        # Эдит нажимает на ссылку
        self.browser.get(url)

        # Она зарегистрирована в системе!
        self.wait_to_be_logged_in(test_email)

        # Теперь она выходит из системы
        self.browser.find_element(by=By.LINK_TEXT, value='Log out').click()

        # Она вышла из системы
        self.wait_to_be_logged_out(test_email)
