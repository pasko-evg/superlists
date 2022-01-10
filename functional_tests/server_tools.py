from fabric.api import run
from fabric.context_managers import settings


def _get_manage_dot_py(site_name):
    """ Получить manage.py """
    return f'~/sites/{site_name}/virtualenv/bin/python ~/sites/{site_name}/source/manage.py'


def reset_database(host, site_name):
    """ Обнулить базу данных """
    manage_dot_py = _get_manage_dot_py(site_name)
    with settings(host_string=f'evgeniy@{host}'):
        run(f'{manage_dot_py} flush --noinput')


def create_session_on_server(host, site_name, email):
    """ Создать сеанс на сервере """
    manage_dot_py = _get_manage_dot_py(site_name)
    with settings(host_string=f'evgeniy@{host}'):
        session_key = run(f'{manage_dot_py} create_session {email}')
        return session_key.strip()
