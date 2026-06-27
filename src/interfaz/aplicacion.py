import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from src.configuracion import (
    Estado, COLORES, ConfigSimulacion, PRESETS_ENFERMEDADES,
    ANCHO_SIM, ALTO_SIM, ANCHO_GRAFICO, ALTO_GRAFICO,
    ANCHO_CONTROL, ALTO_BARRA, FONDO_OSCURO, FONDO_PANEL, COLOR_TEXTO,
    INTERVALO_GRAFICO, COLOR_SLIDER_TROUGH, COLOR_COMBOBOX_BG, COLOR_CARD_BG,
)
from src.simulacion.motor import MotorSimulacion
from src.interfaz.componentes import SliderEtiquetado, SelectorEnfermedad, BotoneraControl
from src.interfaz.grafico import Grafico
from src.almacenamiento.manejador_excel import guardar_resultado


class Aplicacion:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Simulación de Epidemia")
        self.root.configure(bg=FONDO_OSCURO)
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)

        self.motor = MotorSimulacion()
        self.particulas_ids: list[int] = []
        self.pausado = False
        self._enfermedad_actual = "Personalizada"
        self.fase = "listo"
        self._canvas_sim_ancho = ANCHO_SIM
        self._canvas_sim_alto = ALTO_SIM
        self._canvas_graf_ancho = ANCHO_GRAFICO
        self._canvas_graf_alto = ALTO_GRAFICO
        self._resultado_guardar: dict | None = None

        self._configurar_estilo()
        self._crear_interfaz()
        self._mostrar_bienvenida()

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style()
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("TFrame", background=FONDO_PANEL)
        estilo.configure("Dark.TFrame", background=FONDO_OSCURO)
        estilo.configure("TLabel", background=FONDO_PANEL, foreground=COLOR_TEXTO, font=("Segoe UI", 10))
        estilo.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), padding=10)
        estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        estilo.map("TButton", background=[("active", "#4CD137")])
        estilo.configure("TScale", background=FONDO_PANEL, troughcolor=COLOR_SLIDER_TROUGH)
        estilo.configure("Card.TFrame", background=COLOR_CARD_BG)
        estilo.configure("Vertical.TScrollbar",
                         background=COLOR_SLIDER_TROUGH,
                         troughcolor=FONDO_OSCURO,
                         bordercolor=FONDO_OSCURO,
                         arrowcolor=COLOR_TEXTO)
        estilo.configure("Header.TFrame", background=FONDO_PANEL)
        estilo.configure("HeaderLabel.TLabel",
                         background=FONDO_PANEL, foreground=COLOR_TEXTO,
                         font=("Segoe UI", 11, "bold"))
        estilo.configure("Dia.TLabel",
                         background="#2F3640", foreground=COLOR_TEXTO,
                         font=("Segoe UI", 11, "bold"), padding=(10, 4))
        estilo.configure("Dark.TCombobox",
                         fieldbackground=COLOR_COMBOBOX_BG,
                         background=COLOR_COMBOBOX_BG,
                         foreground=COLOR_TEXTO,
                         selectbackground=COLOR_COMBOBOX_BG,
                         selectforeground=COLOR_TEXTO,
                         arrowcolor=COLOR_TEXTO)
        estilo.map("Dark.TCombobox",
                   fieldbackground=[("readonly", COLOR_COMBOBOX_BG)])

    def _crear_barra_estado(self, master: tk.Widget) -> None:
        self._barra = ttk.Frame(master, style="Header.TFrame", height=ALTO_BARRA)
        self._barra.pack(fill=tk.X, pady=(0, 5))
        self._barra.pack_propagate(False)

        self._header_labels: dict[str, tk.Label] = {}
        self._label_dia = tk.Label(
            self._barra, text="⏱ DÍA: 0",
            bg="#2F3640", fg=COLOR_TEXTO,
            font=("Segoe UI", 11, "bold"), padx=10, pady=2,
        )
        self._label_dia.pack(side=tk.RIGHT, padx=(0, 10))

        for estado, texto in [(Estado.SANO, "SANOS"), (Estado.INFECTADO, "INFECTADOS"),
                              (Estado.INMUNE, "INMUNES"), (Estado.MUERTO, "MUERTOS")]:
            frame = tk.Frame(self._barra, bg=FONDO_PANEL)
            frame.pack(side=tk.LEFT, padx=(15, 0))
            circulo = tk.Label(frame, text="●", fg=COLORES[estado],
                               bg=FONDO_PANEL, font=("Segoe UI", 14))
            circulo.pack(side=tk.LEFT)
            lbl = tk.Label(frame, text=f"{texto}: 0",
                           bg=FONDO_PANEL, fg=COLOR_TEXTO,
                           font=("Segoe UI", 11, "bold"))
            lbl.pack(side=tk.LEFT, padx=(4, 0))
            self._header_labels[estado] = lbl

    def _crear_interfaz(self) -> None:
        self.val_velocidad = tk.DoubleVar(value=1.0)
        self.val_num_individuos = tk.IntVar(value=0)
        self.val_infectados_ini = tk.IntVar(value=0)
        self.val_inmunes_ini = tk.IntVar(value=0)
        self.val_radio_infeccion = tk.IntVar(value=0)
        self.val_prob_infeccion = tk.DoubleVar(value=0.0)
        self.val_prob_inmunidad = tk.DoubleVar(value=0.0)
        self.val_tiempo_muerte = tk.IntVar(value=0)
        self.val_max_dias = tk.IntVar(value=0)

        marco_ppal = ttk.Frame(self.root, style="Dark.TFrame")
        marco_ppal.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        marco_izq = ttk.Frame(marco_ppal, style="Dark.TFrame")
        marco_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._crear_barra_estado(marco_izq)

        self.canvas_sim = tk.Canvas(
            marco_izq, bg="#11151C", highlightthickness=2, highlightbackground="#353b48",
        )
        self.canvas_sim.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.canvas_sim.bind("<Configure>", self._on_sim_redimensionar)

        self.canvas_graf = tk.Canvas(
            marco_izq, height=ALTO_GRAFICO,
            bg="#11151C", highlightthickness=2, highlightbackground="#353b48",
        )
        self.canvas_graf.pack(fill=tk.X)
        self.canvas_graf.bind("<Configure>", self._on_graf_redimensionar)
        self.grafico = Grafico(self.canvas_graf)

        ANCHO_SCROLLBAR = 16
        self._marco_scroll = ttk.Frame(marco_ppal, width=ANCHO_CONTROL, style="Dark.TFrame")
        self._marco_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))
        self._marco_scroll.pack_propagate(False)

        self._scroll_canvas = tk.Canvas(
            self._marco_scroll, width=ANCHO_CONTROL - ANCHO_SCROLLBAR,
            bg=FONDO_OSCURO, highlightthickness=0,
        )
        self._scrollbar = ttk.Scrollbar(
            self._marco_scroll, orient="vertical", command=self._scroll_canvas.yview,
        )
        self._scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._marco_ctrl = ttk.Frame(self._scroll_canvas, style="Dark.TFrame")
        self._marco_ctrl.bind(
            "<Configure>",
            lambda e: self._scroll_canvas.configure(
                scrollregion=self._scroll_canvas.bbox("all"),
            ),
        )
        self._scroll_canvas.create_window(
            (0, 0), window=self._marco_ctrl, anchor="nw",
            width=ANCHO_CONTROL - ANCHO_SCROLLBAR,
        )
        self._scroll_canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scroll_canvas.bind("<Configure>", lambda e: self._ajustar_scroll())

        card_params = ttk.Frame(self._marco_ctrl, style="Card.TFrame")
        card_params.pack(fill=tk.X, padx=5, pady=(0, 8))

        ttk.Label(card_params, text="PARÁMETROS", style="Title.TLabel").pack(pady=(5, 5))
        ttk.Label(
            card_params, text="CONFIGURACIÓN DE SIMULACIÓN",
            font=("Segoe UI", 9), foreground="#57606F",
        ).pack(pady=(0, 5))

        self._slider_poblacion = SliderEtiquetado(
            card_params, "Población Total", self.val_num_individuos, 0, 500, 10,
            descripcion="Define el número de individuos presentes en el entorno.",
        )
        self.slider_infectados = SliderEtiquetado(
            card_params, "Infectados Iniciales", self.val_infectados_ini, 0, 0, 1,
        )
        self.slider_inmunes = SliderEtiquetado(
            card_params, "Inmunes Iniciales", self.val_inmunes_ini, 0, 0, 1,
        )

        self.val_num_individuos.trace_add("write", self._actualizar_max_iniciales)

        SliderEtiquetado(
            card_params, "Velocidad de Simulación", self.val_velocidad,
            0.5, 3.0, 0.1, formato="velocidad",
            descripcion="Ajusta la rapidez con la que transcurre el tiempo y el movimiento.",
        )

        self._slider_radio = SliderEtiquetado(
            card_params, "Radio de Infección", self.val_radio_infeccion, 0, 100, 1,
            descripcion="Distancia máxima a la que un infectado puede contagiar a otros.",
        )
        self._slider_prob_inf = SliderEtiquetado(
            card_params, "Prob. de Infección", self.val_prob_infeccion, 0.0, 1.0, 0.01,
            formato="porcentaje",
            descripcion="Probabilidad de que el virus se transmita en cada contacto.",
        )
        self._slider_prob_inm = SliderEtiquetado(
            card_params, "Prob. de Inmunidad", self.val_prob_inmunidad, 0.0, 0.10, 0.001,
            formato="porcentaje",
            descripcion="Probabilidad de que un individuo se recupere y se vuelva inmune.",
        )
        self._slider_tiempo_muerte = SliderEtiquetado(
            card_params, "Tiempo de Vida (Frames)", self.val_tiempo_muerte, 0, 1200, 10,
            descripcion="Duración de la infección antes de que el individuo muera o se recupere.",
        )
        self._slider_max_dias = SliderEtiquetado(
            card_params, "Días Máximo", self.val_max_dias, 0, 500, 1,
            descripcion="Límite de duración de la simulación en días. 0 = sin límite.",
        )

        ttk.Separator(self._marco_ctrl, orient="horizontal").pack(fill=tk.X, padx=10, pady=4)

        card_act = ttk.Frame(self._marco_ctrl, style="Card.TFrame")
        card_act.pack(fill=tk.X, padx=5, pady=(0, 8))

        self.selector_enfermedad = SelectorEnfermedad(
            card_act, al_seleccionar=self._al_seleccionar_enfermedad,
            titulo="SELECCIONAR ENFERMEDAD",
        )
        self.botones = BotoneraControl(
            card_act,
            al_iniciar=self._preparar,
            al_comenzar=self._iniciar_simulacion,
            al_volver=self._mostrar_bienvenida,
            al_pausar=self._alternar_pausa,
            al_nueva_simulacion=self._mostrar_bienvenida,
            al_finalizar=self._finalizar_simulacion,
        )

        self.root.after_idle(self._ajustar_scroll)

    def _on_mousewheel(self, event: tk.Event) -> None:
        if event.num == 4:
            self._scroll_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._scroll_canvas.yview_scroll(1, "units")
        else:
            self._scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _ajustar_scroll(self) -> None:
        self.root.update_idletasks()
        contenido = self._marco_ctrl.winfo_reqheight()
        visible = self._scroll_canvas.winfo_height()
        if contenido <= visible:
            self._scrollbar.pack_forget()
            self._scroll_canvas.unbind("<MouseWheel>")
            self._scroll_canvas.unbind("<Button-4>")
            self._scroll_canvas.unbind("<Button-5>")
        else:
            self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self._scroll_canvas.bind("<MouseWheel>", self._on_mousewheel)
            self._scroll_canvas.bind("<Button-4>", self._on_mousewheel)
            self._scroll_canvas.bind("<Button-5>", self._on_mousewheel)

    def _on_sim_redimensionar(self, event: tk.Event) -> None:
        self._canvas_sim_ancho = event.width
        self._canvas_sim_alto = event.height

    def _on_graf_redimensionar(self, event: tk.Event) -> None:
        self._canvas_graf_ancho = event.width
        self._canvas_graf_alto = event.height
        self.grafico.redimensionar(event.width, event.height)

    def _habilitar_parametros(self, habilitar: bool) -> None:
        estado = "normal" if habilitar else "disabled"
        for s in (
            self._slider_poblacion, self.slider_infectados, self.slider_inmunes,
            self._slider_radio, self._slider_prob_inf, self._slider_prob_inm,
            self._slider_tiempo_muerte, self._slider_max_dias,
        ):
            s.scale.config(state=estado)
        self.selector_enfermedad.combo.config(state=estado)

    def _construir_config(self) -> ConfigSimulacion:
        return ConfigSimulacion(
            num_individuos=self.val_num_individuos.get(),
            num_infectados_iniciales=self.val_infectados_ini.get(),
            num_inmunes_iniciales=self.val_inmunes_ini.get(),
            radio_infeccion=self.val_radio_infeccion.get(),
            prob_infeccion=self.val_prob_infeccion.get(),
            prob_inmunidad=self.val_prob_inmunidad.get(),
            tiempo_muerte=self.val_tiempo_muerte.get(),
            fps=60,
            max_dias=self.val_max_dias.get(),
        )

    def _actualizar_max_iniciales(self, *_):
        max_ = self.val_num_individuos.get()
        self.slider_infectados.configurar_rango(max_)
        self.slider_inmunes.configurar_rango(max_)

    def _al_seleccionar_enfermedad(self) -> None:
        nombre = self.selector_enfermedad.combo.get()
        if nombre == "Personalizada":
            self._enfermedad_actual = nombre
            return
        cfg = PRESETS_ENFERMEDADES.get(nombre)
        if cfg is None:
            return
        self._enfermedad_actual = nombre
        self.val_radio_infeccion.set(cfg.radio_infeccion)
        self.val_prob_infeccion.set(cfg.prob_infeccion)
        self.val_prob_inmunidad.set(cfg.prob_inmunidad)
        self.val_tiempo_muerte.set(cfg.tiempo_muerte)
        self._mostrar_bienvenida()

    def _mostrar_bienvenida(self) -> None:
        self.fase = "listo"
        self.pausado = False
        self.motor.ejecutando = False
        self.canvas_sim.delete("particle", "overlay", "dialog", "welcome")
        self.grafico.limpiar()
        self.particulas_ids = []
        self._actualizar_header(
            {Estado.SANO: 0, Estado.INFECTADO: 0,
             Estado.INMUNE: 0, Estado.MUERTO: 0},
            0,
        )

        cx = self._canvas_sim_ancho // 2
        cy = self._canvas_sim_alto // 2
        self.canvas_sim.create_text(
            cx, cy,
            text="SIMULACIÓN DE EPIDEMIA\n\n"
                 "Ajusta los parámetros en el panel derecho\n"
                 "y presiona INICIAR para comenzar",
            fill="#718093", font=("Segoe UI", 16, "bold"),
            justify=tk.CENTER, tags="welcome",
        )

        self._habilitar_parametros(True)
        self.botones.configurar_fase("listo")

    def _preparar(self) -> None:
        errores: list[str] = []
        if self.val_num_individuos.get() == 0:
            errores.append("Población Total")
        if self.val_infectados_ini.get() == 0:
            errores.append("Infectados Iniciales")
        if self.val_radio_infeccion.get() == 0:
            errores.append("Radio de Infección")
        if self.val_prob_infeccion.get() == 0.0:
            errores.append("Prob. de Infección")
        if self.val_tiempo_muerte.get() == 0:
            errores.append("Tiempo de Vida (Frames)")
        if errores:
            messagebox.showwarning(
                "Parámetros sin ajustar",
                "Los siguientes parámetros están en 0:\n\n"
                + "\n".join(f"  • {e}" for e in errores)
                + "\n\nAjústalos antes de iniciar.",
            )
            return

        n_ind = self.val_num_individuos.get()
        if self.val_infectados_ini.get() + self.val_inmunes_ini.get() > n_ind:
            messagebox.showwarning(
                "Población excedida",
                "La suma de Infectados e Inmunes iniciales "
                f"({self.val_infectados_ini.get()} + {self.val_inmunes_ini.get()} = "
                f"{self.val_infectados_ini.get() + self.val_inmunes_ini.get()}) "
                f"supera la población total ({n_ind}).\n\n"
                "Reduce la cantidad de Infectados o Inmunes iniciales.",
            )
            return

        self._habilitar_parametros(False)

        config = self._construir_config()
        self.motor.reiniciar(config)

        self.canvas_sim.delete("particle", "overlay", "dialog", "welcome")
        self.particulas_ids = []

        sx_sim = self._canvas_sim_ancho / ANCHO_SIM
        sy_sim = self._canvas_sim_alto / ALTO_SIM
        r_sim = max(3, int(6 * min(sx_sim, sy_sim)))

        for ind in self.motor.poblacion:
            px = ind.x * sx_sim
            py = ind.y * sy_sim
            pid = self.canvas_sim.create_oval(
                px - r_sim, py - r_sim,
                px + r_sim, py + r_sim,
                fill=COLORES[ind.estado], outline="", tags="particle",
            )
            self.particulas_ids.append(pid)

        inicial = self.motor.estado_inicial
        cx_sim = self._canvas_sim_ancho // 2
        cy_sim = self._canvas_sim_alto // 2

        self.canvas_sim.create_rectangle(
            0, 0, self._canvas_sim_ancho, self._canvas_sim_alto,
            fill="#11151C", stipple="gray25", tags="overlay",
        )
        self.canvas_sim.create_rectangle(
            cx_sim - 190, cy_sim - 145, cx_sim + 190, cy_sim + 145,
            fill="#0D1117", outline="", tags="overlay",
        )
        self.canvas_sim.create_rectangle(
            cx_sim - 185, cy_sim - 140, cx_sim + 185, cy_sim + 140,
            fill="#252C34", outline="#4B7BEC", width=2, tags="overlay",
        )
        self.canvas_sim.create_text(
            cx_sim, cy_sim - 115, text="📊 POBLACIÓN INICIAL (Día 0)",
            fill="#F5F6FA", font=("Segoe UI", 14, "bold"),
            justify=tk.CENTER, tags="overlay",
        )
        self.canvas_sim.create_line(
            cx_sim - 155, cy_sim - 85, cx_sim + 155, cy_sim - 85,
            fill="#4B7BEC", width=1, tags="overlay",
        )
        self.canvas_sim.create_text(
            cx_sim - 90, cy_sim - 50, text="Estado", fill="#718093",
            font=("Segoe UI", 10, "bold"), anchor="w", tags="overlay",
        )
        self.canvas_sim.create_text(
            cx_sim + 90, cy_sim - 50, text="Inicial", fill="#718093",
            font=("Segoe UI", 10, "bold"), anchor="e", tags="overlay",
        )
        y_sim = cy_sim - 25
        for estado, icono in [(Estado.SANO, "🟦"), (Estado.INFECTADO, "🟥"),
                               (Estado.INMUNE, "🟩"), (Estado.MUERTO, "⬜")]:
            self.canvas_sim.create_text(
                cx_sim - 90, y_sim, text=f"{icono} {estado.name}", fill=COLORES[estado],
                font=("Segoe UI", 12, "bold"), anchor="w", tags="overlay",
            )
            self.canvas_sim.create_text(
                cx_sim + 90, y_sim, text=str(inicial[estado]), fill=COLOR_TEXTO,
                font=("Segoe UI", 12, "bold"), anchor="e", tags="overlay",
            )
            y_sim += 26
        self.canvas_sim.create_text(
            cx_sim, cy_sim + 105, text="Presiona COMENZAR para iniciar la simulación",
            fill="#718093", font=("Segoe UI", 11, "bold"),
            justify=tk.CENTER, tags="overlay",
        )
        self._actualizar_header(inicial, 0)

        self.fase = "preparado"
        self.botones.configurar_fase("preparado")

    def _iniciar_simulacion(self) -> None:
        self.canvas_sim.delete("overlay")
        self.fase = "ejecutando"
        self.pausado = False
        self.botones.configurar_fase("ejecutando")
        self._bucle_principal()

    def _actualizar_header(self, stats: dict[Estado, int], dias: int) -> None:
        for estado, conteo in stats.items():
            self._header_labels[estado].config(text=f"{estado.name}: {conteo}")
        self._label_dia.config(text=f"⏱ DÍA: {dias}")

    def _bucle_principal(self) -> None:
        config = self._construir_config()

        velocidad = self.val_velocidad.get()
        demora = 33
        pasos = max(1, int(velocidad))

        if not self.pausado:
            for _ in range(pasos):
                self.motor.avanzar(config)
                if not self.motor.ejecutando:
                    break

        sx_sim = self._canvas_sim_ancho / ANCHO_SIM
        sy_sim = self._canvas_sim_alto / ALTO_SIM
        r_sim = max(3, int(6 * min(sx_sim, sy_sim)))

        for i, ind in enumerate(self.motor.poblacion):
            pid = self.particulas_ids[i]
            px = ind.x * sx_sim
            py = ind.y * sy_sim
            self.canvas_sim.coords(
                pid, px - r_sim, py - r_sim,
                px + r_sim, py + r_sim,
            )
            self.canvas_sim.itemconfig(pid, fill=COLORES[ind.estado])

        dias = self.motor.frames_transcurridos // 60
        stats = self.motor.obtener_estadisticas()
        self._actualizar_header(stats, dias)

        if (
            not self.motor.ejecutando
            and not self.pausado
            and len(self.canvas_sim.find_withtag("dialog")) == 0
        ):
            motivo = "limite" if (config.max_dias > 0 and dias >= config.max_dias) else "extinguida"
            self._mostrar_resultados(config, stats, dias, motivo)
            return

        if self.motor.frames_transcurridos % INTERVALO_GRAFICO == 0:
            self.grafico.actualizar(
                self.motor.historial, self.motor.num_individuos,
                self._canvas_graf_ancho, self._canvas_graf_alto,
            )

        if self.motor.ejecutando or self.pausado:
            self.root.after(demora, self._bucle_principal)

    def _mostrar_resultados(
        self, config: ConfigSimulacion,
        stats: dict[Estado, int], dias: int,
        motivo: str = "extinguida",
    ) -> None:
        self._resultado_guardar = {
            "config": config, "stats": stats, "dias": dias,
        }

        inicial = self.motor.estado_inicial
        cx_sim = self._canvas_sim_ancho // 2
        cy_sim = self._canvas_sim_alto // 2

        self.canvas_sim.create_rectangle(
            cx_sim - 205, cy_sim - 160, cx_sim + 205, cy_sim + 160,
            fill="#0D1117", outline="", tags="dialog",
        )
        self.canvas_sim.create_rectangle(
            cx_sim - 200, cy_sim - 155, cx_sim + 200, cy_sim + 155,
            fill="#252C34", outline="#E74C3C", width=2, tags="dialog",
        )
        titulos = {
            "extinguida": f"🏁 EPIDEMIA EXTINGUIDA (Día {dias})",
            "limite": f"⏰ LÍMITE DE DÍAS ALCANZADO (Día {dias})",
            "manual": f"⏹ SIMULACIÓN FINALIZADA (Día {dias})",
        }
        self.canvas_sim.create_text(
            cx_sim, cy_sim - 125, text=titulos.get(motivo, titulos["extinguida"]),
            fill="#F5F6FA", font=("Segoe UI", 13, "bold"),
            justify=tk.CENTER, tags="dialog",
        )
        self.canvas_sim.create_line(
            cx_sim - 170, cy_sim - 100, cx_sim + 170, cy_sim - 100,
            fill="#E74C3C", width=1, tags="dialog",
        )
        y_sim = cy_sim - 75
        self.canvas_sim.create_text(
            cx_sim - 100, y_sim, text="Estado", fill="#718093",
            font=("Segoe UI", 10, "bold"), anchor="w", tags="dialog",
        )
        self.canvas_sim.create_text(
            cx_sim + 40, y_sim, text="Inicial", fill="#718093",
            font=("Segoe UI", 10, "bold"), anchor="e", tags="dialog",
        )
        self.canvas_sim.create_text(
            cx_sim + 130, y_sim, text="Final", fill="#718093",
            font=("Segoe UI", 10, "bold"), anchor="e", tags="dialog",
        )
        y_sim += 25
        for estado, icono in [(Estado.SANO, "🟦"), (Estado.INFECTADO, "🟥"),
                               (Estado.INMUNE, "🟩"), (Estado.MUERTO, "⬜")]:
            self.canvas_sim.create_text(
                cx_sim - 100, y_sim, text=f"{icono} {estado.name}", fill=COLORES[estado],
                font=("Segoe UI", 11, "bold"), anchor="w", tags="dialog",
            )
            self.canvas_sim.create_text(
                cx_sim + 40, y_sim, text=str(inicial[estado]), fill=COLOR_TEXTO,
                font=("Segoe UI", 11), anchor="e", tags="dialog",
            )
            self.canvas_sim.create_text(
                cx_sim + 130, y_sim, text=str(stats[estado]), fill=COLOR_TEXTO,
                font=("Segoe UI", 11, "bold"), anchor="e", tags="dialog",
            )
            y_sim += 26
        y_sim += 4
        self.canvas_sim.create_line(
            cx_sim - 110, y_sim, cx_sim + 140, y_sim,
            fill="#57606F", width=1, tags="dialog",
        )
        y_sim += 20
        total = self.motor.num_individuos
        vivos = total - stats[Estado.MUERTO]
        self.canvas_sim.create_text(
            cx_sim - 110, y_sim, text="TOTAL", fill="#F5F6FA",
            font=("Segoe UI", 11, "bold"), anchor="w", tags="dialog",
        )
        self.canvas_sim.create_text(
            cx_sim + 40, y_sim, text=str(total), fill=COLOR_TEXTO,
            font=("Segoe UI", 11, "bold"), anchor="e", tags="dialog",
        )
        self.canvas_sim.create_text(
            cx_sim + 130, y_sim, text=str(vivos), fill=COLOR_TEXTO,
            font=("Segoe UI", 11, "bold"), anchor="e", tags="dialog",
        )

        y_sim += 30
        btn_x1 = cx_sim - 70
        btn_x2 = cx_sim + 70
        btn_y1 = y_sim
        btn_y2 = y_sim + 32
        self.canvas_sim.create_rectangle(
            btn_x1, btn_y1, btn_x2, btn_y2,
            fill="#4B7BEC", outline="", tags=("dialog", "btn_bg"),
        )
        self.canvas_sim.create_text(
            cx_sim, y_sim + 16, text="💾 GUARDAR",
            fill="#F5F6FA", font=("Segoe UI", 11, "bold"),
            tags=("dialog", "btn_txt"),
        )

        def btn_enter(_):
            self.canvas_sim.itemconfig("btn_bg", fill="#5B8BFC")

        def btn_leave(_):
            self.canvas_sim.itemconfig("btn_bg", fill="#4B7BEC")

        def btn_click(_):
            self.canvas_sim.itemconfig("btn_bg", fill="#4B7BEC")
            self._guardar_resultados()

        for t in ("btn_bg", "btn_txt"):
            self.canvas_sim.tag_bind(t, "<Enter>", btn_enter)
            self.canvas_sim.tag_bind(t, "<Leave>", btn_leave)
            self.canvas_sim.tag_bind(t, "<Button-1>", btn_click)

        self.grafico.actualizar(
            self.motor.historial, self.motor.num_individuos,
            self._canvas_graf_ancho, self._canvas_graf_alto,
        )

        self._habilitar_parametros(True)
        self.fase = "terminado"
        self.botones.configurar_fase("terminado")

    def _dialogo_guardar_nombre(self) -> str | None:
        sugerido = f"simulacion_{self._enfermedad_actual.replace(' ', '_')}.xlsx"

        dialogo = tk.Toplevel(self.root)
        dialogo.title("Guardar Simulación")
        dialogo.configure(bg=FONDO_OSCURO)
        dialogo.resizable(False, False)
        dialogo.transient(self.root)
        dialogo.wait_visibility()
        dialogo.grab_set()

        ancho, alto = 420, 200
        px = self.root.winfo_x() + (self.root.winfo_width() - ancho) // 2
        py = self.root.winfo_y() + (self.root.winfo_height() - alto) // 2
        dialogo.geometry(f"{ancho}x{alto}+{px}+{py}")

        tk.Label(
            dialogo, text="💾 Guardar resultados", bg=FONDO_OSCURO, fg=COLOR_TEXTO,
            font=("Segoe UI", 13, "bold"),
        ).pack(pady=(18, 2))

        ttk.Separator(dialogo, orient="horizontal").pack(fill=tk.X, padx=25)

        frame = tk.Frame(dialogo, bg=FONDO_OSCURO)
        frame.pack(pady=(12, 0), padx=25, fill=tk.X)

        tk.Label(
            frame, text="Nombre del archivo:", bg=FONDO_OSCURO, fg="#A0AAB5",
            font=("Segoe UI", 9), anchor="w",
        ).pack(fill=tk.X)

        var_nombre = tk.StringVar(value=sugerido)
        entrada = tk.Entry(
            frame, textvariable=var_nombre, bg="#1E272E", fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO, relief="flat", bd=0,
            font=("Segoe UI", 11), highlightthickness=2,
            highlightbackground="#353B48", highlightcolor="#4B7BEC",
        )
        entrada.pack(fill=tk.X, pady=(5, 0), ipady=4)
        entrada.focus_set()
        entrada.select_range(0, tk.END)

        dir_actual = Path.cwd().as_posix()
        tk.Label(
            dialogo, text=f"Se guardará en: {dir_actual}/", bg=FONDO_OSCURO, fg="#57606F",
            font=("Segoe UI", 8), anchor="w",
        ).pack(fill=tk.X, padx=25, pady=(4, 0))

        resultado: list[str | None] = [None]

        def accion_guardar() -> None:
            nombre_final = var_nombre.get().strip()
            if not nombre_final:
                return
            if not nombre_final.endswith(".xlsx"):
                nombre_final += ".xlsx"
            resultado[0] = nombre_final
            dialogo.destroy()

        def accion_cancelar() -> None:
            dialogo.destroy()

        btn_frame = tk.Frame(dialogo, bg=FONDO_OSCURO)
        btn_frame.pack(pady=(14, 0))

        btn_cancelar = tk.Button(
            btn_frame, text="  CANCELAR  ", command=accion_cancelar,
            bg="#353B48", fg=COLOR_TEXTO, activebackground="#454B58",
            activeforeground=COLOR_TEXTO, relief="flat", bd=0,
            font=("Segoe UI", 10, "bold"), cursor="hand2", padx=16, pady=6,
        )
        btn_cancelar.pack(side=tk.LEFT, padx=(0, 6))

        btn_guardar = tk.Button(
            btn_frame, text="  💾 GUARDAR  ", command=accion_guardar,
            bg="#4B7BEC", fg="white", activebackground="#5B8BFC",
            activeforeground="white", relief="flat", bd=0,
            font=("Segoe UI", 10, "bold"), cursor="hand2", padx=16, pady=6,
        )
        btn_guardar.pack(side=tk.LEFT, padx=(6, 0))

        dialogo.bind("<Return>", lambda _: accion_guardar())
        dialogo.bind("<Escape>", lambda _: accion_cancelar())

        btn_cancelar.bind("<Enter>", lambda _: btn_cancelar.config(bg="#454B58"))
        btn_cancelar.bind("<Leave>", lambda _: btn_cancelar.config(bg="#353B48"))
        btn_guardar.bind("<Enter>", lambda _: btn_guardar.config(bg="#5B8BFC"))
        btn_guardar.bind("<Leave>", lambda _: btn_guardar.config(bg="#4B7BEC"))

        self.root.wait_window(dialogo)

        if resultado[0] is None:
            return None
        return str(Path.cwd() / resultado[0])

    def _guardar_resultados(self) -> None:
        datos = self._resultado_guardar
        if datos is None:
            return

        ruta = self._dialogo_guardar_nombre()
        if not ruta:
            return

        guardar_resultado(
            Path(ruta),
            enfermedad=self._enfermedad_actual,
            config=datos["config"],
            estadisticas=datos["stats"],
            dias=datos["dias"],
        )

    def _alternar_pausa(self) -> None:
        if not self.motor.ejecutando:
            return
        self.pausado = not self.pausado
        self.botones.configurar_texto_pausa(self.pausado)

    def _finalizar_simulacion(self) -> None:
        self.motor.ejecutando = False
        self.pausado = False
        stats = self.motor.obtener_estadisticas()
        dias = self.motor.frames_transcurridos // 60
        self._mostrar_resultados(self._construir_config(), stats, dias, "manual")

    def cerrar(self) -> None:
        self.motor.ejecutando = False
        self.root.destroy()
