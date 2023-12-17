import re
import PyPDF2
 
def import_pdf_text(file_path, start_page=None, end_page=None):
    """
    Извлекает текст из PDF-файла для заданного диапазона страниц.

    Args:
        file_path (str): Путь к PDF-файлу.
        start_page (int, optional): Начальная страница для извлечения текста. None вернёт все страницы, начиная с первой.
        end_page (int, optional): Конечная страница для извлечения текста. None вернёт страницы до последней.

    Returns:
        list: Массив с текстами (постранично) из указанного диапазона страниц.
    """
    try:
        # Открываем PDF-файл для чтения в бинарном режиме
        with open(file_path, 'rb') as pdf_file:
            # Создаем объект для чтения PDF
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Создаем список для хранения извлеченного текста
            texts = []

            # Извлекаем текст из указанного диапазона страниц PDF и добавляем его в список
            for page_num in range(start_page - 1 if start_page else 0, end_page if end_page else len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                texts.append(page.extract_text())

        return texts

    except Exception as e:
        print(f"Произошла ошибка при извлечении текста из PDF: {e}")
        return None


def clean_text(text, mode='normal', preserve_symbols=None, remove_symbols=None, remove_caps=False):
    """Очищает текст от лишних символов

    Args:
        text (str): Входной текст для очистки
        mode (str): Режим очистки: 'soft', 'normal', 'aggressive' или 'bypass'. Режим 'bypass' возвращает исходный текст без изменений.
        preserve_symbols (list): Список символов, которые нужно оставить
        remove_symbols (list): Список символов, которые нужно удалить
        remove_caps (bool): Нужно ли удалять слова, написанные ЦЕЛИКОМ КАПСОМ

    Returns:
        str: Очищенный текст
    """
    
    # Удаляем капс в начале, т.к. может привести к лишним пробелам
    if remove_caps:
        text = re.sub(r'\b[A-ZА-ЯЁ0-9]+\b', '', text)

    if mode == 'soft':
        # Удаление переносов слов и замена переносов строк на пробелы
        text = re.sub("\s-\n", "", text)  # Удаляем переносы слов
        text = re.sub("\n", " ", text)    # Заменяем переносы строк на пробелы

    elif mode == 'normal':
        # Выполнение очистки для режима 'normal'
        text = re.sub("\s-\n", "", text)        # Удаляем переносы слов
        text = re.sub("\n", " ", text)          # Заменяем переносы строк на пробелы
        text = re.sub(r'\s+', ' ', text)        # Заменяем последовательности пробелов на один
        text = re.sub(r'\.{3,}', '.', text)     # Заменяем три и более точки на одну
        text = re.sub(r'[^ «»;:—!.,()\-А-Яа-яЁёA-Za-z0-9]', '', text)  # Удаляем все символы, кроме букв, цифр и пробелов

    elif mode == 'aggressive':
                    
        text = remove_links(text)  # Удаляем ссылки из текста

        # Удаляем переносы слов и заменяем переносы строк на пробелы
        text = re.sub("\s?-\n", "", text)
        text = re.sub("\n", " ", text)
        
        text = re.sub('[^ «»;:—!.,()\-А-Яа-яЁёA-Za-z]', '', text) # Удаляем все символы, кроме букв, пробелов и пунктуации
        text = re.sub(r'(\w):(\w)', r'\1: \2', text) # Добавляем пробел после двоеточия
        text = re.sub(r'(\s):', ':', text) # Удаляем пробелы перед двоеточием
        text = re.sub(r'\s\;', ';', text)# Удаляем пробелы перед точкой с запятой
        text = re.sub(r'\s\,', ',', text) # Удаляем пробелы перед запятой
        
        text = re.sub(r'\,\s+', ', ', text) # Удаляем лишние пробелы после запятой
        text = re.sub(r'\s*\.\s*', '. ', text) # Удаляем лишний пробел рядом с точкой
        text = re.sub(r'(\.\s+)+', '. ', text)# Удаляем лишние пробелы после точки
        text = re.sub(r'\s?«\s+', ' «', text) # Удаляем лишние пробелы рядом с открывающей кавычкой
        text = re.sub(r'\s+»\s?', '» ', text) # Удаляем лишние пробелы рядом с закрывающей кавычкой
        text = re.sub(r'\(\s', '(', text) # Удаляем лишние пробелы после открывающей скобки
        text = re.sub(r'\s\)', ')', text) # Удаляем лишние пробелы перед открывающей скобкой

        text = re.sub(r'[,.—\-:;]{3,}', ' ', text) # Удаляем много подряд идущих символов пунктуации
        
        text = re.sub('\s+', ' ', text) # Удаляем лишние пробелы
        
        text = re.sub(r'\.{2,}', '.', text) # Заменяем n подряд идущих точек на одну
        
    elif mode == 'bypass':
        return text

    if preserve_symbols:
        # Оставляем указанные символы
        preserved_pattern = f"[^{re.escape(''.join(preserve_symbols))}]"
        text = re.sub(preserved_pattern, '', text)

    if remove_symbols:
        # Удаляем указанные символы
        remove_pattern = f"[{''.join(remove_symbols)}]"
        text = re.sub(remove_pattern, '', text)

    return text


def remove_links(text):
    """
    Удаляет ссылки из текста.

    Args:
    text (str): Исходный текст с ссылками

    Returns:
    str: Текст без ссылок
    """

    import urlextract

    # Создание экземпляра urlextract для поиска URL-адресов
    extractor = urlextract.URLExtract()

    # Извлечение всех найденных URL-адресов в тексте
    urls = extractor.find_urls(text)

    # Создание копии входного текста для последующей очистки
    cleaned_text = text

    # Замена всех найденных URL-адресов на пустую строку
    for url in urls:
        cleaned_text = cleaned_text.replace(url, "")

    return cleaned_text


def import_text(file_path, encoding='utf-8'):
    """
    Импортирует текст из файла.

    Args:
    file_path (str): Путь к файлу, из которого будет импортирован текст.
    encoding (str, optional): Кодировка файла. По умолчанию 'windows-1251'.

    Returns:
    str: Импортированный текст.
    """

    with open(file_path, 'r', encoding=encoding) as file:
        imported_text = file.read()

    return imported_text


def export_text(file_path, text, encoding='utf-8'):
    """
    Экспортирует текст в файл с заданной кодировкой.

    Args:
    file_path (str): Путь к файлу, в который будет экспортирован текст.
    text (str): Текст для экспорта.
    encoding (str, optional): Кодировка файла. По умолчанию 'utf-8'.
    """

    with open(file_path, 'w', encoding=encoding) as file:
        file.write(text)
        
        
def text_preprocess(file_path, clean_mode='soft', preserve_symbols=None, remove_symbols=None):
    """
    Загружает и предобрабатывает текст из файла.

    Args:
        file_path (str): Путь к файлу с текстом.
        clean_mode (str, optional): Режим предобработки текста для clean_text. По умолчанию 'soft'.
        preserve_symbols (list, optional): Список символов для сохранения. По умолчанию None.
        remove_symbols (list, optional): Список символов для удаления из текста. По умолчанию None.

    Returns:
        str: Предобработанный текст.

    Raises:
        ValueError: Если указан недопустимый режим clean_mode.
    """

    # Загружаем файл с prompt'ом
    file = open(file_path, 'r')
    text = file.read()

    # Проверка режима clean_mode
    if clean_mode in ['bypass', 'soft', 'normal', 'aggressive']:
        text = clean_text(text, mode=clean_mode, preserve_symbols=preserve_symbols, remove_symbols=remove_symbols)
        return text
    else:
        raise ValueError("Недопустимый режим clean_mode. Используйте 'bypass', 'soft', 'normal' или 'aggressive'.")
