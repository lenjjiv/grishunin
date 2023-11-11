from pedalboard import Compressor, Gain, LowShelfFilter, Pedalboard
from pedalboard.io import AudioFile
from functions import *

def process_audio(input_file, 
                 output_file = None, 
                 gain_db = 27,
                 comp_ratio = 4,
                 comp_attack_ms = 10,
                 comp_threshold_db = -32,
                 filter_db = -20,
                 filter_q = 0.71,
                 cutoff_hz = 150
                 ):
  
  # Создаём цепочку обработки звука:
  board = Pedalboard([

        # Обрезка нижних частот (гул в аудитории)
        LowShelfFilter(cutoff_frequency_hz = cutoff_hz, 
                       gain_db=filter_db,
                      q=filter_q), 

        # Компрессия звука
        Compressor(threshold_db=comp_threshold_db, 
                  ratio=comp_ratio, 
                  attack_ms=comp_attack_ms),  

        # Увеличение громкости    
        Gain(gain_db=gain_db) 

    ])

  # Открываем аудиофайл для чтения:
  with AudioFile(input_file) as f:
    
    # Если не указано иное, файл сохраняем с префиксом _ (для различения)
    if output_file == None:
      output_file = add_prefix(input_file)

    # Открываем аудиофайл для записи
    with AudioFile(output_file, 'w', f.samplerate, f.num_channels) as o:
    
      # Читаем по одной секунде за раз
      while f.tell() < f.frames:
        chunk = f.read(f.samplerate)
        
        # Пропускаем звук через цепочку обработки:
        effected = board(chunk, f.samplerate, reset=False)
        
        # Записываем вывод в output_file:
        o.write(effected)