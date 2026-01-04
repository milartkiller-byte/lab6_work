import os
from LogicForFiles import CSVHandler, FileNotFound, FileCorrupted

def show_help():
    print("\nДоступні команди:")
    print(" read            - прочитати CSV")
    print(" write           - перезаписати CSV (JSON-подібний ввід списку словників)")
    print(" append_row      - дописати один рядок (JSON-подібний словник)")
    print(" append_rows     - дописати кілька рядків (JSON-подібний список словників)")
    print(" help            - показати команди")
    print(" exit            - вихід")

def create_csv_if_needed(file_path: str):
    if not os.path.exists(file_path):
        print(f"Файл '{file_path}' не знайдено.")
        create = input("Створити новий CSV-файл? (y/n): ").strip().lower()
        if create == "y":
            
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                f.write("id,name,age\n")
            print("Файл створено з заголовком: id,name,age")
        else:
            raise FileNotFound(f"File '{file_path}' not found")

def main():
    print("CSV Processor")
    file_path = "data.csv"

    try:
        create_csv_if_needed(file_path)
        handler = CSVHandler(file_path)
    except FileNotFound as e:
        print(f"Помилка: {e}")
        return

    show_help()

    while True:
        cmd = input("\nКоманда: ").strip().lower()

        try:
            if cmd == "read":
                data = handler.read()
                if not data:
                    print("\nCSV порожній або містить лише заголовок.")
                else:
                    print("\nВміст CSV:")
                    for row in data:
                        print(row)

            elif cmd == "write":
                print("Введіть дані як список словників. Наприклад:")
                print('[{"id":"1","name":"Bob","age":"25"}, {"id":"2","name":"Ann","age":"22"}]')
                raw = input(">> ")
                
                rows = eval(raw)  
                
                headers = list(rows[0].keys()) if rows else None
                handler.write(rows, headers=headers)
                print("CSV перезаписано.")

            elif cmd == "append_row":
                print('Введіть один рядок як словник. Наприклад: {"id":"3","name":"Kate","age":"28"}')
                raw = input(">> ")
                row = eval(raw)
                handler.append_row(row)
                print("Рядок дописано.")

            elif cmd == "append_rows":
                print('Введіть кілька рядків як список словників. Наприклад:')
                print('[{"id":"4","name":"Tom","age":"30"}, {"id":"5","name":"Iryna","age":"21"}]')
                raw = input(">> ")
                rows = eval(raw)
                handler.append_rows(rows)
                print("Рядки дописано.")

            elif cmd == "help":
                show_help()

            elif cmd == "exit":
                print("Вихід...")
                break

            else:
                print("Невідома команда.")

        except FileCorrupted as e:
            print(f"Помилка файлу: {e}")
        except Exception as e:
            print(f"Неочікувана помилка: {e}")

if __name__ == "__main__":
    main()

