import os
import re
import ssl
import mailparser
import time
from datetime import datetime

from django.core import mail
from imapclient import IMAPClient
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from functional_tests.base import FunctionalTest

SUBJECT = 'Your login link for Superlists'


class LoginTest(FunctionalTest):
    """ Тестирование регистрации в системе """

    def wait_for_email(self, test_email, subject):
        """ Ожидать электронное сообщение """
        if not self.staging_server:
            email = mail.outbox[0]
            self.assertIn(test_email, email.to)
            self.assertEqual(email.subject, subject)
            return email.body

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        start = time.time()
        start_date = datetime.utcnow()

        email_id = None
        email_body = None
        email_user = test_email
        email_password = os.environ['TEST_MAIL_PASSWORD']
        email_server = 'mail.evg-project.org'

        with IMAPClient(host=email_server, ssl_context=ssl_context) as client:
            client.login(email_user, email_password)
            client.select_folder('INBOX')
            messages = client.search(['NOT', 'DELETED'])
            while time.time() - start < 60:
                response = client.fetch(messages, ['RFC822'])
                for message_id, data in reversed(response.items()):
                    email = mailparser.parse_from_bytes(data[b'RFC822'])
                    mail_send_date_delta = (start_date - email.date).total_seconds()
                    if mail_send_date_delta < 20 and subject in email.mail.get('subject'):
                        email_id = message_id
                        email_body = email.body
                if email_body:
                    break
                else:
                    time.sleep(5)
            if email_id:
                client.move([email_id], 'Trash')
        return email_body

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
