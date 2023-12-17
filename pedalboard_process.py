from pedalboard import Gain, Pedalboard, Limiter
from pedalboard import HighpassFilter, LowpassFilter
from pedalboard.io import AudioFile
from functions import change_name
import numpy as np

def process_audio(input_file: str, 
                 output_file: str = None, 
                 chunk_s: float = 1.,
                 target_dB: float = None,
                 gain_db: float = None,
                 limiter_threshold_db: float = None,
                 filter_hipass_hz: float = None,
                 filter_lowpass_hz: float = None,
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
        - filter_hipass_hz (float, опционально): Частота среза низких частот.
        - filter_lowpass_hz (float, опционально): Частота среза высоких частот.

        Возвращает:
        - None: Функция сохранит результат в файл output_file. 

    """
    
    with AudioFile(input_file) as audio:

        # Создаём цепочку эффектов
        effects = []

        # Обрезка нижних частот (и оставление верхних ~ HighPass) 
        if filter_hipass_hz:
            effects.append(
                HighpassFilter(cutoff_frequency_hz = filter_hipass_hz)
            )
            
        # Обрезка верхних частот (и оставление нижних ~ LowPass) 
        if filter_lowpass_hz:
            effects.append(
                LowpassFilter(cutoff_frequency_hz = filter_lowpass_hz)
            )
        
        # Усиление громкости (нормализация аудио)
        if target_dB and not gain_db:
            
            # Оцениваем громкость по первым 10 секундам
            audio_data = audio.read(audio.samplerate * 10) 
        
            # Посчитаем амплитуду аудиосигнала
            amplitude = np.sqrt(np.mean(audio_data**2))
            
            # Оценка громкости в дБ
            volume_dB = 20 * np.log10(amplitude)
            
            # Добавляем в цепочку эффектов усиление громкости
            effects.append(
                Gain(gain_db = target_dB - volume_dB)
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

