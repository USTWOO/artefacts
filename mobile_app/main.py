from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.utils import platform
from plyer import camera
from kivy.clock import Clock
import os
from datetime import datetime

# Import our logic
from ocr import perform_ocr
from processor import extract_info
from database import save_receipt, get_receipts, get_monthly_stats, get_category_stats

Builder.load_string('''
<RootScreenManager>:
    ScanScreen:
    HistoryScreen:
    StatsScreen:

<ScanScreen>:
    name: 'scan'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10

        Label:
            text: 'Receipt Scanner'
            font_size: 24
            size_hint_y: None
            height: 50

        Button:
            text: '📷 Take Photo'
            size_hint_y: None
            height: 60
            on_press: root.take_photo()

        ScrollView:
            BoxLayout:
                id: edit_form
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
                padding: [0, 10]
                opacity: 0
                disabled: True

                Image:
                    id: img_preview
                    size_hint_y: None
                    height: 200

                Label:
                    text: 'Vendor:'
                    size_hint_y: None
                    height: 30
                    halign: 'left'
                TextInput:
                    id: vendor
                    size_hint_y: None
                    height: 40
                    multiline: False

                Label:
                    text: 'Date:'
                    size_hint_y: None
                    height: 30
                TextInput:
                    id: date
                    size_hint_y: None
                    height: 40
                    multiline: False

                Label:
                    text: 'Subtotal:'
                    size_hint_y: None
                    height: 30
                TextInput:
                    id: subtotal
                    size_hint_y: None
                    height: 40
                    input_filter: 'float'

                Label:
                    text: 'VAT:'
                    size_hint_y: None
                    height: 30
                TextInput:
                    id: vat
                    size_hint_y: None
                    height: 40
                    input_filter: 'float'

                Label:
                    text: 'Total:'
                    size_hint_y: None
                    height: 30
                TextInput:
                    id: total
                    size_hint_y: None
                    height: 40
                    input_filter: 'float'

                Label:
                    text: 'Category:'
                    size_hint_y: None
                    height: 30
                Spinner:
                    id: category
                    text: 'Miscellaneous'
                    values: ('Food', 'Travel', 'Fuel', 'Entertainment', 'Supplies', 'Utilities', 'Miscellaneous')
                    size_hint_y: None
                    height: 40

                BoxLayout:
                    size_hint_y: None
                    height: 50
                    spacing: 10
                    Button:
                        text: 'Save'
                        background_color: [0, 1, 0, 1]
                        on_press: root.save_data()
                    Button:
                        text: 'Cancel'
                        background_color: [1, 0, 0, 1]
                        on_press: root.reset_form()

        BoxLayout:
            size_hint_y: None
            height: 60
            spacing: 5
            Button:
                text: 'Scan'
                on_press: root.manager.current = 'scan'
            Button:
                text: 'History'
                on_press: root.manager.current = 'history'
            Button:
                text: 'Stats'
                on_press: root.manager.current = 'stats'

<HistoryScreen>:
    name: 'history'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        Label:
            text: 'History'
            font_size: 24
            size_hint_y: None
            height: 50
        ScrollView:
            BoxLayout:
                id: history_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
        Button:
            text: '📊 Export to Excel'
            size_hint_y: None
            height: 50
            on_press: root.export_excel()
        BoxLayout:
            size_hint_y: None
            height: 60
            spacing: 5
            Button:
                text: 'Scan'
                on_press: root.manager.current = 'scan'
            Button:
                text: 'History'
                on_press: root.manager.current = 'history'
            Button:
                text: 'Stats'
                on_press: root.manager.current = 'stats'

<StatsScreen>:
    name: 'stats'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        Label:
            text: 'Statistics'
            font_size: 24
            size_hint_y: None
            height: 50
        ScrollView:
            BoxLayout:
                id: stats_content
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
        BoxLayout:
            size_hint_y: None
            height: 60
            spacing: 5
            Button:
                text: 'Scan'
                on_press: root.manager.current = 'scan'
            Button:
                text: 'History'
                on_press: root.manager.current = 'history'
            Button:
                text: 'Stats'
                on_press: root.manager.current = 'stats'
''')

class ScanScreen(Screen):
    def take_photo(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_path = os.path.join(App.get_running_app().user_data_dir, f"receipt_{timestamp}.jpg")
        try:
            camera.take_picture(filename=self.temp_path, on_complete=self.on_camera_complete)
        except NotImplementedError:
            # Fallback for desktop testing
            self.on_camera_complete(self.temp_path)

    def on_camera_complete(self, filename):
        if not os.path.exists(filename):
            return

        # Show form
        self.ids.edit_form.opacity = 1
        self.ids.edit_form.disabled = False
        self.ids.img_preview.source = filename

        # OCR
        with open(filename, 'rb') as f:
            image_bytes = f.read()
            text = perform_ocr(image_bytes)
            data = extract_info(text)

            self.ids.vendor.text = data.get('vendor', 'Unknown')
            self.ids.date.text = data.get('date', 'Unknown')
            self.ids.subtotal.text = str(data.get('amount', 0.0))
            self.ids.vat.text = str(data.get('vat', 0.0))
            self.ids.total.text = str(data.get('total', 0.0))
            self.ids.category.text = data.get('category', 'Miscellaneous')

    def save_data(self):
        data = {
            "vendor": self.ids.vendor.text,
            "date": self.ids.date.text,
            "subtotal": float(self.ids.subtotal.text or 0),
            "vat": float(self.ids.vat.text or 0),
            "total": float(self.ids.total.text or 0),
            "category": self.ids.category.text,
            "image_path": self.temp_path
        }
        save_receipt(data)
        self.reset_form()
        App.get_running_app().root.get_screen('history').refresh_history()

    def reset_form(self):
        self.ids.edit_form.opacity = 0
        self.ids.edit_form.disabled = True
        self.ids.vendor.text = ""
        self.ids.date.text = ""
        self.ids.subtotal.text = ""
        self.ids.vat.text = ""
        self.ids.total.text = ""
        self.ids.category.text = 'Miscellaneous'

class HistoryScreen(Screen):
    def on_enter(self):
        self.refresh_history()

    def refresh_history(self):
        self.ids.history_list.clear_widgets()
        receipts = get_receipts()
        for r in receipts:
            lbl = Builder.load_string(f'''
BoxLayout:
    orientation: 'horizontal'
    size_hint_y: None
    height: 60
    padding: 5
    canvas.before:
        Color:
            rgba: 1, 1, 1, 0.1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: "{r['vendor']}"
            bold: True
            halign: 'left'
        Label:
            text: "{r['date']} - {r['category']}"
            font_size: 12
    Label:
        text: "${r['total']:.2f}"
        color: [0, 1, 0, 1]
''')
            self.ids.history_list.add_widget(lbl)

    def export_excel(self):
        import pandas as pd
        receipts = get_receipts()
        if receipts:
            df = pd.DataFrame(receipts)
            path = os.path.join(App.get_running_app().user_data_dir, "receipts.xlsx")
            df.to_excel(path, index=False)
            print(f"Exported to {path}")

class StatsScreen(Screen):
    def on_enter(self):
        self.refresh_stats()

    def refresh_stats(self):
        self.ids.stats_content.clear_widgets()

        # Monthly
        self.ids.stats_content.add_widget(Builder.load_string("Label: text: 'Monthly Summary'; bold: True; height: 30; size_hint_y: None"))
        m_stats = get_monthly_stats()
        for s in m_stats:
            self.ids.stats_content.add_widget(Builder.load_string(f"Label: text: '{s['month']}: ${s['total_expense']:.2f} (VAT: ${s['total_vat']:.2f})'; height: 30; size_hint_y: None"))

        # Category
        self.ids.stats_content.add_widget(Builder.load_string("Label: text: 'Category Summary'; bold: True; height: 30; size_hint_y: None; padding: [0, 20, 0, 0]"))
        c_stats = get_category_stats()
        for s in c_stats:
            self.ids.stats_content.add_widget(Builder.load_string(f"Label: text: '{s['category']}: ${s['total_expense']:.2f}'; height: 30; size_hint_y: None"))

class RootScreenManager(ScreenManager):
    pass

class ReceiptScannerApp(App):
    def build(self):
        return RootScreenManager()

if __name__ == '__main__':
    ReceiptScannerApp().run()
