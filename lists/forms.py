from django import forms

from lists.models import Item

EMPTY_ITEM_ERROR = "You can't have an empty list item"


class ItemForm(forms.models.ModelForm):
    """ Форма для элемента списка """

    class Meta:
        model = Item
        fields = ('text',)
        widgets = {
            'text': forms.fields.TextInput(attrs={
                'placeholder': 'Enter a to-do item',
                'class': 'form-control input-group-lg',
            }),
        }
        error_messages = {
            'text': {'required': EMPTY_ITEM_ERROR}
        }

    def save(self, *args, **kwargs):
        if 'for_list' in kwargs.keys():
            for_list = kwargs.pop('for_list')
            self.instance.list = for_list
        return super().save(*args, **kwargs)
