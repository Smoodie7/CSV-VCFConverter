import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import os


# Constants
ENCODINGS = ['utf-8', 'latin-1', 'utf-16', 'utf-32', 'utf-8-sig', 'utf-16-le', 'utf-16-be',
             'utf-32-le', 'utf-32-be', 'ISO-8859-1', 'GBK', 'Windows-1251', 'ANSI', 'Big5',
             'EUC-JP', 'Windows-1254', 'ASCII']


# --------- BROWSE FUNCTIONS ---------


# Function to browse and select the input file
def browse_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("VCF Files", "*.vcf")])
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(tk.END, file_path)


# Function to browse and select the output destination folder
def browse_output_destination():
    folder_path = filedialog.askdirectory()
    output_destination_entry.delete(0, tk.END)
    output_destination_entry.insert(tk.END, folder_path)


# --------- CONVERT FUNCTIONS ---------


# General/Main function
def convert_file():
    # Logs enabling
    if log_checkbox_var.get():
        # If the log checkbox is checked, enable logging with the specified format and level
        logging.basicConfig(filename='logs.txt', level=logging.INFO, filemode='w',
                            format='%(asctime)s - %(levelname)s - %(message)s')

    input_file = input_file_entry.get()
    output_destination = output_destination_entry.get()

    if not input_file:
        messagebox.showerror("Error", "Please select an input file.")
        return

    if not output_destination:
        messagebox.showerror("Error", "Please select an output destination.")
        return

    if not os.path.isdir(output_destination) or not output_destination:
        messagebox.showerror("Error", "Invalid output destination.")
        return

    input_extension = input_file.split(".")[-1]
    output_format = "vcf" if input_extension.lower() == "csv" else "csv"

    try:
        encoding = detect_encoding(input_file)
        if output_format == "csv":
            output_file = get_output_file_path(output_destination, input_file, "csv")
            convert_vcf_to_csv(input_file, output_file, encoding)
            logging.info(f"Converted VCF to CSV: {input_file} -> {output_file}")
        else:
            output_file = get_output_file_path(output_destination, input_file, "vcf")
            convert_csv_to_vcf(input_file, output_file, encoding)
            logging.info(f"Converted CSV to VCF: {input_file} -> {output_file}")

        messagebox.showinfo("Conversion Completed", "Conversion was successful.")
    except Exception as e:
        logging.error(f"Conversion Error: {str(e)}")
        messagebox.showerror("Error", str(e))


# Function to generate the output file path and handle naming conflicts
def get_output_file_path(output_destination, input_file, output_format):
    base_name = os.path.basename(input_file)
    file_name = os.path.splitext(base_name)[0]
    output_file = f"{output_destination}/{file_name}.{output_format}"
    counter = 1

    while os.path.exists(output_file):
        # If a file with the same name exists, append a counter to the filename
        output_file = f"{output_destination}/{file_name}_{counter}.{output_format}"
        counter += 1

    return output_file


# Function to convert VCF file to CSV file
def convert_vcf_to_csv(vcf_file, csv_file, encoding):
    with open(vcf_file, 'r', encoding=encoding) as file:
        vcard_list = []
        vcard = {}

        for line in file:
            if line.startswith("BEGIN:VCARD"):
                vcard = {}
            elif line.startswith("END:VCARD"):
                vcard_list.append(vcard)
            else:
                key, value = line.strip().split(":", 1)
                vcard[key] = value

    if vcard_list:
        with open(csv_file, 'w', newline='', encoding=encoding) as file:
            writer = csv.DictWriter(file, fieldnames=vcard_list[0].keys())
            writer.writeheader()
            writer.writerows(vcard_list)


# Function to convert CSV file to VCF file
def convert_csv_to_vcf(csv_file, vcf_file, encoding):
    with open(csv_file, 'r', encoding=encoding) as file:
        reader = csv.DictReader(file)
        vcard_list = list(reader)

    if vcard_list:
        with open(vcf_file, 'w', encoding=encoding) as file:
            for vcard in vcard_list:
                file.write("BEGIN:VCARD\n")
                for key, value in vcard.items():
                    file.write(f"{key}:{value}\n")
                file.write("END:VCARD\n")


# Function to detect the encoding of a file
def detect_encoding(file_path):
    for encoding in ENCODINGS:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                file.read()
            return encoding
        except UnicodeDecodeError:
            continue
        except Exception:
            break

    # Encoding not detected, prompt the user for encoding
    ask_encoding_window = tk.Tk()
    ask_encoding_window.title("Encoding not recognized!")

    encoding = None

    def submit_encoding():
        nonlocal encoding
        encoding = entry.get()
        ask_encoding_window.destroy()

    label = tk.Label(ask_encoding_window, text="Enter the encoding for the file:")
    label.pack()

    entry = tk.Entry(ask_encoding_window)
    entry.pack()

    submit_button = tk.Button(ask_encoding_window, text="Submit", command=submit_encoding)
    submit_button.pack()

    ask_encoding_window.mainloop()

    return encoding


# --------- GUI ---------


# User Interface
root = tk.Tk()
root.title("CSV/VCF Conversion")

# Interface Elements
input_file_label = tk.Label(root, text="Input File:")
input_file_entry = tk.Entry(root, width=40)
input_file_browse_btn = tk.Button(root, text="Browse", command=browse_input_file)

output_destination_label = tk.Label(root, text="Output Destination:")
output_destination_entry = tk.Entry(root, width=40)
output_destination_browse_btn = tk.Button(root, text="Browse", command=browse_output_destination)

log_checkbox_var = tk.IntVar()
log_checkbox = tk.Checkbutton(root, text="Enable Logs", variable=log_checkbox_var)

convert_btn = tk.Button(root, text="Convert", command=convert_file)

# Placing elements in the window
input_file_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
input_file_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
input_file_browse_btn.grid(row=0, column=3, padx=5, pady=5)

output_destination_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
output_destination_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
output_destination_browse_btn.grid(row=1, column=3, padx=5, pady=5)

log_checkbox.grid(row=2, column=0, columnspan=2, padx=6, pady=10)

convert_btn.grid(row=2, column=0, columnspan=4, padx=6, pady=10)

root.mainloop()
