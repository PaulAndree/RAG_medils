from __future__ import annotations

import numpy as np
import umap
from sklearn.mixture import GaussianMixture


RANDOM_STATE = 42
MAX_CLUSTERS = 8
MIN_LOCAL_CLUSTER_SIZE = 5


def _reduce_embeddings(embeddings: np.ndarray, dim: int) -> np.ndarray:
    """Reduce dense vectors with UMAP while respecting small sample sizes."""

    sample_count, source_dimension = embeddings.shape
    if sample_count < 3:
        return embeddings

    n_components = max(1, min(dim, source_dimension, sample_count - 2))
    reducer = umap.UMAP(
        n_components=n_components,
        n_neighbors=max(2, min(10, sample_count - 1)),
        metric="cosine",
        random_state=RANDOM_STATE,
    )
    return reducer.fit_transform(embeddings)


def _best_gmm(embeddings: np.ndarray) -> GaussianMixture:
    """Select a compact GMM using the Bayesian information criterion."""

    max_clusters = min(MAX_CLUSTERS, max(1, len(embeddings) // 2))
    best_model: GaussianMixture | None = None
    best_bic = float("inf")

    for cluster_count in range(1, max_clusters + 1):
        model = GaussianMixture(
            n_components=cluster_count,
            covariance_type="full",
            reg_covar=1e-6,
            n_init=3,
            random_state=RANDOM_STATE,
        )
        model.fit(embeddings)
        bic = model.bic(embeddings)
        if bic < best_bic:
            best_model = model
            best_bic = bic

    if best_model is None:  # Defensive; at least the one-component fit is tried.
        raise RuntimeError("Could not fit a Gaussian mixture model")
    return best_model


def _soft_clusters(
    embeddings: np.ndarray,
    threshold: float,
) -> list[list[int]]:
    """Assign every row to all GMM components above the probability threshold."""

    model = _best_gmm(embeddings)
    probabilities = model.predict_proba(embeddings)
    memberships: list[list[int]] = []

    for row in probabilities:
        # This is the key RAPTOR soft-clustering step: predict_proba allows a
        # semantically overlapping node to appear in more than one cluster.
        selected = np.flatnonzero(row >= threshold).tolist()
        if not selected:
            selected = [int(np.argmax(row))]
        memberships.append(selected)

    return memberships


def perform_clustering(
    embeddings: list[list[float]],
    dim: int = 10,
    threshold: float = 0.1,
) -> list[list[int]]:
    """Run RAPTOR-style global UMAP/GMM then local UMAP/GMM clustering.

    The return value contains one list of cluster IDs for each input node.
    A node can have multiple IDs because both clustering stages are soft.
    """

    matrix = np.asarray(embeddings, dtype=float)
    if matrix.ndim != 2 or len(matrix) == 0:
        raise ValueError("embeddings must be a non-empty rectangular matrix")
    if not np.isfinite(matrix).all():
        raise ValueError("embeddings contain NaN or infinite values")
    if dim < 1:
        raise ValueError("dim must be at least 1")
    if not 0.0 < threshold <= 1.0:
        raise ValueError("threshold must be in the interval (0, 1]")
    if len(matrix) == 1:
        return [[0]]

    # Global clustering finds broad regions of the embedding space.
    global_memberships = _soft_clusters(
        _reduce_embeddings(matrix, dim),
        threshold,
    )
    global_cluster_ids = sorted(
        {cluster_id for memberships in global_memberships for cluster_id in memberships}
    )

    final_memberships: list[list[int]] = [[] for _ in range(len(matrix))]
    next_cluster_id = 0

    # Each global region is clustered again in the original embedding space.
    # Overlapping global memberships are retained, as in RAPTOR.
    for global_cluster_id in global_cluster_ids:
        member_indices = [
            index
            for index, memberships in enumerate(global_memberships)
            if global_cluster_id in memberships
        ]

        if len(member_indices) < MIN_LOCAL_CLUSTER_SIZE:
            for index in member_indices:
                final_memberships[index].append(next_cluster_id)
            next_cluster_id += 1
            continue

        local_matrix = matrix[member_indices]
        local_memberships = _soft_clusters(
            _reduce_embeddings(local_matrix, dim),
            threshold,
        )
        local_cluster_ids = sorted(
            {
                cluster_id
                for memberships in local_memberships
                for cluster_id in memberships
            }
        )

        for local_cluster_id in local_cluster_ids:
            for local_index, memberships in enumerate(local_memberships):
                if local_cluster_id in memberships:
                    original_index = member_indices[local_index]
                    final_memberships[original_index].append(next_cluster_id)
            next_cluster_id += 1

    # Remove duplicate IDs without changing their deterministic order.
    return [list(dict.fromkeys(memberships)) for memberships in final_memberships]
