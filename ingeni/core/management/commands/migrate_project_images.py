import os
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Project, ProjectImage


class Command(BaseCommand):
    help = "Mueve imagenes antiguas (static/img) a media/ y las asocia a proyectos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra lo que haria sin modificar archivos ni BD.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        static_dirs = getattr(settings, "STATICFILES_DIRS", []) or []
        static_dir = static_dirs[0] if static_dirs else (settings.BASE_DIR / "static")
        static_dir = Path(static_dir)
        media_root = Path(settings.MEDIA_ROOT)

        if not static_dir.exists():
            self.stdout.write(self.style.ERROR(f"No existe static dir: {static_dir}"))
            return

        migrated_total = 0
        project_total = 0

        for project in Project.objects.all():
            legacy_paths = list(project.images or [])
            if not legacy_paths:
                continue

            project_total += 1
            remaining = []
            added_images = 0

            for idx, rel_path in enumerate(legacy_paths, start=1):
                if not isinstance(rel_path, str):
                    continue
                if rel_path.startswith("http") or rel_path.startswith("/") or rel_path.startswith("media/"):
                    remaining.append(rel_path)
                    continue
                if not rel_path.startswith("img/"):
                    remaining.append(rel_path)
                    continue

                src = static_dir / rel_path
                if not src.exists():
                    remaining.append(rel_path)
                    continue

                ext = src.suffix or ".jpg"
                filename = f"{project.slug}-{idx}{ext}"
                dest_rel = Path("projects/gallery") / filename
                dest = media_root / dest_rel
                dest.parent.mkdir(parents=True, exist_ok=True)

                if dry_run:
                    self.stdout.write(f"[dry] {src} -> {dest}")
                else:
                    shutil.copy2(src, dest)
                    # primera imagen como cover si no hay
                    if not project.cover_image:
                        project.cover_image = str(dest_rel).replace(os.sep, "/")
                    ProjectImage.objects.create(project=project, image=str(dest_rel).replace(os.sep, "/"))
                added_images += 1
                migrated_total += 1

            if not dry_run:
                project.images = remaining
                project.save(update_fields=["images", "cover_image"])

            if added_images:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{project.slug}: {added_images} imagen(es) migradas."
                    )
                )

        if project_total == 0:
            self.stdout.write("No hay proyectos con imagenes legacy.")
        else:
            self.stdout.write(self.style.SUCCESS(f"Total migradas: {migrated_total}"))
