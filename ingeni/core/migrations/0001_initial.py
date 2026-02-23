from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(unique=True)),
                ("title", models.CharField(max_length=160)),
                ("summary", models.TextField(blank=True)),
                ("category", models.CharField(blank=True, max_length=120)),
                ("badges", models.JSONField(blank=True, default=list)),
                ("images", models.JSONField(blank=True, default=list)),
                ("tags", models.JSONField(blank=True, default=list)),
                ("client", models.CharField(blank=True, max_length=160)),
                ("role", models.CharField(blank=True, max_length=160)),
                ("team", models.JSONField(blank=True, default=list)),
                ("problem", models.TextField(blank=True)),
                ("materials", models.JSONField(blank=True, default=list)),
                ("finishing", models.JSONField(blank=True, default=list)),
                ("process", models.JSONField(blank=True, default=list)),
                ("challenges", models.JSONField(blank=True, default=list)),
                ("outcome", models.TextField(blank=True)),
                ("metrics", models.JSONField(blank=True, default=dict)),
                ("timeline", models.JSONField(blank=True, default=dict)),
                ("links", models.JSONField(blank=True, default=list)),
                ("specs", models.JSONField(blank=True, default=dict)),
                ("is_public", models.BooleanField(default=True)),
                ("is_featured", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("-is_featured", "sort_order", "-created_at"),
            },
        ),
    ]
