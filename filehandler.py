import os
import shutil
import time


def read_paths_from_file(file_path):
    """Liest die Pfade und das Intervall aus der Konfigurationsdatei."""
    paths = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                paths[key] = value
    except Exception as e:
        print(f"Fehler beim Lesen der Datei {file_path}: {e}")
        raise

    src_path = paths.get('src_path')
    target_path = paths.get('target_path')
    check_interval = paths.get('check_interval')

    if not src_path or not target_path or not check_interval:
        raise ValueError("Die 'paths.txt' Datei muss 'src_path', 'target_path' und 'check_interval' enthalten.")

    try:
        check_interval = int(check_interval)
    except ValueError:
        raise ValueError(f"Ungültiges Intervall in 'paths.txt': {check_interval}")

    return src_path, target_path, check_interval


def is_file_in_use(filepath):
    """Überprüft, ob die Datei von einem anderen Prozess verwendet wird (Lese- oder Schreibmodus)."""
    try:
        with open(filepath, 'r'):
            pass
    except IOError:
        return True

    try:
        with open(filepath, 'r+'):
            pass
    except IOError:
        return True

    return False


def get_unique_target_file(target_path, file_name):
    """Generiert einen einzigartigen Dateinamen, falls eine Datei bereits existiert."""
    base_name, ext = os.path.splitext(file_name)
    new_file_name = file_name
    counter = 1

    while os.path.exists(os.path.join(target_path, new_file_name)):
        new_file_name = f"{base_name}_x{counter}{ext}"
        counter += 1

    return new_file_name


def move_files(src_path, target_path, check_interval):
    """Verschiebt Dateien, die nicht in Verwendung sind, in das Zielverzeichnis."""
    for file_name in os.listdir(src_path):
        if file_name.endswith('.eds'):
            src_file = os.path.join(src_path, file_name)
            target_file_name = get_unique_target_file(target_path, file_name)
            target_file = os.path.join(target_path, target_file_name)

            while is_file_in_use(src_file):
                print(f"{file_name} ist in Verwendung, warte...")
                time.sleep(check_interval)

            try:
                shutil.move(src_file, target_file)
                print(f"{file_name} wurde nach {target_file_name} verschoben.")
            except Exception as e:
                print(f"Fehler beim Verschieben von {file_name}: {e}")


if __name__ == "__main__":
    try:
        src_path, target_path, check_interval = read_paths_from_file('paths.txt')
        print(
            f"Überwache {src_path} und verschiebe Dateien nach {target_path}, Überprüfungsintervall: {check_interval} Sekunden")

        while True:
            move_files(src_path, target_path, check_interval)
            time.sleep(check_interval)
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
