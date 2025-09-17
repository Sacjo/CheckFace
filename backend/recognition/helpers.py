# backend/recognition/helpers.py

import numpy as np

def l2_normalize(v: np.ndarray, eps=1e-10) -> np.ndarray:
    """Normaliza un vector a norma L2."""
    n = np.linalg.norm(v) + eps
    return v / n

def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Distancia coseno entre vectores normalizados."""
    return 1.0 - float(np.dot(a, b))

def robust_mean(embs: np.ndarray, z=2.0) -> np.ndarray:
    """Calcula un centroide robusto eliminando outliers."""
    if embs.ndim != 2 or embs.shape[0] == 0:
        raise ValueError("Embeddings vacíos o con forma inválida")

    # normalizar todos
    embs_norm = np.apply_along_axis(l2_normalize, 1, embs)

    # media inicial
    centroid = l2_normalize(embs_norm.mean(axis=0))

    # distancias al centroide
    dists = np.array([cosine_distance(e, centroid) for e in embs_norm])
    thr = dists.mean() + z * (dists.std() if dists.std() > 0 else 0)

    # filtrar outliers y recomputar si hay suficientes
    keep = dists <= thr
    kept = embs_norm[keep]
    if kept.shape[0] >= max(3, int(0.6 * embs_norm.shape[0])):
        centroid = l2_normalize(kept.mean(axis=0))

    return centroid

def calcular_distancia_promedio(embeddings_list):
    if len(embeddings_list) < 2:
        return 0.0
    embs = [l2_normalize(np.array(e)) for e in embeddings_list]
    dist = []
    for i in range(len(embs)):
        for j in range(i + 1, len(embs)):
            dist.append(cosine_distance(embs[i], embs[j]))
    return float(np.mean(dist)) if dist else 0.0