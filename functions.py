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


def change_folder_name(file_path, new_folder):
    """
    Изменяет путь к файлу, переместив его в новую папку.

    Аргументы:
    file_path (str): Путь к файлу.
    new_folder (str): Новый путь к папке.

    Возвращает:
    str: Путь к файлу в новой папке.
    """
    # Получаем имя файла из исходного пути
    file_name = os.path.basename(file_path)

    # Объединяем новый путь к папке и имя файла
    new_file_path = os.path.join(new_folder, file_name)

    return new_file_path


def process_folder(folder_path, processing_function, output_folder = None, kwargs = {}):
    """
    Обрабатывает все файлы в указанной папке с помощью переданной функции.

    Аргументы:
    folder_path (str): Путь к папке, содержащей файлы для обработки.
    processing_function (callable): Функция для обработки каждого файла. Должна принимать один аргумент - путь к файлу.
    output_folder (str): Папка для сохранения результатов. Имя output_file передаётся в исполняющую функцию, если она не принимает такой аргумент, вылетит ошибка.
    kwargs (dict): Словарь с аргументами для передачи их в processing_function.

    Возвращает:
    None
    """
    # Проверяем, существует ли указанная папка
    if not os.path.exists(folder_path):
        print(f"Папка {folder_path} не существует.")
        return
    
    # Создаём папку output_path, если такая не существует
    if output_folder != None:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    # Получаем список файлов в указанной папке
    files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

    # Применяем функцию к каждому файлу с передачей аргументов из словаря kwargs
    for file_name in files:
        
        # Берём файл из папки
        file_path = os.path.join(folder_path, file_name)
        
        # Меняем output_path, если указана output_folder
        if output_folder != None:
            output_file = change_folder_name(file_path, output_folder)
            processing_function(file_path, output_file = output_file, **kwargs)
        
        else: # В противном случае, просто выполняем функцию, которую указали
            processing_function(file_path, output_file = None, **kwargs)


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