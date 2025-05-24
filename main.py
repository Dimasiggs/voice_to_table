import time
import pyaudio
import wave
import kivy
from kivy.app import App
import openpyxl
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
import threading
import vosk
import json
import pandas as pd
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
import ai_token
from text_to_command import *

from kivy.core.window import Window

CHUNK = 4000 # определяет форму ауди сигнала
FRT = pyaudio.paInt16 # шестнадцатибитный формат задает значение амплитуды
CHAN = 1 # канал записи звука
RT = 16000 # частота
REC_SEC = 10 #длина записи

PLAY_ICON_PATH = 'static/play-icon.png'
STOP_ICON_PATH = 'static/stop-icon.png'
#MODEL_PATH = "vosk-model-ru-0.42"
MODEL_PATH = "vosk-model-small-ru-0.22"

EXPORT_XLS = "XLS"
EXPORT_CSV = "CSV"

table = pd.DataFrame([[1,2,3,4,5], [6,7,8,9,10], [11,12,13,14,15]], columns=['a', 'b', 'c', 'd', 'e'])

vosk_model = vosk.Model(model_path=MODEL_PATH)
p = pyaudio.PyAudio()
recognizer = vosk.KaldiRecognizer(vosk_model, RT)

Window.clearcolor = (0.9, 0.9, 0.9, 1)


def get_data_table(dataframe):
    column_data = list(dataframe.columns)
    row_data = dataframe.to_records(index=False)
    return column_data, row_data

class MyApp(MDApp):
    def build(self):
        self.is_recording = False
        self.current_export_format = None
        self.export_disabled = True
        self.float_layout = FloatLayout()
        self.frames = []

        self.box_layout = BoxLayout(orientation='vertical')

        self.anchor_layout = AnchorLayout()
        self.anchor_layout.anchor_x = 'center'
        self.anchor_layout.anchor_y = 'bottom'
        self.anchor_layout.size_hint_y = 0.2

        self.button = Button()
        self.button.background_normal = PLAY_ICON_PATH
        self.button.background_down = PLAY_ICON_PATH
        self.button.on_press = self.btn_press
        self.button.size_hint = (None, None)
        self.button.size = (150,150)

        self.anchor_layout_text = AnchorLayout()
        self.anchor_layout_text.anchor_x = 'center'
        self.anchor_layout_text.anchor_y = 'top'
        self.anchor_layout_text.size_hint_y = 0.1

        self.label = Label()
        self.label.size_hint = (None, None)
        self.label.size = (200, 100)
        self.label.max_lines = 1
        self.label.text = "Hello world"
        self.label.font_size = 28
        self.label.color = (0,0,0,1)

        self.anchor_layout_table = AnchorLayout()
        self.anchor_layout_table.anchor_x = 'center'
        self.anchor_layout_table.anchor_y = 'top'
        self.anchor_layout_table.size_hint_y = 0.6
        self.anchor_layout_table.padding = 15

        column_data, row_data = get_data_table(table)
        column_data = [(x, dp(12)) for x in column_data]

        self.table_view = MDDataTable(
            column_data=column_data,
            row_data=row_data)
        self.table_view.size_hint_x = 1

        self.anchor_layout_export = AnchorLayout()
        self.anchor_layout_export.anchor_x = 'center'
        self.anchor_layout_export.anchor_y = 'top'
        self.anchor_layout_export.size_hint_y = 0.1
        self.anchor_layout_export.padding = 20

        self.box_layout_export = BoxLayout()

        self.spinner = Spinner(
            text='Формат экспорта',
            values=(EXPORT_XLS, EXPORT_CSV),
            size_hint=(None, None),
            size=(200, 50),
            font_size=20
        )
        self.spinner.bind(text=self.on_spinner_select)

        self.export_file_input = TextInput(
            hint_text='Название экспортного файла',
            multiline=False,  # Однострочный режим
            size_hint=(1, None),
            height=50,
            halign='center',
            text='output',
            font_size=20
        )
        self.export_file_input.bind(text=self.changed_export_file_text)

        self.export_button = Button(text='Экспорт')
        self.export_button.size_hint = (None, None)
        self.export_button.size = (200, 50)
        self.export_button.disabled = self.export_disabled
        self.export_button.font_size = 20
        self.export_button.on_press = self.export_btn_click

        self.box_layout_export.add_widget(self.spinner)
        self.box_layout_export.add_widget(self.export_file_input)
        self.box_layout_export.add_widget(self.export_button)

        self.anchor_layout.add_widget(self.button)
        self.anchor_layout_text.add_widget(self.label)
        self.anchor_layout_table.add_widget(self.table_view)
        self.anchor_layout_export.add_widget(self.box_layout_export)
        self.box_layout.add_widget(self.anchor_layout)
        self.box_layout.add_widget(self.anchor_layout_text)
        self.box_layout.add_widget(self.anchor_layout_table)
        self.box_layout.add_widget(self.anchor_layout_export)
        self.float_layout.add_widget(self.box_layout)
        return self.float_layout

    def btn_press(self):
        if not self.is_recording:
            self.is_recording = True
            self.start_record()
            self.button.background_normal = STOP_ICON_PATH
            self.button.background_down = STOP_ICON_PATH
        else:
            self.stop_record()
            self.button.background_normal = PLAY_ICON_PATH
            self.button.background_down = PLAY_ICON_PATH

    def start_record(self):
        self.record_thread = threading.Thread(target=self.listen_info_task, daemon=True)
        self.record_thread.start()

    def stop_record(self):
        self.is_recording = False
        if self.record_thread is not None:
            self.record_thread = None


    def listen_info_task(self):
        stream = p.open(format=FRT,channels=CHAN,rate=RT,input=True,frames_per_buffer=CHUNK) # открываем поток для записи
        partial_parts = []
        r = ""
        while True:
            if not self.is_recording:
                print(r)
                _access_token = get_access_token(ai_token.token)
                print(parse_command(r, _access_token)["choices"][0]["message"]["content"])
                break
            data = stream.read(CHUNK)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                r += " " + result["text"]
                self.label.text = result["text"]
                partial_parts = []
            else:
                partial = json.loads(recognizer.PartialResult())
                partial_parts.append(partial)

            # final_result = json.loads(recognizer.FinalResult())
            # results.append(final_result.get("text", ""))
            # print(results, flush=True)
            # for i in range(0, int(RT / CHUNK * REC_SEC)):
            #     data = stream.read(CHUNK)
            #     self.frames.append(data)

    def on_spinner_select(self, spinner, text):
        self.current_export_format = text
        self.export_button.disabled = self.is_export_button_disabled()

    def export_btn_click(self):
        if self.is_export_button_disabled():
            return

        if self.current_export_format == EXPORT_XLS:
            file_path = f'{self.export_file_input.text}.xlsx'
            table.to_excel(file_path, sheet_name='Sheet1', index=False)
        if self.current_export_format == EXPORT_CSV:
            table.to_csv(f'{self.export_file_input.text}.csv', index=False)

    def changed_export_file_text(self, window, text):
        self.export_button.disabled = self.is_export_button_disabled()

    def is_export_button_disabled(self):
        return self.is_export_type_empty() or self.is_export_file_name_empty()

    def is_export_file_name_empty(self):
        return self.export_file_input.text == '' or self.export_file_input.text is None

    def is_export_type_empty(self):
        return self.current_export_format is None


if __name__ == '__main__':
    MyApp().run()

# CHUNK = 1024 # определяет форму ауди сигнала
# FRT = pyaudio.paInt16 # шестнадцатибитный формат задает значение амплитуды
# CHAN = 1 # канал записи звука
# RT = 44100 # частота
# REC_SEC = 3 #длина записи
#
# p = pyaudio.PyAudio()
# stream = p.open(format=FRT,channels=CHAN,rate=RT,input=True,frames_per_buffer=CHUNK) # открываем поток для записи
# print("rec")
# frames = []  # формируем выборку данных фреймов
# while True:
#     for i in range(0, int(RT / CHUNK * REC_SEC)):
#         data = stream.read(CHUNK)
#         frames.append(data)
#
#     print('stop')
#     command = input()
#     if command == 'q':
#         break
#
# print("done")
#
# stream.stop_stream()  # останавливаем и закрываем поток
# stream.close()
# p.terminate()
#
# w = wave.open("output.wav", 'wb')
# w.setnchannels(CHAN)
# w.setsampwidth(p.get_sample_size(FRT))
# w.setframerate(RT)
# w.writeframes(b''.join(frames))
# w.close()