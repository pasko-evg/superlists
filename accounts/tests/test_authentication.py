from django.test import TestCase

from accounts.authentication import PasswordlessAuthenticationBackend
from accounts.models import Token, User


class AuthenticateTest(TestCase):
    """ Тестирование аутентификации """

    def test_returns_None_if_no_such_token(self):
        """ Тест: Возвращается None, если нет такого маркера """
        result = PasswordlessAuthenticationBackend().authenticate('no-such-token')
        self.assertIsNone(result)

    def test_returns_new_user_with_correct_email_if_token_exist(self):
        """ Тест: Возвращается новый пользователь с правильной электронной почтой, если маркер существует """
        email = 'testuser@evg-project.org'
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(uid=token.uid)
        new_user = User.objects.get(email=email)
        self.assertEqual(user, new_user)

    def test_returns_existing_user_with_correct_email_if_token_exist(self):
        """ Тест: Возвращается существующий пользователь с правильной электронной почтой, если маркер существует """
        email = 'testuser@evg-project.org'
        existing_user = User.objects.create(email=email)
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(uid=token.uid)
        self.assertEqual(user, existing_user)


class GetUserTest(TestCase):
    """ Тестирование получения пользователя """

    def test_gets_user_by_email(self):
        """ Тест: Получение пользователя по адресу электронной почты """
        User.objects.create(email='first_user@example.com')
        desired_user = User.objects.create(email='second_user@example.com')
        found_user = PasswordlessAuthenticationBackend().get_user('second_user@example.com')
        self.assertEqual(found_user, desired_user)

    def test_returns_None_if_no_user_with_that_email(self):
        """ Тест: возвращается None, если нет пользователя с таким адресом электронной почты """
        self.assertIsNone(PasswordlessAuthenticationBackend().get_user('not_ex_user@example.com'))
