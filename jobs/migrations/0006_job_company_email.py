# Generated by Django 5.1.7 on 2025-03-27 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_jobcategory_remove_job_user_job_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='company_email',
            field=models.EmailField(default=1, max_length=254),
            preserve_default=False,
        ),
    ]
