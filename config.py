import os

# Базовая директория проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Пути к папкам
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Пути к файлам
ERROR_LOG_FILE = os.path.join(LOGS_DIR, "errors.log")
OUTPUT_FILE = os.path.join(REPORTS_DIR, "summary_report.csv")

# Настройки фильтрации и колонок
TARGET_STATUS = "Delivered"
STATUS_COLUMN = "status"
AMOUNT_COLUMN = "total_amount"