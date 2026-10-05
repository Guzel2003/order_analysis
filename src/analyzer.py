import pandas as pd
import os
import glob
import logging
import config

# Настройка логирования
os.makedirs(config.LOGS_DIR, exist_ok=True)

logging.basicConfig(
    filename=config.ERROR_LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)


class OrderAnalyzer:
    def __init__(self):
        """Инициализация анализатора и создание необходимых директорий."""
        os.makedirs(config.DATA_DIR, exist_ok=True)
        os.makedirs(config.REPORTS_DIR, exist_ok=True)
        os.makedirs(config.LOGS_DIR, exist_ok=True)

    def load_file(self, filepath):
        """
        Загружает CSV-файл с обработкой ошибок.
        Возвращает DataFrame или None в случае ошибки.
        """
        try:
            df = pd.read_csv(filepath)

            # Конкретная проверка каждой колонки отдельно
            if config.STATUS_COLUMN not in df.columns:
                raise ValueError(f"В файле отсутствует обязательная колонка '{config.STATUS_COLUMN}'. "
                                 f"Ожидаемые колонки: {list(df.columns)}")

            if config.AMOUNT_COLUMN not in df.columns:
                raise ValueError(f"В файле отсутствует обязательная колонка '{config.AMOUNT_COLUMN}'. "
                                 f"Ожидаемые колонки: {list(df.columns)}")

            # Проверка, что в колонке total_amount только числа
            # to_numeric с errors='coerce' превратит нечисловые значения в NaN
            df[config.AMOUNT_COLUMN] = pd.to_numeric(df[config.AMOUNT_COLUMN], errors='coerce')

            if df[config.AMOUNT_COLUMN].isna().any():
                raise ValueError(f"В колонке '{config.AMOUNT_COLUMN}' обнаружены нечисловые значения. "
                                 f"Файл: {os.path.basename(filepath)}")

            return df

        except pd.errors.EmptyDataError:
            logging.error(f"Файл пуст или не содержит данных: {os.path.basename(filepath)}")
            return None
        except pd.errors.ParserError:
            logging.error(f"Ошибка парсинга CSV (неверный формат файла): {os.path.basename(filepath)}")
            return None
        except ValueError as e:
            # Ловим наши конкретные ValueError и пишем их в лог
            logging.error(f"Ошибка в файле {os.path.basename(filepath)}: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Неожиданная ошибка при загрузке файла {os.path.basename(filepath)}: {str(e)}")
            return None

    def filter_delivered(self, df):
        """
        Фильтрует DataFrame, оставляя только заказы со статусом 'Delivered'.
        Возвращает отфильтрованный DataFrame.
        """
        return df[df[config.STATUS_COLUMN] == config.TARGET_STATUS]

    def calculate_metrics(self, df):
        """
        Рассчитывает метрики по отфильтрованному DataFrame.
        Возвращает словарь с метриками.
        """
        if df.empty:
            return {
                "total_revenue": 0.0,
                "avg_check": 0.0,
                "order_count": 0
            }

        total_revenue = float(df[config.AMOUNT_COLUMN].sum())
        avg_check = float(df[config.AMOUNT_COLUMN].mean())
        order_count = int(len(df))

        return {
            "total_revenue": round(total_revenue, 2),
            "avg_check": round(avg_check, 2),
            "order_count": order_count
        }

    def process_single_file(self, filepath):
        """
        Обрабатывает один файл: загружает, фильтрует, рассчитывает метрики.
        Возвращает словарь с результатами и именем файла или None в случае ошибки.
        """
        # Загрузка файла
        df = self.load_file(filepath)
        if df is None:
            return None

        # Фильтрация доставленных заказов
        filtered_df = self.filter_delivered(df)

        # Расчёт метрик
        metrics = self.calculate_metrics(filtered_df)

        # Создаём итоговый словарь с filename ПЕРВЫМ
        return {
            "filename": os.path.basename(filepath),
            "total_revenue": metrics["total_revenue"],
            "avg_check": metrics["avg_check"],
            "order_count": metrics["order_count"]
        }

    def process_all_files(self):
        """
        Находит все CSV-файлы в папке data/ и обрабатывает их.
        Возвращает кортеж: (список успешных результатов, общее кол-во файлов, кол-во ошибок).
        """
        csv_pattern = os.path.join(config.DATA_DIR, "*.csv")
        csv_files = glob.glob(csv_pattern)

        results = []
        error_count = 0

        for filepath in csv_files:
            result = self.process_single_file(filepath)
            if result is not None:
                results.append(result)
            else:
                error_count += 1

        return results, len(csv_files), error_count

    def save_report(self, results):
        """Сохраняет список результатов в итоговый CSV-файл."""
        if not results:
            print("Нет данных для сохранения в отчет.")
            return

        df = pd.DataFrame(results)
        os.makedirs(config.REPORTS_DIR, exist_ok=True)
        df.to_csv(config.OUTPUT_FILE, index=False, encoding='utf-8')