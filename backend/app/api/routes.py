"""MoneyGraph investigation routes."""

import os
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from backend.app.agent.investigator import (
    DEFAULT_MODEL,
    InvestigatorError,
    MoneyGraphInvestigator,
)
from backend.app.api.models import (
    ClusterDetailResponse,
    ClustersResponse,
    EgoGraphResponse,
    InvestigatorRequest,
    InvestigatorResponse,
    NodeDetailResponse,
    PrioritiesResponse,
    SummaryResponse,
)
from backend.app.api.repository import MoneyGraphRepository, get_repository
from backend.app.agent.localization import message


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


@router.post(
    "/investigator",
    response_model=InvestigatorResponse,
    responses={503: {"model": InvestigatorResponse}},
)
def investigate(
    request: InvestigatorRequest,
    repository: MoneyGraphRepository = Depends(get_repository),
) -> Union[InvestigatorResponse, JSONResponse]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        unavailable = InvestigatorResponse(
            status="unavailable",
            answer=message("unavailable", request.locale),
            referenced_gids=[],
            tool_calls=[],
        )
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=unavailable.model_dump())

    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    try:
        return MoneyGraphInvestigator(
            repository=repository,
            api_key=api_key,
            model=model,
        ).ask(request.question, locale=request.locale, selected_gid=request.selected_gid)
    except InvestigatorError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=message("failed", request.locale),
        ) from exc
