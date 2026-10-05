import sys
import os

# Добавляем папку src в пути поиска модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from analyzer import OrderAnalyzer
import config


def main():
    """Основная функция запуска анализа."""
    analyzer = OrderAnalyzer()
    results, total_files, error_count = analyzer.process_all_files()

    if results:
        analyzer.save_report(results)

    print("=" * 40)
    print("Анализ заказов завершен.")
    print(f"Всего найдено CSV-файлов: {total_files}")
    print(f"Успешно обработано файлов: {len(results)}")
    print(f"Файлов с ошибками (пропущено): {error_count}")

    if results:
        print(f"Итоговый отчет сохранен: {config.OUTPUT_FILE}")
    if error_count > 0:
        print(f"Детали ошибок записаны в: {config.ERROR_LOG_FILE}")
    print("=" * 40)


if __name__ == "__main__":
    main()