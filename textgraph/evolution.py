from typing import List

from .models import EvolutionFrame
from .parsing import align_tokens


def build_evolution_sequence(original_tokens: List[str], edited_tokens: List[str]) -> List[EvolutionFrame]:
    frames: List[EvolutionFrame] = []
    alignments = align_tokens(original_tokens, edited_tokens)

    replaced = []
    removed = []
    inserted = []
    for a in alignments:
        if a[0] is not None and a[2] is not None and a[4] < 0.95:
            replaced.append((a[0], a[1], a[2], a[3]))
        elif a[0] is not None and a[2] is None:
            removed.append((a[0], a[1]))
        elif a[0] is None and a[2] is not None:
            inserted.append((a[2], a[3]))

    nodes1 = {f"O_{i}:{token}" for i, token in enumerate(original_tokens)}
    edges1 = {(f"O_{i}:{original_tokens[i]}", f"O_{i+1}:{original_tokens[i+1]}") for i in range(len(original_tokens) - 1)}
    frames.append(EvolutionFrame(1, "Начальное состояние", "Исходный текст", nodes1, edges1, {"всего": len(original_tokens)}))

    nodes2 = set()
    for i, token in enumerate(original_tokens):
        is_removed = any(r[0] == i for r in removed)
        label = f"[УДАЛ:{token}]" if is_removed else token
        nodes2.add(f"O_{i}:{label}")
    frames.append(EvolutionFrame(2, "Этап удаления", "Отмечены удаляемые элементы", nodes2, edges1, {"удалено": len(removed)}))

    nodes3 = set()
    for i, token in enumerate(original_tokens):
        is_replaced = any(r[0] == i for r in replaced)
        if is_replaced:
            replacement = next(r[3] for r in replaced if r[0] == i)
            label = f"[ЗАМ:{token}->{replacement}]"
        else:
            is_removed = any(r[0] == i for r in removed)
            label = f"[УДАЛ:{token}]" if is_removed else token
        nodes3.add(f"O_{i}:{label}")
    frames.append(EvolutionFrame(3, "Этап замены", "Отмечены заменяемые элементы", nodes3, edges1, {"заменено": len(replaced)}))

    remaining_indices = [i for i in range(len(original_tokens)) if not any(r[0] == i for r in removed)]
    nodes4 = {f"O_{i}:{original_tokens[i]}" for i in remaining_indices}
    edges4 = set()
    for idx in range(len(remaining_indices) - 1):
        i1 = remaining_indices[idx]
        i2 = remaining_indices[idx + 1]
        edges4.add((f"O_{i1}:{original_tokens[i1]}", f"O_{i2}:{original_tokens[i2]}"))
    frames.append(EvolutionFrame(4, "После удаления", "Удалены избыточные элементы", nodes4, edges4, {"осталось": len(remaining_indices)}))

    nodes5 = set(nodes4)
    for j, token in inserted:
        nodes5.add(f"N_{j}:{token}")
    frames.append(EvolutionFrame(5, "После добавления", "Добавлены новые элементы", nodes5, edges4, {"добавлено": len(inserted)}))

    nodes6 = {f"E_{i}:{token}" for i, token in enumerate(edited_tokens)}
    edges6 = {(f"E_{i}:{edited_tokens[i]}", f"E_{i+1}:{edited_tokens[i+1]}") for i in range(len(edited_tokens) - 1)}
    frames.append(EvolutionFrame(6, "Финальное состояние", "Отредактированный текст", nodes6, edges6, {"всего": len(edited_tokens)}))

    return frames
