import os
import re

# Добавление префикса и суффикса к названиям файлов
def change_name(file_path, 
                name=None,
                extension=None,
                prefix="", 
                suffix="",
               ):

    # Парсим исходное имя файла
    path, filename = os.path.split(file_path)
    name_, extension_ = os.path.splitext(filename)
        
    # Вручную присваиваем расширение, если требуется
    if extension != None:
        extension_ = extension

    # Вручную присваиваем имя, если требуется
    if name != None:
        name_ = name

    # Добавляем префикс и суффикс к имени, если требуется
    new_name = f"{prefix}{name_}{suffix}{extension_}"

    # Возвращаем новое имя файла
    return os.path.join(path, new_name).replace("\\", "/")


# Обработка всех файлов в папке функцией processing_function
def process_folder(folder_path, processing_function):

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


# Парсинг строки с указанием времени (вида "1h10m1s10ms")
def parse_time(time_str):

    # Регулярное выражение для парсинга
    match = re.match(r'(?:(\d+h))?(?:(\d+m(?!s)))?(?:(\d+s))?(?:(\d+ms))?', time_str)
    
    # Получение часов, минут, секунд и миллисекунд из результатов поиска
    hours = int(match.group(1)[:-1]) if match.group(1) else 0
    minutes = int(match.group(2)[:-1]) if match.group(2) else 0
    seconds = int(match.group(3)[:-1]) if match.group(3) else 0
    milliseconds = int(match.group(4)[:-2]) if match.group(4) else 0

    # Возвращаем время в миллисекундах
    return hours * 60 * 60 * 1000 + minutes * 60 * 1000 + seconds * 1000 + milliseconds
