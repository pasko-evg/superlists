from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Token

User = get_user_model()


class UserModelTest(TestCase):
    """ Тестирование модели пользователя """

    def test_user_is_valid_with_email_only(self):
        """ Тест: Пользователь допустим только с электронной почтой """
        user = User(email='a@b.com')
        user.full_clean()  # Не должно поднимать исключение

    def test_email_is_primary_key(self):
        """ Тест: Адрес электронной почты является первичным ключом """
        user = User(email='a@b.com')
        self.assertEqual(user.pk, 'a@b.com')


class TokenModelTest(TestCase):
    """ Тестирование модули маркера """

    def test_links_user_with_auto_generated_uid(self):
        """ Тест: Соединение пользователя с авто-генерированным uid """
        token1 = Token.objects.create(email='a@b.com')
        token2 = Token.objects.create(email='a@b.com')
        self.assertNotEqual(token1.uid, token2.uid)
