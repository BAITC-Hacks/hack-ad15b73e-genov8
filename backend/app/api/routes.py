"""Read-only MoneyGraph investigation routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.api.models import (
    ClusterDetailResponse,
    ClustersResponse,
    EgoGraphResponse,
    NodeDetailResponse,
    PrioritiesResponse,
    SummaryResponse,
)
from backend.app.api.repository import MoneyGraphRepository, get_repository


router = APIRouter(prefix="/api")


@router.get("/summary", response_model=SummaryResponse)
def summary(repository: MoneyGraphRepository = Depends(get_repository)) -> SummaryResponse:
    return repository.summary()


@router.get("/priorities", response_model=PrioritiesResponse)
def priorities(
    repository: MoneyGraphRepository = Depends(get_repository),
) -> PrioritiesResponse:
    return repository.priorities()


@router.get("/nodes/{gid}", response_model=NodeDetailResponse)
def node_detail(
    gid: str, repository: MoneyGraphRepository = Depends(get_repository)
) -> NodeDetailResponse:
    node = repository.node(gid)
    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown MoneyGraph gid: {gid}",
        )
    return node


@router.get("/nodes/{gid}/graph", response_model=EgoGraphResponse)
def node_graph(
    gid: str,
    limit: int = Query(default=25, ge=1, le=100),
    repository: MoneyGraphRepository = Depends(get_repository),
) -> EgoGraphResponse:
    graph = repository.ego_graph(gid, limit)
    if graph is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown MoneyGraph gid: {gid}",
        )
    return graph


@router.get("/clusters", response_model=ClustersResponse)
def clusters(
    repository: MoneyGraphRepository = Depends(get_repository),
) -> ClustersResponse:
    return repository.clusters()


@router.get("/clusters/{cluster_id}", response_model=ClusterDetailResponse)
def cluster_detail(
    cluster_id: int, repository: MoneyGraphRepository = Depends(get_repository)
) -> ClusterDetailResponse:
    cluster = repository.cluster(cluster_id)
    if cluster is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown MoneyGraph cluster: {cluster_id}",
        )
    return cluster
