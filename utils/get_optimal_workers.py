import os

def get_optimal_workers():
    cores = os.cpu_count()
    if not cores:
        cores = 4  # fallback seguro
    
    # Para I/O-bound 4× cores suele ser óptimo
    workers = cores * 4

    # Límite superior razonable
    return min(workers, 64)