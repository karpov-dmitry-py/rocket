# Generated by Django 3.1.3 on 2020-12-27 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parser_app', '0003_auto_20201227_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='marketplace',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='parser_app.marketplace'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='url',
            field=models.CharField(default=1, max_length=1000),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('url', models.CharField(max_length=1000)),
                ('marketplace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parser_app.marketplace')),
            ],
        ),
    ]