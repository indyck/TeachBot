from argparse import ArgumentParser
from speechkit import model_repository, configure_credentials, creds
from speechkit.stt import AudioProcessingType
import assets
import os
# Аутентификация через API-ключ.


def recognize(path):
   configure_credentials(
   yandex_credentials=creds.YandexCredentials(
      api_key=assets.API_KEY_SST
      )
   )
   model = model_repository.recognition_model()

   # Задайте настройки распознавания.
   model.model = 'general'
   model.language = 'ru-RU'
   model.audio_processing_type = AudioProcessingType.Full

   # Распознавание речи в указанном аудиофайле и вывод результатов в консоль.
   result = model.transcribe_file(path)
   os.remove(path)
   return str(result[0])
   

if __name__ == '__main__':

   print(recognize("app/voice.wav"))
