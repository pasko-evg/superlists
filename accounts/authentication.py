from accounts.models import Token, User


class PasswordlessAuthenticationBackend:
    """ Беспарольный серверный процессор аутентификации """

    def authenticate(self, request=None, uid=''):
        """ Аутентификация """
        token: Token or None = None
        try:
            token = Token.objects.get(uid=uid)
            return User.objects.get(email=token.email)
        except User.DoesNotExist:
            return User.objects.create(email=token.email)
        except Token.DoesNotExist:
            return None

    def get_user(self, email):
        """ Получить пользователя """
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
