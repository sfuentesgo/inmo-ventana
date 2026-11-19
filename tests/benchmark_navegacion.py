import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import requests

BASE_URL = "http://127.0.0.1:8000"
TOTAL_PETICIONES = 100
USUARIOS_CONCURRENTES = 10
IDS_PRUEBA = [1, 2, 3, 4, 5, 10, 25, 50, 100, 250]


def ejecutar_escenario(ruta_base: str, nombre: str):
    requests.post(f"{BASE_URL}/api/cache/limpiar")
    latencias_ms = []
    nodos_lista = []

    def tarea(i: int):
        inmueble_id = IDS_PRUEBA[i % len(IDS_PRUEBA)]
        pagina = (i % 3) + 1
        t0 = time.perf_counter()
        resp = requests.get(f"{BASE_URL}{ruta_base}/{inmueble_id}?pagina={pagina}")
        dt = (time.perf_counter() - t0) * 1000
        data = resp.json()
        return dt, data["nodos_evaluados"]

    inicio_total = time.perf_counter()
    with ThreadPoolExecutor(max_workers=USUARIOS_CONCURRENTES) as pool:
        resultados = list(pool.map(tarea, range(TOTAL_PETICIONES)))
    tiempo_total_s = time.perf_counter() - inicio_total

    for dt, nodos in resultados:
        latencias_ms.append(dt)
        nodos_lista.append(nodos)

    promedio = statistics.mean(latencias_ms)
    p95 = sorted(latencias_ms)[int(TOTAL_PETICIONES * 0.95) - 1]
    throughput = TOTAL_PETICIONES / tiempo_total_s
    promedio_nodos = statistics.mean(nodos_lista)

    print(f"\n--- {nombre} ---")
    print(f"Peticiones totales:      {TOTAL_PETICIONES} ({USUARIOS_CONCURRENTES} concurrentes)")
    print(f"Tiempo total ráfaga:     {tiempo_total_s:.3f} s")
    print(f"Throughput:              {throughput:.2f} req/s")
    print(f"Latencia promedio:       {promedio:.2f} ms")
    print(f"Latencia P95:            {p95:.2f} ms")
    print(f"Nodos evaluados/petición:{promedio_nodos:,.0f}")
    return promedio, throughput, promedio_nodos


if __name__ == "__main__":
    print("==========================================================")
    print(" BENCHMARK ARQUITECTÓNICO - INMO-VENTANA (10.000 INMUEBLES)")
    print("==========================================================")

    lat_base, thr_base, nod_base = ejecutar_escenario(
        "/api/navegacion/plana", "ESCENARIO 1: NAVEGACIÓN PLANA (Sin Optimizar)"
    )
    lat_opt, thr_opt, nod_opt = ejecutar_escenario(
        "/api/navegacion/optimizada", "ESCENARIO 2: ARQUITECTURA OPTIMIZADA (Strategy + Iterator + Cache)"
    )

    mejora_latencia = ((lat_base - lat_opt) / lat_base) * 100
    mejora_nodos = ((nod_base - nod_opt) / nod_base) * 100

    print("\n==================== RESUMEN DE MEJORA ====================")
    print(f"Reducción de latencia promedio: {mejora_latencia:.1f}%")
    print(f"Reducción de nodos evaluados:   {mejora_nodos:.1f}%")
    print(f"Incremento de Throughput:       {(thr_opt / thr_base):.2f}x")