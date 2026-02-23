from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="cover_image",
            field=models.ImageField(blank=True, null=True, upload_to="projects/covers/"),
        ),
        migrations.CreateModel(
            name="ProjectImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="projects/gallery/")),
                ("alt", models.CharField(blank=True, max_length=160)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="gallery", to="core.project"),
                ),
            ],
            options={
                "ordering": ("sort_order", "id"),
            },
        ),
    ]
