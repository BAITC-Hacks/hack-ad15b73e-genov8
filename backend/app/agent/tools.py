"""Grounded, read-only tools for the MoneyGraph investigator."""

from collections import deque
from typing import Any, Dict, Iterable, List, Optional, Set

import networkx as nx

from backend.app.api.repository import MoneyGraphRepository


ALLOWED_ROLES = {
    "coordinator",
    "distributor",
    "consolidator",
    "transit",
    "terminal",
    "peripheral",
}
MAX_RESULT_NODES = 50
MAX_WHAT_IF_GIDS = 20


def _string_gid(gid: int) -> str:
    return str(int(gid))


class MoneyGraphTools:
    """Execute bounded graph queries against the cached deterministic snapshot."""

    def __init__(self, repository: MoneyGraphRepository) -> None:
        self.repository = repository
        self.graph = repository.data.graph

    def _parse_gid(self, gid: str) -> Optional[int]:
        return int(gid) if self.repository.has_gid(gid) else None

    def _unknown_gids(self, gids: Iterable[str]) -> List[str]:
        return sorted({gid for gid in gids if self._parse_gid(gid) is None})

    def node_card(self, gid: str) -> Dict[str, Any]:
        node = self.repository.node(gid)
        if node is None:
            return {"error": f"Unknown MoneyGraph gid: {gid}", "referenced_gids": []}
        return {
            "node": node.model_dump(),
            "referenced_gids": [node.gid],
        }

    def _shortest_paths_from(self, source: int, max_hops: int) -> Dict[int, List[int]]:
        paths: Dict[int, List[int]] = {source: [source]}
        queue = deque([source])
        while queue:
            current = queue.popleft()
            current_path = paths[current]
            if len(current_path) - 1 >= max_hops:
                continue
            for neighbor in sorted(self.graph.successors(current)):
                if neighbor in paths:
                    continue
                paths[neighbor] = current_path + [int(neighbor)]
                queue.append(int(neighbor))
        return paths

    def common_receivers(self, gids: List[str], max_hops: int = 2) -> Dict[str, Any]:
        unique_gids = list(dict.fromkeys(gids))
        if len(unique_gids) < 2:
            return {
                "error": "common_receivers requires at least two distinct gids",
                "referenced_gids": [],
            }
        if len(unique_gids) > 20:
            return {"error": "common_receivers accepts at most 20 gids", "referenced_gids": []}
        if max_hops < 1 or max_hops > 2:
            return {"error": "max_hops must be between 1 and 2", "referenced_gids": []}
        unknown = self._unknown_gids(unique_gids)
        if unknown:
            return {"error": "One or more gids are unknown", "unknown_gids": unknown, "referenced_gids": []}

        parsed_sources = [int(gid) for gid in unique_gids]
        paths_by_source = {
            source: self._shortest_paths_from(source, max_hops) for source in parsed_sources
        }
        candidates: Dict[int, List[Dict[str, Any]]] = {}
        source_set = set(parsed_sources)
        for source, paths in paths_by_source.items():
            for target, path in paths.items():
                if target == source or target in source_set:
                    continue
                candidates.setdefault(target, []).append(
                    {
                        "source_gid": _string_gid(source),
                        "hops": len(path) - 1,
                        "path": [_string_gid(node) for node in path],
                    }
                )

        matches = []
        for target, support in candidates.items():
            if len(support) < 2:
                continue
            row = self.repository.nodes_by_gid.loc[target]
            matches.append(
                {
                    "gid": _string_gid(target),
                    "role": str(row["role"]),
                    "priority_score": float(row["priority_score"]),
                    "cluster_id": int(row["cluster_id"]),
                    "supporting_source_count": len(support),
                    "support": sorted(support, key=lambda item: item["source_gid"]),
                    "observability": self.repository._observability(row).model_dump(),
                }
            )
        matches.sort(
            key=lambda item: (
                -item["supporting_source_count"],
                min(entry["hops"] for entry in item["support"]),
                -item["priority_score"],
                item["gid"],
            )
        )
        matches = matches[:20]
        referenced: Set[str] = set(unique_gids)
        for match in matches:
            referenced.add(match["gid"])
            for support in match["support"]:
                referenced.update(support["path"])
        return {
            "source_gids": unique_gids,
            "max_hops": max_hops,
            "common_receivers": matches,
            "match_count": len(matches),
            "note": "Only observed directed paths are included.",
            "referenced_gids": sorted(referenced),
        }

    def _bounded_paths(self, source: int, target: int, max_hops: int, limit: int = 5) -> List[List[int]]:
        found: List[List[int]] = []
        queue = deque([[source]])
        while queue and len(found) < limit:
            path = queue.popleft()
            current = path[-1]
            if len(path) - 1 >= max_hops:
                continue
            for neighbor in sorted(self.graph.successors(current)):
                neighbor = int(neighbor)
                if neighbor in path:
                    continue
                next_path = path + [neighbor]
                if neighbor == target:
                    found.append(next_path)
                    if len(found) >= limit:
                        break
                else:
                    queue.append(next_path)
        return found

    def paths(self, src_gid: str, dst_gid: str, max_hops: int = 4) -> Dict[str, Any]:
        if max_hops < 1 or max_hops > 4:
            return {"error": "max_hops must be between 1 and 4", "referenced_gids": []}
        source = self._parse_gid(src_gid)
        target = self._parse_gid(dst_gid)
        unknown = [gid for gid, parsed in ((src_gid, source), (dst_gid, target)) if parsed is None]
        if unknown:
            return {"error": "One or more gids are unknown", "unknown_gids": unknown, "referenced_gids": []}
        assert source is not None and target is not None

        observed_paths = []
        referenced: Set[str] = {src_gid, dst_gid}
        for path in self._bounded_paths(source, target, max_hops):
            edges = []
            for edge_source, edge_target in zip(path, path[1:]):
                edge = self.graph.edges[edge_source, edge_target]
                edges.append(
                    {
                        "source_gid": _string_gid(edge_source),
                        "target_gid": _string_gid(edge_target),
                        "sum_kzt": float(edge["sum_kzt"]),
                        "transaction_count": int(edge["n_tx"]),
                    }
                )
            path_gids = [_string_gid(gid) for gid in path]
            referenced.update(path_gids)
            observed_paths.append(
                {
                    "gids": path_gids,
                    "hops": len(path) - 1,
                    "edges": edges,
                }
            )

        warnings = []
        for gid in sorted(referenced):
            node = self.repository.node(gid)
            if node is not None and node.observability.warning:
                warnings.append({"gid": gid, "warning": node.observability.warning})
        return {
            "src_gid": src_gid,
            "dst_gid": dst_gid,
            "max_hops": max_hops,
            "paths": observed_paths,
            "path_count": len(observed_paths),
            "observability_warnings": warnings,
            "note": "Paths contain only observed directed edges; absence is not proof that no external path exists.",
            "referenced_gids": sorted(referenced),
        }

    def filter_nodes(
        self,
        role: Optional[str],
        cluster_id: Optional[int],
        min_priority: Optional[float],
        min_observed_kzt: Optional[float],
        limit: int,
    ) -> Dict[str, Any]:
        if role is not None and role not in ALLOWED_ROLES:
            return {"error": f"Unsupported role: {role}", "referenced_gids": []}
        if cluster_id is not None and cluster_id not in self.repository.clusters_by_id.index:
            return {"error": f"Unknown MoneyGraph cluster: {cluster_id}", "referenced_gids": []}
        if min_priority is not None and not 0 <= min_priority <= 1:
            return {"error": "min_priority must be between 0 and 1", "referenced_gids": []}
        if min_observed_kzt is not None and min_observed_kzt < 0:
            return {"error": "min_observed_kzt must be non-negative", "referenced_gids": []}
        if limit < 1 or limit > MAX_RESULT_NODES:
            return {"error": f"limit must be between 1 and {MAX_RESULT_NODES}", "referenced_gids": []}

        matches = self.repository.nodes
        if role is not None:
            matches = matches[matches["role"] == role]
        if cluster_id is not None:
            matches = matches[matches["cluster_id"] == cluster_id]
        if min_priority is not None:
            matches = matches[matches["priority_score"] >= min_priority]
        if min_observed_kzt is not None:
            matches = matches[matches["total_kzt"] >= min_observed_kzt]
        matches = matches.sort_values(
            ["priority_score", "total_kzt", "gid"],
            ascending=[False, False, True],
            kind="mergesort",
        )
        total_matches = int(len(matches))
        matches = matches.head(limit)
        nodes = []
        for row in matches.itertuples(index=False):
            nodes.append(
                {
                    "gid": _string_gid(row.gid),
                    "role": str(row.role),
                    "role_score": float(row.role_score),
                    "priority_score": float(row.priority_score),
                    "cluster_id": int(row.cluster_id),
                    "total_observed_kzt": float(row.total_kzt),
                    "depth": int(row.depth),
                    "is_seed": bool(row.is_seed),
                    "evidence": str(row.evidence),
                    "observability_warning": self.repository._observability(row._asdict()).warning,
                }
            )
        referenced = [node["gid"] for node in nodes]
        return {
            "filters": {
                "role": role,
                "cluster_id": cluster_id,
                "min_priority": min_priority,
                "min_observed_kzt": min_observed_kzt,
            },
            "total_matches": total_matches,
            "returned_count": len(nodes),
            "nodes": nodes,
            "referenced_gids": referenced,
        }

    def cluster_summary(self, cluster_id: int) -> Dict[str, Any]:
        cluster = self.repository.cluster(cluster_id)
        if cluster is None:
            return {"error": f"Unknown MoneyGraph cluster: {cluster_id}", "referenced_gids": []}
        payload = cluster.model_dump()
        referenced = set(payload["top_gids"])
        referenced.update(node["gid"] for node in payload["important_nodes"])
        return {
            "cluster": payload,
            "referenced_gids": sorted(referenced),
        }

    @staticmethod
    def _component_metrics(graph: nx.DiGraph) -> Dict[str, int]:
        components = list(nx.weakly_connected_components(graph))
        return {
            "weak_component_count": len(components),
            "largest_weak_component_nodes": max((len(component) for component in components), default=0),
        }

    @staticmethod
    def _seed_reachable(graph: nx.DiGraph, seeds: Set[int]) -> Set[int]:
        reachable: Set[int] = set()
        for seed in sorted(seeds & set(graph.nodes)):
            reachable.update(int(gid) for gid in nx.descendants(graph, seed))
        return reachable - seeds

    def what_if_remove(self, gids: List[str]) -> Dict[str, Any]:
        unique_gids = list(dict.fromkeys(gids))
        if not unique_gids:
            return {"error": "what_if_remove requires at least one gid", "referenced_gids": []}
        if len(unique_gids) > MAX_WHAT_IF_GIDS:
            return {"error": f"what_if_remove accepts at most {MAX_WHAT_IF_GIDS} gids", "referenced_gids": []}
        unknown = self._unknown_gids(unique_gids)
        if unknown:
            return {"error": "One or more gids are unknown", "unknown_gids": unknown, "referenced_gids": []}

        removed = {int(gid) for gid in unique_gids}
        remaining_graph = self.graph.copy()
        remaining_graph.remove_nodes_from(removed)
        seeds = set(
            int(gid)
            for gid in self.repository.data.nodes.loc[
                self.repository.data.nodes["is_seed"], "gid"
            ]
        )
        baseline_reachable = self._seed_reachable(self.graph, seeds)
        after_reachable = self._seed_reachable(remaining_graph, seeds - removed)
        lost_reachable = sorted((baseline_reachable - removed) - after_reachable)
        incident_edges = self.repository.data.edges[
            self.repository.data.edges["src"].isin(removed)
            | self.repository.data.edges["dst"].isin(removed)
        ]
        before = self._component_metrics(self.graph)
        after = self._component_metrics(remaining_graph)
        referenced = set(unique_gids)
        referenced.update(_string_gid(gid) for gid in lost_reachable[:20])
        return {
            "removed_gids": unique_gids,
            "removed_node_count": len(removed),
            "before": {
                **before,
                "seed_reachable_non_seed_nodes": len(baseline_reachable),
            },
            "after": {
                **after,
                "seed_reachable_non_seed_nodes": len(after_reachable),
            },
            "impact": {
                "weak_component_count_change": after["weak_component_count"] - before["weak_component_count"],
                "largest_weak_component_change": after["largest_weak_component_nodes"] - before["largest_weak_component_nodes"],
                "remaining_nodes_losing_seed_reachability": len(lost_reachable),
                "sample_lost_reachability_gids": [_string_gid(gid) for gid in lost_reachable[:20]],
                "removed_incident_observed_kzt": float(incident_edges["sum_kzt"].sum()),
            },
            "note": (
                "This is a structural simulation of the observed graph only. It does not predict behavior "
                "outside the dataset or beyond the depth-4 boundary."
            ),
            "referenced_gids": sorted(referenced),
        }

    def execute(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        handlers = {
            "node_card": self.node_card,
            "common_receivers": self.common_receivers,
            "paths": self.paths,
            "filter_nodes": self.filter_nodes,
            "cluster_summary": self.cluster_summary,
            "what_if_remove": self.what_if_remove,
        }
        handler = handlers.get(name)
        if handler is None:
            return {"error": f"Unsupported tool: {name}", "referenced_gids": []}
        try:
            return handler(**arguments)
        except (TypeError, ValueError) as exc:
            return {"error": f"Invalid tool arguments: {exc}", "referenced_gids": []}
