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

    def test_create_new_creates_list_and_first_item(self):
        """ Тест: create_new создает список и первый элемент """
        List.create_new(first_item_text='new item text')
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'new item text')
        new_list = List.objects.first()
        self.assertEqual(new_item.list, new_list)

    def test_created_new_optionally_saves_owner(self):
        """ Тест: create_new необязательно сохраняет владельца """
        user = User.objects.create()
        List.create_new(first_item_text='New item text', owner=user)
        new_list = List.objects.first()
        self.assertEqual(new_list.owner, user)

    def test_list_can_have_owners(self):
        """ Тест: Списки могут иметь владельца """
        List(owner=User())  # Не должно поднять исключение

    def test_list_owners_is_optional(self):
        """ Тест: Владелец списка необязательный """
        List().full_clean()  # Не должно поднять исключение

    def test_create_returns_new_list_object(self):
        """ Тест: Create возвращает новый объект списка """
        returned = List.create_new(first_item_text='New item text')
        new_list = List.objects.first()
        self.assertEqual(returned, new_list)

    def test_list_name_is_first_item_text(self):
        """ Тест: Имя списка является текстом первого элемента """
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='First Item')
        Item.objects.create(list=list_, text='Second Item')
        self.assertEqual(list_.name, 'First Item')
