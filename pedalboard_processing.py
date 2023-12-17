from pedalboard import Gain, Pedalboard, Limiter
from pedalboard import HighpassFilter, LowpassFilter
from pedalboard.io import AudioFile
from functions import change_name
import numpy as np

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