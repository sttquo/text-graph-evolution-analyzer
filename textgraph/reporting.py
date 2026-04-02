import os
from typing import Dict, List, Tuple

from .analysis import build_dependency_edges
from .models import EvolutionFrame, SyntaxComparison


def save_text_report(content: str, filename: str, folder: str):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, filename), "w", encoding="utf-8") as f:
        f.write(content)


def save_alignment_report(alignments: List[Tuple], folder: str):
    lines = ["=" * 70, "РўРђР‘Р›РР¦Рђ Р’Р«Р РђР’РќРР’РђРќРРЇ РўРћРљР•РќРћР’", "=" * 70]
    lines.append(f"{'Original':<20} -> {'Edited':<20} {'Type':<12} {'Similarity'}")
    lines.append("-" * 70)
    for a in alignments:
        orig = a[1] if a[0] is not None else "-"
        edit = a[3] if a[2] is not None else "-"
        if a[0] is not None and a[2] is not None:
            type_str = "РЎРћРҐР РђРќР•РќРћ" if a[4] >= 0.95 else "Р—РђРњР•РќР•РќРћ"
        elif a[0] is not None:
            type_str = "РЈР”РђР›Р•РќРћ"
        else:
            type_str = "Р”РћР‘РђР’Р›Р•РќРћ"
        sim_str = f"{a[4]:.2f}" if a[4] > 0 else "-"
        lines.append(f"{orig:<20} -> {edit:<20} {type_str:<12} {sim_str}")
    lines.append("=" * 70)
    save_text_report("\n".join(lines), "1_alignment.txt", folder)


def save_syntax_report(comparisons: List[SyntaxComparison], folder: str):
    lines = ["=" * 70, "РЎРРќРўРђРљРЎРР§Р•РЎРљРР™ РђРќРђР›РР—", "=" * 70]
    lines.append(f"{'РўРѕРєРµРЅ':<15} {'РСЃС…РѕРґРЅР°СЏ СЂРѕР»СЊ':<20} {'РќРѕРІР°СЏ СЂРѕР»СЊ':<20} {'РЎС‚Р°С‚СѓСЃ'}")
    lines.append("-" * 70)
    for c in comparisons:
        status = "РЎРћРҐР РђРќР•РќРђ" if c.is_preserved else "РР—РњР•РќР•РќРђ"
        lines.append(f"{c.token:<15} {c.original_role:<20} {c.edited_role or '-':<20} {status}")
    preserved = sum(1 for c in comparisons if c.is_preserved)
    total = len(comparisons)
    if total > 0:
        lines.append("-" * 70)
        lines.append(f"РЎРѕС…СЂР°РЅРµРЅРѕ: {preserved}/{total} ({preserved / total * 100:.1f}%)")
    lines.append("=" * 70)
    save_text_report("\n".join(lines), "2_syntax_analysis.txt", folder)


def save_dependency_report(tokens: List[str], filename: str, folder: str):
    edges = build_dependency_edges(tokens)
    lines = ["=" * 70, "DEPENDENCY EDGES", "=" * 70]
    lines.append(f"{'Head':<25} {'Dependent':<25} {'Relation'}")
    lines.append("-" * 70)
    if not edges:
        lines.append("No dependency edges.")
    else:
        for head, dep, rel in edges:
            lines.append(f"{head}:{tokens[head]:<22} {dep}:{tokens[dep]:<22} {rel}")
    lines.append("=" * 70)
    save_text_report("\n".join(lines), filename, folder)


def save_semantic_report(semantic_result: Dict, folder: str):
    lines = ["=" * 70, "РЎР•РњРђРќРўРР§Р•РЎРљРР™ РђРќРђР›РР— (AMR-РіСЂР°С„)", "=" * 70]
    lines.append("")
    lines.append(f"РСЃС…РѕРґРЅС‹Р№: {semantic_result['total_original']} С‚СЂРёРїР»РµС‚РѕРІ")
    lines.append(f"Р РµРґР°РєС†РёСЏ: {semantic_result['total_edited']} С‚СЂРёРїР»РµС‚РѕРІ")
    lines.append(f"РћР±С‰РёС…: {len(semantic_result['common'])}")
    lines.append(f"РЎРѕС…СЂР°РЅРµРЅРёРµ: {semantic_result['preservation_rate']:.1f}%")
    if semantic_result["common"]:
        lines.append("")
        lines.append("РРЅРІР°СЂРёР°РЅС‚С‹:")
        for triple in sorted(semantic_result["common"]):
            lines.append(f" - {triple[0]} {triple[1]} -> {triple[2]}")
    if semantic_result["only_original"]:
        lines.append("")
        lines.append("РЈРґР°Р»РµРЅРѕ:")
        for triple in sorted(semantic_result["only_original"]):
            lines.append(f" - {triple[0]} {triple[1]} -> {triple[2]}")
    if semantic_result["only_edited"]:
        lines.append("")
        lines.append("Р”РѕР±Р°РІР»РµРЅРѕ:")
        for triple in sorted(semantic_result["only_edited"]):
            lines.append(f" - {triple[0]} {triple[1]} -> {triple[2]}")
    lines.append("=" * 70)
    save_text_report("\n".join(lines), "3_semantic_analysis.txt", folder)


def save_statistics_report(stats: Dict[str, int], original_len: int, edited_len: int, folder: str):
    lines = ["=" * 70, "РЎРўРђРўРРЎРўРРљРђ РР—РњР•РќР•РќРР™", "=" * 70]
    lines.append("")
    lines.append(f"РСЃС…РѕРґРЅС‹Р№: {original_len} СЃР»РѕРІ")
    lines.append(f"Р РµРґР°РєС†РёСЏ: {edited_len} СЃР»РѕРІ")
    if original_len > 0:
        lines.append(f"РЎР¶Р°С‚РёРµ: {(1 - edited_len / original_len) * 100:.1f}%")
    lines.append("")
    lines.append("РўРёРїС‹ РёР·РјРµРЅРµРЅРёР№:")
    lines.append(f"РЎРћРҐР РђРќР•РќРћ: {stats['preserved']}")
    lines.append(f"Р—РђРњР•РќР•РќРћ: {stats['replaced']}")
    lines.append(f"РЈР”РђР›Р•РќРћ: {stats['removed']}")
    lines.append(f"Р”РћР‘РђР’Р›Р•РќРћ: {stats['inserted']}")
    lines.append("=" * 70)
    save_text_report("\n".join(lines), "4_statistics.txt", folder)


def save_evolution_report(frames: List[EvolutionFrame], folder: str):
    lines = ["=" * 70, "РћРўР§Р•Рў Рћ Р”РРќРђРњРР§Р•РЎРљРћР™ Р­Р’РћР›Р®Р¦РР", "=" * 70]
    for frame in frames:
        lines.append("")
        lines.append(f"РљР°РґСЂ {frame.frame_number}: {frame.timestamp}")
        lines.append(f"РћРїРёСЃР°РЅРёРµ: {frame.description}")
        lines.append(f"РЎС‚Р°С‚РёСЃС‚РёРєР°: {frame.statistics}")
        lines.append(f"РЈР·Р»РѕРІ: {len(frame.nodes)}, Р РµР±РµСЂ: {len(frame.edges)}")
    lines.append("=" * 70)
    save_text_report("\n".join(lines), "5_evolution_report.txt", folder)


def save_full_texts(original_text: str, edited_text: str, folder: str):
    lines = ["=" * 70, "РРЎРҐРћР”РќР«Р• РўР•РљРЎРўР«", "=" * 70]
    lines.append("")
    lines.append("РРЎРҐРћР”РќР«Р™ РўР•РљРЎРў (T1):")
    lines.append(original_text)
    lines.append("")
    lines.append("РћРўР Р•Р”РђРљРўРР РћР’РђРќРќР«Р™ РўР•РљРЎРў (T2):")
    lines.append(edited_text)
    lines.append("")
    lines.append("=" * 70)
    save_text_report("\n".join(lines), "0_original_texts.txt", folder)

