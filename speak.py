import assets
from speechkit import model_repository, configure_credentials, creds
import wave
import os
# Аутентификация через API-ключ.

def say(text):
    model = model_repository.synthesis_model()
    configure_credentials(
    yandex_credentials=creds.YandexCredentials(
      api_key = assets.API_KEY_TTS
      )
    )

   # Задайте настройки синтеза.
    model.voice = 'ermil'
    model.role = 'good'
    model.sample_rate = 24000 
   # Синтез речи и создание аудио с результатом.
    result = model.synthesize(text, raw_format=False)
    result.export('app/TTS_voice.wav', 'wav')
    with wave.open("app/TTS_voice.wav", "rb") as wav_file:

        # Получить параметры звука
        sample_rate = wav_file.getframerate()
        num_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()

        # Создать объект PyAudio
        import pyaudio

        p = pyaudio.PyAudio()

        # Открыть поток вывода звука
        stream = p.open(format=p.get_format_from_width(sample_width),
                        channels=num_channels,
                        rate=sample_rate,
                        output=True)

        # Читать и воспроизводить данные звука
        data = wav_file.readframes(1024)
        while data:
            stream.write(data)
            data = wav_file.readframes(1024)

        # Закрыть поток вывода звука
        stream.stop_stream()
        stream.close()

        # Закрыть объект PyAudio
        p.terminate()
        
    os.remove("app/TTS_voice.wav")
if __name__ == "__main__":
    say("Привет, как дела?")
