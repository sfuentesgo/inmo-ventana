import random
from typing import Dict, List, Optional
from src.models import Inmueble

ZONAS_BOGOTA_SABANA = [
    "Usaquén", "Chapinero", "Suba", "Engativa", "Fontibón", "Kennedy", "Bosa", "Ciudad Bolívar", "Tunjuelito",
     "Teusaquillo", "La Candelaria", "Santa Fe", "San Cristóbal", "Usme", "Sumapaz", "Antonio Nariño", "Puente Aranda",
]

TIPOS_VIVIENDA = ["Apartamento", "Casa"]


class CatalogoRepositorio:
    """Almacén en memoria con 1000 inmuebles en venta para pruebas de navegación."""

    def __init__(self, total_registros: int = 10000):
        self._inmuebles: List[Inmueble] = []
        self._indice_por_id: Dict[int, Inmueble] = {}
        self._indice_por_zona: Dict[str, List[Inmueble]] = {z: [] for z in ZONAS_BOGOTA_SABANA}
        self._generar_catalogo(total_registros)

    def _generar_catalogo(self, total: int) -> None:
        rng = random.Random(69)  # Semilla reproducibilidad
        for i in range(1, total + 1):
            tipo = rng.choice(TIPOS_VIVIENDA)
            zona = rng.choice(ZONAS_BOGOTA_SABANA)
            habitaciones = rng.randint(1, 5)
            banos = max(1, min(habitaciones, rng.randint(1, 4)))
            area = round(rng.uniform(42.0, 260.0), 1)
            estrato = rng.choice([3, 4, 5, 6])
            # Precio realista de venta en COP según área y estrato
            valor_m2 = rng.randint(4_200_000, 9_500_000) + (estrato * 350_000)
            precio = int(round((area * valor_m2) / 1_000_000) * 1_000_000)

            inmueble = Inmueble(
                id=i,
                titulo=f"{tipo} en venta en {zona} #{i}",
                tipo=tipo,
                zona=zona,
                precio=precio,
                area_m2=area,
                habitaciones=habitaciones,
                banos=banos,
                estrato=estrato,
                imagen_url=f"https://picsum.photos/seed/inmo{i}/400/260"
            )
            self._inmuebles.append(inmueble)
            self._indice_por_id[i] = inmueble
            self._indice_por_zona[zona].append(inmueble)

    def obtener_todos(self) -> List[Inmueble]:
        return self._inmuebles

    def obtener_por_id(self, inmueble_id: int) -> Optional[Inmueble]:
        return self._indice_por_id.get(inmueble_id)

    def obtener_por_zona(self, zona: str) -> List[Inmueble]:
        return self._indice_por_zona.get(zona, [])

    def listar_muestra(self, limite: int = 12) -> List[Inmueble]:
        return self._inmuebles[:limite]