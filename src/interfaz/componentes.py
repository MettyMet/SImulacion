import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.configuracion import (
    FONDO_PANEL, COLOR_TEXTO, FONDO_OSCURO, PRESETS_ENFERMEDADES,
    COLOR_BOTON_PRIMARY, COLOR_BOTON_PRIMARY_HOVER,
    COLOR_BOTON_WARNING, COLOR_BOTON_WARNING_HOVER,
    COLOR_BOTON_DANGER, COLOR_BOTON_DANGER_HOVER,
    COLOR_BOTON_OUTLINE_BG, COLOR_BOTON_OUTLINE_HOVER,
    COLOR_SLIDER_TROUGH,
)


class SliderEtiquetado(ttk.Frame):
    def __init__(
        self, master: tk.Widget, etiqueta: str,
        variable: tk.Variable, minimo: float, maximo: float,
        resolucion: float, formato: str = "entero",
        descripcion: str = "",
    ) -> None:
        super().__init__(master)
        self.configure(style="Dark.TFrame")
        self.pack(fill=tk.X, padx=15, pady=5)

        self._var_texto = tk.StringVar()
        self._etiqueta = etiqueta
        self._formato = formato

        def actualizar_texto(*args: object) -> None:
            val = variable.get()
            if self._formato == "porcentaje":
                self._var_texto.set(f"{self._etiqueta}: {val * 100:.2f}%")
            elif self._formato == "decimal":
                self._var_texto.set(f"{self._etiqueta}: {val:.4f}")
            elif self._formato == "velocidad":
                self._var_texto.set(f"{self._etiqueta}: x{val:.1f}")
            else:
                self._var_texto.set(f"{self._etiqueta}: {int(val)}")

        variable.trace_add("write", actualizar_texto)
        actualizar_texto()

        ttk.Label(
            self, textvariable=self._var_texto,
            font=("Segoe UI", 10, "bold"), foreground="#718093",
        ).pack(anchor="w")

        self.scale = tk.Scale(
            self, variable=variable, from_=minimo, to=maximo,
            resolution=resolucion,
            orient=tk.HORIZONTAL,
            bg=FONDO_PANEL, fg=COLOR_TEXTO,
            troughcolor=COLOR_SLIDER_TROUGH,
            highlightthickness=0, bd=0,
        )
        self.scale.pack(fill=tk.X, pady=(5, 0))

        if descripcion:
            ttk.Label(
                self, text=descripcion,
                font=("Segoe UI", 9), foreground="#8A95A5",
                wraplength=220,
            ).pack(anchor="w", pady=(2, 0))

    def configurar_rango(self, max_val: float) -> None:
        self.scale.config(to=max_val)


class SelectorEnfermedad(ttk.Frame):
    def __init__(
        self, master: tk.Widget,
        al_seleccionar: Callable[[], None],
        titulo: str = "Seleccionar Enfermedad:",
    ) -> None:
        super().__init__(master)
        self.configure(style="Dark.TFrame")
        self.pack(pady=(5, 0), fill=tk.X, padx=10)

        ttk.Label(
            self, text=titulo,
            font=("Segoe UI", 9, "bold"), foreground="#57606F",
        ).pack(anchor="w")
        self.combo = ttk.Combobox(
            self, values=list(PRESETS_ENFERMEDADES.keys()),
            state="readonly", font=("Segoe UI", 10),
            style="Dark.TCombobox",
        )
        self.combo.set("Personalizada")
        self.combo.pack(fill=tk.X, pady=(5, 0))
        self.combo.bind("<<ComboboxSelected>>", lambda _: al_seleccionar())


class BotoneraControl(ttk.Frame):
    def __init__(
        self, master: tk.Widget,
        al_iniciar: Callable[[], None],
        al_comenzar: Callable[[], None],
        al_volver: Callable[[], None],
        al_pausar: Callable[[], None],
        al_nueva_simulacion: Callable[[], None],
        al_finalizar: Callable[[], None],
    ) -> None:
        super().__init__(master)
        self.configure(style="Dark.TFrame")
        self.pack(pady=10, fill=tk.X, padx=5)

        self._al_iniciar = al_iniciar
        self._al_comenzar = al_comenzar
        self._al_volver = al_volver
        self._al_pausar = al_pausar
        self._al_nueva_simulacion = al_nueva_simulacion
        self._al_finalizar = al_finalizar

        self.btn_principal = self._crear_btn_primary("▶ INICIAR", self._al_iniciar)
        self.btn_secundario = self._crear_btn_outline("↻ VOLVER", self._al_volver)
        self.btn_pausa = self._crear_btn_warning("⏸ PAUSAR", self._alternar_pausa)
        self.btn_finalizar = self._crear_btn_danger("⏹ FINALIZAR", self._al_finalizar)

    @staticmethod
    def _btn_style(bg: str, hover: str, fg: str = "white") -> dict:
        return dict(
            font=("Segoe UI", 11, "bold"),
            bg=bg, fg=fg,
            activebackground=hover, activeforeground=fg,
            relief="flat", bd=0, cursor="hand2",
            highlightthickness=0, padx=12, pady=8,
        )

    def _crear_btn_generico(self, texto: str, cmd, estilo: dict) -> tk.Button:
        btn = tk.Button(self, text=texto, **estilo, command=cmd)
        btn.bind("<Enter>", lambda e: btn.config(bg=estilo["activebackground"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=estilo["bg"]))
        return btn

    def _crear_btn_primary(self, texto: str, cmd) -> tk.Button:
        return self._crear_btn_generico(
            texto, cmd,
            self._btn_style(COLOR_BOTON_PRIMARY, COLOR_BOTON_PRIMARY_HOVER),
        )

    def _crear_btn_outline(self, texto: str, cmd) -> tk.Button:
        return self._crear_btn_generico(
            texto, cmd,
            dict(
                font=("Segoe UI", 11, "bold"),
                bg=COLOR_BOTON_OUTLINE_BG, fg=COLOR_TEXTO,
                activebackground=COLOR_BOTON_OUTLINE_HOVER, activeforeground=COLOR_TEXTO,
                relief="solid", bd=1, cursor="hand2",
                highlightthickness=0, highlightbackground=COLOR_SLIDER_TROUGH,
                padx=12, pady=8,
            ),
        )

    def _crear_btn_warning(self, texto: str, cmd) -> tk.Button:
        return self._crear_btn_generico(
            texto, cmd,
            self._btn_style(COLOR_BOTON_WARNING, COLOR_BOTON_WARNING_HOVER),
        )

    def _crear_btn_danger(self, texto: str, cmd) -> tk.Button:
        return self._crear_btn_generico(
            texto, cmd,
            self._btn_style(COLOR_BOTON_DANGER, COLOR_BOTON_DANGER_HOVER),
        )

    def _empaquetar_unico(self, btn: tk.Button) -> None:
        btn.pack(fill=tk.X, pady=2)

    def _empaquetar_doble(self, btn1: tk.Button, btn2: tk.Button) -> None:
        btn1.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        btn2.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

    def configurar_fase(self, fase: str) -> None:
        for widget in (self.btn_principal, self.btn_secundario, self.btn_pausa, self.btn_finalizar):
            widget.pack_forget()

        if fase == "listo":
            self._empaquetar_unico(self.btn_principal)
            self.btn_principal.config(text="▶ INICIAR", command=self._al_iniciar)

        elif fase == "preparado":
            self._empaquetar_doble(self.btn_principal, self.btn_secundario)
            self.btn_principal.config(text="▶ COMENZAR", command=self._al_comenzar)
            self.btn_secundario.config(text="↻ VOLVER", command=self._al_volver)

        elif fase == "ejecutando":
            self._empaquetar_unico(self.btn_pausa)
            self.btn_pausa.config(text="⏸ PAUSAR")

        elif fase == "terminado":
            self._empaquetar_unico(self.btn_principal)
            self.btn_principal.config(text="⟳ REINICIAR", command=self._al_nueva_simulacion)

    def configurar_texto_pausa(self, pausado: bool) -> None:
        if pausado:
            self.btn_pausa.pack_forget()
            self._empaquetar_doble(self.btn_pausa, self.btn_finalizar)
            self.btn_pausa.config(text="▶ REANUDAR")
            self.btn_finalizar.config(text="⏹ FINALIZAR", command=self._al_finalizar)
        else:
            self.btn_finalizar.pack_forget()
            self.btn_pausa.pack_forget()
            self._empaquetar_unico(self.btn_pausa)
            self.btn_pausa.config(text="⏸ PAUSAR")

    def _alternar_pausa(self) -> None:
        self._al_pausar()
