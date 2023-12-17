import os
import re

def change_name(file_path: str,
                name: str = None,
                extension: str = None,
                prefix="",
                suffix="",
               ):
    """
    Изменяет имя файла, добавляя префикс и/или суффикс к его названию.\n
    Может изменять расширение файла и его имя.

    Аргументы:
    file_path (str): Путь к файлу, чье имя нужно изменить.
    name (str, optional): Новое имя файла. Если указано, заменяет текущее имя.
    extension (str, optional): Новое расширение файла. Если указано, заменяет текущее расширение.
    prefix (str, optional): Префикс, который добавляется к имени файла перед его текущим названием.
    suffix (str, optional): Суффикс, который добавляется к имени файла после его текущего названия.

    Возвращает:
    str: Новый путь с измененным именем файла.
    """
    
    # Парсим исходное имя файла
    path, filename = os.path.split(file_path)
    name_, extension_ = os.path.splitext(filename)
        
    # Вручную присваиваем расширение, если требуется
    if extension is not None:
        extension_ = extension

    # Вручную присваиваем имя, если требуется
    if name is not None:
        name_ = name

    # Добавляем префикс и суффикс к имени, если требуется
    new_name = f"{prefix}{name_}{suffix}{extension_}"

    # Возвращаем новое имя файла
    return os.path.join(path, new_name).replace("\\", "/")


def process_folder(folder_path, processing_function):
    """
    Обрабатывает все файлы в указанной папке с помощью заданной функции.

    Аргументы:
    folder_path (str): Путь к папке, содержащей файлы для обработки.
    processing_function (callable): Функция для обработки каждого файла. Должна принимать один аргумент - путь к файлу.

    Возвращает:
    None
    """
    # Проверяем, существует ли указанная папка
    if not os.path.exists(folder_path):
        print(f"Папка {folder_path} не существует.")
        return

    # Получаем список файлов в указанной папке
    files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

    # Применяем функцию к каждому файлу
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        processing_function(file_path)


def parse_time(time_str):
    """
    Парсит строку длительности в формате "1h10m1s10ms" и возвращает общее время в миллисекундах.

    Аргументы:
    time_str (str): Строка с указанием времени в формате "1h10m1s10ms".

    Возвращает:
    int: Общее время в миллисекундах, полученное из указанной строки времени.
    """
    # Регулярное выражение для парсинга
    match = re.match(r'(?:(\d+h))?(?:(\d+m(?!s)))?(?:(\d+s))?(?:(\d+ms))?', time_str)
    
    # Получение часов, минут, секунд и миллисекунд из результатов поиска
    hours = int(match.group(1)[:-1]) if match.group(1) else 0
    minutes = int(match.group(2)[:-1]) if match.group(2) else 0
    seconds = int(match.group(3)[:-1]) if match.group(3) else 0
    milliseconds = int(match.group(4)[:-2]) if match.group(4) else 0

    # Возвращаем время в миллисекундах
    return hours * 60 * 60 * 1000 + minutes * 60 * 1000 + seconds * 1000 + milliseconds