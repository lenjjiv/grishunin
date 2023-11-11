import os

# Добавление префикса и суффикса файлам
def add_prefix(file_path, 
               prefix="_", 
               suffix=''
               ):

    path, filename = os.path.split(file_path)
    name, extension = os.path.splitext(filename)
    new_name = f"{prefix}{name}{extension}{suffix}"
    new_path = os.path.join(path, new_name).replace("\\", "/")

    return new_path

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
