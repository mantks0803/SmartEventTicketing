from django.db import migrations
from pgvector.django import VectorExtension


class Migration(migrations.Migration):

    dependencies = [
        ('ai_agent', '0002_initial'),
    ]

    operations = [
        # PostgreSQL phải có extension vector trước khi tạo cột embedding.
        VectorExtension(),
    ]
