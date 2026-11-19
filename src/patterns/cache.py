import time
from typing import Any, Dict, Optional, Tuple


class CacheNavegacion:
    """Patrón Cache-Aside en memoria con TTL para memorizar recorridos frecuentes."""

    def __init__(self, ttl_segundos: int = 60):
        self._ttl = ttl_segundos
        self._almacen: Dict[str, Tuple[Any, float]] = {}

    def obtener(self, clave: str) -> Optional[Any]:
        registro = self._almacen.get(clave)
        if not registro:
            return None
        valor, expira_en = registro
        if time.time() > expira_en:
            del self._almacen[clave]
            return None
        return valor

    def guardar(self, clave: str, valor: Any) -> None:
        self._almacen[clave] = (valor, time.time() + self._ttl)

    def limpiar(self) -> None:
        self._almacen.clear()