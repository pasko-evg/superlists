from unittest.mock import patch, call

from django.test import TestCase

from accounts.models import Token


class SendLoginEmailViewTest(TestCase):
    """ Тестирование представления которое отправляет сообщение для входа в систему """

    def test_redirects_to_home_page(self):
        """ Тест: Переадресация на домашнюю страницу """
        response = self.client.post('/accounts/send_login_email', data={'email': 'testuser@evg-project.org'})
        self.assertRedirects(response, '/')

    @patch('accounts.views.send_mail')
    def test_sends_mail_to_address_from_post(self, mock_send_mail):
        """ Тест: Отправляется сообщение на адрес метода post """
        self.client.post('/accounts/send_login_email', data={'email': 'testuser@evg-project.org'})

        self.assertEqual(mock_send_mail.called, True)
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertEqual(subject, 'Your login link for Superlists')
        self.assertEqual(from_email, 'superlists@evg-project.org')
        self.assertEqual(to_list, ['testuser@evg-project.org'])

    @patch('accounts.views.send_mail')
    def test_sends_link_to_login_using_token_uid(self, mock_send_mail):
        """ Тест: Отправка ссылки на вход в систему, используя uid маркер """
        self.client.post('/accounts/send_login_email', data={'email': 'testuser@evg-project.org'})
        token = Token.objects.first()
        expected_url = f'http://testserver/accounts/login?token={token.uid}'
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertIn(expected_url, body)

    def test_adds_success_messages(self):
        """ Тест: Добавляется сообщение об успехе """
        response = self.client.post(
            '/accounts/send_login_email', data={'email': 'testuser@evg-project.org'}, follow=True)
        message = list(response.context['messages'])[0]
        self.assertEqual(
            message.message,
            'Check your email, we have sent you a link that you can use to log in to the site.'
        )
        self.assertEqual(message.tags, 'success')


@patch('accounts.views.auth')
class LoginViewTest(TestCase):
    """ Тестирование представления входа в систему """

    def test_redirect_to_home_page(self, mock_auth):
        """ Тест: Переадресация на домашнюю страницу """
        response = self.client.get('/accounts/login?token=abcd1234')
        self.assertRedirects(response, '/')

    def test_creates_token_associated_with_email(self, mock_auth):
        """ Тест: Создается маркер, связанный с электронной почтой """
        self.client.post('/accounts/send_login_email', data={'email': 'testuser@evg-project.org'})
        token = Token.objects.first()
        self.assertEqual(token.email, 'testuser@evg-project.org')

    def test_calls_authenticate_with_uid_from_get_request(self, mock_auth):
        """ Тест: Вызов authenticate c uid из GET-запроса """
        self.client.get('/accounts/login?token=abcd1234')
        self.assertEqual(mock_auth.authenticate.call_args, call(uid='abcd1234'))

    def test_calls_auth_login_with_user_if_there_is_one(self, mock_auth):
        """ Тест: Вызов auth_login c пользователем, если такой имеется """
        response = self.client.get('/accounts/login?token=abcd1234')
        self.assertEqual(mock_auth.login.call_args, call(response.wsgi_request, mock_auth.authenticate.return_value))

    def test_does_not_login_if_user_is_not_authenticated(self, mock_auth):
        """ Тест: Не регистрируется в системе, если пользователь не аутентифицирован """
        mock_auth.authenticate.return_value = None
        self.client.get('/accounts/login?token=abcd1234')
        self.assertEqual(mock_auth.login.called, False)
