# Simulación de Propagación de Epidemias

Simulación interactiva de brotes epidémicos con interfaz gráfica en **Python/Tkinter**. Permite configurar parámetros poblacionales y de enfermedad, visualizar la propagación en tiempo real con partículas animadas, y analizar resultados históricos.

---

## Requisitos

- Python **≥ 3.10**
- Tkinter (incluido en la instalación estándar de Python)
- openpyxl (se instala automáticamente — ver Instalación)

---

## Instalación

```bash
git clone <repo>
cd Simulacion
python -m venv .venv
source .venv/bin/activate
pip install -e .
#  ↑ instala automáticamente openpyxl desde pyproject.toml
```

---

## Ejecución

```bash
# Iniciar simulación
python simular.py

# Ejecutar pruebas unitarias
python -m pytest pruebas/
```

---

## Estructura del proyecto

```
Simulacion/
├── simular.py                      ← Punto de entrada — ventana de simulación
├── analiticas.py                   ← Punto de entrada — analíticas históricas
├── src/
│   ├── configuracion.py            ← Constantes, colores, dataclass, presets de enfermedades
│   ├── modelos/
│   │   └── individuo.py            ← Clase Individuo (movimiento, infección, muerte)
│   ├── simulacion/
│   │   ├── motor.py                ← MotorSimulacion (ciclo principal, conteos, historial)
│   │   └── espacial.py             ← HashEspacial (optimización de búsqueda de vecinos)
│   ├── interfaz/
│   │   ├── aplicacion.py           ← Ventana principal, layouts, barras, overlays
│   │   ├── componentes.py          ← Widgets reutilizables (Slider, Selector, Botonera)
│   │   └── grafico.py              ← Gráfico de evolución temporal
│       └── almacenamiento/
│       └── manejador_excel.py       ← Guardado de resultados en Excel
├── pruebas/                        ← Tests unitarios con pytest
│   ├── prueba_individuo.py
│   ├── prueba_motor.py
│   └── prueba_espacial.py
```

---

## Flujo de uso

1. **Ajustar parámetros** en el panel derecho (población, infectados iniciales, radio de infección, etc.)
2. Presionar **▶ INICIAR** — se muestra una tarjeta con el resumen de la población inicial
3. Presionar **▶ COMENZAR** — la simulación se pone en marcha
4. Durante la ejecución se puede:
   - **⏸ PAUSAR / ▶ REANUDAR** la simulación
   - **⏹ FINALIZAR** anticipadamente (visible solo cuando está pausada)
5. Al terminar (por extinción, límite de días o finalización manual) aparece una superposición con tabla comparativa Estado / Inicial / Final y un botón **💾 GUARDAR** para exportar a Excel

---

## Fases de la simulación

| Fase | Estado | Botones disponibles |
|------|--------|-------------------|
| **LISTO** | Configuración inicial | ▶ INICIAR |
| **PREPARADO** | Resumen de población inicial | ▶ COMENZAR / ↻ VOLVER |
| **EJECUTANDO** | Simulación corriendo | ⏸ PAUSAR |
| **TERMINADO** | Resultados mostrados | ⟳ REINICIAR |

---

## Parámetros configurables

| Parámetro | Rango | Descripción |
|-----------|-------|-------------|
| **Población Total** | 0 – 500 | Número de individuos en el entorno |
| **Infectados Iniciales** | 0 – Población | Individuos infectados al día 0 |
| **Inmunes Iniciales** | 0 – Población | Individuos inmunes al día 0 |
| **Velocidad de Simulación** | 0.5× – 3.0× | Velocidad de avance (control continuo deslizante) |
| **Radio de Infección** | 0 – 100 | Distancia máxima para transmisión entre individuos |
| **Prob. de Infección** | 0 – 100% | Probabilidad de contagio en cada contacto |
| **Prob. de Inmunidad** | 0 – 5% | Probabilidad de recuperarse como inmune por frame |
| **Tiempo de Vida** | 0 – 1200 | Frames que un infectado puede vivir antes de morir |
| **Días Máximo** | 0 – 500 | Límite de duración de la simulación (0 = sin límite) |

> **Nota:** Todos los parámetros inician en 0 y deben ajustarse antes de iniciar. La suma de Infectados + Inmunes iniciales no puede superar la Población Total.

---

## Enfermedades predefinidas

El selector de enfermedades carga configuraciones predefinidas para escenarios históricos:

| Enfermedad | Población | Radio | Prob. Infección | Prob. Inmunidad | Tiempo de Vida |
|-----------|-----------|-------|----------------|----------------|---------------|
| COVID-19 | 1000 | 40 | 20% | 0.5% | 450 |
| Peste Negra | 300 | 25 | 15% | 0.1% | 300 |
| Viruela | 600 | 35 | 30% | 0.3% | 600 |
| Gripe Española | 450 | 50 | 40% | 0.8% | 450 |
| Peste de Justiniano | 350 | 20 | 12% | 0.15% | 350 |
| Cólera | 200 | 15 | 80% | 0.6% | 200 |

También está disponible la opción **Personalizada** para configurar manualmente todos los valores.

---

## Interfaz de usuario

- **Tema oscuro** con paleta de colores consistente
- **Barra de estado superior** con indicadores:
  - ● `SANOS` / ● `INFECTADOS` / ● `INMUNES` / ● `MUERTOS` (con colores distintivos)
  - `⏱ DÍA: N` — contador de días transcurridos
- **Canvas de simulación** con partículas animadas que representan individuos
- **Gráfico de evolución temporal** con área rellena por estado sanitario y leyenda
- **Panel derecho scrolleable** con tarjetas que agrupan parámetros, sliders con descripción, selector de enfermedad y botonera de control
- **Diálogos en canvas**: tarjetas estilizadas con sombra para el preparado y los resultados finales
- **Scroll condicional**: la barra de desplazamiento del panel derecho solo aparece cuando el contenido no cabe en la ventana

---

## Persistencia de datos

Al finalizar cada simulación se puede exportar un archivo `.xlsx` con:

- Enfermedad seleccionada y parámetros usados
- Conteo inicial y final de Sanos, Infectados, Inmunes y Muertos
- Días transcurridos
- Población total inicial vs. vivos finales

Al presionar **💾 GUARDAR** en la superposición de resultados se abre un diálogo para elegir el nombre del archivo (se guarda en el directorio de trabajo).

---

## Pruebas

El proyecto incluye **35+ tests unitarios** con pytest que cubren:

- Creación y movimiento de individuos
- Infección, inmunidad y muerte
- Límite por días máximos
- Estructura espacial HashEspacial
- Ciclo de simulación completo

```bash
python -m pytest pruebas/ -v
```

---

## Licencia

Proyecto académico — Autorizadocpor Chayanne.
