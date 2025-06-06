import pyaudio
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
import threading
import vosk
import json
import pandas as pd
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
import ai_token
from text_to_command import *

from run_commands import run_commands
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


vosk_model = vosk.Model(model_path=MODEL_PATH)
p = pyaudio.PyAudio()
recognizer = vosk.KaldiRecognizer(vosk_model, RT)


def get_data_table(dataframe):
    column_data = [str(col) for col in dataframe.columns]  # Принудительно превращаем в строки
    row_data = dataframe.to_records(index=False).tolist()  # Преобразуем в список списков
    return column_data, row_data

class JarvisApp (MDApp):
    def build(self):
        #Window.clearcolor = (0.4, 0.56, 0.68, 1)
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

        self.label = Label(bold=True)
        self.label.size_hint = (None, None)
        self.label.size = (200, 100)
        self.label.max_lines = 1
        self.label.font_size = 28
        self.label.color = (0,0,0,1)

        self.anchor_layout_table = AnchorLayout()
        self.anchor_layout_table.anchor_x = 'center'
        self.anchor_layout_table.anchor_y = 'top'
        self.anchor_layout_table.size_hint_y = 0.6
        self.anchor_layout_table.padding = 15
        try:
            self.table
        except:
            self.table = pd.DataFrame([[1,2,3,4,5], [6,7,8,9,10], [11,12,13,14,15],[1,2,3,4,'dsfsvsdvsdvdsv'], [6,7,8,9,10], [11,12,13,14,15],[1,2,3,4,5], [6,7,8,9,10], [11,12,13,14,15],[1,2,3,4,5], [6,7,8,9,10], [11,12,13,14,15]], columns=['Марка стали', 'Размер', 'Тип изделия', 'Заказчик', 'Срок'])
        column_data, row_data = get_data_table(self.table)
        column_data = [(x, dp(len(x) * 2 + 6)) for x in column_data]

        self.table_view = MDDataTable(
            column_data=column_data,
            row_data=row_data,
            rows_num=1000)
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
        self.spinner.background_color = (0.4, 0.56, 0.68, 1)
        self.spinner.bind(text=self.on_spinner_select)

        self.export_file_input = TextInput(
            hint_text='Название файла экспорта',
            multiline=False,
            size_hint=(1, None),
            height=50,
            halign='center',
            text='output',
            font_size=20
        )
        self.export_file_input.background_color = (0.95, 0.95, 0.95, 1)
        self.export_file_input.bind(text=self.changed_export_file_text)

        self.export_button = Button(text='Экспорт')
        self.export_button.size_hint = (None, None)
        self.export_button.size = (150, 50)
        self.export_button.disabled = self.export_disabled
        self.export_button.font_size = 20
        self.export_button.background_color = (0.4, 0.56, 0.68, 1)
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

    def update_table_in_main_thread(self, dt):
        column_data, row_data = get_data_table(self.table)
        column_data = [(x, dp(len(x) * 2 + 2)) for x in column_data]

        self.table_view = MDDataTable(
            column_data=column_data,
            row_data=row_data)
        self.table_view.size_hint_x = 1

        self.anchor_layout_table.clear_widgets()
        self.anchor_layout_table.add_widget(self.table_view)
        
    def listen_info_task(self):
        stream = p.open(format=FRT,channels=CHAN,rate=RT,input=True,frames_per_buffer=CHUNK) # открываем поток для записи
        partial_parts = []
        r = ""
        while True:
            if not self.is_recording:
                print(r)
                _access_token = get_access_token(ai_token.token)
                raw_commands = parse_command(r, _access_token)["choices"][0]["message"]["content"]
                raw_commands = raw_commands.replace("```", "").replace("json", "")
                commands = json.loads(raw_commands)
                
                print(commands)
                if not type(commands) is list:
                    commands = [commands]
                print(commands)
                
                #commands = json.loads('[{"command": "create_table", "args": {"x": 10, "y": 15}}]')
                
                table = run_commands(commands, self.table)
                self.table = table
                Clock.schedule_once(self.update_table_in_main_thread, 0)
                r = ""
                partial_parts = []
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

    def on_spinner_select(self, spinner, text):
        self.current_export_format = text
        self.export_button.disabled = self.is_export_button_disabled()

    def export_btn_click(self):
        if self.is_export_button_disabled():
            return

        if self.current_export_format == EXPORT_XLS:
            file_path = f'{self.export_file_input.text}.xlsx'
            self.table.to_excel(file_path, sheet_name='Sheet1', index=False)
        if self.current_export_format == EXPORT_CSV:
            self.table.to_csv(f'{self.export_file_input.text}.csv', index=False)

    def changed_export_file_text(self, window, text):
        self.export_button.disabled = self.is_export_button_disabled()

    def is_export_button_disabled(self):
        return self.is_export_type_empty() or self.is_export_file_name_empty()

    def is_export_file_name_empty(self):
        return self.export_file_input.text == '' or self.export_file_input.text is None

    def is_export_type_empty(self):
        return self.current_export_format is None

if __name__ == '__main__':
    JarvisApp().run()