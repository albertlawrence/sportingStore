# Generated by Django 4.2.5 on 2023-10-09 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minisport', '0015_userprofile_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='pdf_file_path',
            field=models.FileField(blank=True, null=True, upload_to='pdfs/'),
        ),
    ]