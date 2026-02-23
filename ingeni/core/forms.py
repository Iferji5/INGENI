from django import forms
from django.core.exceptions import ValidationError

from .models import Project

class ContactForm(forms.Form):
    PROYECTO_CHOICES = [
        ("gran-escala", "Proyectos a gran escala"),
        ("baja-escala", "Proyectos a baja escala"),
        ("personalizados", "Trabajos personalizados"),
        ("funcionales", "Art\u00edculos funcionales"),
        ("equipos", "Equipos"),
        ("mercaderia", "Mercader\u00eda (bares, restaurantes, etc.)"),
    ]

    nombre = forms.CharField(
        max_length=80,
        label="Nombre",
        error_messages={"required": "Por favor indica tu nombre."},
    )
    email = forms.EmailField(
        label="Email",
        error_messages={"required": "Necesitamos tu correo para contactarte."},
    )
    proyecto = forms.ChoiceField(
        choices=PROYECTO_CHOICES,
        label="Tipo de proyecto",
        error_messages={"required": "Selecciona el tipo de proyecto."},
    )
    asunto = forms.CharField(
        max_length=120,
        label="Asunto",
        error_messages={"required": "Cu\u00e9ntanos el tema de tu consulta."},
    )
    mensaje = forms.CharField(
        max_length=2000,
        label="Mensaje",
        widget=forms.Textarea,
        error_messages={"required": "Describe tu proyecto o necesidad."},
    )

    def get_project_label(self):
        return dict(self.PROYECTO_CHOICES).get(self.cleaned_data.get("proyecto"), "")


def _lines(value: str):
    return [line.strip() for line in (value or "").splitlines() if line.strip()]


def _kv_lines(value: str):
    data = {}
    for line in _lines(value):
        if ":" not in line:
            raise ValidationError(f"Linea invalida: '{line}'. Usa el formato clave: valor.")
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if not key:
            raise ValidationError(f"Linea invalida: '{line}'. Falta la clave.")
        data[key] = val
    return data


def _link_lines(value: str):
    items = []
    for line in _lines(value):
        if "|" in line:
            label, url = [p.strip() for p in line.split("|", 1)]
            if not url:
                raise ValidationError(f"Linea invalida: '{line}'. Falta la URL.")
            items.append({"label": label, "url": url})
        else:
            if not line.startswith("http"):
                raise ValidationError(
                    f"Linea invalida: '{line}'. Usa 'Etiqueta | URL' o solo una URL."
                )
            items.append({"label": "", "url": line})
    return items


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        if data in self.empty_values:
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        cleaned = []
        for f in data:
            cleaned.append(super().clean(f, initial))
        return cleaned


class ProjectForm(forms.ModelForm):
    cover_images = MultipleFileField(
        required=False,
        label="Imagenes del proyecto",
        widget=MultipleFileInput(),
        help_text="Puedes seleccionar varias imagenes.",
    )
    badges_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Badges",
        help_text="Una por linea.",
    )
    tags_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Tags",
        help_text="Una por linea.",
    )
    team_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        label="Equipo",
        help_text="Una persona por linea.",
    )
    materials_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Materiales",
        help_text="Uno por linea.",
    )
    finishing_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Acabados",
        help_text="Uno por linea.",
    )
    process_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        label="Proceso",
        help_text="Un paso por linea.",
    )
    challenges_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Desafios",
        help_text="Uno por linea.",
    )
    metrics_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Metricas",
        help_text="Formato: clave: valor (una por linea).",
    )
    specs_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Specs",
        help_text="Formato: clave: valor (una por linea).",
    )
    links_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Links",
        help_text="Formato: Etiqueta | URL (una por linea).",
    )
    timeline_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        label="Timeline",
        help_text="Usa: inicio: YYYY-MM-DD y/o entrega: YYYY-MM-DD",
    )

    class Meta:
        model = Project
        fields = (
            "title",
            "slug",
            "summary",
            "category",
            "badges_text",
            "tags_text",
            "client",
            "role",
            "team_text",
            "problem",
            "materials_text",
            "finishing_text",
            "process_text",
            "challenges_text",
            "outcome",
            "metrics_text",
            "timeline_text",
            "links_text",
            "specs_text",
            "is_public",
            "is_featured",
            "sort_order",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if not instance:
            return
        self.fields["badges_text"].initial = "\n".join(instance.badges or [])
        self.fields["tags_text"].initial = "\n".join(instance.tags or [])
        self.fields["team_text"].initial = "\n".join(instance.team or [])
        self.fields["materials_text"].initial = "\n".join(instance.materials or [])
        self.fields["finishing_text"].initial = "\n".join(instance.finishing or [])
        self.fields["process_text"].initial = "\n".join(instance.process or [])
        self.fields["challenges_text"].initial = "\n".join(instance.challenges or [])
        self.fields["metrics_text"].initial = "\n".join(
            f"{k}: {v}" for k, v in (instance.metrics or {}).items()
        )
        self.fields["specs_text"].initial = "\n".join(
            f"{k}: {v}" for k, v in (instance.specs or {}).items()
        )
        link_lines = []
        for l in (instance.links or []):
            if isinstance(l, dict):
                line = f"{l.get('label', '').strip()} | {l.get('url', '').strip()}".strip(" |")
                if line:
                    link_lines.append(line)
            elif isinstance(l, str):
                link_lines.append(l)
        self.fields["links_text"].initial = "\n".join(link_lines)
        self.fields["timeline_text"].initial = "\n".join(
            f"{k}: {v}" for k, v in (instance.timeline or {}).items()
        )

    def clean(self):
        cleaned = super().clean()
        cleaned["badges"] = _lines(cleaned.get("badges_text", ""))
        cleaned["tags"] = _lines(cleaned.get("tags_text", ""))
        cleaned["team"] = _lines(cleaned.get("team_text", ""))
        cleaned["materials"] = _lines(cleaned.get("materials_text", ""))
        cleaned["finishing"] = _lines(cleaned.get("finishing_text", ""))
        cleaned["process"] = _lines(cleaned.get("process_text", ""))
        cleaned["challenges"] = _lines(cleaned.get("challenges_text", ""))

        try:
            cleaned["metrics"] = _kv_lines(cleaned.get("metrics_text", ""))
        except ValidationError as exc:
            self.add_error("metrics_text", exc)
            cleaned["metrics"] = {}

        try:
            cleaned["specs"] = _kv_lines(cleaned.get("specs_text", ""))
        except ValidationError as exc:
            self.add_error("specs_text", exc)
            cleaned["specs"] = {}

        try:
            cleaned["links"] = _link_lines(cleaned.get("links_text", ""))
        except ValidationError as exc:
            self.add_error("links_text", exc)
            cleaned["links"] = []

        try:
            timeline = _kv_lines(cleaned.get("timeline_text", ""))
            allowed = {"inicio", "entrega"}
            invalid = [k for k in timeline.keys() if k not in allowed]
            if invalid:
                raise ValidationError("Timeline solo acepta: inicio, entrega.")
            cleaned["timeline"] = timeline
        except ValidationError as exc:
            self.add_error("timeline_text", exc)
            cleaned["timeline"] = {}
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        cleaned = getattr(self, "cleaned_data", {})
        instance.badges = cleaned.get("badges", [])
        instance.tags = cleaned.get("tags", [])
        instance.team = cleaned.get("team", [])
        instance.materials = cleaned.get("materials", [])
        instance.finishing = cleaned.get("finishing", [])
        instance.process = cleaned.get("process", [])
        instance.challenges = cleaned.get("challenges", [])
        instance.metrics = cleaned.get("metrics", {})
        instance.timeline = cleaned.get("timeline", {})
        instance.links = cleaned.get("links", [])
        instance.specs = cleaned.get("specs", {})
        if commit:
            instance.save()
        return instance
