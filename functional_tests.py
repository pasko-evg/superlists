import time
import unittest

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By


class NewVisitorTest(unittest.TestCase):
    """ тест нового посетителя """

    def setUp(self) -> None:
        """ Установка """
        self.browser = webdriver.Firefox()

    def tearDown(self) -> None:
        """ Демонтаж """
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
        """ Тест: Можно начать список и получить его позже """
        # Эдит слышала про крутое новое онлайн-приложение со списком
        # неотложных дел. Она решает оценить его домашнюю страницу

        self.browser.get('http://localhost:8000')

        # Она видит, что заголовок и шапка страницы говорят о списках неотложных дел
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element(by=By.TAG_NAME, value='h1').text
        self.assertIn('To-Do', header_text)

        # Ей сразу же предлагается ввести элемент списка
        input_box = self.browser.find_element(by=By.ID, value='id_new_item')
        self.assertEqual(input_box.get_attribute('placeholder'), 'Enter a to-do item')

        # Она набирает в текстовом поле "Купить павлиньи перья" (ее хобби – вязание рыболовных мушек)
        input_box.send_keys('Купить павлиньи перья')

        # Когда она нажимает enter, страница обновляется, и теперь страница
        # содержит "1: Купить павлиньи перья" в качестве элемента списка
        input_box.send_keys(Keys.ENTER)
        time.sleep(1)

        table = self.browser.find_element(by=By.ID, value='id_list_table')
        rows = table.find_elements(by=By.TAG_NAME, value='tr')
        self.assertTrue(any(row.text == '1: Купить павлиньи перья' for row in rows))

        self.fail('Закончить тест!')
        # Текстовое поле по-прежнему приглашает ее добавить еще один элемент.
        # Она вводит "Сделать мушку из павлиньих перьев"
        # (Эдит очень методична)

        # Страница снова обновляется, и теперь показывает оба элемента ее списка

        # Эдит интересно, запомнит ли сайт ее список. Далее она видит, что
        # сайт сгенерировал для нее уникальный URL-адрес – об этом
        # выводится небольшой текст с объяснениями.

        # Она посещает этот URL-адрес – ее список по-прежнему там.

        # Удовлетворенная, она снова ложится спать


if __name__ == '__main__':
    unittest.main()
