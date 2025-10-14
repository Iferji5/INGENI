from django import forms


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
