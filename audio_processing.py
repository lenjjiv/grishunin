import numpy as np
from functions import parse_time, change_name
import os

import noisereduce as nr
import soundfile as sf
import torchaudio
from pydub import AudioSegment
import ffmpeg

from pedalboard import Gain, Pedalboard, Limiter
from pedalboard import HighpassFilter, LowpassFilter
from pedalboard.io import AudioFile


def load_audio(input_file):
    """
    Импортирует аудиофайл с помощью torchaudio. Возвращает массив numpy.

    Args:
        input_file (str): Путь к аудиофайлу.

    Returns:
        np.ndarray, int: Возвращает waveform (массив numpy) и sample_rate (частота дискретизации (Гц)).
    """

    try:
        waveform, sample_rate = torchaudio.load(input_file)
        waveform_np = waveform.numpy()  # Преобразование в массив NumPy
        return waveform_np, sample_rate
    except Exception as e:
        print(f"Ошибка при загрузке аудиофайла: {e}")
        return None, None


def calculate_rms_dB(audio_np):
    """
    Вычисляет уровень громкости звука в децибелах (dB) для аудиосигнала.

    Args:
        audio_np (numpy.ndarray): Аудиосигнал в формате NumPy.

    Returns:
        float: Уровень громкости в децибелах.
    """

    if audio_np is None or len(audio_np) == 0:
        print("Пустой аудиосигнал. Невозможно рассчитать уровень громкости.")
        return None

    try:
        rms = np.sqrt(np.mean(audio_np ** 2))
        rms_dB = 20 * np.log10(rms)
        return rms_dB
    except Exception as e:
        print(f"Ошибка при расчете уровня громкости: {e}")
        return None


# Функция для обрезки аудио по заданному времени
def make_sample(audio_file, 
                output_file = None,
                start="0m0s", 
                end="1m0s",
                format="mp3",
                verbose=False
                ):
    """
    Обрезает аудиофайл по заданным временным точкам и сохраняет отрезок в новый файл.

    Args:
    - audio_file (строка): Путь к исходному аудиофайлу.
    - start (строка): Начальное время для обрезки аудио. Например, "0m30s" обозначает 30 секунд.
    - end (строка): Конечное время для обрезки аудио. Например, "1m0s" обозначает 1 минуту.        
    - format (строка): Формат для сохранения результата. Поддерживаемые форматы — "mp3", "wav".            
    - verbose (булево): Если True, выводит информацию о сохранении отрезка в файл.

    Examples:
    >>> make_sample("input_audio.mp3", start="0m30s", end="1m10s", format="wav", verbose=True)
    # Отрезок сохранится в файл input_audio_0m30s_1m10s.wav
    
    >>> make_sample("music.wav", end="2m0s")
    # Создастся файл "music_0m0s_2m0s.mp3" с началом аудио с 0 секунд и концом на 2 минуты.

    Returns:
        None

    """
    # Приводим время к миллисекундам
    start_ms = parse_time(start)
    end_ms = parse_time(end)

    # Загрузка аудиофайла
    audio = AudioSegment.from_file(audio_file)

    # Вырезаем отрезок из аудио
    audio_segment = audio[start_ms:end_ms]

    # Если имя выходного файла не указано, добавляем суффикс к названию исходного
    if output_file == None:
        output_file = change_name(audio_file, suffix=f'_{start}_{end}')
    
    # Сохранение результата (по умолчанию format="mp3")   
    audio_segment.export(output_file, format=format)
    
    if verbose: # Выводим сообщение, если запрошен verbose
        print(f"Отрезок сохранен в файл: {output_file}")


def denoise_audio(input_file, 
                output_file, 
                device="cuda",
                prop_decrease=0.5,
                ):
    """
    Денойзинг аудиофайла MP3.

    Аргументы:
    input_file (str): Путь к входному аудиофайлу MP3.
    output_file (str): Путь для сохранения улучшенного аудиофайла.
    device (str): Устройство для обработки (по умолчанию "cuda").
    prop_decrease (float): Пропорция уменьшения шума. Разумны значения от 0 до 1. В случае 1 очень вероятны артефакты денойзинга, рекомендуются значения до 0.8.

    Возвращает:
    None
    """
    # Проверка на наличие строки "cuda"
    if device == "cuda" and "cuda" not in device.lower():
        print("CUDA не обнаружен. Используется CPU.")
    
    try: # Пробуем загрузить аудио с torchaudio (удобно дружелюбностью к разным форматам)
        sound, sample_rate = torchaudio.load(input_file, normalize=False)
    except Exception as e:
        print(f"Произошла ошибка при загрузке файла: {e}")
        return
    
    # Преобразование аудио в numpy array (требует денойзер)
    sound_np = sound.squeeze().numpy()

    # Проведение денойзинга
    reduced_noise = nr.reduce_noise(y=sound_np, sr=sample_rate, prop_decrease=prop_decrease, use_torch=True, device=device)
    
    # Сохранение очищенного аудиофайла
    sf.write(output_file, reduced_noise, sample_rate)
    
    
def convert_m4a_to_mp3(input_file, output_file):
    """
    Конвертирует файл формата M4A в файл формата MP3.

    Аргументы:
    input_file (str): Путь к исходному файлу M4A.
    output_file (str): Путь для сохранения конвертированного файла MP3.

    Возвращает:
    None
    """
    try:
        output_file = os.path.splitext(output_file)[0] + '.mp3'
        ffmpeg.input(input_file).output(output_file).run()
        print(f"Файл {input_file} успешно сконвертирован в {output_file}")
    except ffmpeg.Error as e:
        print(f"Произошла ошибка при конвертации: {e.stderr}")
        raise e
    
    
def pedalboard_processing(input_file: str, 
                          output_file: str = None, 
                          chunk_s: float = 1.,
                          target_db: float = None,
                          gain_db: float = None,
                          limiter_threshold_db: float = None,
                          highpass_cutoff: float = None,
                          lowpass_cutoff: float = None,
                          ):
    """
        Обрабатывает аудиофайл цепочкой эффектов.

        Аргументы:
        - input_file (str): Путь к входному аудио.
        - output_file (str, опционально): Путь для сохранения результата. Если None, обработанное аудио сохранится с добавлением суффикса к имени входного файла.
        - chunk_s (float, опционально): Продолжительность обрабатываемых фрагментов в секундах. По умолчанию 1 секунда.
        - target_dB (float, опционально): Целевой уровень громкости в децибелах (dB) для нормализации.
        - gain_db (float, опционально): Усиление громкости в децибелах (dB).
        - limiter_threshold_db (float, опционально): Порог в децибелах (dB) для лимитера (ограничивает предельную громкость пиков).
        - highpass_cutoff (float, опционально): Частота среза низких частот.
        - lowpass_cutoff (float, опционально): Частота среза высоких частот.

        Возвращает:
        - None: Функция сохранит результат в файл output_file. 

    """
    
    with AudioFile(input_file) as audio:

        # Создаём цепочку эффектов
        effects = []

        # Обрезка нижних частот (и оставление верхних ~ HighPass) 
        if highpass_cutoff:
            effects.append(
                HighpassFilter(cutoff_frequency_hz = highpass_cutoff)
            )
            
        # Обрезка верхних частот (и оставление нижних ~ LowPass) 
        if lowpass_cutoff:
            effects.append(
                LowpassFilter(cutoff_frequency_hz = lowpass_cutoff)
            )
        
        # Усиление громкости (нормализация аудио)
        if target_db and not gain_db:
            
            # Оцениваем громкость по первым 10 секундам
            audio_data = audio.read(audio.samplerate * 10) 
        
            # Посчитаем амплитуду аудиосигнала
            amplitude = np.sqrt(np.mean(audio_data**2))
            
            # Оценка громкости в дБ
            volume_dB = 20 * np.log10(amplitude)
            
            # Добавляем в цепочку эффектов усиление громкости
            effects.append(
                Gain(gain_db = target_db - volume_dB)
            )
            
        if gain_db:
            # Добавляем в цепочку эффектов усиление громкости
            effects.append(
                Gain(gain_db = gain_db)
            )
        
        if limiter_threshold_db:
            # Добавляем лимитер, чтобы запретить сигналу превышать порог громкости
            effects.append(
                Limiter(threshold_db=limiter_threshold_db)
            )
        
        # Создаём цепочку обработки звука:
        board = Pedalboard(effects)

        # Если не указано иное, файл сохраняем результат с добавлением суффикса к имени
        if output_file == None:
            output_file = change_name(input_file, suffix='_processed')

        # Открываем аудиофайл для записи
        with AudioFile(output_file, 'w', audio.samplerate, audio.num_channels) as o:

            # Читаем по chunk_s секунд за раз
            while audio.tell() < audio.frames:
                chunk = audio.read(chunk_s * audio.samplerate)
                
                # Пропускаем звук через цепочку обработки:
                effected = board(chunk, audio.samplerate, reset=False)
                
                # Записываем вывод в output_file:
                o.write(effected)
           
                
def extract_left_channel(input_file, output_file):
    """
    Извлекает левый аудиоканал из файла и сохраняет его в формате MP3.

    Аргументы:
    input_file (str): Путь к исходному аудиофайлу.
    output_file (str): Путь для сохранения левого аудиоканала в формате MP3.

    Возвращает:
    None
    """
    audio = AudioSegment.from_file(input_file)
    
    # Извлечение левого канала
    left_channel = audio.split_to_mono()[0]
    
    # Сохранение левого канала в файл
    left_channel.export(output_file, format="mp3")