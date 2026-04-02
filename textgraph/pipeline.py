import os
from datetime import datetime

from .analysis import compare_semantic_graphs, compare_syntax_trees, compute_change_stats
from .evolution import build_evolution_sequence
from .language import detect_text_language
from .models import AnalysisArtifacts
from .parsing import align_tokens, simple_tokenize
from .reporting import (
    save_alignment_report,
    save_dependency_report,
    save_evolution_report,
    save_full_texts,
    save_semantic_report,
    save_statistics_report,
    save_syntax_report,
)
from .visualization import VISUALIZATION_AVAILABLE, save_all_frames, save_syntax_graph


def analyze_dynamic_evolution(original_text: str, edited_text: str, title: str = "") -> AnalysisArtifacts:
    if title:
        print("\n" + "=" * 70)
        print(title)
        print("=" * 70)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    results_root = "results"
    os.makedirs(results_root, exist_ok=True)
    folder = os.path.join(results_root, f"results_{timestamp}")
    print(f"[INFO] Результаты сохраняются в: {folder}/")

    print("\n[1/7] Токенизация...")
    original_tokens = simple_tokenize(original_text)
    edited_tokens = simple_tokenize(edited_text)
    detected_lang = detect_text_language(f"{original_text} {edited_text}")
    print(f"   Исходный: {len(original_tokens)} слов")
    print(f"   Редакция: {len(edited_tokens)} слов")
    print(f"   Язык: {detected_lang}")

    print("\n[2/7] Выравнивание...")
    alignments = align_tokens(original_tokens, edited_tokens, language=detected_lang)
    save_alignment_report(alignments, folder)

    print("\n[3/7] Синтаксический анализ...")
    syntax_comparisons = compare_syntax_trees(original_tokens, edited_tokens, language=detected_lang)
    save_syntax_report(syntax_comparisons, folder)
    save_dependency_report(original_tokens, "2a_dependencies_original.txt", folder)
    save_dependency_report(edited_tokens, "2b_dependencies_edited.txt", folder)

    print("\n[4/7] Семантический анализ...")
    semantic_result = compare_semantic_graphs(original_tokens, edited_tokens, language=detected_lang)
    save_semantic_report(semantic_result, folder)

    print("\n[5/7] Статистика...")
    stats = compute_change_stats(alignments)
    save_statistics_report(stats, len(original_tokens), len(edited_tokens), folder)

    print("\n[6/7] Построение эволюции...")
    frames = build_evolution_sequence(original_tokens, edited_tokens)
    save_evolution_report(frames, folder)
    save_full_texts(original_text, edited_text, folder)

    print("\n[7/7] Визуализация...")
    if VISUALIZATION_AVAILABLE:
        save_all_frames(frames, folder)
        save_syntax_graph(original_tokens, "Синтаксическое дерево (исходный текст)", "syntax_original.png", folder)
        save_syntax_graph(edited_tokens, "Синтаксическое дерево (отредактированный текст)", "syntax_edited.png", folder)
    else:
        print("[WARN] Визуализация недоступна (pip install networkx matplotlib)")

    print(f"[ OK ] Анализ завершен. Результаты: {folder}/")
    return AnalysisArtifacts(folder=folder, original_tokens=original_tokens, edited_tokens=edited_tokens, frames=frames)
