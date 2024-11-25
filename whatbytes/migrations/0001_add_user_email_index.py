from django.db import migrations, models

class Migration(migrations.Migration):
    # No dependencies here since this is your first migration
    dependencies = []

    operations = [
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['email'], name='user_email_idx'),
        ),
    ]
