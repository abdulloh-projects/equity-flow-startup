import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('startupp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Investment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('investor_id', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('message', models.TextField(blank=True, default='')),
                ('status', models.CharField(default='completed', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('startup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='startupp.startup')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='startupp.campaign')),
            ],
            options={
                'db_table': 'investments',
            },
        ),
    ]
