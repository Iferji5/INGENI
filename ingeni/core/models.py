from django.db import models


class Project(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    summary = models.TextField(blank=True)
    category = models.CharField(max_length=120, blank=True)

    badges = models.JSONField(default=list, blank=True)
    images = models.JSONField(default=list, blank=True)
    cover_image = models.ImageField(upload_to="projects/gallery/", blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)

    client = models.CharField(max_length=160, blank=True)
    role = models.CharField(max_length=160, blank=True)
    team = models.JSONField(default=list, blank=True)
    problem = models.TextField(blank=True)
    materials = models.JSONField(default=list, blank=True)
    finishing = models.JSONField(default=list, blank=True)
    process = models.JSONField(default=list, blank=True)
    challenges = models.JSONField(default=list, blank=True)
    outcome = models.TextField(blank=True)

    metrics = models.JSONField(default=dict, blank=True)
    timeline = models.JSONField(default=dict, blank=True)
    links = models.JSONField(default=list, blank=True)
    specs = models.JSONField(default=dict, blank=True)

    is_public = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-is_featured", "sort_order", "-created_at")

    def __str__(self) -> str:
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name="gallery", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="projects/gallery/")
    alt = models.CharField(max_length=160, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "id")

    def __str__(self) -> str:
        return f"{self.project.title} ({self.id})"
