# Generated by Django 5.0.7 on 2024-08-01 18:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_booking_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='room_id',
            new_name='room',
        ),
    ]
