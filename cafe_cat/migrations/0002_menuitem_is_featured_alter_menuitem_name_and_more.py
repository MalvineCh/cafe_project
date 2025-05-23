# Generated by Django 4.2.11 on 2024-04-19 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cafe_cat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='summary',
            field=models.TextField(),
        ),
    ]
