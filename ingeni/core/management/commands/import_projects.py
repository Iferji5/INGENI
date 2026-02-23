from django.core.management.base import BaseCommand

from core.models import Project
from core.views import PROJECT_DEFAULTS, PROJECTS


class Command(BaseCommand):
    help = "Importa los proyectos hardcodeados a la base de datos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            help="Actualiza proyectos existentes (por slug).",
        )

    def handle(self, *args, **options):
        update = options["update"]
        created_count = 0
        updated_count = 0

        for idx, (slug, data) in enumerate(PROJECTS.items(), start=1):
            base = {**PROJECT_DEFAULTS, **data}
            payload = {
                "slug": base.get("slug") or slug,
                "title": base.get("title") or slug,
                "summary": base.get("summary", ""),
                "category": base.get("category", ""),
                "badges": list(base.get("badges") or []),
                "images": list(base.get("images") or []),
                "tags": list(base.get("tags") or []),
                "client": base.get("client", ""),
                "role": base.get("role", ""),
                "team": list(base.get("team") or []),
                "problem": base.get("problem", ""),
                "materials": list(base.get("materials") or []),
                "finishing": list(base.get("finishing") or []),
                "process": list(base.get("process") or []),
                "challenges": list(base.get("challenges") or []),
                "outcome": base.get("outcome", ""),
                "metrics": dict(base.get("metrics") or {}),
                "timeline": dict(base.get("timeline") or {}),
                "links": list(base.get("links") or []),
                "specs": dict(base.get("specs") or {}),
                "is_public": True,
                "is_featured": True,
                "sort_order": idx,
            }

            obj, created = Project.objects.get_or_create(slug=payload["slug"], defaults=payload)
            if created:
                created_count += 1
                continue

            if update:
                for key, value in payload.items():
                    setattr(obj, key, value)
                obj.save(update_fields=list(payload.keys()))
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Importados: {created_count}"))
        if update:
            self.stdout.write(self.style.SUCCESS(f"Actualizados: {updated_count}"))
