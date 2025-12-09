import os
import csv
from typing import List, Dict, Iterable, Optional
from Logger import logged

class FileNotFound(Exception):
    """Файл не знайдено."""
    pass

class FileCorrupted(Exception):
    """Файл пошкоджено або недоступний для читання/запису."""
    pass

class CSVHandler:
    """
    Клас для роботи з CSV-файлом.
    - Перевіряє існування файлу у конструкторі.
    - read(): читає всі рядки як список словників.
    - write(rows): перезаписує файл повністю.
    - append_rows(rows): дописує багато рядків.
    - append_row(row): дописує один рядок.
    """

    @logged(exception=FileNotFound, mode="file", logfile="Logged_Messages.txt")
    def __init__(self, file_path: str, delimiter: str = ",", encoding: str = "utf-8"):
        self.file_path = file_path
        self.delimiter = delimiter
        self.encoding = encoding

        if not os.path.exists(self.file_path):
            raise FileNotFound(f"File '{self.file_path}' not found")

        
        if not os.path.isfile(self.file_path):
            raise FileNotFound(f"Path '{self.file_path}' is not a file")

    def _read_all(self) -> List[Dict[str, str]]:
        """Внутрішній метод: читає файл та повертає список словників."""
        try:
            with open(self.file_path, "r", encoding=self.encoding, newline="") as f:
               
                try:
                    sample = f.read(1024)
                    f.seek(0)
                except Exception as e:
                    raise FileCorrupted(f"Cannot probe file: {e}")

                reader = csv.DictReader(f, delimiter=self.delimiter)
               
                if reader.fieldnames is None or any(h is None or h.strip() == "" for h in reader.fieldnames):
                    raise FileCorrupted("CSV header missing or invalid")

                return [row for row in reader]
        except (OSError, UnicodeError, csv.Error) as e:
            raise FileCorrupted(f"Cannot read CSV: {e}")

    def _write_all(self, rows: List[Dict[str, str]], headers: Optional[List[str]] = None) -> None:
        """Внутрішній метод: повністю перезаписує файл."""
        try:
           
            if headers is None:
                if rows:
                    headers = list(rows[0].keys())
                else:
                    raise FileCorrupted("No data to write and no headers provided")

            with open(self.file_path, "w", encoding=self.encoding, newline="") as f:
                writer = csv.DictWriter(f, fieldnames=headers, delimiter=self.delimiter)
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
        except (OSError, UnicodeError, csv.Error) as e:
            raise FileCorrupted(f"Cannot write CSV: {e}")

    def _append_many(self, rows: Iterable[Dict[str, str]]) -> None:
        """Внутрішній метод: дописує кілька рядків, узгоджуючи їх із заголовком."""
        try:
            
            with open(self.file_path, "r", encoding=self.encoding, newline="") as f:
                reader = csv.reader(f, delimiter=self.delimiter)
                header = next(reader, None)
                if not header:
                    raise FileCorrupted("CSV header missing, cannot append")

            with open(self.file_path, "a", encoding=self.encoding, newline="") as f:
                writer = csv.DictWriter(f, fieldnames=header, delimiter=self.delimiter)
                for row in rows:
                    
                    unknown_keys = set(row.keys()) - set(header)
                    if unknown_keys:
                        raise FileCorrupted(f"Unknown columns for append: {unknown_keys}")
                    writer.writerow(row)
        except (OSError, UnicodeError, csv.Error) as e:
            raise FileCorrupted(f"Cannot append to CSV: {e}")

    @logged(exception=FileCorrupted, mode="file", logfile="Logged_Messages.txt")
    def read(self) -> List[Dict[str, str]]:
        """Публічний метод читання CSV як список словників."""
        return self._read_all()

    @logged(exception=FileCorrupted, mode="file", logfile="Logged_Messages.txt")
    def write(self, rows: List[Dict[str, str]], headers: Optional[List[str]] = None) -> None:
        """Публічний метод перезапису CSV (повністю)."""
        self._write_all(rows, headers=headers)

    @logged(exception=FileCorrupted, mode="file", logfile="Logged_Messages.txt")
    def append_rows(self, rows: Iterable[Dict[str, str]]) -> None:
        """Публічний метод дописування багатьох рядків у CSV."""
        self._append_many(rows)

    @logged(exception=FileCorrupted, mode="file", logfile="Logged_Messages.txt")
    def append_row(self, row: Dict[str, str]) -> None:
        """Публічний метод дописування одного рядка у CSV."""
        self._append_many([row])

