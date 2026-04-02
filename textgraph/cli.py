from .pipeline import analyze_dynamic_evolution
from .visualization import VISUALIZATION_AVAILABLE


def main():
    print("=" * 70)
    print("МОДЕЛИРОВАНИЕ ИЗМЕНЕНИЙ ТЕКСТА КАК ДИНАМИЧЕСКОГО ГРАФА")
    print("Версия 5.0 - Модульная архитектура")
    print("=" * 70)

    if VISUALIZATION_AVAILABLE:
        print("[ OK ] Библиотеки визуализации установлены")
    else:
        print("[WARN] Для визуализации: pip install networkx matplotlib")

    print("\nВыберите режим:")
    print("1. Примеры")
    print("2. Ввод своих текстов")
    print("3. Выход")
    choice = input("\nВаш выбор (1/2/3): ").strip()

    if choice == "1":
        print("\n" + "=" * 70)
        print("ПРИМЕР 1: РЕДАКТУРА НОВОСТНОЙ ЗАМЕТКИ")
        print("=" * 70)
        original1 = "The company launched a new product yesterday, which was developed over three years and cost approximately $5 million."
        edited1 = "Yesterday, the firm released a $5M product developed over three years."
        analyze_dynamic_evolution(original1, edited1, "Редактура новостной заметки")

        print("\n" + "=" * 70)
        print("ПРИМЕР 2: УПРОЩЕНИЕ ТЕКСТА")
        print("=" * 70)
        original2 = "The man who was sitting on the bench quickly stood up and walked away."
        edited2 = "The man stood up and walked away."
        analyze_dynamic_evolution(original2, edited2, "Упрощение текста")
    elif choice == "2":
        print("\n" + "=" * 70)
        print("ВВОД СВОИХ ТЕКСТОВ")
        print("=" * 70)
        original = input("\nИсходный текст: ").strip()
        edited = input("Отредактированный текст: ").strip()
        if original and edited:
            analyze_dynamic_evolution(original, edited, "Пользовательский ввод")
        else:
            print("[ERR ] Оба текста должны быть заполнены")
    else:
        print("До свидания!")


if __name__ == "__main__":
    main()
