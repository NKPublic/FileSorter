
#os useful for interacting with operating system
import os
#shutil adds ability to move/copy files
import shutil
#GUI toolkit
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

#class for sorting logic
class FileSorter:
    def __init__(self, source_path, dest_paths, sort_params, include_subfolders=False):
        #path for folder to be sorted
        self.source_path = source_path
        #dict mapping sorting rules to destination folder
        self.dest_paths = dest_paths  
        #list of sorting params
        self.sort_params = sort_params
        #subfolders included or not
        self.include_subfolders = include_subfolders
    #main method to sort files
    def sort_files(self):
        #verify path is valid, if not, throw error
        if not os.path.isdir(self.source_path):
            raise NotADirectoryError("Invalid source directory.")
        #if user wants to include subfolders
        if self.include_subfolders:
            #walk through all folders and subfolders
            for root, _, files in os.walk(self.source_path):
                #loop through all files in the current directory
                for filename in files:
                    #create the full path to the file
                    file_path = os.path.join(root, filename)
                    #sort this file
                    self.sort_file(file_path, filename)
        #otherwise, only sort top-level files
        else:
            #list items in the source folder
            for filename in os.listdir(self.source_path):
                #create full file path
                file_path = os.path.join(self.source_path, filename)
                #make sure it's a file and not a folder
                if os.path.isfile(file_path):
                    #sort the file
                    self.sort_file(file_path, filename)
    def sort_file(self, file_path, filename):
        #extract file extension for use in sorting
        file_ext = os.path.splitext(filename)[1].lower()
        #gets file size in bits for use in sorting
        file_size = os.path.getsize(file_path)
        #loop through each user defined rule
        for param, dest_folder in self.dest_paths.items():
            #if parameter starts with a . then it is a file size rule, check file against param
            if param.startswith('.') and filename.endswith(param):  
                #move file
                shutil.move(file_path, os.path.join(dest_folder, filename))
                return
            #else if, starts with size< then it is a size rule, parse rule to split parameter int and compare, and finds files smaller than given threshold
            elif param.startswith('size<') and file_size < int(param.split('<')[1]):
                #move file
                shutil.move(file_path, os.path.join(dest_folder, filename))
                return
            #finds file larger than threshold 
            elif param.startswith('size>') and file_size > int(param.split('>')[1]):
                #move file
                shutil.move(file_path, os.path.join(dest_folder, filename))
                return
            #checks file name against rule
            elif param.lower() in filename.lower():  
                #move file
                shutil.move(file_path, os.path.join(dest_folder, filename))
                return
#class to build and handle gui
class FileSorterGUI:
    def __init__(self, master):
        #reference to the main window application
        self.master = master
        #title of the GUI window
        self.master.title("File Sorter")
        #variable to hold the path to be sorted
        self.source_path = tk.StringVar()
        #dictionary to hold sorting rules
        self.sorting_rules = {}
        #tkinter boolean to track if subfolders should be included
        self.include_subfolders = tk.BooleanVar()
        #builds ui
        self.build_gui()
    #construct layout
    def build_gui(self):
        #create frame with padding of 10
        frame = ttk.Frame(self.master, padding=10)
        #places it within window grid
        frame.grid(row=0, column=0, sticky='nsew')
        #label for source folder
        ttk.Label(frame, text="Source Folder:").grid(row=0, column=0, sticky='w')
        #entry box for source path
        entry_source = ttk.Entry(frame, textvariable=self.source_path, width=50)
        #place entry on grid
        entry_source.grid(row=0, column=1, padx=5)
        #button to browse folder
        ttk.Button(frame, text="Browse", command=self.browse_source).grid(row=0, column=2)
        #list box to display added rules
        self.rule_list = tk.Listbox(frame, height=5, width=75)
        #position box in gui
        self.rule_list.grid(row=1, column=0, columnspan=3, pady=5)
        #add rule button
        ttk.Button(frame, text="Add Rule", command=self.add_rule).grid(row=2, column=0, pady=5)
        #run sorting button
        ttk.Button(frame, text="Sort Files", command=self.run_sorter).grid(row=2, column=2)
        #adds checkbox to GUI for subfoldes
        ttk.Checkbutton(frame, text="Include Subfolders", variable=self.include_subfolders).grid(row=3, column=0, columnspan=3, sticky='w')
    #allows user to select a source directory
    def browse_source(self):
        #open folder selection dialog
        path = filedialog.askdirectory()
        if path:
            #set selected path to the variable
            self.source_path.set(path)
    #create a new window to add sorting rules
    def add_rule(self):
        #creates new popup window
        rule_window = tk.Toplevel(self.master)
        #Title of rule window
        rule_window.title("Add Sorting Rule")
        #holds the rule params
        param = tk.StringVar()
        #holds the destination path
        dest = tk.StringVar()
        #label for params with list of possible entires for user
        ttk.Label(rule_window, text="Parameter (.[extension], </>[size], [file name]):").grid(row=0, column=0, padx=5, pady=5)
        #entry for param input
        ttk.Entry(rule_window, textvariable=param).grid(row=0, column=1, padx=5)
        #label for destination folder
        ttk.Label(rule_window, text="Destination Folder:").grid(row=1, column=0, padx=5)
        #entry for destination path
        ttk.Entry(rule_window, textvariable=dest).grid(row=1, column=1, padx=5)
        #button to browse destination
        ttk.Button(rule_window, text="Browse", command=lambda: self.browse_dest(dest)).grid(row=1, column=2)
        #add the rule to the GUI list and internal dict
        def add():
            #add rule to dict
            self.sorting_rules[param.get()] = dest.get()
            #display rule in list box
            self.rule_list.insert(tk.END, f"{param.get()} -> {dest.get()}")
            #close the popup window after rule is added
            rule_window.destroy()
        #add button
        ttk.Button(rule_window, text="Add", command=add).grid(row=2, column=1, pady=10)
    #allow user to browse for destination folder
    def browse_dest(self, dest_var):
        #open folder selection dialog
        path = filedialog.askdirectory()
        if path:
            #set selected path to variable
            dest_var.set(path)
    #run the file sorting logic given user rules
    def run_sorter(self):
        try:
            #initialize sorter object
            sorter = FileSorter(self.source_path.get(), self.sorting_rules, list(self.sorting_rules.keys()), self.include_subfolders.get())
            #execute sorting
            sorter.sort_files()
            #notify user of success
            messagebox.showinfo("Success", "Files sorted successfully!")
        except Exception as e:
            #gives error box if issue found
            messagebox.showerror("Error", str(e))
#main box to start GUI app
if __name__ == '__main__':
    #create root window
    root = tk.Tk()
    #create app obj
    app = FileSorterGUI(root)
    #start the main event loop
    root.mainloop()
