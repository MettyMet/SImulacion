import random

from src.configuracion import Estado, ConfigSimulacion, MAX_HISTORIAL
from src.modelos.individuo import Individuo
from src.simulacion.espacial import HashEspacial


class MotorSimulacion:
    def __init__(self) -> None:
        self.poblacion: list[Individuo] = []
        self._hash: HashEspacial = HashEspacial()
        self.historial: dict[Estado, list[int]] = {
            Estado.SANO: [],
            Estado.INFECTADO: [],
            Estado.INMUNE: [],
            Estado.MUERTO: [],
        }
        self.frames_transcurridos: int = 0
        self.ejecutando: bool = False
        self.num_individuos: int = 0
        self._conteo: dict[Estado, int] = {
            Estado.SANO: 0,
            Estado.INFECTADO: 0,
            Estado.INMUNE: 0,
            Estado.MUERTO: 0,
        }
        self._estado_inicial: dict[Estado, int] = dict(self._conteo)

    def reiniciar(self, cfg: ConfigSimulacion) -> None:
        self.poblacion.clear()
        self._hash.limpiar()
        self.frames_transcurridos = 0
        self.ejecutando = True
        self.num_individuos = cfg.num_individuos

        for estado in self.historial:
            self.historial[estado].clear()

        self._conteo[Estado.SANO] = 0
        self._conteo[Estado.INFECTADO] = 0
        self._conteo[Estado.INMUNE] = 0
        self._conteo[Estado.MUERTO] = 0

        n_infectados = cfg.num_infectados_iniciales
        n_inmunes = cfg.num_inmunes_iniciales

        for i in range(cfg.num_individuos):
            x = random.randint(20, 780)
            y = random.randint(20, 480)
            if i < n_infectados:
                estado = Estado.INFECTADO
            elif i < n_infectados + n_inmunes:
                estado = Estado.INMUNE
            else:
                estado = Estado.SANO
            ind = Individuo(x=x, y=y, estado=estado)
            self.poblacion.append(ind)
            self._conteo[estado] += 1
            self._hash.insertar(i, x, y)

        for i, ind in enumerate(self.poblacion):
            if ind.estado == Estado.INFECTADO:
                ind.infectar(cfg.tiempo_muerte)

        self._estado_inicial = dict(self._conteo)

    @property
    def estado_inicial(self) -> dict[Estado, int]:
        return dict(self._estado_inicial)

    def avanzar(self, cfg: ConfigSimulacion) -> dict[Estado, int]:
        if not self.ejecutando:
            return dict(self._conteo)

        self.frames_transcurridos += 1

        recien_infectados: list[int] = []

        for i, ind in enumerate(self.poblacion):
            x_ant, y_ant = ind.x, ind.y
            ind.mover()
            if ind.estado == Estado.INFECTADO:
                if ind.actualizar_infeccion(cfg.prob_inmunidad, cfg.prob_infeccion):
                    self._conteo[ind.estado] += 1
                    if ind.estado == Estado.MUERTO:
                        self._conteo[Estado.INFECTADO] -= 1
                    elif ind.estado == Estado.INMUNE:
                        self._conteo[Estado.INFECTADO] -= 1
            if ind.estado != Estado.MUERTO:
                self._hash.actualizar(i, x_ant, y_ant, ind.x, ind.y)

        for i, infectado in enumerate(self.poblacion):
            if infectado.estado != Estado.INFECTADO:
                continue

            vecinos = self._hash.consultar_radio(
                infectado.x, infectado.y, cfg.radio_infeccion,
            )
            for j in vecinos:
                if j in recien_infectados:
                    continue
                vecino = self.poblacion[j]
                if vecino.estado == Estado.SANO:
                    if random.random() < cfg.prob_infeccion:
                        vecino.infectar(cfg.tiempo_muerte)
                        recien_infectados.append(j)
                        self._conteo[Estado.INFECTADO] += 1
                        self._conteo[Estado.SANO] -= 1
                elif vecino.estado == Estado.INMUNE:
                    if random.random() < vecino.prob_reinfeccion:
                        vecino.infectar(cfg.tiempo_muerte)
                        recien_infectados.append(j)
                        self._conteo[Estado.INFECTADO] += 1
                        self._conteo[Estado.INMUNE] -= 1

        if self._conteo[Estado.INFECTADO] == 0:
            self.ejecutando = False
        if cfg.max_dias > 0 and self.frames_transcurridos >= cfg.max_dias * cfg.fps:
            self.ejecutando = False

        stats = dict(self._conteo)
        for estado in self.historial:
            self.historial[estado].append(stats[estado])
            if len(self.historial[estado]) > MAX_HISTORIAL:
                self.historial[estado].pop(0)

        return stats

    def obtener_estadisticas(self) -> dict[Estado, int]:
        return dict(self._conteo)
