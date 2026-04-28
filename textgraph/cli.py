from .examples import EXAMPLES
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
        for index, example in enumerate(EXAMPLES, start=1):
            print("\n" + "=" * 70)
            print(f"ПРИМЕР {index}: {example['title'].upper()}")
            print("=" * 70)
            analyze_dynamic_evolution(example["original"], example["edited"], example["title"])
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
