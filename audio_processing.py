import speech_recognition as sr
from pydub import AudioSegment
from functions import change_name

# Функция для преобразования в .wav-файл (.mp3 не принимаются)
def convert_audio(input_file, 
                  output_file=None, 
                  format='wav'
                  ):

    if output_file == None:
        output_file = change_name(input_file, extension=f".{format}")

    # Загрузка аудиофайла
    audio = AudioSegment.from_file(input_file)

    # Сохранение в формате WAV
    audio.export(output_file, format=format)

    # Возвращаем имя выходного файла 
    return output_file

# Функция для транскрибирования аудио
def transcript(audio_file,
               verbose = False,
               lang='ru'
               ):

    # Создание объекта распознавания речи
    recognizer = sr.Recognizer()

    # Открытие аудиофайла
    with sr.AudioFile(audio_file) as source:

        # Загрузка аудио для обработки
        audio = recognizer.record(source)
        
        try: # Распознание речи на мощностях Google
            text = recognizer.recognize_google(audio, language=lang)

            # Если запрошено, выводим текст на экран
            if verbose:            
                print("Текст сообщения:", text)
                
            return text

        # Обработка ошибок
        except sr.UnknownValueError as exc:
            print(f"Не удалось распознать речь: {exc}")
        except sr.RequestError as e:
            print("Ошибка сервиса распознавания речи; {0}".format(e))


# Функция для обрезки аудио по заданному времени
def make_sample(audio_file, 
                start="0m0s", 
                end="1m0s",
                format="mp3",
                verbose=False
                ):
    
    from functions import parse_time, change_name

    # Приводим время к миллисекундам
    start_ms = parse_time(start)
    end_ms = parse_time(end)

    # Загрузка аудиофайла
    audio = AudioSegment.from_file(audio_file)

    # Вырезаем отрезок из аудио
    audio_segment = audio[start_ms:end_ms]

    # Сохранение результата (по умолчанию format="mp3")
    output_file_name = change_name(audio_file, suffix=f'_{start}_{end}')
    audio_segment.export(output_file_name, format=format)
    
    if verbose: # Выводим сообщение, если это было запрошено
        print(f"Отрезок сохранен в файл: {output_file_name}")
