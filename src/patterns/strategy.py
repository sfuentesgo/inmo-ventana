from abc import ABC, abstractmethod
from typing import List, Tuple
from src.models import Inmueble
from src.repository import CatalogoRepositorio


class EstrategiaRecomendacion(ABC):
    """Interfaz base del Patrón Strategy para algoritmos de navegación."""

    @property
    @abstractmethod
    def nombre(self) -> str:
        pass

    @abstractmethod
    def recomendar(
        self, base: Inmueble, repositorio: CatalogoRepositorio
    ) -> Tuple[List[Inmueble], int]:
        """Retorna (lista_ordenada_recomendados, cantidad_nodos_evaluados)."""
        pass


class EstrategiaCercaniaPrecio(EstrategiaRecomendacion):
    """Recomienda inmuebles en venta con presupuesto cercano (+/- 15%) al inmueble visto."""

    def __init__(self, tolerancia: float = 0.15):
        self.tolerancia = tolerancia

    @property
    def nombre(self) -> str:
        return "Cercanía de Precio (±15%)"

    def recomendar(
        self, base: Inmueble, repositorio: CatalogoRepositorio
    ) -> Tuple[List[Inmueble], int]:
        min_precio = base.precio * (1 - self.tolerancia)
        max_precio = base.precio * (1 + self.tolerancia)

        candidatos = []
        todos = repositorio.obtener_todos()
        nodos_evaluados = len(todos)

        for item in todos:
            if item.id != base.id and min_precio <= item.precio <= max_precio:
                candidatos.append(item)

        candidatos.sort(key=lambda x: abs(x.precio - base.precio))
        return candidatos, nodos_evaluados


class EstrategiaMismaZona(EstrategiaRecomendacion):
    """Recomienda inmuebles en la misma localidad/municipio ordenados por área similar."""

    @property
    def nombre(self) -> str:
        return "Misma Zona y Área Similar"

    def recomendar(
        self, base: Inmueble, repositorio: CatalogoRepositorio
    ) -> Tuple[List[Inmueble], int]:
        # Aprovecha el índice por zona para evaluar solo el subconjunto geográfico
        subconjunto_zona = repositorio.obtener_por_zona(base.zona)
        nodos_evaluados = len(subconjunto_zona)

        candidatos = [
            item for item in subconjunto_zona
            if item.id != base.id and item.tipo == base.tipo
        ]
        candidatos.sort(key=lambda x: abs(x.area_m2 - base.area_m2))
        return candidatos, nodos_evaluados