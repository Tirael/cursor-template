from __future__ import annotations

import base64
import json
import math
import os
import random
import sys
import urllib.parse
import uuid
import zlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class NodeSpec:
    id: str
    label: str
    kind: str
    width: int
    height: int


@dataclass(frozen=True)
class EdgeSpec:
    source: str
    target: str
    label: str


@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float

    def inflate(self, m: float) -> "Rect":
        return Rect(self.x - m, self.y - m, self.w + 2 * m, self.h + 2 * m)

    def contains(self, px: float, py: float) -> bool:
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h


def _load_spec(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(raw)
    if path.suffix.lower() in {".yml", ".yaml"}:
        try:
            import yaml  # type: ignore
        except Exception as e:  # noqa: BLE001
            raise RuntimeError("YAML input requires PyYAML (pip install pyyaml)") from e
        return yaml.safe_load(raw)
    raise RuntimeError("Unsupported spec format. Use .json (or .yml/.yaml with PyYAML).")


def _parse_spec(data: dict[str, Any]) -> tuple[str, list[NodeSpec], list[EdgeSpec]]:
    diagram_name = str(data.get("diagram", {}).get("name", "C4"))
    nodes_raw = data.get("nodes", [])
    edges_raw = data.get("edges", [])
    if not isinstance(nodes_raw, list) or not isinstance(edges_raw, list):
        raise RuntimeError("Spec must contain 'nodes' and 'edges' arrays.")

    nodes: list[NodeSpec] = []
    seen: set[str] = set()
    for n in nodes_raw:
        if not isinstance(n, dict):
            raise RuntimeError("Each node must be an object.")
        node_id = str(n.get("id", "")).strip()
        if not node_id:
            raise RuntimeError("Node.id is required.")
        if node_id in seen:
            raise RuntimeError(f"Duplicate node id: {node_id}")
        seen.add(node_id)
        label = str(n.get("label", node_id))
        kind = str(n.get("kind", "Container"))
        width = int(n.get("width", 180))
        height = int(n.get("height", 80))
        nodes.append(NodeSpec(id=node_id, label=label, kind=kind, width=width, height=height))

    node_ids = {n.id for n in nodes}
    edges: list[EdgeSpec] = []
    for e in edges_raw:
        if not isinstance(e, dict):
            raise RuntimeError("Each edge must be an object.")
        source = str(e.get("source", "")).strip()
        target = str(e.get("target", "")).strip()
        if not source or not target:
            raise RuntimeError("Edge.source and Edge.target are required.")
        if source not in node_ids or target not in node_ids:
            raise RuntimeError(f"Edge references unknown node: {source}->{target}")
        label = str(e.get("label", "")).strip()
        edges.append(EdgeSpec(source=source, target=target, label=label))

    return diagram_name, nodes, edges


def _build_graph(nodes: list[NodeSpec], edges: list[EdgeSpec]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    out: dict[str, list[str]] = {n.id: [] for n in nodes}
    inc: dict[str, list[str]] = {n.id: [] for n in nodes}
    for e in edges:
        out[e.source].append(e.target)
        inc[e.target].append(e.source)
    return out, inc


def _assign_layers(nodes: list[NodeSpec], edges: list[EdgeSpec]) -> dict[str, int]:
    out, inc = _build_graph(nodes, edges)
    indeg = {n.id: len(inc[n.id]) for n in nodes}
    roots = [n.id for n in nodes if indeg[n.id] == 0]
    if not roots:
        roots = sorted((n.id for n in nodes), key=lambda nid: (-len(out[nid]) - len(inc[nid]), nid))[:1]

    layer = {n.id: (0 if n.id in roots else 0) for n in nodes}
    for _ in range(max(1, len(nodes))):
        updated = False
        for e in edges:
            v = layer[e.source] + 1
            if v > layer[e.target]:
                layer[e.target] = v
                updated = True
        if not updated:
            break

    min_layer = min(layer.values()) if layer else 0
    if min_layer < 0:
        layer = {k: v - min_layer for k, v in layer.items()}
    return layer


def _reduce_crossings(
    layers: list[list[str]],
    inc: dict[str, list[str]],
    out: dict[str, list[str]],
    max_iters: int,
) -> list[list[str]]:
    order: dict[str, int] = {}
    for li, layer_nodes in enumerate(layers):
        for i, nid in enumerate(layer_nodes):
            order[nid] = i

    def barycenter(nid: str, neigh: Iterable[str]) -> float:
        xs = [order[x] for x in neigh if x in order]
        return sum(xs) / len(xs) if xs else float(order[nid])

    for _ in range(max_iters):
        changed = False
        for li in range(1, len(layers)):
            prev = layers[li - 1]
            if not prev:
                continue
            prev_set = set(prev)
            def key(nid: str) -> tuple[float, str]:
                neigh = [p for p in inc[nid] if p in prev_set]
                return (barycenter(nid, neigh), nid)

            new_layer = sorted(layers[li], key=key)
            if new_layer != layers[li]:
                layers[li] = new_layer
                changed = True
                for i, nid in enumerate(new_layer):
                    order[nid] = i

        for li in range(len(layers) - 2, -1, -1):
            nxt = layers[li + 1]
            if not nxt:
                continue
            nxt_set = set(nxt)
            def key(nid: str) -> tuple[float, str]:
                neigh = [t for t in out[nid] if t in nxt_set]
                return (barycenter(nid, neigh), nid)

            new_layer = sorted(layers[li], key=key)
            if new_layer != layers[li]:
                layers[li] = new_layer
                changed = True
                for i, nid in enumerate(new_layer):
                    order[nid] = i

        if not changed:
            break

    return layers


def _layout_layered(
    nodes: list[NodeSpec],
    edges: list[EdgeSpec],
    h_gap: int,
    v_gap: int,
    crossing_iters: int,
) -> dict[str, Rect]:
    layer_by = _assign_layers(nodes, edges)
    out, inc = _build_graph(nodes, edges)

    max_layer = max(layer_by.values()) if layer_by else 0
    layers: list[list[str]] = [[] for _ in range(max_layer + 1)]
    for n in sorted(nodes, key=lambda x: x.id):
        layers[layer_by[n.id]].append(n.id)

    layers = _reduce_crossings(layers, inc, out, max_iters=crossing_iters)

    node_by_id = {n.id: n for n in nodes}
    col_width = max((n.width for n in nodes), default=180)
    x0 = 0

    placed: dict[str, Rect] = {}
    for li, layer_nodes in enumerate(layers):
        x = x0 + li * (col_width + h_gap)
        y = 0
        for nid in layer_nodes:
            spec = node_by_id[nid]
            r = Rect(x, y, spec.width, spec.height)
            placed[nid] = r
            y += spec.height + v_gap

    min_x = min((r.x for r in placed.values()), default=0.0)
    min_y = min((r.y for r in placed.values()), default=0.0)
    if min_x < 0 or min_y < 0:
        dx = -min_x if min_x < 0 else 0.0
        dy = -min_y if min_y < 0 else 0.0
        for nid, r in placed.items():
            placed[nid] = Rect(r.x + dx, r.y + dy, r.w, r.h)

    return placed


def _kind_style(kind: str) -> str:
    k = kind.strip().lower()
    base = "whiteSpace=wrap;html=1;rounded=1;"
    if k == "person":
        return base + "shape=ellipse;fillColor=#dae8fc;strokeColor=#6c8ebf;"
    if k in {"softwaresystem", "system"}:
        return base + "fillColor=#d5e8d4;strokeColor=#82b366;"
    if k == "container":
        return base + "fillColor=#ffe6cc;strokeColor=#d79b00;"
    if k == "component":
        return base + "fillColor=#f8cecc;strokeColor=#b85450;"
    return base + "fillColor=#ffffff;strokeColor=#000000;"


def _edge_style() -> str:
    return (
        "edgeStyle=orthogonalEdgeStyle;"
        "rounded=0;"
        "orthogonalLoop=1;"
        "jettySize=auto;"
        "html=1;"
        "endArrow=block;"
        "endFill=1;"
        "strokeColor=#000000;"
    )


def _point_on_border(src: Rect, dst: Rect) -> tuple[float, float]:
    sx = src.x + src.w / 2
    sy = src.y + src.h / 2
    dx = dst.x + dst.w / 2
    dy = dst.y + dst.h / 2
    vx = dx - sx
    vy = dy - sy
    if abs(vx) >= abs(vy):
        if vx >= 0:
            return (src.x + src.w, sy)
        return (src.x, sy)
    if vy >= 0:
        return (sx, src.y + src.h)
    return (sx, src.y)


@dataclass(frozen=True)
class Grid:
    cell: int
    ox: float
    oy: float
    w: int
    h: int
    blocked: set[tuple[int, int]]

    def to_cell(self, x: float, y: float) -> tuple[int, int]:
        cx = int(round((x - self.ox) / self.cell))
        cy = int(round((y - self.oy) / self.cell))
        return (max(0, min(self.w - 1, cx)), max(0, min(self.h - 1, cy)))

    def to_point(self, cx: int, cy: int) -> tuple[float, float]:
        return (self.ox + cx * self.cell, self.oy + cy * self.cell)


def _build_grid(
    rects: dict[str, Rect],
    cell: int,
    pad: int,
    node_obstacle_pad: int,
    extra_margin: int,
    reserved: set[tuple[int, int]],
) -> Grid:
    min_x = min((r.x for r in rects.values()), default=0.0) - extra_margin
    min_y = min((r.y for r in rects.values()), default=0.0) - extra_margin
    max_x = max((r.x + r.w for r in rects.values()), default=800.0) + extra_margin
    max_y = max((r.y + r.h for r in rects.values()), default=600.0) + extra_margin

    ox = math.floor((min_x - pad) / cell) * cell
    oy = math.floor((min_y - pad) / cell) * cell
    w = int(math.ceil((max_x - ox + pad) / cell)) + 1
    h = int(math.ceil((max_y - oy + pad) / cell)) + 1

    blocked: set[tuple[int, int]] = set(reserved)
    inflated = [r.inflate(node_obstacle_pad) for r in rects.values()]
    for cx in range(w):
        px = ox + cx * cell
        for cy in range(h):
            if (cx, cy) in reserved:
                continue
            py = oy + cy * cell
            for rr in inflated:
                if rr.contains(px, py):
                    blocked.add((cx, cy))
                    break

    return Grid(cell=cell, ox=ox, oy=oy, w=w, h=h, blocked=blocked)


def _astar_route(
    grid: Grid,
    start: tuple[int, int],
    goal: tuple[int, int],
    bend_penalty: int,
) -> list[tuple[int, int]]:
    from heapq import heappop, heappush

    def h(a: tuple[int, int], b: tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    start_state = (start[0], start[1], -1)
    goal_xy = (goal[0], goal[1])

    open_heap: list[tuple[int, int, tuple[int, int, int]]] = []
    g_score: dict[tuple[int, int, int], int] = {start_state: 0}
    came: dict[tuple[int, int, int], tuple[int, int, int]] = {}

    heappush(open_heap, (h(start, goal), 0, start_state))

    while open_heap:
        _, cur_g, cur = heappop(open_heap)
        if cur_g != g_score.get(cur, 0):
            continue

        cx, cy, cdir = cur
        if (cx, cy) == goal_xy:
            path: list[tuple[int, int]] = []
            t = cur
            while True:
                path.append((t[0], t[1]))
                if t == start_state:
                    break
                t = came[t]
            path.reverse()
            return path

        for ndir, (dx, dy) in enumerate(dirs):
            nx, ny = cx + dx, cy + dy
            if nx < 0 or ny < 0 or nx >= grid.w or ny >= grid.h:
                continue
            if (nx, ny) in grid.blocked and (nx, ny) != goal_xy:
                continue
            step = 1
            if cdir != -1 and ndir != cdir:
                step += bend_penalty
            nxt = (nx, ny, ndir)
            ng = cur_g + step
            if ng < g_score.get(nxt, 1_000_000_000):
                g_score[nxt] = ng
                came[nxt] = cur
                heappush(open_heap, (ng + h((nx, ny), goal), ng, nxt))

    raise RuntimeError("No route found (grid too tight).")


def _compress_points(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if len(points) <= 2:
        return points
    out = [points[0]]
    for i in range(1, len(points) - 1):
        ax, ay = out[-1]
        bx, by = points[i]
        cx, cy = points[i + 1]
        if (ax == bx == cx) or (ay == by == cy):
            continue
        out.append((bx, by))
    out.append(points[-1])
    return out


def _cells_on_path(path: list[tuple[int, int]]) -> set[tuple[int, int]]:
    return set(path)


def _route_edges(
    rects: dict[str, Rect],
    edges: list[EdgeSpec],
    cell: int,
    pad: int,
    node_obstacle_pad: int,
    bend_penalty: int,
    reserve_radius: int,
    expand_tries: int,
) -> dict[tuple[str, str, str], list[tuple[float, float]]]:
    edge_points: dict[tuple[str, str, str], list[tuple[float, float]]] = {}

    def edge_key(e: EdgeSpec) -> tuple[int, int, str, str]:
        a = rects[e.source].x
        b = rects[e.target].x
        return (-int(abs(b - a)), -len(e.label), e.source, e.target)

    edges_ordered = sorted(edges, key=edge_key)

    for expand in range(expand_tries + 1):
        reserved: set[tuple[int, int]] = set()
        edge_points.clear()
        ok = True
        extra = expand * cell * 6
        for e in edges_ordered:
            src = rects[e.source]
            dst = rects[e.target]
            sx, sy = _point_on_border(src, dst)
            tx, ty = _point_on_border(dst, src)

            grid = _build_grid(
                rects=rects,
                cell=cell,
                pad=pad,
                node_obstacle_pad=node_obstacle_pad,
                extra_margin=extra,
                reserved=reserved,
            )

            start = grid.to_cell(sx, sy)
            goal = grid.to_cell(tx, ty)
            for c in [start, goal]:
                if c in grid.blocked:
                    grid.blocked.discard(c)

            try:
                path_cells = _astar_route(grid, start, goal, bend_penalty=bend_penalty)
            except Exception:  # noqa: BLE001
                ok = False
                break

            pts = [grid.to_point(cx, cy) for (cx, cy) in path_cells]
            if pts:
                pts[0] = (sx, sy)
                pts[-1] = (tx, ty)
            pts = _compress_points(pts)

            edge_points[(e.source, e.target, e.label)] = pts

            used = _cells_on_path(path_cells)
            expanded_used: set[tuple[int, int]] = set()
            for cx, cy in used:
                for dx in range(-reserve_radius, reserve_radius + 1):
                    for dy in range(-reserve_radius, reserve_radius + 1):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < grid.w and 0 <= ny < grid.h:
                            expanded_used.add((nx, ny))

            s0x, s0y = start
            t0x, t0y = goal
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    expanded_used.discard((s0x + dx, s0y + dy))
                    expanded_used.discard((t0x + dx, t0y + dy))

            reserved |= expanded_used

        if ok:
            return edge_points

    raise RuntimeError("Failed to route edges without intersections. Increase spacing or simplify graph.")


def _mx_graph_model(
    diagram_name: str,
    nodes: list[NodeSpec],
    edges: list[EdgeSpec],
    rects: dict[str, Rect],
    edge_points: dict[tuple[str, str, str], list[tuple[float, float]]],
) -> ET.Element:
    m = ET.Element("mxGraphModel", attrib={"dx": "0", "dy": "0", "grid": "1", "gridSize": "10", "guides": "1"})
    root = ET.SubElement(m, "root")
    ET.SubElement(root, "mxCell", attrib={"id": "0"})
    ET.SubElement(root, "mxCell", attrib={"id": "1", "parent": "0"})

    id_map: dict[str, str] = {}
    next_id = 2
    for n in nodes:
        cid = str(next_id)
        next_id += 1
        id_map[n.id] = cid
        cell = ET.SubElement(
            root,
            "mxCell",
            attrib={
                "id": cid,
                "value": n.label,
                "style": _kind_style(n.kind),
                "vertex": "1",
                "parent": "1",
            },
        )
        r = rects[n.id]
        ET.SubElement(
            cell,
            "mxGeometry",
            attrib={"x": str(int(round(r.x))), "y": str(int(round(r.y))), "width": str(int(r.w)), "height": str(int(r.h)), "as": "geometry"},
        )

    for e in edges:
        cid = str(next_id)
        next_id += 1
        cell = ET.SubElement(
            root,
            "mxCell",
            attrib={
                "id": cid,
                "value": e.label,
                "style": _edge_style(),
                "edge": "1",
                "parent": "1",
                "source": id_map[e.source],
                "target": id_map[e.target],
            },
        )
        geom = ET.SubElement(cell, "mxGeometry", attrib={"relative": "1", "as": "geometry"})
        pts = edge_points.get((e.source, e.target, e.label), [])
        if len(pts) >= 3:
            arr = ET.SubElement(geom, "Array", attrib={"as": "points"})
            for (x, y) in pts[1:-1]:
                ET.SubElement(arr, "mxPoint", attrib={"x": str(int(round(x))), "y": str(int(round(y)))})

    return m


def _xml_to_bytes(elem: ET.Element) -> bytes:
    return ET.tostring(elem, encoding="utf-8", method="xml")


def _drawio_compress(xml_bytes: bytes) -> str:
    compressor = zlib.compressobj(level=9, wbits=-15)
    raw = compressor.compress(xml_bytes) + compressor.flush()
    b64 = base64.b64encode(raw).decode("ascii")
    return urllib.parse.quote(b64, safe="-_.!~*'()")


def _mxfile(diagram_name: str, diagram_xml: bytes) -> bytes:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    mx = ET.Element(
        "mxfile",
        attrib={
            "host": "app.diagrams.net",
            "modified": now,
            "agent": "c4_drawio_autolayout.py",
            "version": "22.1.2",
            "type": "device",
        },
    )
    diag = ET.SubElement(mx, "diagram", attrib={"id": uuid.uuid4().hex, "name": diagram_name})
    diag.text = _drawio_compress(diagram_xml)
    return _xml_to_bytes(mx)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Generate draw.io C4-like diagram with auto-layout and routing")
    parser.add_argument("--input", required=True, help="Path to spec (.json, or .yml/.yaml with PyYAML)")
    parser.add_argument("--output", required=True, help="Output .drawio path")
    parser.add_argument("--h-gap", type=int, default=220, help="Horizontal gap between layers/columns")
    parser.add_argument("--v-gap", type=int, default=80, help="Vertical gap within a layer/column")
    parser.add_argument("--crossing-iters", type=int, default=8, help="Crossing-reduction sweeps for layered layout")
    parser.add_argument("--cell", type=int, default=20, help="Routing grid cell size")
    parser.add_argument("--pad", type=int, default=80, help="Extra padding for routing grid bounds")
    parser.add_argument("--node-pad", type=int, default=26, help="Inflation of node rectangles for routing obstacles")
    parser.add_argument("--bend-penalty", type=int, default=8, help="Penalty per bend in routing")
    parser.add_argument("--reserve-radius", type=int, default=1, help="How many grid cells to reserve around routed wires")
    parser.add_argument("--expand-tries", type=int, default=6, help="Routing retries with expanding margins")
    parser.add_argument("--seed", type=int, default=1, help="Random seed (reserved for future heuristics)")
    args = parser.parse_args()

    random.seed(args.seed)

    in_path = Path(args.input)
    out_path = Path(args.output)
    if not in_path.is_file():
        raise RuntimeError(f"Input not found: {in_path}")

    data = _load_spec(in_path)
    diagram_name, nodes, edges = _parse_spec(data)
    rects = _layout_layered(nodes, edges, h_gap=args.h_gap, v_gap=args.v_gap, crossing_iters=args.crossing_iters)
    edge_points = _route_edges(
        rects=rects,
        edges=edges,
        cell=args.cell,
        pad=args.pad,
        node_obstacle_pad=args.node_pad,
        bend_penalty=args.bend_penalty,
        reserve_radius=args.reserve_radius,
        expand_tries=args.expand_tries,
    )
    model = _mx_graph_model(diagram_name, nodes, edges, rects, edge_points)
    mx_bytes = _mxfile(diagram_name, _xml_to_bytes(model))

    os.makedirs(out_path.parent, exist_ok=True)
    out_path.write_bytes(mx_bytes)
    sys.stdout.write(f"Wrote {out_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
