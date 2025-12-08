import os
import csv
import logging

# --- 1. Створюємо власні винятки (Exceptions) ---
class CustomFileNotFoundError(Exception):
    """Виняток, що виникає, коли файл не знайдено при ініціалізації."""
    def init(self, message="Файл не знайдено"):
        super().init(message)

class FileCorruptedError(Exception):
    """Виняток, що виникає при помилках доступу або пошкодженні даних."""
    def init(self, message="Файл пошкоджено або помилка доступу"):
        super().init(message)

# --- 2. Декоратор для логування ---
def logged(exception_cls, mode):
    """
    exception_cls: клас помилки, яку ми відловлюємо (наприклад, FileCorruptedError)
    mode: режим логування ("console" або "file")
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                # Намагаємося виконати метод класу
                return func(*args, **kwargs)
            except exception_cls as e:
                # Налаштування логера
                logger = logging.getLogger("AppLogger")
                logger.setLevel(logging.ERROR)
                
                # Очищуємо попередні хендлери, щоб логи не дублювалися
                if logger.hasHandlers():
                    logger.handlers.clear()

                if mode == "console":
                    handler = logging.StreamHandler() # Вивід у консоль
                elif mode == "file":
                    handler = logging.FileHandler("app_log.txt", encoding='utf-8') # Запис у файл
                else:
                    handler = logging.StreamHandler()

                # Формат повідомлення
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)

                # Логуємо помилку
                logger.error(f"Сталася помилка в методі '{func.name}': {e}")
                
                # Прокидаємо помилку далі, щоб програма знала, що щось пішло не так
                raise e 
        return wrapper
    return decorator

# --- 3. Клас для роботи з CSV файлом ---
class CSVFileManager:
    def init(self, file_path):
        self.file_path = file_path
        
        # Перевірка існування файлу при створенні об'єкта
        if not os.path.exists(self.file_path):
            raise CustomFileNotFoundError(f"Файл за шляхом '{self.file_path}' не знайдено.")

    @logged(FileCorruptedError, mode="file")
    def read_file(self):
        """Читає весь вміст CSV файлу."""
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                data = list(reader)
                return data
        except (IOError, PermissionError, csv.Error) as e:
            # Перехоплюємо системні помилки і викликаємо нашу власну
            raise FileCorruptedError(f"Неможливо прочитати файл: {e}")

    @logged(FileCorruptedError, mode="file")
    def write_file(self, data):
        """Повністю перезаписує файл новими даними."""
        try:
            with open(self.file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(data)
        except (IOError, PermissionError, csv.Error) as e:
            raise FileCorruptedError(f"Неможливо записати у файл: {e}")

    @logged(FileCorruptedError, mode="file")
    def append_file(self, data):
        """Дописує дані в кінець файлу."""
        try:
            with open(self.file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(data)
        except (IOError, PermissionError, csv.Error) as e:
            raise FileCorruptedError(f"Неможливо дописати у файл: {e}")

# --- 4. Приклад використання (Демонстрація) ---
if __name__ == "main":
    # Спершу створимо тестовий файл, щоб конструктор не сварився (бо за умовою файл має існувати)
    filename = "data.csv"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Name,Age\nStudent,20\n")

    try:
        # 1. Створення екземпляру
        manager = CSVFileManager(filename)
        print("--- Читання файлу ---")
        print(manager.read_file())

        # 2. Дописування у файл
        print("\n--- Дописування даних ---")
        new_data = [["Teacher", "45"], ["Engineer", "30"]]
        manager.append_file(new_data)
        print("Дані дописано.")
        
        # Перевіримо читання знову
        print(manager.read_file())

        # 3. Перезапис файлу
        print("\n--- Перезапис файлу ---")
        manager.write_file([["ID", "Value"], ["1", "100"]])
        print(manager.read_file())

    except CustomFileNotFoundError as e:
        print(f"Помилка ініціалізації: {e}")
    except FileCorruptedError as e:
        print(f"Помилка операції: {e}")