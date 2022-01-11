from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from lists.models import Item, List

User = get_user_model()


class ListModelsTest(TestCase):
    """ Тестирование модели элемента списка """

    def test_default_text(self):
        """ Тест: заданного по умолчанию текста """
        item = Item()
        self.assertEqual(item.text, '')

    def test_item_is_related_to_list(self):
        """ Тест: элемент связан со списком """
        list_ = List.objects.create()
        item = Item()
        item.list = list_
        item.save()
        self.assertIn(item, list_.item_set.all())

    def test_cannot_save_empty_list_items(self):
        """ Тест: Нельзя добавить пустые элементы списка """
        list_ = List.objects.create()
        item = Item(list=list_, text='')
        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()

    def test_duplicate_items_are_invalid(self):
        """ Тест: Повторы элементов в одном списке недопустимы """
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='bla')
        with self.assertRaises(ValidationError):
            item = Item(list=list_, text='bla')
            item.full_clean()
            # item.save()

    def test_CAN_save_same_item_to_different_lists(self):
        """ Тест: МОЖНО сохранить одинаковые элементы в разные списки """
        list1 = List.objects.create()
        list2 = List.objects.create()
        Item.objects.create(list=list1, text='bla')
        item = Item(list=list2, text='bla')
        item.full_clean()  # не должен поднимать исключение

    def test_list_ordering(self):
        """ Тест: Упорядочивание списка """
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='Item 1')
        item2 = Item.objects.create(list=list1, text='Item 2')
        item3 = Item.objects.create(list=list1, text='Item 3')
        self.assertEqual(
            list(Item.objects.all()),
            [item1, item2, item3]
        )

    def test_string_representation(self):
        """ Тест: Строковое представление """
        item = Item(text='some text')
        self.assertEqual(str(item), 'some text')


class ListModelTest(TestCase):
    """ Тестирование модели списка """

    def test_get_absolute_url(self):
        """ Тест: Наличие абсолютной ссылки """
        list_ = List.objects.create()
        self.assertEqual(list_.get_absolute_url(), f'/lists/{list_.id}/')

    def test_lists_owner_is_optional(self):
        """ Тест: Владелец списка является необязательным """
        List.objects.create()

    def test_lists_can_have_owners(self):
        """ Тест: Списки могут иметь владельцев """
        user = User.objects.create(email='a@b.com')
        list_ = List.objects.create(owner=user)
        self.assertIn(list_, user.list_set.all())

    def test_list_name_is_first_item_text(self):
        """ Тест: Имя списка является текстом первого элемента """
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='First item')
        Item.objects.create(list=list_, text='Second item')
        self.assertEqual(list_.name, 'First item')
