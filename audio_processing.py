import torch
import torchaudio
import numpy as np
import noisereduce as nr
from torchaudio import functional as F
from pydub import AudioSegment
from functions import parse_time, change_name

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
    
    
def increase_volume(audio_np, db_increase):
    """
    Увеличивает громкость аудио на заданное количество децибел.

    Args:
        audio_np (np.ndarray): Массив NumPy, представляющий аудио.
        db_increase (float): Количество децибел для увеличения громкости.

    Returns:
        np.ndarray: Массив NumPy с увеличенной громкостью аудио.
    """

    # Преобразование децибел в коэффициент амплитуды
    amplitude_ratio = 10 ** (db_increase / 20)

    # Увеличение громкости аудио на указанное количество децибел
    amplified_audio_np = audio_np * amplitude_ratio

    return amplified_audio_np


def normalize_audio(audio_np, sample_rate, target_dB=-9.):
    """
    Приводит громкость аудио к заданному уровню децибел (нормализация).\n
    Внимание! Возможен клиппинг (обрезка слишком громких пиков)!\n
    По возможности стоит обратиться к продвинутым методам, например, pedalboard.

    Args:
        audio_np (np.ndarray): Массив NumPy, представляющий аудио.
        target_dB (float, optional): Желаемый уровень громкости в децибеллах. По умолчанию -9 dB.

    Returns:
        np.ndarray: Массив NumPy с нормализованной громкостью аудио.
    """

    # Рассчитываем текущую громкость аудиосигнала
    current_dB = calculate_rms_dB(audio_np)

    # Вычисляем разницу между текущей и желаемой громкостью
    dB_difference = target_dB - current_dB

    # Прибавляем нужное количество децибел к аудио
    amplified_audio_np = increase_volume(audio_np, dB_difference)

    return amplified_audio_np, sample_rate


def highpass_filter(audio_np, sample_rate: int, cutoff_freq=350.):
    """
    Применяет фильтр нижних частот (hi-pass filter) к аудио.

    Args:
        audio_np (np.ndarray): Аудио в формате массива numpy.
        sample_rate (int): Частота дискретизации сигнала (Гц).
        cutoff_freq (float, optional): Частота среза фильтра в герцах. По умолчанию 350 Гц

    Returns:
        np.ndarray, int: Возвращает отфильтрованное аудио и его частоту дискретизации (в Гц).
    """

    # Преобразование массива NumPy в тензор PyTorch
    waveform = torch.from_numpy(audio_np)

    # Применение фильтра нижних частот
    waveform = F.highpass_biquad(waveform, sample_rate, cutoff_freq)

    # Преобразование обратно в массив NumPy
    audio_np_filtered = waveform.numpy()

    return audio_np_filtered, sample_rate


def reduce_noise(waveform, sample_rate: int, y_noise: str = None,
                 prop_decrease=0.75, stationary=True, n_jobs=-1, device='cpu'):
    """
    Уменьшает шум в аудиосигнале.

    Args:
        waveform (numpy.ndarray): Аудиосигнал в формате numpy.
        sample_rate (int): Частота дискретизации.
        waveform_noise (str, optional): Путь к образцу шума (опционально). Используется для получения спектра шума. 
        prop_decrease (float, optional): Пропорция уменьшения шума. По умолчанию 0.75.
        stationary (bool, optional): Если True, предполагается, что шум стационарный.
        n_jobs (int, optional): Количество потоков для обработки. -1 для максимального числа доступных потоков.
        device (str, optional): Устройство для вычислений. По умолчанию 'cpu'.

    Returns:
        numpy.ndarray, int: Возвращает уменьшенный шум в аудиосигнале и частоту дискретизации.
    """
    # Денойзинг с образцом шума
    if y_noise:
        reduced_noise = nr.reduce_noise(y=waveform, sr=sample_rate,
                                        y_noise=y_noise, 
                                        stationary=stationary, 
                                        prop_decrease=prop_decrease, 
                                        device=device,
                                        n_jobs=n_jobs)
        
    # Денойзинг без образца   
    else:
        reduced_noise = nr.reduce_noise(y=waveform, stationary=stationary, sr=sample_rate,
                                        prop_decrease=prop_decrease, device=device,
                                        n_jobs=n_jobs)
        

    return reduced_noise, sample_rate

def save_audio_to_file(audio_np, sample_rate: int, output_file: str):
    """
    Сохраняет аудио в файл с использованием torchaudio.save().

    Args:
        audio_np (numpy.ndarray): Аудиосигнал в формате numpy.
        sample_rate (int): Частота дискретизации аудиосигнала.
        output_file (str): Путь к файлу для сохранения аудиосигнала.

    Returns:
        None
    """
    torchaudio.save(output_file, torch.from_numpy(audio_np), sample_rate)
    
    
def denoise_audio(audio_path: str, output_path: str, 
                  y_noise: str = None,
                  device: str = 'cpu', 
                  prop_decrease: float = 0.5, 
                  apply_filter: bool = False,
                  highpass_cutoff: float = 350., 
                  stationary: bool =True, 
                  n_jobs: int =-1
                  ):
    """
    Применяет фильтр и денойзинг к аудиосигналу и сохраняет результат.

    Args:
        audio_path (str): Путь к исходному аудиофайлу.
        output_path (str): Путь для сохранения обработанного аудиофайла.
        y_noise (str): Путь к образцу шума из аудио (для извлечения его спектра).
        device (str, optional): Устройство для вычислений. По умолчанию 'cuda'.
        prop_decrease (float, optional): Пропорция уменьшения шума. По умолчанию 0.5.
        apply_filter (bool, optional): Флаг применения фильтра. По умолчанию False.
        highpass_cutoff (int, optional): Частота среза для фильтра нижних частот. По умолчанию 350.
        waveform_noise (numpy.ndarray, optional): Образец шума. По умолчанию None.
        sample_rate_noise (int, optional): Частота дискретизации образца шума. По умолчанию None.
        stationary (bool, optional): Если True, предполагается, что шум стационарный. По умолчанию True.
        n_jobs (int, optional): Количество потоков для обработки. По умолчанию -1.

    Returns:
        None
    """
    # Загрузка аудиофайла
    audio_np, sample_rate = load_audio(audio_path)
    
    # Применение high-pass фильтра для обрезки гула
    if apply_filter:
        audio_np, sample_rate = highpass_filter(audio_np, sample_rate, cutoff_freq=highpass_cutoff)
        
    # Денойзинг аудиозаписи
    audio_denoised, sample_rate = reduce_noise(audio_np, sample_rate, y_noise=y_noise, 
                                               device=device, prop_decrease=prop_decrease, 
                                               stationary=stationary, n_jobs=n_jobs)
    
    # Сохранение обработанного аудиофайла
    save_audio_to_file(audio_denoised, sample_rate, output_path)


# Функция для обрезки аудио по заданному времени
def make_sample(audio_file, 
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

    # Сохранение результата (по умолчанию format="mp3")
    output_file_name = change_name(audio_file, suffix=f'_{start}_{end}')
    audio_segment.export(output_file_name, format=format)
    
    if verbose: # Выводим сообщение, если запрошен verbose
        print(f"Отрезок сохранен в файл: {output_file_name}")