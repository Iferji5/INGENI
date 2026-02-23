
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.db.utils import OperationalError, ProgrammingError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
import os
from django.templatetags.static import static
from django.urls import reverse

from django.contrib.admin.views.decorators import staff_member_required

from .forms import ContactForm, ProjectForm
from .models import Project, ProjectImage


logger = logging.getLogger(__name__)


def home(request):
    try:
        projects_qs = Project.objects.filter(is_public=True).order_by(
            "-is_featured", "sort_order", "-updated_at"
        )
        projects = [_serialize_project(p) for p in projects_qs]
    except (OperationalError, ProgrammingError):
        projects = []
    if not projects:
        projects = [_serialize_legacy_project(_get_project(slug)) for slug in PROJECTS.keys()]
        projects = [p for p in projects if p]
    return render(request, "home.html", {"projects": projects})


PRODUCT_DEFAULTS = {
    "summary": "",
    "category": "",
    "category_label": "",
    "price": None,
    "images": [],
    "features": [],
    "specs": {},
    "tags": [],
    "downloads": [],
    "use_cases": [],
    "faq": [],
}


PRODUCTS = {
    "decoracion-arte": {
        "slug": "decoracion-arte",
        "title": "Decoración & Arte",
        "summary": "Piezas decorativas, esculturas y elementos de ambientación con acabados premium.",
        "category": "decoracion-arte",
        "category_label": "Decoración & Arte",
        "price": None,
        "images": ["img/arte.png"],
        "features": ["Detalle artístico de alta precisión", "Acabado premium personalizado", "Gran formato disponible","Edición exclusiva bajo pedido","Presencia visual imponente" ],

    },
    "senaletica-branding": {
        "slug": "senaletica-branding",
        "title": "Señalética & Branding",
        "summary": "Letras corpóreas, logotipos, displays y señalética para potenciar tu marca.",
        "category": "senaletica-branding",
        "category_label": "Señalética & Branding",
        "price": None,
        "images": ["img/senales.png"],
        "features": [
  "Iluminación LED opcional",
  "Montaje limpio y seguro",
  "Material resistente y duradero",
  "Acabado mate o brillante",
  "Impresión 3D de alta precisión",
  "Colores personalizados",
  "Uso interior y exterior",
  "Fácil instalación",
  "Diseño moderno y profesional",
  "Alta visibilidad"
],

    },
    "productos-personalizados": {
        "slug": "productos-personalizados",
        "title": "Productos Personalizados",
        "summary": "Objetos únicos con tu idea, medidas y branding.",
        "category": "productos-personalizados",
        "category_label": "Productos Personalizados",
        "price": None,
        "images": ["img/personalizados.png"],
        "features": [
  "Iluminación LED integrada",
  "Diseño personalizado a pedido",
  "Material resistente y duradero",
  "Acabado premium mate o brillante",
  "Colores y nombres personalizables",
  "Alta visibilidad en interiores",
  "Ideal para eventos y celebraciones",
  "Instalación sencilla",
  "Impresión 3D de alta precisión",
  "Detalles en relieve y multicolor"
]


    },
    "organizacion-utilidad": {
        "slug": "organizacion-utilidad",
        "title": "Organización & Utilidad",
        "summary": "Herramientas, organizadores y piezas funcionales para uso diario o industrial.",
        "category": "organizacion-utilidad",
        "category_label": "Organización & Utilidad",
        "price": None,
        "images": ["img/utilidad.png"],
        "features": [
  "Diseño funcional y práctico",
  "Optimización de espacios",
  "Material resistente de alta durabilidad",
  "Impresión 3D de precisión",
  "Personalización de medidas y diseño",
  "Soluciones a medida",
  "Fácil instalación y uso",
  "Ideal para hogar y negocio",
  "Acabado limpio y profesional",
  "Producción en pequeñas y grandes cantidades"
],

    },
    "gran-formato": {
        "slug": "gran-formato",
        "title": "Gran Formato",
        "summary": "Estructuras, displays y piezas de gran volumen con alta presencia.",
        "category": "gran-formato",
        "category_label": "Gran Formato",
        "price": None,
        "images": ["img/GranFormato.png"],
        "features": [
  "Impresión 3D en gran formato",
  "Diseños personalizados a escala real",
  "Alta resistencia estructural",
  "Acabados profesionales y detallados",
  "Ideal para decoración comercial",
  "Impacto visual de gran escala",
  "Materiales duraderos",
  "Montaje seguro y estable"
],

    },
}

def productos(request):
    return render(request, "productos.html", {"products": PRODUCTS.values()})

def product_detail(request, slug):
    product = PRODUCTS.get(slug)
    if not product:
        raise Http404("Producto no encontrado")
    return render(request, "product_detail.html", {"product": product})


def sobre(request):
    return render(request, "sobre.html")


def contacto(request):
    initial = {}
    ref = request.GET.get("ref")
    if ref:
        initial["asunto"] = f"Consulta sobre {ref}"

    success_message = None

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            project_label = form.get_project_label()
            message_lines = [
                "Nuevo mensaje desde el sitio web INGENI:",
                "",
                f"Nombre: {data['nombre']}",
                f"Correo: {data['email']}",
                f"Tipo de proyecto: {project_label or data['proyecto']}",
                f"Asunto: {data['asunto']}",
                "",
                data["mensaje"],
                "",
                f"URL del formulario: {request.build_absolute_uri()}",
            ]
            email = EmailMessage(
                subject=f"[INGENI] {data['asunto']}",
                body="\n".join(message_lines),
                from_email=settings.DEFAULT_FROM_EMAIL or None,
                to=[settings.CONTACT_EMAIL],
                reply_to=[data["email"]],
            )

            try:
                email.send(fail_silently=False)
            except Exception:
                logger.exception("No se pudo enviar el correo de contacto.")
                form.add_error(None, "No pudimos enviar tu mensaje. Intenta nuevamente en unos minutos.")
            else:
                request.session["contact_last_project"] = project_label
                request.session["contact_last_name"] = data["nombre"]
                return redirect(f"{reverse('contacto')}?enviado=1")
    else:
        form = ContactForm(initial=initial)

    if request.method == "GET" and request.GET.get("enviado"):
        last_name = request.session.pop("contact_last_name", None)
        last_project = request.session.pop("contact_last_project", None)
        if last_name and last_project:
            success_message = f"\u00a1Gracias, {last_name}! Te contactaremos sobre: {last_project}."
        elif last_name:
            success_message = f"\u00a1Gracias, {last_name}! Nos pondremos en contacto muy pronto."
        elif last_project:
            success_message = f"\u00a1Gracias! Te contactaremos sobre: {last_project}."
        else:
            success_message = "\u00a1Gracias! Tu mensaje ha sido enviado."

    return render(
        request,
        "contacto.html",
        {
            "form": form,
            "success_message": success_message,
        },
    )




PROJECT_DEFAULTS = {
    # Básico
    "slug": "",
    "title": "",
    "summary": "",
    "category": "",
    "badges": [],
    "images": [],
    "tags": [],

    # Historia del proyecto
    "client": "",
    "role": "",
    "team": [],
    "problem": "",
    "materials": [],
    "finishing": [],
    "process": [],
    "challenges": [],
    "outcome": "",

    # Métricas y tiempos (opcional)
    "metrics": {},
    "timeline": {"inicio": "", "entrega": ""},

    # Extras (opcionales)
    "links": [],
    "specs": {},
}


PROJECTS = {
    "porta-shots": {
        "slug": "porta-shots",
        "title": "Porta-shots de Guitarra",
        "summary": "Soporte modular para presentación y servicio de shots en eventos, fabricado mediante manufactura aditiva.",
        "category": "diseño de producto",
        "badges": ["Diseño personalizado", "Gran Formato"],
        "images": ["img/porta-shots.png", "img/guitar_shots-01.jpeg", "img/guitar_shots-02.jpeg", "img/guitar_shots-03.jpg"],
        "tags": ["PLA+", "0.16 mm capa", "Bambu Lab X1C"],

        # — Historia —
        "client": "Fulcro Studio",
        "role": "Diseño + fabricación",
        "team": ["Iván Fernández"],
        "problem": "Crear un soporte resistente, atractivo y modular que facilite el transporte y la exposición de vasos tipo shot sin riesgo de vuelco.",
        "materials": ["PLA/PETG + negro mate", "adhesivo cianoacrilato", "pintura acrílica"],
        "finishing": [
            "Lijado progresivo (grano 200–600)",
            "Pintura en aerosol negro satinado",
            "Sellado con barniz protector UV"
        ],
        "process": [
            "Diseño paramétrico en Fusion 360.",
            "Validación de dimensiones con prototipo a escala reducida.",
            "Impresión FDM 0.16 mm capa / 4 perímetros / 20% infill.",
            "Montaje de componentes impresos y unión con adhesivo industrial.",
            "Recubriendo base premier, lijado progresivo."
        ],
        "challenges": [
            "Evitar deformaciones en las cavidades circulares tras múltiples usos.",
            "Optimizar la rigidez estructural con el mínimo consumo de material.",
            "Garantizar un acabado homogéneo y sin líneas visibles de capa."
        ],
        "outcome": "Un porta-shots ergonómico, elegante y fácil de reproducir. El diseño modular permite escalar su capacidad y personalizar el branding según la marca o evento.",

        "metrics": {
            "tiempo_impresion": "9h 45min",
            "peso_total": "312g",
            "versiones_iteradas": 3
        },
        "timeline": {"inicio": "2025-09-10", "entrega": "2025-09-25"},
        "links": [],
    },

     "Gundam-Head": {
        "slug": "Gundam-Head",
        "title": "Gundam Unicorn real size head",
        "summary": "Cabeza de Gundam estilo mecha, fabricada mediante impresión 3D FDM, con diseño angular, alto nivel "
                   "de detalle y acabado tipo maqueta coleccionable. La pieza destaca por sus antenas frontales amarillas, "
                   "visor rojo y geometría mecánica inspirada en modelos clásicos de Gundam. ",
        "category": "Personalizados",
        "badges": ["Serie corta", "Personalización"],
        "images": ["img/Gundam-head-01.jpeg","img/Gundam-head-02.jpeg","img/Gundam-head-03.jpeg"],
        "tags": ["Impresión 3D FDM", "0.28 mm", "post-proceso: Lijado y pintura manual"],

        # — Historia —

        "materials": ["PETG blanco (estructura principal)", "PETG amarillo (antenas)", "PETG rojo (visor)", "Tornillería interna / ensamble por encastre (según versión)."],
        "finishing": [
            "Lijado fino de aristas visibles",
            "pintura acrílica mate/satinada",
            "sellado con barniz protector UV y detalles pintados a mano para resaltar volúmenes mecánicos."
        ],
        "process": [
            "Selección y ajuste del modelo 3D (escala y proporciones).",
            "Separación del modelo en piezas para impresión optimizada.",
            "Impresión FDM en PETG (0.28 mm, 4 perímetros, ~30% infill).",
            "Limpieza de soportes y lijado progresivo.",
            "Ensamble de piezas (encastre/adhesivo)",
            "Pintura base, detalles y sellado final."
        ],
        "challenges": [
            "Mantener precisión en piezas angulares pequeñas.",
            "Evitar deformaciones en antenas largas.",
            "Lograr alineación simétrica del rostro y visor.",
            "Conseguir contraste limpio entre colores sin sangrado."
        ],
        "outcome": "Modelo de cabeza Gundam altamente reconocible, con excelente presencia visual y acabado sólido. "
                   "Las proporciones y el contraste de colores realzan los rasgos mecha, logrando una pieza llamativa incluso en espacios con iluminación media.",

        "metrics": {
            "≈ 25 - 30cm": "Altura",
            "≈ 18 - 22cm": "Ancho",
            "≈ 1.5 - 2kg)": "Peso",

        },
        "timeline": {"inicio": "2025-10-10", "entrega": "2025-10-14"},

    },

    "Small-3D-Printed-Products": {
    "slug": "Small-3D-Printed-Products",
    "title": "Producción en serie de objetos personalizados impresos en 3D",
    "summary": "Colección de proyectos de impresión 3D enfocados en la fabricación en lote de objetos pequeños "
               "personalizados, como marcos decorativos, llaveros y recuerdos. Estas piezas combinan impresión FDM, "
               "ensamble manual y elementos personalizados como fotografías, textos y decoraciones en relieve, "
               "permitiendo producir múltiples unidades con estética consistente y acabado artesanal.",

    "category": "Producción en serie",
    "badges": ["Impresión 3D", "Producción en lote", "Personalización"],
    "images": ["img/mothers-day1.jpg","img/mothers-day2.jpg","img/mini-guitars.jpg"],
    "tags": ["Impresión 3D FDM", "Producción artesanal", "Objetos personalizados"],

    "materials": [
        "PLA (estructura principal)",
        "PLA de colores para detalles decorativos",
        "Fotografías impresas (según proyecto)",
        "Aros metálicos para llaveros",
        "Adhesivos de ensamblaje"
    ],

    "finishing": [
        "Remoción de soportes",
        "lijado ligero en bordes visibles",
        "ensamblaje manual de componentes",
        "colocación de elementos personalizados",
        "control visual de calidad por lote"
    ],

    "process": [
        "Diseño o adaptación de modelos 3D pequeños.",
        "Optimización para impresión en múltiples unidades.",
        "Impresión FDM en PLA.",
        "Post-proceso y limpieza de piezas.",
        "Ensamble manual de accesorios y decoraciones.",
        "Revisión final del lote."
    ],

    "challenges": [
        "Mantener consistencia dimensional entre múltiples unidades.",
        "Reducir tiempos de impresión en producción en serie.",
        "Evitar deformaciones en piezas pequeñas.",
        "Asegurar calidad uniforme en ensamblaje manual."
    ],

    "outcome": "Producción eficiente de múltiples objetos personalizados con acabado uniforme y buena resistencia. "
               "La combinación de impresión 3D y ensamblaje manual permite crear recuerdos únicos manteniendo "
               "repetibilidad en la fabricación.",

    "metrics": {
        "≈ 6 - 20cm": "Altura de piezas",
        "≈ 50 - 200g": "Peso promedio por unidad",
        "10 - 40 unidades": "Producción por lote"
    },

    "timeline": {"inicio": "2025-10-20", "entrega": "2025-10-23"}
}

,

    "3D-Printed-Signs": {
        "slug": "3D-Printed-Signs",
        "title": "Señales personalizadas impresas en 3D",
        "summary": "Señales y rótulos funcionales fabricados mediante impresión 3D FDM, diseñados para espacios comerciales, "
                   "oficinas y hogares. Incluye texto en relieve o bajo relieve, iconografía clara y bordes limpios para "
                   "mejor legibilidad. Las piezas pueden producirse en colores contrastantes (fondo/letras) y con acabados "
                   "tipo placa profesional para montaje en pared, puerta o señalización interna. ",
        "category": "Personalizados",
        "badges": ["Serie corta", "Personalización"],
        "images": ["img/sing_1.png","img/sing_2.png","img/sing_3.png"],
        "tags": ["Impresión 3D FDM", "0.20 - 0.28 mm", "post-proceso: Lijado y pintura manual"],

        # — Historia —

        "materials": ["PLA/PETG (estructura principal)", "PLA/PETG color contraste (texto o marco)", "Adhesivo (montaje)", "Cinta doble cara / tornillería (según instalación)."],
        "finishing": [
            "Lijado fino de bordes visibles",
            "pintura acrílica mate/satinada (opcional)",
            "sellado con barniz protector (opcional) y limpieza final para resaltar relieve y mejorar legibilidad."
        ],
        "process": [
            "Diseño del rótulo (texto, íconos y medidas).",
            "Conversión a 3D con relieve/bajo relieve y preparación de tolerancias.",
            "Impresión FDM en PLA/PETG (0.20–0.28 mm, 3-4 perímetros, ~15-30% infill).",
            "Remoción de soportes y lijado progresivo.",
            "Ensamble de capas (fondo/letras) si aplica (encastre/adhesivo).",
            "Acabado final y preparación para montaje (cinta/tornillos)."
        ],
        "challenges": [
            "Mantener legibilidad en tipografías pequeñas.",
            "Evitar warping en placas planas de gran superficie.",
            "Lograr alineación limpia entre letras y fondo en diseños multicapa.",
            "Conseguir contraste uniforme sin marcas visibles de adhesivo o pintura."
        ],
        "outcome": "Señales impresas en 3D con acabado consistente y lectura clara a distancia corta y media. "
                   "El relieve y el contraste mejoran la visibilidad, mientras que la fabricación por capas permite "
                   "personalización rápida en nombres, números, pictogramas y estilos de montaje.",

        "metrics": {


        },
        "timeline": {"inicio": "2025-11-05", "entrega": "2025-11-12"},

    },

    "Metallic-Designer-Figure": {
        "slug": "Metallic-Designer-Figure",
        "title": "Figura tipo designer toy acabado metálico",
        "summary": "Escultura estilo designer toy con acabado metálico brillante y superficies altamente reflectivas. "
                   "La pieza presenta proporciones estilizadas, extremidades redondeadas y cabeza icónica con ojos en forma de X, "
                   "inspirada en el arte urbano contemporáneo. Su acabado glossy resalta volúmenes y curvas, generando "
                   "una presencia visual fuerte y estética premium ideal para exhibición en espacios modernos o boutiques. ",
        "category": "Arte / Escultura decorativa",
        "badges": ["Edición artística", "Acabado premium", "Exhibición"],
        "images": [
            "img/metallic-figure-black-01.jpg",
            "img/metallic-figure-green-01.jpg",
            "img/metallic-figure-green-02.jpg",
            "img/metallic-figure-black-02.jpg"
        ],
        "tags": ["Designer Toy", "Acabado brillante", "Escultura contemporánea"],

        # — Historia —

        "materials": [
            "Resina / Filamento (estructura base)",
            "Primer de preparación de superficie",
            "Pintura automotriz metálica",
            "Barniz gloss de alto brillo"
        ],
        "finishing": [
            "Lijado progresivo de superficie",
            "Aplicación de primer y sellado",
            "Pintura metálica multicapa",
            "Barnizado gloss para acabado espejo"
        ],
        "process": [
            "Preparación del modelo base (impresión o moldeado).",
            "Corrección de imperfecciones superficiales.",
            "Aplicación de primer para uniformidad.",
            "Pintura metálica en capas finas.",
            "Secado controlado y aplicación de barniz protector.",
            "Pulido final para efecto brillante uniforme."
        ],
        "challenges": [
            "Evitar imperfecciones visibles en superficies reflectivas.",
            "Mantener uniformidad del color metálico en curvas amplias.",
            "Controlar reflejos no deseados durante el barnizado.",
            "Preservar proporciones originales sin pérdida de detalle."
        ],
        "outcome": "Figura escultórica con acabado metálico profundo y alto impacto visual. "
                   "El efecto reflectivo potencia la estética contemporánea y convierte la pieza "
                   "en un elemento decorativo protagonista en ambientes de exhibición o retail.",

        "metrics": {
            "≈ 35 - 50cm": "Altura estimada",
            "≈ 3 - 6kg": "Peso estimado",
            "Acabado 100% glossy": "Tipo de superficie"
        },

        "timeline": {"inicio": "2025-11-01", "entrega": "2025-11-10"},

    },

    "Roman-Lion-Helmet": {
        "slug": "Roman-Lion-Helmet",
        "title": "Casco romano con forma de león",
        "summary": "Casco decorativo inspirado en armaduras romanas clásicas, fabricado mediante impresión 3D de alta precisión. "
                   "El diseño incorpora relieves detallados con textura orgánica, cuernos laterales y rasgos felinos "
                   "que aportan carácter imponente y presencia escultórica. Su acabado glossy o metálico resalta cada "
                   "volumen y detalle ornamental, logrando una pieza visualmente impactante para exhibición. ",
        "category": "Gran Formato",
        "badges": ["Arte funcional", "Personalizable", "Acabado premium"],
        "images": [
            "img/roman-helmet-03.jpg",
            "img/roman-helmet-01.jpg",
            "img/roman-helmet-02.jpg",
            "img/roman-helmet-04.jpg"
        ],
        "tags": ["Impresión 3D FDM", "Gran detalle", "Post-proceso avanzado"],

        # — Historia —

        "materials": [
            "PLA / PETG (estructura principal)",
            "Refuerzos internos estructurales",
            "Primer de preparación",
            "Pintura metálica / acrílica",
            "Barniz protector gloss o satinado"
        ],
        "finishing": [
            "Lijado progresivo para suavizar capas visibles",
            "Aplicación de primer para uniformidad",
            "Pintura en tonos metálicos (negro, oro u otros personalizados)",
            "Sellado final con barniz protector",
            "Revisión de simetría y detalles ornamentales"
        ],
        "process": [
            "Preparación y escalado del modelo 3D.",
            "Optimización para impresión en volumen grande.",
            "Impresión FDM en múltiples secciones (si aplica).",
            "Ensamble estructural interno.",
            "Corrección de uniones y superficie.",
            "Aplicación de pintura y acabado final."
        ],
        "challenges": [
            "Mantener nitidez en relieves profundos.",
            "Evitar deformaciones en piezas de gran tamaño.",
            "Controlar marcas de capa en superficies curvas.",
            "Lograr uniformidad en acabados metálicos reflectivos."
        ],
        "outcome": "Pieza escultórica de alto impacto visual con estética histórica reinterpretada en impresión 3D. "
                   "El casco combina detalle ornamental, presencia volumétrica y acabado profesional, convirtiéndose "
                   "en elemento central para decoración temática, colecciones o espacios comerciales.",

        "metrics": {
            "≈ 30 - 45cm": "Altura estimada",
            "≈ 2 - 5kg": "Peso aproximado",
            "Escala personalizable": "Tamaño ajustable"
        },

        "timeline": {"inicio": "2025-11-15", "entrega": "2025-11-25"},

    },
}


def _get_project(slug):
    data = PROJECTS.get(slug)
    if not data: return None
    # completa campos faltantes con defaults
    base = {**PROJECT_DEFAULTS, **data}
    base["badges"] = list(base.get("badges") or [])
    base["tags"] = list(base.get("tags") or [])
    base["images"] = list(base.get("images") or [])
    return base


def _normalize_image_paths(paths):
    urls = []
    for path in paths or []:
        if not path:
            continue
        if path.startswith("media/"):
            urls.append(f"/{path}")
            continue
        if path.startswith("http") or path.startswith("/"):
            urls.append(path)
        else:
            urls.append(static(path))
    return urls


def _serialize_legacy_project(project):
    if not project:
        return None
    images = _normalize_image_paths(project.get("images") or [])
    return {**project, "images": images}


def _serialize_project(project: Project):
    import os
    images = []
    seen = set()
    seen_names = set()
    if project.cover_image:
        images.append(project.cover_image.url)
        seen.add(project.cover_image.url)
        seen_names.add(os.path.basename(project.cover_image.name or ""))
    gallery_urls = [
        img.image.url for img in project.gallery.all().order_by("sort_order", "id")
    ]
    for url in gallery_urls:
        name = os.path.basename(url)
        if url not in seen and name not in seen_names:
            images.append(url)
            seen.add(url)
            seen_names.add(name)
    for url in _normalize_image_paths(project.images or []):
        name = os.path.basename(url)
        if url not in seen and name not in seen_names:
            images.append(url)
            seen.add(url)
            seen_names.add(name)
    return {
        "slug": project.slug,
        "title": project.title,
        "summary": project.summary,
        "category": project.category,
        "badges": list(project.badges or []),
        "images": images,
        "tags": list(project.tags or []),
        "client": project.client,
        "role": project.role,
        "team": list(project.team or []),
        "problem": project.problem,
        "materials": list(project.materials or []),
        "finishing": list(project.finishing or []),
        "process": list(project.process or []),
        "challenges": list(project.challenges or []),
        "outcome": project.outcome,
        "metrics": dict(project.metrics or {}),
        "timeline": dict(project.timeline or {}),
        "links": list(project.links or []),
        "specs": dict(project.specs or {}),
    }

def project_detail(request, slug):
    project = None
    try:
        qs = Project.objects.filter(slug=slug)
        if not request.user.is_staff:
            qs = qs.filter(is_public=True)
        obj = qs.first()
        project = _serialize_project(obj) if obj else None
    except (OperationalError, ProgrammingError):
        project = None
    if not project:
        project = _serialize_legacy_project(_get_project(slug))
    if not project:
        raise Http404("Proyecto no encontrado")
    return render(request, "project_detail.html", {"project": project})


def _staff_required(view_func):
    return staff_member_required(view_func, login_url="/panel/login/")


@_staff_required
def panel_project_list(request):
    projects = Project.objects.all().order_by("-is_featured", "sort_order", "-updated_at")
    return render(request, "panel_project_list.html", {"projects": projects})


@_staff_required
def panel_project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            uploads = form.cleaned_data.get("cover_images") or request.FILES.getlist("cover_image")
            main_source = request.POST.get("cover_main_source", "upload")
            main_index_raw = request.POST.get("cover_main_pick") or request.POST.get("cover_main_index", "0")
            main_existing_raw = request.POST.get("cover_main_existing_pick") or request.POST.get("cover_main_existing", "")
            try:
                main_index = max(0, int(main_index_raw))
            except (TypeError, ValueError):
                main_index = 0
            existing_selected = bool(main_existing_raw)
            if existing_selected:
                main_source = "existing"
            if main_source == "existing" and main_existing_raw:
                try:
                    existing_id = int(main_existing_raw)
                except (TypeError, ValueError):
                    existing_id = None
                if existing_id:
                    existing = ProjectImage.objects.filter(id=existing_id).first()
                    if existing:
                        project.cover_image = existing.image
            elif uploads:
                main_index = main_index if main_index < len(uploads) else 0
                main_file = uploads[main_index]
                project.cover_image.save(main_file.name, main_file, save=False)
            project.save()
            if uploads:
                for image in uploads:
                    ProjectImage.objects.create(project=project, image=image)
            if main_source == "upload" and uploads:
                main_name = os.path.basename(project.cover_image.name or "")
                if main_name:
                    ProjectImage.objects.filter(project=project, image__icontains=main_name).exclude(image=project.cover_image).delete()
            return redirect("panel_project_list")
    else:
        form = ProjectForm()
    return render(request, "panel_project_form.html", {"form": form, "mode": "create"})


@_staff_required
def panel_project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            uploads = form.cleaned_data.get("cover_images") or request.FILES.getlist("cover_image")
            main_source = request.POST.get("cover_main_source", "upload")
            main_index_raw = request.POST.get("cover_main_pick") or request.POST.get("cover_main_index", "0")
            main_existing_raw = request.POST.get("cover_main_existing_pick") or request.POST.get("cover_main_existing", "")
            try:
                main_index = max(0, int(main_index_raw))
            except (TypeError, ValueError):
                main_index = 0
            existing_selected = bool(main_existing_raw)
            if existing_selected:
                main_source = "existing"
            if main_source == "existing" and main_existing_raw:
                try:
                    existing_id = int(main_existing_raw)
                except (TypeError, ValueError):
                    existing_id = None
                if existing_id:
                    existing = ProjectImage.objects.filter(project=project, id=existing_id).first()
                    if existing:
                        project.cover_image = existing.image
            elif uploads:
                main_index = main_index if main_index < len(uploads) else 0
                main_file = uploads[main_index]
                project.cover_image.save(main_file.name, main_file, save=False)
            project.save()
            delete_ids = request.POST.getlist("delete_images")
            if delete_ids:
                ProjectImage.objects.filter(project=project, id__in=delete_ids).delete()
            if uploads:
                for image in uploads:
                    ProjectImage.objects.create(project=project, image=image)
            if main_source == "upload" and uploads:
                main_name = os.path.basename(project.cover_image.name or "")
                if main_name:
                    ProjectImage.objects.filter(project=project, image__icontains=main_name).exclude(image=project.cover_image).delete()
            return redirect("panel_project_list")
    else:
        form = ProjectForm(instance=project)
    return render(
        request,
        "panel_project_form.html",
        {"form": form, "mode": "edit", "project": project},
    )


@_staff_required
def panel_project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        project.delete()
        return redirect("panel_project_list")
    return render(request, "panel_project_delete.html", {"project": project})
