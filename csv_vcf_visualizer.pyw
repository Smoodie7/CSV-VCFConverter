import tkinter as tk
from tkinter import filedialog
import csv
from threading import Thread
from tkinter.ttk import Progressbar
import chardet

VERSION = 'v0.0.1a'

class FileViewer:
    def __init__(self):
        self.file_path = None
        self.file_data = None
        self.file_type = None

        self.window = tk.Tk()
        self.window.title(f"CSV/VCF Viewer {VERSION}")
        self.window.geometry("600x400")

        self.select_button = tk.Button(self.window, text="Select File", command=self.select_file)
        self.select_button.pack(pady=10)

        self.content_text = tk.Text(self.window, height=20, width=80)
        self.content_text.pack()

        self.prev_button = tk.Button(self.window, text="Previous", command=self.show_previous)
        self.prev_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.next_button = tk.Button(self.window, text="Next", command=self.show_next)
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.loading_bar = Progressbar(self.window, mode="indeterminate")

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("VCF Files", "*.vcf")])
        if self.file_path:
            self.load_file()

    def load_file(self):
        encoding = self.detect_encoding()
        if self.file_path.endswith(".csv"):
            self.file_type = "csv"
            thread = Thread(target=self.load_csv, args=(encoding,))
        elif self.file_path.endswith(".vcf"):
            self.file_type = "vcf"
            thread = Thread(target=self.load_vcf, args=(encoding,))
        else:
            raise IOError("Invalid file selected.")
        thread.start()
        self.loading_bar.start()
        self.window.after(10, self.check_thread, thread)

    def load_csv(self, encoding):
        data = []
        with open(self.file_path, "r", encoding=encoding) as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
        self.file_data = data
        self.display_data(0)

    def load_vcf(self, encoding):
        data = []
        with open(self.file_path, "rb") as file:
            try:
                lines = file.readlines()
                entry = []
                for line in lines:
                    if line.startswith(b"BEGIN:VCARD"):
                        if entry:
                            data.append(entry)
                            entry = []
                    entry.append(line.decode(encoding).strip())
                if entry:
                    data.append(entry)
            except UnicodeDecodeError:
                # Failed to decode with specified encoding, try other encodings
                ENCODINGS = ['utf-8', 'utf-16', 'latin-1', 'utf-8-sig', 'utf-16-le', 'utf-16-be', 'utf-32',
                 'utf-32-le', 'utf-32-be', 'ISO-8859-1', 'GBK', 'Windows-1251', 'ANSI', 'Big5',
                 'EUC-JP', 'Windows-1254', 'ASCII', 'UTF-7', 'UTF-16-LE-BOM', 'UTF-16-BE-BOM',
                 'UTF-32-LE-BOM', 'UTF-32-BE-BOM', 'Shift_JIS', 'EUC-KR', 'ISO-8859-2', 'ISO-8859-15',
                 'Windows-1252', 'Windows-1256', 'ISO-8859-9', 'KOI8-R']
                for alt_encoding in encodings:
                    if alt_encoding != encoding:
                        try:
                            file.seek(0)  # Reset file pointer
                            lines = file.readlines()
                            entry = []
                            for line in lines:
                                if line.startswith(b"BEGIN:VCARD"):
                                    if entry:
                                        data.append(entry)
                                        entry = []
                                entry.append(line.decode(alt_encoding).strip())
                            if entry:
                                data.append(entry)
                            break  # Successful decoding, exit the loop
                        except UnicodeDecodeError:
                            continue  # Try next encoding
                else:
                    # Failed to decode with all encodings
                    raise IOError("Failed to decode the VCF file with any available encoding.")
        self.file_data = data
        self.display_data(0)


    def display_data(self, index):
        self.content_text.delete("1.0", tk.END)
        if self.file_type == "csv":
            data_row = self.file_data[index]
            for row in data_row:
                self.content_text.insert(tk.END, f"{row}\n")
        elif self.file_type == "vcf":
            data_entry = self.file_data[index]
            for line in data_entry:
                self.content_text.insert(tk.END, f"{line}\n")

    def show_previous(self):
        if self.file_data:
            current_index = self.file_data.index(self.content_text.get("1.0", tk.END).strip().split("\n"))
            previous_index = max(current_index - 1, 0)
            self.display_data(previous_index)

    def show_next(self):
        if self.file_data:
            current_index = self.file_data.index(self.content_text.get("1.0", tk.END).strip().split("\n"))
            next_index = min(current_index + 1, len(self.file_data) - 1)
            self.display_data(next_index)

    def check_thread(self, thread):
        if thread.is_alive():
            self.window.after(10, self.check_thread, thread)
        else:
            self.loading_bar.stop()

    def detect_encoding(self):
        with open(self.file_path, 'rb') as file:
            raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        return encoding

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    file_viewer = FileViewer()
    file_viewer.run()
