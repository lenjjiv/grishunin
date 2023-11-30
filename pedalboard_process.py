from pedalboard import Compressor, Gain, HighpassFilter, Pedalboard
from pedalboard.io import AudioFile
from functions import *
from pydub import AudioSegment, effects  
from audio_processing import audio_normalize

def process_audio(input_file, 
                 output_file = None, 
                 normalize=True,
                 filter_cutoff_hz = 200
                 ):

    sound = AudioSegment.from_file(input_file)
    loud = sound.dBFS

    # Создаём цепочку эффектов
    effects = []

    # Обрезка нижних частот (гул в аудитории)
    effects.append(
      HighpassFilter(cutoff_frequency_hz = filter_cutoff_hz)
    )
    
    # Усиление громкости (нормализация аудио)
    if normalize:
       effects.append(
        Gain(gain_db=-12-loud)
      )
    
    # Создаём цепочку обработки звука:
    board = Pedalboard(effects)

    # Открываем аудиофайл для чтения:
    with AudioFile(input_file) as f:

      # Если не указано иное, файл сохраняем с префиксом _ (для различения)
      if output_file == None:
        output_file = change_name(input_file, suffix='_processed')

      # Открываем аудиофайл для записи
      with AudioFile(output_file, 'w', f.samplerate, f.num_channels) as o:

        # Читаем по одной секунде за раз
        while f.tell() < f.frames:
          chunk = f.read(f.samplerate)
          
          # Пропускаем звук через цепочку обработки:
          effected = board(chunk, f.samplerate, reset=False)
          
          # Записываем вывод в output_file:
          o.write(effected)