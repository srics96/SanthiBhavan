# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-05 18:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enquiry', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='room_type',
            field=models.CharField(choices=[(b'Premium Single', b'Premium Single'), (b'Premium Double', b'Premium Double'), (b'Deluxe Double', b'Deluxe Double')], default=b'Premium Single', max_length=2),
        ),
    ]