import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from src.models import Inmueble, RespuestaNavegacion
from src.repository import CatalogoRepositorio
from src.patterns.strategy import (
    EstrategiaCercaniaPrecio,
    EstrategiaMismaZona,
    EstrategiaRecomendacion,
)
from src.patterns.iterator import IteradorRecomendaciones
from src.patterns.cache import CacheNavegacion

app = FastAPI(
    title="Inmo-Ventana | Motor de Navegación Arquitectónica",
    description="Prototipo de optimización de navegación inmobiliaria con Strategy, Iterator y Cache-Aside",
    version="1.0.0",
)

repositorio = CatalogoRepositorio(total_registros=10000)
cache_rutas = CacheNavegacion(ttl_segundos=120)

ESTRATEGIAS: dict[str, EstrategiaRecomendacion] = {
    "precio": EstrategiaCercaniaPrecio(tolerancia=0.15),
    "zona": EstrategiaMismaZona(),
}


@app.get("/", response_class=HTMLResponse)
def servir_interfaz():
    ruta_html = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(content=ruta_html.read_text(encoding="utf-8"))


@app.get("/api/inmuebles", response_model=list[Inmueble])
def listar_inmuebles(limite: int = 8):
    return repositorio.listar_muestra(limite=limite)


@app.get("/api/navegacion/plana/{inmueble_id}", response_model=RespuestaNavegacion)
def navegacion_plana_sin_optimizar(inmueble_id: int, pagina: int = Query(1, ge=1)):
    """
    ESCENARIO BASE (NO OPTIMIZADO):
    - Sin caché (recalcula en cada clic o cambio de página).
    - Recorrido secuencial O(n) rígido sin índices ni separación de estrategias.
    - Evalúa y ordena todo el catálogo completo en cada petición.
    """
    inicio = time.perf_counter()

    # Búsqueda lineal O(n) simulando ausencia de índice directo
    base = None
    todos = repositorio.obtener_todos()
    for item in todos:
        if item.id == inmueble_id:
            base = item
            break

    if not base:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")

    # Filtrado rígido acoplado y evaluación de similitud multi-criterio sin poda
    resultados = []
    min_p, max_p = base.precio * 0.85, base.precio * 1.15
    for candidato in todos:
        if candidato.id != base.id and min_p <= candidato.precio <= max_p:
            # Cálculo pesado innecesario sobre strings y múltiples atributos en cada iteración
            score = (
                abs(candidato.precio - base.precio) / base.precio
                + abs(candidato.area_m2 - base.area_m2) / base.area_m2
                + (0 if candidato.zona.lower() == base.zona.lower() else 0.5)
            )
            resultados.append((score, candidato))

    resultados.sort(key=lambda par: par[0])
    solo_inmuebles = [par[1] for par in resultados]

    # Paginación manual volcando todo el arreglo
    tam_pagina = 4
    idx_inicio = (pagina - 1) * tam_pagina
    bloque = solo_inmuebles[idx_inicio : idx_inicio + tam_pagina]

    duracion_ms = round((time.perf_counter() - inicio) * 1000, 3)

    return RespuestaNavegacion(
        modo="PLANO (Sin optimizar)",
        estrategia_aplicada="Barrido Lineal Acoplado O(n)",
        inmueble_base=base,
        recomendaciones=bloque,
        total_encontrados=len(solo_inmuebles),
        pagina_actual=pagina,
        tiene_siguiente=(idx_inicio + tam_pagina) < len(solo_inmuebles),
        nodos_evaluados=len(todos) * 2,
        tiempo_ms=duracion_ms,
        origen_datos="Cómputo Directo (Sin Caché)",
    )


@app.get("/api/navegacion/optimizada/{inmueble_id}", response_model=RespuestaNavegacion)
def navegacion_optimizada(
    inmueble_id: int,
    estrategia: str = Query("precio", pattern="^(precio|zona)$"),
    pagina: int = Query(1, ge=1),
):
    """
    ESCENARIO OPTIMIZADO:
    - Acceso O(1) al inmueble base.
    - Patrón Cache-Aside para memorizar resultados de rutas frecuentes.
    - Patrón Strategy para desacoplar e intercambiar el algoritmo de recomendación.
    - Patrón Iterator para entregar páginas de resultados bajo demanda.
    """
    inicio = time.perf_counter()

    base = repositorio.obtener_por_id(inmueble_id)
    if not base:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")

    estrategia_obj = ESTRATEGIAS[estrategia]
    clave_cache = f"nav:{estrategia}:{inmueble_id}"

    datos_cacheados = cache_rutas.obtener(clave_cache)
    if datos_cacheados is not None:
        lista_recomendados = datos_cacheados
        nodos_evaluados = 0
        origen = "MEMORIA CACHÉ (Cache Hit)"
    else:
        lista_recomendados, nodos_evaluados = estrategia_obj.recomendar(base, repositorio)
        cache_rutas.guardar(clave_cache, lista_recomendados)
        origen = "MOTOR STRATEGY (Cache Miss -> Guardado en Caché)"

    # Patrón Iterator: entrega solo la ventana solicitada
    iterador = IteradorRecomendaciones(lista_recomendados, tamano_pagina=4)
    bloque, tiene_siguiente = iterador.obtener_pagina(pagina)

    duracion_ms = round((time.perf_counter() - inicio) * 1000, 3)

    return RespuestaNavegacion(
        modo="OPTIMIZADO (Strategy + Iterator + Cache)",
        estrategia_aplicada=estrategia_obj.nombre,
        inmueble_base=base,
        recomendaciones=bloque,
        total_encontrados=len(lista_recomendados),
        pagina_actual=pagina,
        tiene_siguiente=tiene_siguiente,
        nodos_evaluados=nodos_evaluados,
        tiempo_ms=duracion_ms,
        origen_datos=origen,
    )


@app.post("/api/cache/limpiar")
def limpiar_cache():
    cache_rutas.limpiar()
    return {"mensaje": "Caché de navegación reiniciada"}