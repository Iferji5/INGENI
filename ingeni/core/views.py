
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import ContactForm


logger = logging.getLogger(__name__)


def home(request):
    return render(request, "home.html")


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
    "solucion-modular-1": {
        "slug": "solucion-modular-1",
        "title": "Solución modular 1",
        "summary": "Componentes optimizados para ensamblajes precisos.",
        "category": "gran-escala",
        "category_label": "Proyectos a gran escala",
        "price": 0,  # o None si cotizas a medida
        "images": ["img/Proyectos_gran_escala.png"],
        "features": ["Diseño paramétrico", "Refuerzos en zonas de carga"],
        "specs": {"Material": "PLA/PETG", "Tolerancia": "±0.2 mm"},
        "tags": ["Batch corto","Alta rigidez"],
        "downloads": [{"label":"Ficha técnica (PDF)", "url": "/static/docs/sol-mod-1.pdf"}],
        "use_cases": ["Estructuras de stand", "Señalización de gran formato"],
        "faq": [
            {"q":"¿Soporta intemperie?", "a":"Recomendamos PETG o ASA con recubrimiento."},
        ],
    },
    "solucion-modular-2": {
        "slug": "solucion-modular-2",
        "title": "Solución modular 2",
        "summary": "Prototipos rápidos de escritorio.",
        "category": "baja-escala",
        "category_label": "Proyectos a baja escala",
        "images": ["img/Proyectos_baja_escala.png"],    # ← uniformado (no 'image')
        "features": ["Iteración rápida", "Coste reducido"],
        "specs": {"Volumen": "200×200×200 mm"},
        "tags": ["Prototipo","Express"],
    },
    "solucion-modular-3": {
        "slug": "solucion-modular-3",
        "title": "Solución modular 3",
        "summary": "Diseño a medida según tu idea.",
        "category": "personalizados",
        "category_label": "Trabajos personalizados",
        "images": ["img/personalizados.png"],
        "features": ["Co-diseño con el cliente"],
        "specs": {"Entrega": "Según alcance"},
        "tags": ["Custom"],
    },

    "jig-alineacion-a": {
        "slug": "jig-alineacion-a",
        "title": "Jig de alineación A",
        "summary": "Útil de posicionamiento para ensamblajes repetitivos.",
        "category": "funcionales",
        "category_label": "Artículos funcionales",
        "price": None,
        "images": ["img/jig.png"],
        "features": ["Pines de centrado", "Asas ergonómicas", "Color por etapa"],
        "specs": {"Superficie": "120×80 mm", "Material": "PETG/TPU"},
        "tags": ["Jig", "Ensambles"],
        "downloads": [],
        "use_cases": ["Alineación de tapas", "Verificación dimensional"],
        "faq": [],
    },


    "integracion-escaner-3d": {
        "slug": "integracion-escaner-3d",
        "title": "Integración de escáner 3D",
        "summary": "Flujo completo: captura → malla → CAD → inspección.",
        "category": "equipos",
        "category_label": "Equipos",
        "price": None,
        "images": ["img/escaner_3D.png"],
        "features": ["Calibración", "Pipeline automatizado", "SOPs y capacitación"],
        "specs": {"Precisión": "hasta 0.05 mm", "Formatos": "OBJ, STL, PLY"},
        "tags": ["Escaneo 3D", "Reverse"],
        "downloads": [],
        "use_cases": ["Ingeniería inversa", "Control de calidad"],
        "faq": [],
    },

    "logo-3d-barra": {
        "slug": "logo-3d-barra",
        "title": "Logo 3D para barra",
        "summary": "Logotipo retroiluminado para alto impacto visual.",
        "category": "mercaderia",
        "category_label": "Mercadería (bares, restaurantes, etc.)",
        "price": None,
        "images": ["img/mercaderia.png"],
        "features": ["LED regulable", "Difusor homogéneo", "Fijación oculta"],
        "specs": {"Ancho": "400 mm", "Alimentación": "12 VDC"},
        "tags": ["Display", "Iluminación"],
        "downloads": [],
        "use_cases": ["Barras", "Retail"],
        "faq": [],
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
        "badges": ["Diseño personalizado", "Entrega 5 dias", "Gran Formato"],
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
        "badges": ["Serie corta", "Personalización", "Entrega 72h"],
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

    "soporte-funcional-linea": {
        "slug": "soporte-funcional-linea",
        "title": "Soporte funcional de línea",
        "summary": "Bracket robusto para guiado y fijación de componentes.",
        "category": "industria",
        "badges": ["Entrega 72h", "Tolerancia ±0.2 mm"],
        "images": ["img/Soporte.png"],
        "tags": ["Fixture", "Guiado"],
        "client": "Planta de ensamble (conf.)",
        "role": "Diseño + validación",
        "team": ["CAD", "Operación FDM"],
        "problem": "Sujeción estable sin mecanizado CNC urgente.",
        "materials": ["PETG naranja", "Inserto M6", "Tornillería DIN"],
        "finishing": ["Avellanados", "Roscas insertadas"],
        "process": [
            "Topología con refuerzos en Z y filetes de 2 mm.",
            "Pruebas de carga estática y ajuste de luz.",
        ],
        "challenges": ["Vibración de línea", "Contacto con aceite mineral"],
        "outcome": "Soporte estable; reemplazo rápido si se daña.",
        "metrics": {"coste": "−65% vs. mecanizado", "plazo": "72 h"},
        "timeline": {"inicio": "2025-05-18", "entrega": "2025-05-21"},
        "links": [],
    },

    "logo-3d-retroiluminado": {
        "slug": "logo-3d-retroiluminado",
        "title": "Logo 3D retroiluminado",
        "summary": "Identidad de marca con difusor homogéneo y montaje oculto.",
        "category": "retail",
        "badges": ["Iluminación LED", "Personalizable"],
        "images": ["img/letrero_iluminado.png"],
        "tags": ["LED", "Branding"],
        "client": "Bar & Co. (conf.)",
        "role": "Diseño + integración eléctrica",
        "team": ["Diseño", "Electricidad baja tensión"],
        "problem": "Logo visible en ambiente oscuro sin hotspots de LED.",
        "materials": ["PLA blanco", "Difusor PETG translúcido", "LED 12V"],
        "finishing": ["Pintura negra trasera", "Cableado oculto"],
        "process": [
            "Cavidades internas y separación LED-difusor 12–15 mm.",
            "Pruebas de uniformidad y fijación invisible a muro."
        ],
        "challenges": ["Disipación de calor", "Paso de cables oculto"],
        "outcome": "Logo con halo suave y montaje limpio.",
        "metrics": {"consumo": "≤ 9 W", "peso": "≤ 600 g"},
        "timeline": {"inicio": "2025-04-02", "entrega": "2025-04-06"},
        "links": [],
    },

    "maqueta-volumetrica-s": {
        "slug": "maqueta-volumetrica-s",
        "title": "Maqueta volumétrica S",
        "summary": "Modelos de escritorio para validación de forma y proporción.",
        "category": "arquitectura",
        "badges": ["Iteración rápida", "SLA/FDM"],
        "images": ["img/maqueta_volumtrica.png"],
        "tags": ["Maqueta", "Escala 1:200"],
        "client": "Estudio XYZ (conf.)",
        "role": "Modelado + impresión",
        "team": ["SLA detalle", "FDM base"],
        "problem": "Evaluar volumetría y sombras antes del anteproyecto.",
        "materials": ["Resina blanca (SLA)", "PLA gris (FDM)"],
        "finishing": ["Lijado fino", "Ensamble con pasadores"],
        "process": [
            "Simplificación CAD y separación por color/material.",
            "Base en FDM y detalles en SLA, unión por pasadores."
        ],
        "challenges": ["Fragilidad en piezas delgadas", "Planitud de base"],
        "outcome": "Lectura clara de masas y jerarquías.",
        "metrics": {"tiempo_total": "48 h", "piezas": "14"},
        "timeline": {"inicio": "2025-03-15", "entrega": "2025-03-17"},
        "links": [],
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

from django.http import Http404
from django.shortcuts import render

def project_detail(request, slug):
    project = _get_project(slug)
    if not project:
        raise Http404("Proyecto no encontrado")
    return render(request, "project_detail.html", {"project": project})
