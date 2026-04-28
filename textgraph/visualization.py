import os
from typing import List

from .analysis import build_dependency_edges, get_syntax_role
from .models import EvolutionFrame

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import networkx as nx

    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


def extract_label_from_node(node: str) -> str:
    return node.split(":", 1)[1] if ":" in node else node


def get_node_color(node: str) -> str:
    if "[УДАЛ:" in node:
        return "#FF6B6B"
    if "[ЗАМ:" in node:
        return "#FFD700"
    if node.startswith("N_"):
        return "#87CEEB"
    if node.startswith("E_"):
        return "#90EE90"
    return "#D3D3D3"


def save_single_frame(frame: EvolutionFrame, folder: str):
    if not VISUALIZATION_AVAILABLE:
        return

    fig, ax = plt.subplots(figsize=(14, 6))
    graph = nx.DiGraph()
    for node in frame.nodes:
        graph.add_node(node, label=extract_label_from_node(node), color=get_node_color(node))
    for src, tgt in frame.edges:
        graph.add_edge(src, tgt)

    # Some edges may introduce implicit nodes. Normalize their attrs.
    for node in graph.nodes:
        if "label" not in graph.nodes[node]:
            graph.nodes[node]["label"] = extract_label_from_node(str(node))
        if "color" not in graph.nodes[node]:
            graph.nodes[node]["color"] = get_node_color(str(node))

    if graph.nodes:
        pos = {node: (i * 0.8, 0) for i, node in enumerate(graph.nodes)}
        nx.draw_networkx_nodes(graph, pos, node_color=[graph.nodes[n]["color"] for n in graph.nodes], node_size=2800, ax=ax)
        nx.draw_networkx_edges(graph, pos, edge_color="gray", arrows=True, arrowsize=20, ax=ax)
        nx.draw_networkx_labels(graph, pos, {n: graph.nodes[n]["label"] for n in graph.nodes}, font_size=10, ax=ax)

    ax.set_title(f"Кадр {frame.frame_number}: {frame.timestamp}\n{frame.description}", fontsize=14, fontweight="bold")
    ax.axis("off")
    stats_text = "\n".join([f"{k}: {v}" for k, v in frame.statistics.items()])
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10, va="top", bbox=dict(boxstyle="round", facecolor="white", alpha=0.9))
    plt.tight_layout()
    filename = f"frame_{frame.frame_number:02d}_{frame.timestamp.replace(' ', '_')}.png"
    plt.savefig(os.path.join(folder, filename), dpi=150, bbox_inches="tight")
    plt.close(fig)


def save_all_frames(frames: List[EvolutionFrame], folder: str):
    if not VISUALIZATION_AVAILABLE:
        return
    frames_folder = os.path.join(folder, "frames")
    os.makedirs(frames_folder, exist_ok=True)
    for frame in frames:
        save_single_frame(frame, frames_folder)


def save_syntax_graph(tokens: List[str], title: str, filename: str, folder: str):
    if not VISUALIZATION_AVAILABLE:
        return

    graph = nx.DiGraph()
    for i, token in enumerate(tokens):
        role = get_syntax_role(token)
        graph.add_node(i, label=f"{token}\n({role})")
    for head, dep, rel in build_dependency_edges(tokens):
        graph.add_edge(head, dep, relation=rel)

    fig, ax = plt.subplots(figsize=(max(12, len(tokens) * 0.95), 7))
    pos = nx.spring_layout(graph, k=1.2, iterations=200, seed=42) if len(graph.nodes) > 1 else {0: (0, 0)}
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_color=["#FF6B6B" if get_syntax_role(tokens[i]) == "ROOT" else "#90EE90" for i in graph.nodes],
        node_size=3000,
        ax=ax,
    )
    nx.draw_networkx_edges(graph, pos, edge_color="gray", arrows=True, arrowsize=18, connectionstyle="arc3,rad=0.08", ax=ax)
    nx.draw_networkx_labels(graph, pos, {i: graph.nodes[i]["label"] for i in graph.nodes}, font_size=10, ax=ax)
    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels={(u, v): d.get("relation", "") for u, v, d in graph.edges(data=True)},
        font_size=8,
        rotate=False,
        ax=ax,
    )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(os.path.join(folder, filename), dpi=150, bbox_inches="tight")
    plt.close(fig)

