from pedalboard import Compressor, Gain, HighpassFilter, Pedalboard
from pedalboard.io import AudioFile
from functions import *

def process_audio(input_file, 
                 output_file = None, 
                 gain_db = 27,
                 use_compressor = False,
                 comp_ratio = 4,
                 comp_attack_ms = 10,
                 comp_threshold_db = -32,
                 filter_cutoff_hz = 200
                 ):

    # Создаём цепочку эффектов
    effects = []

    # Обрезка нижних частот (гул в аудитории)
    effects.append(
      HighpassFilter(cutoff_frequency_hz = filter_cutoff_hz)
    )

    # Компрессия звука
    if use_compressor:
      effects.append(
        Compressor(threshold_db=comp_threshold_db, 
                  ratio=comp_ratio, 
                  attack_ms=comp_attack_ms)
      )

    # Увеличение громкости
    effects.append(
      Gain(gain_db=gain_db) 
    )
    
    # Создаём цепочку обработки звука:
    board = Pedalboard(effects)

    # Открываем аудиофайл для чтения:
    with AudioFile(input_file) as f:
      
      # Если не указано иное, файл сохраняем с префиксом _ (для различения)
      if output_file == None:
        output_file = change_name(input_file, prefix='_')

      # Открываем аудиофайл для записи
      with AudioFile(output_file, 'w', f.samplerate, f.num_channels) as o:
      
        # Читаем по одной секунде за раз
        while f.tell() < f.frames:
          chunk = f.read(f.samplerate)
          
          # Пропускаем звук через цепочку обработки:
          effected = board(chunk, f.samplerate, reset=False)
          
          # Записываем вывод в output_file:
          o.write(effected)