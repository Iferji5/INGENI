from django.contrib import admin

from .forms import ProjectForm
from .models import Project, ProjectImage
class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm
    inlines = [ProjectImageInline]
    list_display = ("title", "slug", "is_public", "is_featured", "sort_order", "updated_at")
    list_filter = ("is_public", "is_featured")
    search_fields = ("title", "summary", "category", "client")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-is_featured", "sort_order", "-updated_at")
