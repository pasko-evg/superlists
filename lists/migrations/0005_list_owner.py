# Generated by Django 4.0 on 2022-01-11 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_token'),
        ('lists', '0004_list_item_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='list',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.user'),
        ),
    ]
