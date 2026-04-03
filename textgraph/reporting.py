import os
from typing import Dict, List, Tuple

from .analysis import build_dependency_edges
from .models import EvolutionFrame, SyntaxComparison


def save_text_report(content: str, filename: str, folder: str):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, filename), "w", encoding="utf-8") as f:
        f.write(content)


def save_alignment_report(alignments: List[Tuple], folder: str):
    lines = ["=" * 70, "ТАБЛИЦА ВЫРАВНИВАНИЯ ТОКЕНОВ", "=" * 70]
    lines.append(f"{'Original':<20} -> {'Edited':<20} {'Type':<12} {'Similarity'}")
    lines.append("-" * 70)
    for a in alignments:
        orig = a[1] if a[0] is not None else "-"
        edit = a[3] if a[2] is not None else "-"
        if a[0] is not None and a[2] is not None:
            type_str = "СОХРАНЕНО" if a[4] >= 0.95 else "ЗАМЕНЕНО"
        elif a[0] is not None:
            type_str = "УДАЛЕНО"
        else:
            type_str = "ДОБАВЛЕНО"
        sim_str = f"{a[4]:.2f}" if a[4] > 0 else "-"
        lines.append(f"{orig:<20} -> {edit:<20} {type_str:<12} {sim_str}")
    lines.append("=" * 70)
    save_text_report("\n".join(lines), "1_alignment.txt", folder)


def save_syntax_report(comparisons: List[SyntaxComparison], folder: str):
    lines = ["=" * 70, "СИНТАКСИЧЕСКИЙ АНАЛИЗ", "=" * 70]
    lines.append(f"{'Токен':<15} {'Исходная роль':<20} {'Новая роль':<20} {'Статус'}")
    lines.append("-" * 70)
    for c in comparisons:
        status = "СОХРАНЕНА" if c.is_preserved else "ИЗМЕНЕНА"
        lines.append(f"{c.token:<15} {c.original_role:<20} {c.edited_role or '-':<20} {status}")
    preserved = sum(1 for c in comparisons if c.is_preserved)
    total = len(comparisons)
    if total > 0:
        lines.append("-" * 70)
        lines.append(f"Сохранено: {preserved}/{total} ({preserved / total * 100:.1f}%)")
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
    lines = ["=" * 70, "СЕМАНТИЧЕСКИЙ АНАЛИЗ (AMR-граф)", "=" * 70]
    lines.append("")
    lines.append(f"Исходный: {semantic_result['total_original']} триплетов")
    lines.append(f"Редакция: {semantic_result['total_edited']} триплетов")
    lines.append(f"Общих: {len(semantic_result['common'])}")
    lines.append(f"Сохранение: {semantic_result['preservation_rate']:.1f}%")
    if semantic_result["common"]:
        lines.append("")
        lines.append("Инварианты:")
        for triple in sorted(semantic_result["common"]):
            lines.append(f" - {triple[0]} {triple[1]} -> {triple[2]}")
    if semantic_result["only_original"]:
        lines.append("")
        lines.append("Удалено:")
        for triple in sorted(semantic_result["only_original"]):
            lines.append(f" - {triple[0]} {triple[1]} -> {triple[2]}")
    if semantic_result["only_edited"]:
        lines.append("")
        lines.append("Добавлено:")
        for triple in sorted(semantic_result["only_edited"]):
            lines.append(f" - {triple[0]} {triple[1]} -> {triple[2]}")
    lines.append("=" * 70)
    save_text_report("\n".join(lines), "3_semantic_analysis.txt", folder)


def save_statistics_report(stats: Dict[str, int], original_len: int, edited_len: int, folder: str):
    lines = ["=" * 70, "СТАТИСТИКА ИЗМЕНЕНИЙ", "=" * 70]
    lines.append("")
    lines.append(f"Исходный: {original_len} слов")
    lines.append(f"Редакция: {edited_len} слов")
    if original_len > 0:
        lines.append(f"Сжатие: {(1 - edited_len / original_len) * 100:.1f}%")
    lines.append("")
    lines.append("Типы изменений:")
    lines.append(f"СОХРАНЕНО: {stats['preserved']}")
    lines.append(f"ЗАМЕНЕНО: {stats['replaced']}")
    lines.append(f"УДАЛЕНО: {stats['removed']}")
    lines.append(f"ДОБАВЛЕНО: {stats['inserted']}")
    lines.append("=" * 70)
    save_text_report("\n".join(lines), "4_statistics.txt", folder)


def save_evolution_report(frames: List[EvolutionFrame], folder: str):
    lines = ["=" * 70, "ОТЧЕТ О ДИНАМИЧЕСКОЙ ЭВОЛЮЦИИ", "=" * 70]
    for frame in frames:
        lines.append("")
        lines.append(f"Кадр {frame.frame_number}: {frame.timestamp}")
        lines.append(f"Описание: {frame.description}")
        lines.append(f"Статистика: {frame.statistics}")
        lines.append(f"Узлов: {len(frame.nodes)}, Ребер: {len(frame.edges)}")
    lines.append("=" * 70)
    save_text_report("\n".join(lines), "5_evolution_report.txt", folder)


def save_full_texts(original_text: str, edited_text: str, folder: str):
    lines = ["=" * 70, "ИСХОДНЫЕ ТЕКСТЫ", "=" * 70]
    lines.append("")
    lines.append("ИСХОДНЫЙ ТЕКСТ (T1):")
    lines.append(original_text)
    lines.append("")
    lines.append("ОТРЕДАКТИРОВАННЫЙ ТЕКСТ (T2):")
    lines.append(edited_text)
    lines.append("")
    lines.append("=" * 70)
    save_text_report("\n".join(lines), "0_original_texts.txt", folder)
