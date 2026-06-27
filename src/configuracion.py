from enum import IntEnum
from dataclasses import dataclass, field


class Estado(IntEnum):
    SANO = 0
    INFECTADO = 1
    INMUNE = 2
    MUERTO = 3


ANCHO_SIM = 800
ALTO_SIM = 500
ANCHO_GRAFICO = 800
ALTO_GRAFICO = 150
ANCHO_CONTROL = 280
ALTO_BARRA = 50
NUM_INDIVIDUOS = 150
INICIAL_INFECTADOS = 3
INTERVALO_GRAFICO = 5
MAX_HISTORIAL = 2000


COLORES: dict[Estado, str] = {
    Estado.SANO: "#00A8FF",
    Estado.INFECTADO: "#FF4757",
    Estado.INMUNE: "#2ED573",
    Estado.MUERTO: "#747D8C",
}

FONDO_OSCURO = "#1E272E"
FONDO_PANEL = "#2F3640"
COLOR_TEXTO = "#F5F6FA"

COLOR_BOTON_PRIMARY = "#4B7BEC"
COLOR_BOTON_PRIMARY_HOVER = "#5B8BFC"
COLOR_BOTON_WARNING = "#F39C12"
COLOR_BOTON_WARNING_HOVER = "#F1C40F"
COLOR_BOTON_DANGER = "#E74C3C"
COLOR_BOTON_DANGER_HOVER = "#C0392B"
COLOR_BOTON_OUTLINE_BG = "#1E272E"
COLOR_BOTON_OUTLINE_HOVER = "#2F3640"
COLOR_SLIDER_TROUGH = "#353B48"
COLOR_COMBOBOX_BG = "#2F3640"
COLOR_CARD_BG = "#252C34"


@dataclass
class ConfigSimulacion:
    num_individuos: int = NUM_INDIVIDUOS
    num_infectados_iniciales: int = 0
    num_inmunes_iniciales: int = 0
    radio_infeccion: int = 30
    prob_infeccion: float = 0.05
    prob_inmunidad: float = 0.002
    tiempo_muerte: int = 450
    fps: int = 60
    max_dias: int = 0


PRESETS_ENFERMEDADES: dict[str, ConfigSimulacion | None] = {
    "Personalizada": None,
    "COVID-19": ConfigSimulacion(
        num_individuos=1000, radio_infeccion=40, prob_infeccion=0.20,
        prob_inmunidad=0.005, tiempo_muerte=450,
    ),
    "Peste Negra": ConfigSimulacion(
        num_individuos=300, radio_infeccion=25, prob_infeccion=0.15,
        prob_inmunidad=0.001, tiempo_muerte=300,
    ),
    "Viruela": ConfigSimulacion(
        num_individuos=600, radio_infeccion=35, prob_infeccion=0.30,
        prob_inmunidad=0.003, tiempo_muerte=600,
    ),
    "Gripe Española": ConfigSimulacion(
        num_individuos=450, radio_infeccion=50, prob_infeccion=0.40,
        prob_inmunidad=0.008, tiempo_muerte=450,
    ),
    "Peste de Justiniano": ConfigSimulacion(
        num_individuos=350, radio_infeccion=20, prob_infeccion=0.12,
        prob_inmunidad=0.0015, tiempo_muerte=350,
    ),
    "Cólera": ConfigSimulacion(
        num_individuos=200, radio_infeccion=15, prob_infeccion=0.80,
        prob_inmunidad=0.006, tiempo_muerte=200,
    ),
}
