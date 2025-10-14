
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
    "jig-x12": {
        "slug": "jig-x12",
        "title": "Jig de alineación X12",
        "summary": "Útil de posicionamiento para ensamblaje repetitivo en línea.",
        "category": "industria",
        "badges": ["Entrega 48h", "Serie corta"],
        "images": ["img/jigx12.png",

                   ],
        "tags": ["PETG", "±0.2 mm"],

        # — Historia —
        "client": "Línea de montaje automotriz (conf.)",
        "role": "Diseño + fabricación",
        "team": ["Diseño mecánico", "Operación FDM"],
        "problem": "Reducir tiempos de alineación y variabilidad entre operarios.",
        "materials": ["PETG negro", "Tornillería M5", "Insertos latón M5"],
        "finishing": ["Lijado ligero en caras de contacto", "Roscas con inserto térmico"],
        "process": [
            "Relevamiento en línea y ajuste de tolerancias (±0.2 mm).",
            "Diseño paramétrico con nervaduras para rigidez sin peso extra.",
            "Impresión FDM 0.4 mm / 0.28 capa / 4 perímetros / 35% infill.",
            "Prueba en banco + iteración 1: cambio de asa y chaflán guía.",
        ],
        "challenges": [
            "Evitar flexión en saliente larga.",
            "Compatibilidad con guantes y herramientas manuales."
        ],
        "outcome": "Útil robusto, ergonómico y fácil de reemplazar en planta.",
        "metrics": {"ahorro_tiempo": "−35% en ciclo", "rechazos": "−60%", "peso": "−28% vs. versión metal"},
        "timeline": {"inicio": "2025-08-01", "entrega": "2025-08-03"},
        "links": [],
    },

    "display-portamenu-pro": {
        "slug": "display-portamenu-pro",
        "title": "Display portamenú PRO",
        "summary": "Exhibidor modular con branding y acabado premium.",
        "category": "retail",
        "badges": ["Personalizado", "Acabado pintura"],
        "images": ["img/menu.png"],
        "tags": ["Branding"],
        "client": "Cadena de restaurantes (conf.)",
        "role": "Diseño industrial + prototipado",
        "team": ["Modelado 3D", "Pintura poliuretano"],
        "problem": "Portamenús pesados, poco estables y sin identidad de marca.",
        "materials": ["PLA reforzado", "Acrílico 3 mm", "Vinil impreso"],
        "finishing": ["Primer + pintura PU satinado", "Logotipo INGENI aplicado"],
        "process": [
            "Diseño base desmontable para transporte.",
            "Optimización de centro de masa para estabilidad en barra.",
            "Plantilla para acrílico y ranuras anti-deslizamiento."
        ],
        "challenges": ["Resistencia a limpieza diaria con químicos.", "Evitar marcas de capa visibles."],
        "outcome": "Pieza ligera, estable y con branding consistente.",
        "metrics": {"peso": "−40% vs. MDF", "tiempo_armado": "< 30 s"},
        "timeline": {"inicio": "2025-07-10", "entrega": "2025-07-14"},
        "links": [],
    },

    "panel-fachada-parametrico": {
        "slug": "panel-fachada-parametrico",
        "title": "Panel de fachada paramétrico",
        "summary": "Módulos ligeros para ensayo de fachada ventilada.",
        "category": "arquitectura",
        "badges": ["Gran formato", "Prototipo"],
        "images": ["img/GranFormato.png"],
        "tags": ["Paramétrico", "Gran formato"],
        "client": "Estudio de arquitectura (conf.)",
        "role": "Parametrización + fabricación",
        "team": ["Computational design", "Post-proceso"],
        "problem": "Validar patrón y uniones de un sistema modular sin moldes costosos.",
        "materials": ["PLA+ (prototipo)", "Tornillería M4", "Anclajes impresos"],
        "finishing": ["Lijado grano 320", "Pintura base para visualización"],
        "process": [
            "Generación de paneles con Grasshopper; límites de boquilla 0.8.",
            "Segmentación por volumen de impresión y solapes atornillados.",
            "Plantillas de montaje y numeración por módulo."
        ],
        "challenges": ["Deformación por contracción en piezas largas.", "Tolerancias en uniones múltiples."],
        "outcome": "Prototipo montado, validación de ritmo y uniones.",
        "metrics": {"paneles": "12 uds", "tiempo_montaje": "90 min (2 personas)"},
        "timeline": {"inicio": "2025-06-01", "entrega": "2025-06-07"},
        "links": [],
    },

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
