import tkinter as tk
from tkinter import filedialog, messagebox
import csv
from threading import Thread, Lock
from tkinter.ttk import Progressbar
import chardet

VERSION = 'v0.0.2a'

class FileViewer:
    def __init__(self):
        self.file_path = None
        self.file_data = None
        self.file_type = None
        self.current_index = 0
        self.load_lock = Lock()

        self.window = tk.Tk()
        self.window.title(f"CSV/VCF Viewer {VERSION}")
        self.window.geometry("600x400")

        self.select_button = tk.Button(self.window, text="Select File", command=self.select_file)
        self.select_button.pack(pady=10)

        self.content_text = tk.Text(self.window, height=20, width=80)
        self.content_text.pack()

        self.prev_button = tk.Button(self.window, text="Previous", command=self.show_previous, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.next_button = tk.Button(self.window, text="Next", command=self.show_next, state=tk.DISABLED)
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.loading_bar = Progressbar(self.window, mode="indeterminate")
        self.loading_bar.pack()

    def select_file(self):
        if self.load_lock.locked():
            messagebox.showinfo("Wait", "Please wait until the current file has finished loading.")
            return
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("VCF Files", "*.vcf")])
        if self.file_path:
            self.load_file()

    def detect_encoding(file_path):
        encodings = ['utf8', 'iso-8859-1', 'iso-8859-2', 'iso-8859-15', 'cp437', 'cp850', 'cp852', 'cp855', 
                 'cp857', 'cp860', 'cp861', 'cp862', 'cp863', 'cp865', 'cp866', 'cp869', 'cp874', 
                 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258']

        for encoding in encodings:
            try:
                file = open(file_path, encoding=encoding)
                file.readlines()
                file.seek(0)
            except:
                pass
            else:
                return encoding
        raise UnicodeDecodeError('None of the provided encodings could decode the file.')


    def load_file(self):
        encoding = self.detect_encoding()
        self.loading_bar.start()
        self.load_lock.acquire()
        self.current_index = 0
        if self.file_path.endswith(".csv"):
            self.file_type = "csv"
            thread = Thread(target=self.load_csv, args=(encoding,))
        elif self.file_path.endswith(".vcf"):
            self.file_type = "vcf"
            thread = Thread(target=self.load_vcf, args=(encoding,))
        else:
            raise IOError("Invalid file selected.")
        thread.start()
        self.window.after(10, self.check_thread, thread)

    # Rest of the code remains same.

    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_data(self.current_index)

    def show_next(self):
        if self.current_index < len(self.file_data) - 1:
            self.current_index += 1
            self.display_data(self.current_index)

    def check_thread(self, thread):
        if thread.is_alive():
            self.window.after(10, self.check_thread, thread)
        else:
            self.loading_bar.stop()
            self.load_lock.release()
            self.prev_button['state'] = tk.NORMAL
            self.next_button['state'] = tk.NORMAL

if __name__ == "__main__":
    file_viewer = FileViewer()
    file_viewer.run()
