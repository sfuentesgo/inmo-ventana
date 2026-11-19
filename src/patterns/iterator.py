from typing import Iterator, List, Tuple
from src.models import Inmueble


class IteradorRecomendaciones(Iterator[List[Inmueble]]):
    """Patrón Iterator para navegación paginada bajo demanda sobre resultados."""

    def __init__(self, coleccion: List[Inmueble], tamano_pagina: int = 4):
        self._coleccion = coleccion
        self._tamano_pagina = tamano_pagina
        self._indice = 0

    def __iter__(self) -> "IteradorRecomendaciones":
        return self

    def __next__(self) -> List[Inmueble]:
        if self._indice >= len(self._coleccion):
            raise StopIteration
        inicio = self._indice
        fin = inicio + self._tamano_pagina
        self._indice = fin
        return self._coleccion[inicio:fin]

    def obtener_pagina(self, numero_pagina: int) -> Tuple[List[Inmueble], bool]:
        """Posiciona el cursor en la página solicitada (1-based) y retorna (items, hay_mas)."""
        pagina_segura = max(1, numero_pagina)
        self._indice = (pagina_segura - 1) * self._tamano_pagina
        try:
            bloque = next(self)
            hay_mas = self._indice < len(self._coleccion)
            return bloque, hay_mas
        except StopIteration:
            return [], False