# Импорт необходимых модулей
from PyQt6 import QtCore, QtWidgets, QtGui
import YAGPT
import speak  
import pyaudio
import wave
from speechkit import configure_credentials, creds
import assets
import recognize
frames = []


# Класс для обработки текстового запроса в отдельном потоке
class GPThread(QtCore.QThread):
    data_received = QtCore.pyqtSignal(str)
    def run(self):
        client_data = self.client_data
        response_data = YAGPT.gpt_answer(client_data) 
        self.data_received.emit(response_data)

# Класс для проигрывания аудиофайла с ответом в отдельном потоке

class TTSThread(QtCore.QThread):  
    def run(self):
        text = self.text
        speak.say(text)

# Класс для распознавания речи пользователя в отдельном потоке
class Recording(QtCore.QThread):
    def __init__(self):
        super().__init__()
        self.isPlay = False
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    def run(self):
        while self.isPlay:
            data = self.stream.read(1024)
            frames.append(data)
            
        else:
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            sf = wave.open("app/voice.wav","wb")
            sf.setnchannels(1)
            sf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            sf.setframerate(44100)
            sf.writeframes(b''.join(frames))
            frames.clear()
            sf.close()


class STThread(QtCore.QThread):
    data_received = QtCore.pyqtSignal(str)

    def run(self):
        response_data = recognize.recognize("app/voice.wav")        
        self.data_received.emit(response_data)

# Класс для главного окна приложения
class Ui_MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
    def setupUi(self, window):
        self.rec = None
        self.audio = pyaudio.PyAudio()
        self.isPlay = False
        # Настройка элементов интерфейса
        window.setObjectName("MainWindow")
        window.setEnabled(True)
        window.resize(802, 500)
        window.setAutoFillBackground(False)
        window.setSizeGripEnabled(False)
        window.setModal(False)
        
        self.layout = QtWidgets.QHBoxLayout()
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Maximum)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        
        self.plainTextEdit = QtWidgets.QPlainTextEdit(parent=window)
        self.plainTextEdit.setFixedHeight(51)
        self.plainTextEdit.setMaximumWidth(641)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEdit.sizePolicy().hasHeightForWidth())
        
        self.plainTextEdit.setSizePolicy(sizePolicy)
        self.plainTextEdit.setMouseTracking(False)
        self.plainTextEdit.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.plainTextEdit.setPlainText("")
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.plainTextEdit.setPlaceholderText("Введите текст")
        

        self.pushButton = QtWidgets.QPushButton(parent=MainWindow)
        self.pushButton.setMaximumWidth(70)
        self.pushButton.setFixedHeight(51)
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setAcceptDrops(False)
        self.pushButton.setCheckable(False)
        self.pushButton.setDefault(False)
        self.pushButton.setFlat(False)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.generateCompetition)

        self.audioButton = QtWidgets.QPushButton(parent=MainWindow)
        self.audioButton.setMaximumWidth(70)
        self.audioButton.setFixedHeight(51)
        self.audioButton.setSizePolicy(sizePolicy)
        self.audioButton.setAcceptDrops(False)
        self.audioButton.setCheckable(False)
        self.audioButton.setDefault(False)
        self.audioButton.setFlat(False)
        self.audioButton.setObjectName("audioButton")
        self.audioButton.clicked.connect(self.recordingAudio)

        self.next_button = QtWidgets.QPushButton("Чебурашка")
        self.next_button.clicked.connect(self.open_second_widget)
        self.next_button.setFixedHeight(51)
        self.next_button.setMaximumWidth(150)
    
        self.new_text = QtWidgets.QLabel(MainWindow)
        self.new_text.move(10, -150)
        self.new_text.setWordWrap(True)
        self.new_text.setFixedSize(700,400)
        
        self.layout.addWidget(self.next_button)
        self.layout.addWidget(self.plainTextEdit)
        self.layout.addWidget(self.audioButton)
        self.layout.addWidget(self.pushButton)
        self.retranslateUi(MainWindow)
        
        QtCore.QMetaObject.connectSlotsByName(window)
    
    def retranslateUi(self, window):
        _translate = QtCore.QCoreApplication.translate
        window.setWindowTitle(_translate("MainWindow", "Ассистент"))
        self.pushButton.setText(_translate("MainWindow", "->"))
        self.audioButton.setText(_translate("MainWindow", "audio"))
        window.setLayout(self.layout)

    def generateCompetition(self):
        if self.plainTextEdit.toPlainText() in ("", " "):
            self.new_text.setText("Введите запрос")
        else:
            self.client_data = self.plainTextEdit.toPlainText()
            
            # Создание и запуск потока для обработки запроса
            self.gpt_thread = GPThread()
            self.gpt_thread.client_data = self.client_data
            self.gpt_thread.data_received.connect(self.handle_response)
            self.gpt_thread.start()
            
    def handle_response(self, response_data):
        self.tts_thread = TTSThread()
        self.tts_thread.text = response_data
        self.tts_thread.start()

        self.new_text.setText(response_data)
        
    def open_second_widget(self):
        MainWindow.hide()
        SecondWindow.show()
    
    def recordingAudio(self):
        self.isPlay = not self.isPlay
        if self.isPlay:
            self.rec = Recording()
            self.rec.isPlay = self.isPlay
            self.rec.start()
        else:
            self.rec.isPlay = False
            self.stt_thread = STThread()
            self.stt_thread.data_received.connect(self.set_audio_text)
            self.stt_thread.start()
    def set_audio_text(self, response_data):
        self.plainTextEdit.setPlainText(response_data)
# Класс для второго окна приложения
class SecondWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
    def setupUi(self, window):
        window.setWindowTitle("Второй виджет")
        window.setGeometry(802, 300, 1000, 750)

        self.layout = QtWidgets.QVBoxLayout(window)
        
        self.image_label = QtWidgets.QLabel()
        self.pixmap = QtGui.QPixmap("app/cheb.png")
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setScaledContents(True)
        
        self.button = QtWidgets.QPushButton("Вернуться на первый виджет")
        self.button.clicked.connect(self.open_first_widget)
        
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.button)
        window.setLayout(self.layout)
        
    def open_first_widget(self):
        MainWindow.show()
        SecondWindow.hide()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    MainWindow = QtWidgets.QDialog()    
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    SecondWindow = QtWidgets.QDialog()
    widget = SecondWidget()
    widget.setupUi(SecondWindow)
    
    MainWindow.show()

    sys.exit(app.exec())
