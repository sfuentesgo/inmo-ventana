from pydantic import BaseModel
from typing import List, Optional


class Inmueble(BaseModel):
    id: int
    titulo: str
    tipo: str              # "Apartamento" o "Casa"
    zona: str              # Localidad de Bogotá
    precio: int            # COP (exclusivo venta)
    area_m2: float
    habitaciones: int
    banos: int
    estrato: int
    imagen_url: str


class RespuestaNavegacion(BaseModel):
    modo: str
    estrategia_aplicada: str
    inmueble_base: Inmueble
    recomendaciones: List[Inmueble]
    total_encontrados: int
    pagina_actual: int
    tiene_siguiente: bool
    nodos_evaluados: int
    tiempo_ms: float
    origen_datos: str