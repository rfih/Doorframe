import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from PIL import Image, ImageTk, ImageDraw, ImageFont
import math

try:
    import PIL._tkinter_finder
except ImportError:
    pass

# Determine the path to the JSON files
if getattr(os, 'frozen', False):
    application_path = os.path.expanduser(sys.executable)
else:
    application_path = os.path.dirname(__file__)

LOCK_FILE = os.path.join(application_path, 'electric_locks.json')
TRANSLATIONS_FILE = os.path.join(application_path, 'translations.json')
BOXLOCK_FILE = os.path.join(application_path, 'box_locks.json')
CONCEALED_FILE = os.path.join(application_path, 'concealeds.json')


# Load electric lock types from file
def load_electric_locks():
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# Save electric lock types to file
def save_electric_locks(electric_locks):
    with open(LOCK_FILE, 'w', encoding='utf-8') as file:
        json.dump(electric_locks, file, ensure_ascii=False, indent=4)
        
# Load box lock types from file
def load_box_locks():
    if os.path.exists(BOXLOCK_FILE):
        with open(BOXLOCK_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# Save box lock types to file
def save_box_locks(box_locks):
    with open(BOXLOCK_FILE, 'w', encoding='utf-8') as file:
        json.dump(box_locks, file, ensure_ascii=False, indent=4)
        
# Load box lock types from file
def load_concealed_door():
    if os.path.exists(CONCEALED_FILE):
        with open(CONCEALED_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# Save box lock types to file
def save_concealed_door(concealeds):
    with open(CONCEALED_FILE, 'w', encoding='utf-8') as file:
        json.dump(concealeds, file, ensure_ascii=False, indent=4)

# Load translations from file
def load_translations():
    if os.path.exists(TRANSLATIONS_FILE):
        with open(TRANSLATIONS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# Initialize electric locks and translations
electric_locks = load_electric_locks()
translations = load_translations()
box_locks = load_box_locks()
concealeds = load_concealed_door()

class ToolTip:
    def __init__(self, widget, text, calculator):
        self.widget = widget
        self.text = text
        self.calculator = calculator  # Reference to DoorFrameCalculator for checking tooltip status
        self.tip_window = None
        self.tooltip = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        # Only show the tooltip if tooltips are enabled
        if self.calculator.tooltips_enabled.get():
            self.tip_window = tk.Toplevel(self.widget)
            self.tip_window.wm_overrideredirect(True)
            label = tk.Label(self.tip_window, text=self.text, font=("Helvetica", 13),  background="#ffffe0", borderwidth=1)
            label.pack()
            x, y = event.x_root + 10, event.y_root + 10
            self.tip_window.geometry(f"+{x}+{y}")
        pass

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
        pass
            
    def update_text(self, new_text):
        self.text = new_text

class DoorFrameCalculator:
    def __init__(self, root):
        self.root = root
        self.root.geometry("950x775")
        self.current_language = "zh"
        self.entries = {}
            
        # Create a canvas and a scrollbar for the entire application
        self.canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        
        self.tooltips_enabled = tk.BooleanVar(value=False)

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind the scroll region configuration to the scrollable frame's size changes
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Initialize translated door type labels
        self.simple_label = translations[self.current_language]["simple"].lower()
        self.electric_lock_label = translations[self.current_language]["electric lock"].lower()
        self.ub_label = translations[self.current_language]["UB"].lower()
        self.box_lock_label = translations[self.current_language]["box lock"].lower()
        self.yipaiyikong_label = translations[self.current_language]["yipaiyikong"].lower()
        self.top_label = translations[self.current_language]["top"].lower()
        self.bottom_label = translations[self.current_language]["bottom"].lower()
        self.concealed_label = translations[self.current_language]["concealed door closer"].lower()
        
        self.tooltips = {}
        
        self.guidance_images_simple = {
            "en": os.path.join(application_path, 'simple_english.png'),
            "zh": os.path.join(application_path, 'simple_mandarin.png'),
            "id": os.path.join(application_path, 'simple_indo.png')
        }
        
        self.guidance_images_ub = {
            "en": os.path.join(application_path, 'ub_english.png'),
            "zh": os.path.join(application_path, 'ub_mandarin.png'),
            "id": os.path.join(application_path, 'ub_indo.png')
        }
        
        self.guidance_images_electric = {
            "en": os.path.join(application_path, 'electric_english.png'),
            "zh": os.path.join(application_path, 'electric_mandarin.png'),
            "id": os.path.join(application_path, 'electric_indo.png')
        }
        
        self.guidance_images_box = {
            "en": os.path.join(application_path, 'box_english.png'),
            "zh": os.path.join(application_path, 'box_mandarin.png'),
            "id": os.path.join(application_path, 'box_indo.png')
        }
        
        self.original_image = None
        self.photo = None
        self.canvas = None
        self.scroll_x = None
        self.scroll_y = None
        self.image_id = None

        # Variables for dragging
        self.drag_data = {"x": 0, "y": 0}
        
        self.image_label = None
        
        self.create_widgets()
        
        
    def create_widgets(self):
        self.root.title("Door Frame Material Calculator")
        
        frame = ttk.Frame(self.scrollable_frame, padding="10")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid(row=22, column=0, columnspan=3, sticky="nsew")

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
                
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=translations[self.current_language]["edit_menu"], menu=self.edit_menu)
        self.edit_menu.add_command(label=translations[self.current_language]["add_electric_lock"], command=self.add_electric_lock)
        self.edit_menu.add_command(label=translations[self.current_language]["remove_electric_lock"], command=self.remove_electric_lock)
        self.edit_menu.add_command(label=translations[self.current_language]["add_box_lock"], command=self.add_box_lock)
        self.edit_menu.add_command(label=translations[self.current_language]["remove_box_lock"], command=self.remove_box_lock)
        self.edit_menu.add_command(label=translations[self.current_language]["add_concealed_door_closer"], command=self.add_concealed)
        self.edit_menu.add_command(label=translations[self.current_language]["remove_concealed_door_closer"], command=self.remove_concealed)

        self.language_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=translations[self.current_language]["language"], menu=self.language_menu)
        self.language_menu.add_command(label="English", command=lambda: self.change_language("en"))
        self.language_menu.add_command(label="中文", command=lambda: self.change_language("zh"))
        self.language_menu.add_command(label="Bahasa", command=lambda: self.change_language("id"))
        
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=translations[self.current_language]["help"], menu=self.help_menu)
        self.help_menu.add_command(label=translations[self.current_language]["simple_help"], command=self.simple_help)
        self.help_menu.add_command(label=translations[self.current_language]["ub_help"], command=self.ub_help)
        self.help_menu.add_command(label=translations[self.current_language]["electric_lock_help"], command=self.electric_lock_help)
        self.help_menu.add_command(label=translations[self.current_language]["box_lock_help"], command=self.box_lock_help)
        
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Guidance", menu=self.view_menu)
        self.view_menu.add_checkbutton(label=translations[self.current_language]["Enable_"], variable=self.tooltips_enabled, command=self.toggle_tooltips)
        
        current_row = 0
        current_row= self.create_label_and_entry(frame, "door_type", current_row, "door_type")
        self.entries["door_type"][1]['values'] = ("simple", "UB", "electric lock", "box lock", "yipaiyikong")
        self.tooltips["door_type"] = ToolTip(self.entries["door_type"][1], translations[self.current_language]["tooltips"]["door_type"], self)
        self.entries["door_type"][1].bind("<<ComboboxSelected>>", self.update_inputs)

        current_row= self.create_label_and_entry(frame, "num_doors", current_row, add_separator=True)
        self.tooltips["num_doors"] = ToolTip(self.entries["num_doors"][1], translations[self.current_language]["tooltips"]["num_doors"], self)
        current_row= self.create_label_and_entry(frame, "right_vpiece_width", current_row)
        self.tooltips["right_vpiece_width"] = ToolTip(self.entries["right_vpiece_width"][1], translations[self.current_language]["tooltips"]["right_vpiece_width"], self)
        current_row= self.create_label_and_entry(frame, "left_vpiece_width", current_row)
        self.tooltips["left_vpiece_width"] = ToolTip(self.entries["left_vpiece_width"][1], translations[self.current_language]["tooltips"]["left_vpiece_width"], self)
        current_row= self.create_label_and_entry(frame, "upper_hpiece_width", current_row)
        self.tooltips["upper_hpiece_width"] = ToolTip(self.entries["upper_hpiece_width"][1], translations[self.current_language]["tooltips"]["upper_hpiece_width"], self)
        current_row= self.create_label_and_entry(frame, "lower_hpiece_width", current_row, add_separator=True)
        self.tooltips["lower_hpiece_width"] = ToolTip(self.entries["lower_hpiece_width"][1], translations[self.current_language]["tooltips"]["lower_hpiece_width"], self)
        # separator = ttk.Separator(frame, orient="horizontal")
        # separator.grid(row=6, column=0, columnspan=3, sticky="ew", pady=10)  # Adjust the row and columns

        
        current_row= self.create_label_and_entry(frame, "edge_sealing_type", current_row, "edge_sealing_type")
        self.entries["edge_sealing_type"][1]['values'] = ("6mm 實木", "4mm 白木", "6mm 鋁封邊", "1mm 鐡封邊 + 1mm 石墨片", "1mm 鐡封邊", "1mm 不織布", "0.8mm 美耐板", "0.5mm ABS")
        self.tooltips["edge_sealing_type"] = ToolTip(self.entries["edge_sealing_type"][1], translations[self.current_language]["tooltips"]["edge_sealing_type"], self)

        current_row= self.create_label_and_entry(frame, "edge_sealing_thickness", current_row, add_separator=True)
        self.tooltips["edge_sealing_thickness"] = ToolTip(self.entries["edge_sealing_thickness"][1], translations[self.current_language]["tooltips"]["edge_sealing_thickness"], self)
        current_row= self.create_label_and_entry(frame, "max_height", current_row)
        self.tooltips["max_height"] = ToolTip(self.entries["max_height"][1], translations[self.current_language]["tooltips"]["max_height"], self)
        current_row= self.create_label_and_entry(frame, "min_height", current_row, add_separator=True)
        self.tooltips["min_height"] = ToolTip(self.entries["min_height"][1], translations[self.current_language]["tooltips"]["min_height"], self)
        current_row= self.create_label_and_entry(frame, "electric_lock_name", current_row, "electric_lock_name")
        self.entries["electric_lock_name"][1]['values'] = list(electric_locks.keys())
        self.tooltips["electric_lock_name"] = ToolTip(self.entries["electric_lock_name"][1], translations[self.current_language]["tooltips"]["electric_lock_name"], self)
        current_row= self.create_label_and_entry(frame, "box_lock_name", current_row, "box_lock_name")
        self.entries["box_lock_name"][1]['values'] = list(box_locks.keys())
        self.tooltips["box_lock_name"] = ToolTip(self.entries["box_lock_name"][1], translations[self.current_language]["tooltips"]["box_lock_name"], self)
        
        current_row= self.create_label_and_entry(frame, "slats_width", current_row)
        self.tooltips["slats_width"] = ToolTip(self.entries["slats_width"][1], translations[self.current_language]["tooltips"]["slats_width"], self)
        current_row= self.create_label_and_entry(frame, "gap_width", current_row)
        self.tooltips["gap_width"] = ToolTip(self.entries["gap_width"][1], translations[self.current_language]["tooltips"]["gap_width"], self)

        current_row= self.create_label_and_entry(frame, "lock_length", current_row)
        self.tooltips["lock_length"] = ToolTip(self.entries["lock_length"][1], translations[self.current_language]["tooltips"]["lock_length"], self)
        current_row= self.create_label_and_entry(frame, "lock_height", current_row)
        self.tooltips["lock_height"] = ToolTip(self.entries["lock_height"][1], translations[self.current_language]["tooltips"]["lock_height"], self)
        current_row= self.create_label_and_entry(frame, "lock_direction", current_row, "lock_direction")
        self.entries["lock_direction"][1]['values'] = ("top", "bottom")
        self.tooltips["lock_direction"] = ToolTip(self.entries["lock_direction"][1], translations[self.current_language]["tooltips"]["lock_direction"], self)
        current_row= self.create_label_and_entry(frame, "concealed_door_closer_name", current_row, "concealed_door_closer_name", add_separator=True)
        self.entries["concealed_door_closer_name"][1]['values'] = list(concealeds.keys())
        self.tooltips["concealed_door_closer_name"] = ToolTip(self.entries["concealed_door_closer_name"][1], translations[self.current_language]["tooltips"]["concealed_door_closer_name"], self)

        current_row= self.create_label_and_entry(frame, "lock_offset_bottom", current_row)
        current_row= self.create_label_and_entry(frame, "frame_height", current_row)
        self.tooltips["frame_height"] = ToolTip(self.entries["frame_height"][1], translations[self.current_language]["tooltips"]["frame_height"], self)
        current_row= self.create_label_and_entry(frame, "frame_width", current_row)
        self.tooltips["frame_width"] = ToolTip(self.entries["frame_width"][1], translations[self.current_language]["tooltips"]["frame_width"], self)

        calculate_button = ttk.Button(frame, text=translations[self.current_language]["calculate"], command=self.calculate_material)
        calculate_button.grid(row=current_row, column=0, columnspan=2, pady=(10, 0))
        current_row +=1
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.grid(row=current_row, column=2, sticky="nsew", padx=(0, 200), pady=(10, 10))

        self.result_text = tk.Text(frame, width=100, height=30, font=("Helvetica", 13))
        self.result_text.grid(row=current_row, column=0, columnspan=2, sticky="nsew", padx=(0, 0), pady=(0, 0))
        # current_row +=1
        self.result_image = tk.Text(frame, width=50, height=30)
        self.result_image.grid(row=current_row, column=1, columnspan=3, sticky="nsew", padx=(0,0), pady=(0,0))
        scrollbar.config(command=self.result_text.yview)
        scrollbar.config(command=self.result_image.yview)
        trademark_label = ttk.Label(frame, text="© 2024 HBB", font=("Helvetica", 8))
        trademark_label.grid(row=current_row-1, column=0, columnspan=3, padx=(0, 1000))
        
        self.update_inputs()

    def create_label_and_entry(self, frame, key, row, entry_type="entry", add_separator=False):
        label = ttk.Label(frame, text=translations[self.current_language][key], font=("Helvetica", 13))
        label.grid(row=row, column=0, sticky=tk.W)
        if entry_type == "entry":
            entry = ttk.Entry(frame, font=("Helvetica", 13))
        elif entry_type == "door_type" or entry_type == "edge_sealing_type" or entry_type == "electric_lock_name" or entry_type == "lock_direction" or entry_type == "concealed_door_closer_name" or entry_type == "box_lock_name":
            entry = ttk.Combobox(frame, font=("Helvetica", 13))
        entry.grid(row=row, column=1, sticky=tk.E, padx=5, pady=1)
        self.entries[key] = (label, entry)  
        # Add an optional separator after this row
        # Add an optional separator after this row
        separator = None
        if add_separator:
            separator = ttk.Separator(frame, orient="horizontal")
            separator.grid(row=row + 1, column=0, columnspan=2, sticky="ew", pady=10)
            self.entries[f"{key}_separator"] = separator  # Store separator in entries dictionary
    
        return row + (2 if add_separator else 1)  # Increment rows correctly

    def update_inputs(self, *args):
        door_type = self.entries["door_type"][1].get().strip().lower()
        # electric_lock_label = translations[self.current_language]["electric lock"].lower()
        # ub_label = translations[self.current_language]["UB"].lower()
        # box_lock_label = translations[self.current_language]["box lock"].lower()
        if door_type == self.electric_lock_label:
            self.show_entries(["left_vpiece_width"], False)
            self.show_entries(["electric_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name"], True)
            self.show_entries(["max_height", "min_height", "box_lock_name","slats_width", "gap_width"], False)
        elif door_type == self.ub_label:
            self.show_entries(["electric_lock_name", "lock_length", "lock_height", "lock_direction", "lock_offset_bottom", "frame_height","slats_width", "gap_width"], False)
            self.show_entries(["max_height", "min_height"], True)
        elif door_type == self.box_lock_label:
            self.show_entries(["left_vpiece_width"], False)
            self.show_entries(["box_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name"], True)
            self.show_entries(["max_height", "min_height", "electric_lock_name","slats_width", "gap_width"], False)
        elif door_type == self.yipaiyikong_label:
            self.show_entries(["slats_width", "left_vpiece_width", "gap_width"], True)
            self.show_entries(["electric_lock_name", "box_lock_name", "lock_length", "lock_height", "lock_direction", "lock_offset_bottom"], False)
            self.show_entries(["max_height", "min_height", "concealed_door_closer_name"], False)
        else:
            self.show_entries(["left_vpiece_width"], True)
            self.show_entries(["electric_lock_name", "lock_length", "lock_height", "lock_direction", "lock_offset_bottom", "max_height", "min_height", "box_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "gap_width", "slats_width"], False)


    def show_entries(self, keys, show):
        for key in keys:
            if key in self.entries:
                label, widget = self.entries[key]
                if show:
                    label.grid()
                    widget.grid()
                else:
                    label.grid_remove()
                    widget.grid_remove()
    
                # Check for an associated separator
                separator_key = f"{key}_separator"
                if separator_key in self.entries:
                    separator = self.entries[separator_key]
                    if show:
                        separator.grid()
                    else:
                        separator.grid_remove()

    def change_language(self, language):
        self.current_language = language
        self.update_language()
        self.update_inputs()
        # Update tooltips
        for key, tooltip in self.tooltips.items():
            tooltip.text = translations[self.current_language]["tooltips"][key]

        
        self.simple_label = translations[self.current_language]["simple"].lower()
        self.electric_lock_label = translations[self.current_language]["electric lock"].lower()
        self.ub_label = translations[self.current_language]["UB"].lower()
        self.box_lock_label = translations[self.current_language]["box lock"].lower()
        self.yipaiyikong_label = translations[self.current_language]["yipaiyikong"].lower()
        self.top_label = translations[self.current_language]["top"].lower()
        self.bottom_label = translations[self.current_language]["bottom"].lower()
        self.concealed_label = translations[self.current_language]["concealed door closer"].lower()

    def update_language(self):
        self.root.title(translations[self.current_language]["app_title"])
        self.menu_bar.entryconfig(1, label=translations[self.current_language]["edit_menu"])
        self.edit_menu.entryconfig(0, label=translations[self.current_language]["add_electric_lock"])
        self.edit_menu.entryconfig(1, label=translations[self.current_language]["remove_electric_lock"])
        self.edit_menu.entryconfig(2, label=translations[self.current_language]["add_box_lock"])
        self.edit_menu.entryconfig(3, label=translations[self.current_language]["remove_box_lock"])
        self.edit_menu.entryconfig(4, label=translations[self.current_language]["add_concealed_door_closer"])
        self.edit_menu.entryconfig(5, label=translations[self.current_language]["remove_concealed_door_closer"])

        
        self.menu_bar.entryconfig(2, label=translations[self.current_language]["language"])
        
        
        self.menu_bar.entryconfig(3, label=translations[self.current_language]["help"])
        self.help_menu.entryconfig(0, label=translations[self.current_language]["simple_help"])
        self.help_menu.entryconfig(1, label=translations[self.current_language]["ub_help"])
        self.help_menu.entryconfig(2, label=translations[self.current_language]["electric_lock_help"])
        self.help_menu.entryconfig(3, label=translations[self.current_language]["box_lock_help"])
        
        self.menu_bar.entryconfig(4, label=translations[self.current_language]["Guidance"])
        self.view_menu.entryconfig(0, label=translations[self.current_language]["Enable_"])
        
        for key, value in self.entries.items():
            if isinstance(value, tuple) and len(value) == 2:
                label, entry = value
                if isinstance(label, tk.Widget):
                    label.config(text=translations[self.current_language].get(key, key))
                if isinstance(entry, tk.Widget):
                    if hasattr(entry, "set"):  # For comboboxes
                        values_key = f"{key}_values"
                        if values_key in translations[self.current_language]:
                            entry['values'] = translations[self.current_language][values_key]
        
        self.entries["door_type"][1]['values'] = (
        translations[self.current_language]["simple"],
        translations[self.current_language]["UB"],
        translations[self.current_language]["electric lock"],
        translations[self.current_language]["box lock"],
        translations[self.current_language]["yipaiyikong"]
        )
        self.entries["edge_sealing_type"][1]['values'] = ("6mm 實木", "4mm 白木", "6mm 鋁封邊", "1mm 鐡封邊 + 1mm 石墨片", "1mm 鐡封邊", "1mm 不織布", "0.8mm 美耐板", "0.5mm ABS")
        self.entries["electric_lock_name"][1]['values'] = list(electric_locks.keys())
        self.entries["box_lock_name"][1]['values'] = list(box_locks.keys())
        self.entries["concealed_door_closer_name"][1]['values'] = list(concealeds.keys())
        self.entries["lock_direction"][1]['values'] = (
        translations[self.current_language]["top"],
        translations[self.current_language]["bottom"]
        )
        self.language_menu.entryconfig(0, label="English")
        self.language_menu.entryconfig(1, label="中文")
        self.language_menu.entryconfig(2, label="Bahasa")
        
    def add_annotations(self, image_path, vertical_length, horizontal_length, door_type, outer_wood_upper, inner_wood_upper, outer_wood_bottom, inner_wood_bottom, concealed_length, very_upper_horizontal_piece_length, concealed_door_closer_name, slats_count):
        # Open the image file
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # Define font and size
        font = ImageFont.truetype("DejaVuSans.ttf", 24)  # Ensure the font file is available
        
        if concealed_door_closer_name in concealeds:
            concealed_length = concealeds[concealed_door_closer_name]['length']
        else:
            # Set default values if no concealed door closer is selected
            concealed_length = 0

        # Annotation positions can be adjusted based on door_type
        if door_type == self.simple_label:
            annotations = {
            f"{horizontal_length} mm": ((100, 20), "red"),   # Position and color for horizontal length
            f"{vertical_length} mm": ((10, 210), "blue")     # Position and color for vertical length
        }
        elif door_type == self.electric_lock_label and concealed_length > 0:
            annotations = {
                f"{very_upper_horizontal_piece_length} mm": ((130, 20), "magenta"),
                f"{outer_wood_upper} mm": ((10, 190), "green"),
                f"{inner_wood_upper} mm": ((10, 80), "purple"),
                f"{outer_wood_bottom} mm": ((10, 280), "orange"),
                f"{inner_wood_bottom} mm": ((10, 380), "brown"),
                f"{vertical_length} mm": ((390, 250), "blue"),
                f"{horizontal_length} mm": ((200, 430), "red"),
                f"{concealed_length} mm": ((280, 20), "black")
            }
        elif door_type == self.electric_lock_label and concealed_length == 0:
            annotations = {
                f"{horizontal_length} mm": ((130, 20), "red"),
                f"{outer_wood_upper} mm": ((10, 190), "green"),
                f"{inner_wood_upper} mm": ((10, 80), "purple"),
                f"{outer_wood_bottom} mm": ((10, 280), "orange"),
                f"{inner_wood_bottom} mm": ((10, 380), "brown"),
                f"{vertical_length} mm": ((390, 260), "blue")
            }
        elif door_type == self.box_lock_label and concealed_length > 0:
            annotations = {
                f"{very_upper_horizontal_piece_length} mm": ((130, 20), "magenta"),
                f"{outer_wood_upper} mm": ((10, 190), "green"),
                f"{inner_wood_upper} mm": ((10, 80), "purple"),
                f"{outer_wood_bottom} mm": ((10, 280), "orange"),
                f"{inner_wood_bottom} mm": ((10, 380), "brown"),
                f"{vertical_length} mm": ((390, 250), "blue"),
                f"{horizontal_length} mm": ((200, 430), "red"),
                f"{concealed_length} mm": ((280, 20), "black")
            }
        elif door_type == self.box_lock_label and concealed_length == 0:
            annotations = {
                f"{horizontal_length} mm": ((130, 20), "red"),
                f"{outer_wood_upper} mm": ((10, 190), "green"),
                f"{inner_wood_upper} mm": ((10, 80), "purple"),
                f"{outer_wood_bottom} mm": ((10, 280), "orange"),
                f"{inner_wood_bottom} mm": ((10, 380), "brown"),
                f"{vertical_length} mm": ((390, 260), "blue")
            }
        elif door_type == self.ub_label:
            annotations = {
                f"{horizontal_length} mm": ((100, 20), "red"),   # Position and color for horizontal length
                f"{vertical_length} mm": ((10, 210), "blue")
                }
        elif door_type == self.yipaiyikong_label:
            annotations = {
                f"{horizontal_length} mm": ((100, 20), "red"),   # Position and color for horizontal length
                f"{vertical_length} mm": ((10, 210), "blue"),
                f"{slats_count}": ((370, 260), "green")
                }

        for text, (position, color) in annotations.items():
            draw.text(position, text, fill=color, font=font)

        # Save the modified image
        annotated_image_path = image_path.replace(".png", "_annotated.png")
        image.save(annotated_image_path)
        
        return annotated_image_path

    def calculate_material(self):
        try:
            # for key in ["num_doors", "right_vpiece_width", "left_vpiece_width", "upper_hpiece_width", "lower_hpiece_width", "lock_height", "frame_height", "frame_width"]:
            #     if not self.entries[key][1].get().strip().isdigit():
            #         raise ValueError(f"Please enter a valid number for {translations[self.current_language][key]}")
            door_type = self.entries["door_type"][1].get().strip().lower()
            num_doors = int(self.entries["num_doors"][1].get())

            right_vertical_piece_width = int(self.entries["right_vpiece_width"][1].get())

            if door_type != self.electric_lock_label and door_type != self.box_lock_label:
                left_vertical_piece_width = int(self.entries["left_vpiece_width"][1].get())
            else:
                left_vertical_piece_width = 70
                
            

            upper_horizontal_piece_width = int(self.entries["upper_hpiece_width"][1].get())
            lower_horizontal_piece_width = int(self.entries["lower_hpiece_width"][1].get())

            edge_sealing_options = {
                "6mm 實木": 6,
                "6mm 鋁封邊": 6,
                "0.5mm ABS": 0.5,
                "1mm 鐡封邊 + 1mm 石墨片": 2,
                "1mm 鐡封邊": 1,
                "4mm 白木": 4,
                "0.8mm 美耐板": 0.8,
                "1mm 不織布": 1
            }

            edge_sealing_type = self.entries["edge_sealing_type"][1].get().strip()
            edge_sealing = edge_sealing_options.get(edge_sealing_type, None)

            if edge_sealing is None:
                edge_sealing = float(self.entries["edge_sealing_thickness"][1].get())

            if right_vertical_piece_width == left_vertical_piece_width:
                vertical_piece_width = right_vertical_piece_width
            else:
                vertical_piece_width = None

            if upper_horizontal_piece_width == lower_horizontal_piece_width:
                horizontal_piece_width = upper_horizontal_piece_width
            else:
                horizontal_piece_width = None

            max_height = min_height = None
            electric_lock_name = ""
            lock_length = 0
            electric_lock_height = 0
            lock_direction = ""
            lock_offset_bottom = 0
            lock_offset_top = 0
            concealed_door_closer_name = ""
            concealed_length = 0
            box_lock_name = ""
            box_lock_height = 0
            gap_width = 0
            slats_width = 0


            if door_type == self.ub_label:
                max_height = int(self.entries["max_height"][1].get())
                min_height = int(self.entries["min_height"][1].get())
                frame_height = max_height
                frame_width = int(self.entries["frame_width"][1].get())
            elif door_type == self.box_lock_label:
                for key in ["num_doors", "right_vpiece_width", "upper_hpiece_width", "lower_hpiece_width", "lock_height", "frame_height", "frame_width"]:
                    if not self.entries[key][1].get().strip().isdigit():
                        raise ValueError(f"請輸入有效的數字以 {translations[self.current_language][key]}")
                box_lock_name = self.entries["box_lock_name"][1].get().strip()
                concealed_door_closer_name = self.entries["concealed_door_closer_name"][1].get().strip()
                if box_lock_name in box_locks:
                    lock_length = box_locks[box_lock_name]['length']
                    lock_offset_bottom = box_locks[box_lock_name]['offset_bottom']
                    lock_offset_top = box_locks[box_lock_name]['offset_top']
                elif concealed_door_closer_name in concealeds:
                    concealed_length = concealeds[concealed_door_closer_name]['length']
                else:
                    lock_length = int(self.entries["lock_length"][1].get())
                    lock_offset_bottom = int(self.entries["lock_offset_bottom"][1].get())
                    lock_offset_top = lock_length - lock_offset_bottom
                    # concealed_length = ""
                box_lock_height = int(self.entries["lock_height"][1].get())
                lock_direction = self.entries["lock_direction"][1].get().strip().lower()
                # concealed_door_closer = self.entries["concealed_door_closer"][1].get().strip().lower()
                frame_height = int(self.entries["frame_height"][1].get())
                frame_width = int(self.entries["frame_width"][1].get())
            elif door_type == self.electric_lock_label:
                for key in ["num_doors", "right_vpiece_width", "upper_hpiece_width", "lower_hpiece_width", "lock_height", "frame_height", "frame_width"]:
                    if not self.entries[key][1].get().strip().isdigit():
                        raise ValueError(f"請輸入有效的數字以 {translations[self.current_language][key]}")
                electric_lock_name = self.entries["electric_lock_name"][1].get().strip()
                concealed_door_closer_name = self.entries["concealed_door_closer_name"][1].get().strip()
                if electric_lock_name in electric_locks:
                    lock_length = electric_locks[electric_lock_name]['length']
                    lock_offset_bottom = electric_locks[electric_lock_name]['offset_bottom']
                    lock_offset_top = electric_locks[electric_lock_name]['offset_top']
                elif concealed_door_closer_name in concealeds:
                    concealed_length = concealeds[concealed_door_closer_name]['length']
                    # print(f"\nelectriiicccconcealed_door_closer_name: {concealed_door_closer_name}")
                else:
                    lock_length = int(self.entries["lock_length"][1].get())
                    lock_offset_bottom = int(self.entries["lock_offset_bottom"][1].get())
                    lock_offset_top = lock_length - lock_offset_bottom
                    # concealed_length = ""
                electric_lock_height = int(self.entries["lock_height"][1].get())
                lock_direction = self.entries["lock_direction"][1].get().strip().lower()
                # concealed_door_closer = self.entries["concealed_door_closer"][1].get().strip().lower()
                frame_height = int(self.entries["frame_height"][1].get())
                frame_width = int(self.entries["frame_width"][1].get())

                if edge_sealing_type in ["1mm 鐡封邊 + 1mm 石墨片"]:
                    electric_lock_height += 3
                    box_lock_height += 3
                    
                elif edge_sealing_type in ["1mm 鐡封邊", "0.5mm ABS", "0.8mm 美耐板", "1mm 不織布"]:
                    electric_lock_height += 4
                    box_lock_height += 4
                    
            elif door_type == self.yipaiyikong_label:
                gap_width = int(self.entries["gap_width"][1].get())
                slats_width = int(self.entries["slats_width"][1].get())
                frame_height = int(self.entries["frame_height"][1].get())
                frame_width = int(self.entries["frame_width"][1].get())
            else:
                frame_height = int(self.entries["frame_height"][1].get())
                frame_width = int(self.entries["frame_width"][1].get())
                

            if edge_sealing_type in ["0.5mm ABS", "0.8mm 美耐板", "1mm 不織布"]:
                frame_height += 10
                frame_width += 10
            elif edge_sealing_type in ["1mm 鐡封邊 + 1mm 石墨片", "1mm 鐡封邊", "4mm 白木"]:
                frame_height += 5
                frame_width += 5
                

            inner_width, slats_length, plywood_width, plywood_height, total_length_all_doors, vertical_piece_length, \
                horizontal_pieces_length, frame_width, outer_wood_bottom, inner_wood_bottom, \
                outer_wood_upper, inner_wood_upper,very_upper_horizontal_piece_width,very_upper_horizontal_piece_length, gap_width, slats_width,\
                    slats_count, total_blocks = self.calculate_material_requirements(
                    door_type, num_doors, frame_height, right_vertical_piece_width, left_vertical_piece_width,
                    upper_horizontal_piece_width, lower_horizontal_piece_width, edge_sealing, max_height, min_height,
                    vertical_piece_width, horizontal_piece_width, frame_width, electric_lock_name, box_lock_name, lock_length,
                    electric_lock_height, box_lock_height, lock_direction, concealed_door_closer_name, concealed_length, lock_offset_bottom, lock_offset_top, gap_width, slats_width)

            report = self.generate_report(door_type, num_doors, inner_width, slats_length, gap_width, slats_count, total_blocks, plywood_width, plywood_height, total_length_all_doors,
                                          vertical_piece_length, horizontal_pieces_length, right_vertical_piece_width,
                                          left_vertical_piece_width, upper_horizontal_piece_width, lower_horizontal_piece_width,
                                          edge_sealing, max_height, min_height, vertical_piece_width, horizontal_piece_width,
                                          electric_lock_name, box_lock_name, lock_length, electric_lock_height, box_lock_height, lock_direction, concealed_door_closer_name, concealed_length,
                                          outer_wood_bottom, inner_wood_bottom, outer_wood_upper, inner_wood_upper,very_upper_horizontal_piece_width,very_upper_horizontal_piece_length, frame_width)
            
            # Determine the image to display based on door type
            door_type = self.entries["door_type"][1].get().strip().lower()
            
            # Debugging output
            # print(f"door_type: '{door_type}'")
            # print(f"Expected: simple_label='{self.simple_label}', ub_label='{self.ub_label}', electric_lock_label='{self.electric_lock_label}', box_lock_label='{self.box_lock_label}'")

            if concealed_door_closer_name in concealeds:
                concealed_length = concealeds[concealed_door_closer_name]['length']
            else:
                # Set default values if no concealed door closer is selected
                concealed_length = 0            

            if door_type == self.simple_label:
                image_path = os.path.join(application_path, 'simple.png')
            elif door_type == self.ub_label:
                image_path = os.path.join(application_path, 'UB.png')
            elif door_type == self.electric_lock_label and concealed_length > 0:
                image_path = os.path.join(application_path, 'kunci menkongqi.png')
            elif door_type == self.box_lock_label and concealed_length > 0:
                image_path = os.path.join(application_path, 'kunci menkongqi.png')
            elif door_type == self.electric_lock_label and concealed_length == 0:
                image_path = os.path.join(application_path, 'kunci.png')
            elif door_type == self.box_lock_label and concealed_length == 0:
                image_path = os.path.join(application_path, 'kunci.png')
            elif door_type == self.yipaiyikong_label:
                image_path = os.path.join(application_path, 'yipaiyikong.png')
            else:
                # print("No match found, defaulting to None")
                image_path = None
                
            # print(f"door_type: '{door_type}', concealed_door_closer: '{concealed_door_closer}'")
                
            # print(f"Image path: {image_path}")

            if image_path and os.path.exists(image_path):
                image = Image.open(image_path)
            else:
                raise FileNotFoundError(f"Image file not found at {image_path}")
            
            # Annotate the image
            annotated_image_path = self.add_annotations(image_path, vertical_piece_length, horizontal_pieces_length, door_type, outer_wood_upper, inner_wood_upper, outer_wood_bottom, inner_wood_bottom, concealed_length, very_upper_horizontal_piece_length, concealed_door_closer_name, slats_count)
            
            # Configure text tags for styling
            self.result_text.tag_configure("title", foreground="black", font=("Helvetica", 13, "bold"))
            self.result_text.tag_configure("titlelow", foreground="black", font=("Helvetica", 13, "bold"))
            self.result_text.tag_configure("vertical_length", foreground="blue", font=("Helvetica", 12))
            self.result_text.tag_configure("outer_wood_upper", foreground="green", font=("Helvetica", 12))
            self.result_text.tag_configure("inner_wood_upper", foreground="purple", font=("Helvetica", 12))
            self.result_text.tag_configure("outer_wood_bottom", foreground="orange", font=("Helvetica", 12))
            self.result_text.tag_configure("inner_wood_bottom", foreground="brown", font=("Helvetica", 12))
            self.result_text.tag_configure("horizontal_length", foreground="red", font=("Helvetica", 12))
            self.result_text.tag_configure("very_upper_horizontal_piece_length", foreground="magenta", font=("Helvetica", 12))
            self.result_text.tag_configure("slats_count", foreground="green", font=("Helvetica", 12))
            
            self.result_text.tag_configure("highlight", foreground="red", font=("Helvetica", 12))
            self.result_text.tag_configure("normal", font=("Helvetica", 12))
            
            lang = self.current_language
            # Use translated terms for checking content
            door_type_label = translations[lang]["door_type"]
            electric_lock_label = translations[lang]["electric_lock"]
            plywood_dimensions_label = translations[lang]["plywood_dimensions"]
            xisuangai_label = translations[lang]["xisuangai"]
            vertical_length_label = translations[lang]["length_each_piecev"]
            outer_wood_upper_label = translations[lang]["outer_wood_upper_part"]
            inner_wood_upper_label = translations[lang]["inner_wood_upper_part"]
            outer_wood_bottom_label = translations[lang]["outer_wood_bottom_part"]
            inner_wood_bottom_label = translations[lang]["inner_wood_bottom_part"]
            horizontal_length_label = translations[lang]["length_each_pieceh"]
            very_upper_horizontal_piece_length_label = translations[lang]["very_upper_horizontal_piece_length"]
            gap_width_label = translations[lang]["gap_width"]
            slats_length_label = translations[lang]["slats_length"]
            slats_count = translations[lang]["slats_count"]
            total_blocks = translations[lang]["total_blocks"]
        
            # Insert the report with different styles based on content
            lines = report.split('\n')
            for line in lines:
                if door_type_label in line or electric_lock_label in line:
                    self.result_text.insert(tk.END, line + "\n", "title")  # Apply the "title" style
                elif plywood_dimensions_label in line:
                    self.result_text.insert(tk.END, line + "\n", "titlelow")
                elif xisuangai_label in line:
                    self.result_text.insert(tk.END, line + "\n", "titlelow")
                elif vertical_length_label in line:
                    self.result_text.insert(tk.END, line + "\n", "vertical_length")
                elif outer_wood_upper_label in line:
                    self.result_text.insert(tk.END, line + "\n", "outer_wood_upper")
                elif inner_wood_upper_label in line:
                    self.result_text.insert(tk.END, line + "\n", "inner_wood_upper")
                elif outer_wood_bottom_label in line:
                    self.result_text.insert(tk.END, line + "\n", "outer_wood_bottom")
                elif inner_wood_bottom_label in line:
                    self.result_text.insert(tk.END, line + "\n", "inner_wood_bottom")
                elif horizontal_length_label in line:
                    self.result_text.insert(tk.END, line + "\n", "horizontal_length")
                elif very_upper_horizontal_piece_length_label in line:
                    self.result_text.insert(tk.END, line + "\n", "very_upper_horizontal_piece_length")
                elif slats_count in line:
                    self.result_text.insert(tk.END, line + "\n", "slats_count")
                else:
                    self.result_text.insert(tk.END, line + "\n", "normal")  # Default style
            
            # Display in Tkinter
            # self.result_text.delete("1.0", tk.END)
            
            # Create a frame within the result text area
            result_frame = ttk.Frame(self.result_text)
            # result_frame.pack(fill="both", expand=True)
            result_frame.grid_columnconfigure(0, weight=1)  # Text column
            result_frame.grid_columnconfigure(3, weight=3)  # Image column
            
            result_imageframe = ttk.Frame(self.result_image)
            
            # Insert the calculated text result into a Label inside the frame
            # text_result = tk.Label(result_frame, text=report, font=("Helvetica", 13), anchor="w", justify="left")
            # text_result.grid(row=0, column=0, sticky="nsew", padx=(10, 10), pady=(10, 10))
            
            # Add the annotated image inside the same frame, next to the text
            image = Image.open(annotated_image_path)
            image = image.resize((300, 400), Image.LANCZOS)  # Resize as needed
            photo = ImageTk.PhotoImage(image)
            
            image_label = tk.Label(result_imageframe, image=photo)
            image_label.image = photo  # Keep a reference to avoid garbage collection
            image_label.grid(row=0, column=3, sticky="nsew", padx=(10, 10), pady=(10, 10))
            
            self.result_text.window_create("end", window=result_frame)
            self.result_image.window_create("end", window=result_imageframe)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def calculate_material_requirements(self, door_type, num_doors, frame_height, right_vertical_piece_width,
                                        left_vertical_piece_width, upper_horizontal_piece_width, lower_horizontal_piece_width,
                                        edge_sealing, max_height, min_height, vertical_piece_width, horizontal_piece_width,
                                        frame_width, electric_lock_name, box_lock_name, lock_length, electric_lock_height, box_lock_height, lock_direction, concealed_door_closer_name, concealed_length, 
                                        lock_offset_bottom, lock_offset_top, gap_width, slats_width):
        if door_type in [self.electric_lock_label, self.box_lock_label]:
            inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2)
        else:
            inner_width = frame_width - right_vertical_piece_width - left_vertical_piece_width

        if door_type == self.ub_label:
            plywood_height = max_height - (upper_horizontal_piece_width * 2) - lower_horizontal_piece_width
        else:
            plywood_height = frame_height - upper_horizontal_piece_width - lower_horizontal_piece_width
            
        if door_type == self.yipaiyikong_label:
            inner_width = frame_width - right_vertical_piece_width - left_vertical_piece_width
            
        if door_type == self.ub_label:
            if max_height - min_height > upper_horizontal_piece_width:
                raise ValueError(f"the difference height should not exceed wood width\n 高度差異不應超過角材的寬度\n Perbedaan tinggi tidak boleh melebihi lebar kayu sisi")
            
        slats_length = 0
        total_blocks = 0
        slats_count = 0
        # gap_width = 0
        slats_length = inner_width
        plywood_width = inner_width
        vertical_piece_length = frame_height
        horizontal_pieces_length = inner_width
        # print("test3", horizontal_pieces_length)
        very_upper_horizontal_piece_width = 100
        very_upper_horizontal_piece_length = horizontal_pieces_length

        total_length_per_door = vertical_piece_length * 2 + horizontal_pieces_length * 2
        total_length_all_doors = total_length_per_door * num_doors
        
        # if concealed_door_closer_name == self.concealed_label:

        outer_wood_bottom = inner_wood_bottom = outer_wood_upper = inner_wood_upper = None
        if door_type == self.electric_lock_label:
            if lock_direction == self.bottom_label:
                outer_wood_bottom = electric_lock_height - lock_offset_bottom
                inner_wood_bottom = outer_wood_bottom - 30
                outer_wood_upper = frame_height - (outer_wood_bottom + lock_length)
                inner_wood_upper = outer_wood_upper - 75
            if lock_direction == self.top_label:
                outer_wood_upper = electric_lock_height - lock_offset_top
                inner_wood_upper = outer_wood_upper - 75
                outer_wood_bottom = frame_height - (outer_wood_upper + lock_length)
                inner_wood_bottom = outer_wood_bottom - 30
                
            if concealed_door_closer_name in concealeds:
                concealed_length = concealeds[concealed_door_closer_name]['length']
                very_upper_horizontal_piece_width = 100
                very_upper_horizontal_piece_length -= concealed_length
                very_upper_horizontal_piece_length = horizontal_pieces_length - concealed_length
            #     print(f"\nConcealed Length: {concealed_length}")
            # print(f"\n222Very Upper Horizontal Piece Length: {very_upper_horizontal_piece_length}")

            # if concealed_door_closer == "no":
            #     very_upper_horizontal_piece_width = 0
            #     very_upper_horizontal_piece_length = 0
                
        if door_type == self.box_lock_label:
            if lock_direction == self.bottom_label:
                outer_wood_bottom = box_lock_height - lock_offset_bottom
                inner_wood_bottom = outer_wood_bottom - 30
                outer_wood_upper = frame_height - (outer_wood_bottom + lock_length)
                inner_wood_upper = outer_wood_upper - 30
            if lock_direction == self.top_label:
                outer_wood_upper = box_lock_height - lock_offset_top
                inner_wood_upper = outer_wood_upper - 30
                outer_wood_bottom = frame_height - (outer_wood_upper + lock_length)
                inner_wood_bottom = outer_wood_bottom - 30
                
            if concealed_door_closer_name in concealeds:
                very_upper_horizontal_piece_width = 100
                very_upper_horizontal_piece_length -= concealed_length
                very_upper_horizontal_piece_length = horizontal_pieces_length - concealed_length
                
        elif door_type == self.yipaiyikong_label:
            slats_length = inner_width
            slats_count = frame_height // (slats_width + gap_width)
            total_blocks = slats_count + 4
            # print("test4", slats_length)
                
        if (door_type == self.electric_lock_label or door_type == self.box_lock_label) and concealed_door_closer_name == self.concealed_label:
            inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2)
            plywood_height = frame_height - upper_horizontal_piece_width - lower_horizontal_piece_width - very_upper_horizontal_piece_width
            plywood_width = inner_width
            # print("test4", inner_width)


        return inner_width, slats_length, plywood_width, plywood_height, total_length_all_doors, vertical_piece_length, \
               horizontal_pieces_length, frame_width, outer_wood_bottom, inner_wood_bottom, outer_wood_upper, inner_wood_upper, very_upper_horizontal_piece_width,\
               very_upper_horizontal_piece_length, gap_width, slats_width, slats_count, total_blocks

    def generate_report(self, door_type, num_doors, inner_width, slats_length, gap_width, slats_count, total_blocks, plywood_width, plywood_height, total_length_all_doors,
                        vertical_piece_length, horizontal_pieces_length, right_vertical_piece_width,
                        left_vertical_piece_width, upper_horizontal_piece_width, lower_horizontal_piece_width,
                        edge_sealing, max_height, min_height, vertical_piece_width, horizontal_piece_width,
                        electric_lock_name, box_lock_name, lock_length, electric_lock_height, box_lock_height, lock_direction, concealed_door_closer_name, concealed_length, outer_wood_bottom,
                        inner_wood_bottom, outer_wood_upper, inner_wood_upper,very_upper_horizontal_piece_width,very_upper_horizontal_piece_length, frame_width):
        lang = self.current_language
        total_right_vertical_pieces = num_doors if right_vertical_piece_width else 0
        total_left_vertical_pieces = num_doors if left_vertical_piece_width else 0

        if (door_type == self.electric_lock_label or door_type == self.box_lock_label):
            total_left_vertical_pieces = num_doors * 4

        total_horizontal_pieces = num_doors * sum(h is not None for h in [upper_horizontal_piece_width, lower_horizontal_piece_width])
        # print("test 3",slats_length)


        if door_type == self.ub_label:
            total_horizontal_pieces += num_doors
        

        report = f"""
        {translations[lang]["app_title"]}

        {translations[lang]["door_type"]}: {door_type.upper()}
        {translations[lang]["num_doors"]}: {num_doors}
        {translations[lang]["plywood_dimensions"]}: {plywood_width} mm x {plywood_height} mm 
        {translations[lang]["xisuangai"]}: {frame_width} mm x {vertical_piece_length} mm 
        {translations[lang]["edge_sealing"]}: {edge_sealing} mm
        """

        if door_type == self.electric_lock_label:
            report += f"""
            {translations[lang]["electric_lock"]}: {electric_lock_name}
            {translations[lang]["electric_lock_height"]}: {electric_lock_height} mm
            {translations[lang]["direction"]}: {lock_direction.capitalize()}

            {translations[lang]["total_wood_length"]}: {outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length +(horizontal_pieces_length * 2)*num_doors:.2f} mm
            {translations[lang]["total_wood"]}: {math.ceil((outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length +(horizontal_pieces_length * 2)*num_doors)/2400)}
            """
            report += f"""
            {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
              - {translations[lang]["length_each_piecev"]}: {vertical_piece_length} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors}
              - {translations[lang]["total_num_pieces"]}: {total_right_vertical_pieces}
              - {translations[lang]["total_wood_length"]}: {vertical_piece_length*num_doors:.2f} mm
              - {translations[lang]["total_wood"]}: {math.ceil((vertical_piece_length*num_doors)/2400)}

            {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
              - {translations[lang]["outer_wood_upper_part"]}: {outer_wood_upper} mm
              - {translations[lang]["inner_wood_upper_part"]}: {inner_wood_upper} mm
              - {translations[lang]["outer_wood_bottom_part"]}: {outer_wood_bottom} mm
              - {translations[lang]["inner_wood_bottom_part"]}: {inner_wood_bottom} mm
              - {translations[lang]["num_pieces_per_door"]}: {len([outer_wood_upper, inner_wood_upper, outer_wood_bottom, inner_wood_bottom])}
              - {translations[lang]["total_num_pieces"]}: {total_left_vertical_pieces}
              - {translations[lang]["total_wood_length"]}: {(outer_wood_upper + inner_wood_upper + outer_wood_bottom + inner_wood_bottom + very_upper_horizontal_piece_length)*num_doors:.2f} mm
              - {translations[lang]["total_wood"]}: {math.ceil(((outer_wood_upper + inner_wood_upper + outer_wood_bottom + inner_wood_bottom + very_upper_horizontal_piece_length)*num_doors)/2400)}
            """
            report +=f""" 
            """
            unique_horizontal_widths = {
                upper_horizontal_piece_width: {"length": horizontal_pieces_length, "count": 0},
                lower_horizontal_piece_width: {"length": horizontal_pieces_length, "count": 0},
                }
            unique_horizontal_widths = {width: data for width, data in unique_horizontal_widths.items() if width}
            
            # Calculate counts for horizontal pieces
            for width, data in unique_horizontal_widths.items():
                data["count"] += num_doors*2  # One horizontal piece per door
            report += f"""{translations[lang]["horizontal_pieces"]}"""
            for width, data in unique_horizontal_widths.items():
                report += f"""
                Width {width} mm:"""
            if concealed_door_closer_name in concealeds:
                report += f"""
            - {translations[lang]["concealed_door_closer"]}: {concealed_door_closer_name} {very_upper_horizontal_piece_length} mm"""
            report += f"""
            - {translations[lang]["length_each_pieceh"]}: {inner_width} mm
            - {translations[lang]["num_pieces_per_door"]}: {len([inner_width, inner_width, very_upper_horizontal_piece_length])}
            - {translations[lang]["total_num_pieces"]}: {(len([inner_width, inner_width, very_upper_horizontal_piece_length]))*num_doors}
            - {translations[lang]["total_wood_length"]}: {(very_upper_horizontal_piece_length + inner_width + inner_width)*num_doors:.2f} mm
            - {translations[lang]["total_wood"]}: {math.ceil(((very_upper_horizontal_piece_length + inner_width + inner_width)*num_doors)/2400)}
            """
        elif door_type == self.box_lock_label:
            report += f"""
            {translations[lang]["box_lock"]}: {box_lock_name}
            {translations[lang]["box_lock_height"]}: {box_lock_height} mm
            {translations[lang]["direction"]}: {lock_direction.capitalize()}

            {translations[lang]["total_wood_length"]}: {outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length +(horizontal_pieces_length * 2)*num_doors:.2f} mm
            {translations[lang]["total_wood"]}: {math.ceil((outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length +(horizontal_pieces_length * 2)*num_doors)/2400)}
            """
            report += f"""
            {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
              - {translations[lang]["length_each_piecev"]}: {vertical_piece_length} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors}
              - {translations[lang]["total_num_pieces"]}: {total_right_vertical_pieces}
              - {translations[lang]["total_wood_length"]}: {vertical_piece_length*num_doors:.2f} mm
              - {translations[lang]["total_wood"]}: {math.ceil((vertical_piece_length*num_doors)/2400)}

            {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
              - {translations[lang]["outer_wood_upper_part"]}: {outer_wood_upper} mm
              - {translations[lang]["inner_wood_upper_part"]}: {inner_wood_upper} mm
              - {translations[lang]["outer_wood_bottom_part"]}: {outer_wood_bottom} mm
              - {translations[lang]["inner_wood_bottom_part"]}: {inner_wood_bottom} mm
              - {translations[lang]["num_pieces_per_door"]}: {len([outer_wood_upper, inner_wood_upper, outer_wood_bottom, inner_wood_bottom])}
              - {translations[lang]["total_num_pieces"]}: {total_left_vertical_pieces}
              - {translations[lang]["total_wood_length"]}: {(outer_wood_upper + inner_wood_upper + outer_wood_bottom + inner_wood_bottom + very_upper_horizontal_piece_length)*num_doors:.2f} mm
              - {translations[lang]["total_wood"]}: {math.ceil(((outer_wood_upper + inner_wood_upper + outer_wood_bottom + inner_wood_bottom + very_upper_horizontal_piece_length)*num_doors)/2400)}
            """
            report +=f""" 
            """
            unique_horizontal_widths = {
                upper_horizontal_piece_width: {"length": horizontal_pieces_length, "count": 0},
                lower_horizontal_piece_width: {"length": horizontal_pieces_length, "count": 0},
                }
            unique_horizontal_widths = {width: data for width, data in unique_horizontal_widths.items() if width}
            
            # Calculate counts for horizontal pieces
            for width, data in unique_horizontal_widths.items():
                data["count"] += num_doors*2  # One horizontal piece per door
            report += f"""{translations[lang]["horizontal_pieces"]}"""
            for width, data in unique_horizontal_widths.items():
                report += f"""
                Width {width} mm:"""
            if concealed_door_closer_name in concealeds:
                report += f"""
            - {translations[lang]["concealed_door_closer"]}: {concealed_door_closer_name} {very_upper_horizontal_piece_length} mm
                """
            report += f"""
            - {translations[lang]["length_each_pieceh"]}: {inner_width} mm
            - {translations[lang]["num_pieces_per_door"]}: {len([inner_width, inner_width, very_upper_horizontal_piece_length])}
            - {translations[lang]["total_num_pieces"]}: {(len([inner_width, inner_width, very_upper_horizontal_piece_length]))*num_doors}
            - {translations[lang]["total_wood_length"]}: {(very_upper_horizontal_piece_length + inner_width + inner_width)*num_doors:.2f} mm
            - {translations[lang]["total_wood"]}: {math.ceil(((very_upper_horizontal_piece_length + inner_width + inner_width)*num_doors)/2400)}
            """
        elif door_type == self.yipaiyikong_label:
            report = f"""
            {translations[lang]["app_title"]}

            {translations[lang]["door_type"]}: {door_type.upper()}
            {translations[lang]["num_doors"]}: {num_doors}
            {translations[lang]["slats_length"]}: {slats_length} mm 
            {translations[lang]["edge_sealing"]}: {edge_sealing} mm
            {translations[lang]["slats_count"]}: {slats_count} 
            {translations[lang]["gap_width"]}: {gap_width} mm
            {translations[lang]["total_blocks"]}: {total_blocks}
            {translations[lang]["yipaiyikong_note"]}
            
            """
            report += f"""
            {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
              - {translations[lang]["length_each_piecev"]}: {vertical_piece_length} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors}
              - {translations[lang]["total_num_pieces"]}: {total_right_vertical_pieces}
              - {translations[lang]["total_wood_length"]}: {(vertical_piece_length)*num_doors:.2f} mm
              - {translations[lang]["total_wood"]}: {math.ceil(((vertical_piece_length)*num_doors)/2400)}

            {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
              - {translations[lang]["length_each_piecev"]}: {vertical_piece_length} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors}
              - {translations[lang]["total_num_pieces"]}: {total_left_vertical_pieces}
              - {translations[lang]["total_wood_length"]}: {(vertical_piece_length)*num_doors:.2f} mm
              - {translations[lang]["total_wood"]}: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
            """
            report +=f""" 
            {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
              - {translations[lang]["length_each_pieceh"]}: {inner_width} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors * 2}
              - {translations[lang]["total_num_pieces"]}: {total_horizontal_pieces}
              - {translations[lang]["total_wood_length"]}: {(inner_width)*num_doors:.2f} mm
              - {translations[lang]["total_wood"]}: {math.ceil(((inner_width)*num_doors)/2400)}"""
        else:
            report += f"""
            {translations[lang]["total_wood_length"]}: {total_length_all_doors:.2f} mm
            {translations[lang]["total_wood"]}: {math.ceil((total_length_all_doors)/2400)}

            """
            if vertical_piece_width:
                report += f"""
            {translations[lang]["vertical_pieces"]} ({vertical_piece_width}mm):
              - {translations[lang]["length_each_piecev"]}: {vertical_piece_length} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors * 2}
              - {translations[lang]["total_num_pieces"]}: {num_doors * 2}
              - {translations[lang]["total_wood_length"]}: {(vertical_piece_length)*num_doors:.2f} mm
              - {translations[lang]["total_wood"]}: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
                """
            else:
                report += f"""
            {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
              - {translations[lang]["length_each_piecev"]}: {vertical_piece_length} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors}
              - {translations[lang]["total_num_pieces"]}: {total_right_vertical_pieces}
              - {translations[lang]["total_wood_length"]}: {(vertical_piece_length)*num_doors:.2f} mm
              - {translations[lang]["total_wood"]}: {math.ceil(((vertical_piece_length)*num_doors)/2400)}

            {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
              - {translations[lang]["length_each_piecev"]}: {vertical_piece_length} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors}
              - {translations[lang]["total_num_pieces"]}: {total_left_vertical_pieces}
              - {translations[lang]["total_wood_length"]}: {(vertical_piece_length)*num_doors:.2f} mm
              - {translations[lang]["total_wood"]}: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
                """
            if horizontal_piece_width:
                report += f"""
                {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
                  - {translations[lang]["length_each_pieceh"]}: {inner_width} mm
                  - {translations[lang]["num_pieces_per_door"]}: {num_doors * 2}
                  - {translations[lang]["total_num_pieces"]}: {total_horizontal_pieces}
                  - {translations[lang]["total_wood_length"]}: {(inner_width)*num_doors:.2f} mm
                  - {translations[lang]["total_wood"]}: {math.ceil(((inner_width)*num_doors)/2400)}
                    """
            else:
                report += f"""
                {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
                  - {translations[lang]["length_each_pieceh"]}: {inner_width} mm
                  - {translations[lang]["num_pieces_per_door"]}: {num_doors}
                  - {translations[lang]["total_num_pieces"]}: {num_doors}
                  - {translations[lang]["total_wood_length"]}: {(inner_width)*num_doors:.2f} mm
                  - {translations[lang]["total_wood"]}: {math.ceil(((inner_width)*num_doors)/2400)}
    
                {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
                  - {translations[lang]["length_each_pieceh"]}: {inner_width} mm
                  - {translations[lang]["num_pieces_per_door"]}: {num_doors}
                  - {translations[lang]["total_num_pieces"]}: {num_doors}
                  - {translations[lang]["total_wood_length"]}: {(inner_width)*num_doors:.2f} mm
                  - {translations[lang]["total_wood"]}: {math.ceil(((inner_width)*num_doors)/2400)}
                    """
        
        
        if door_type == self.ub_label:
            report += f"""
            {translations[lang]["ub_note"]}
            """
            
        self.result_text.delete("1.0", tk.END)
        self.result_image.delete("1.0", tk.END)

       
        return report

    def add_electric_lock(self):
        def save_new_lock():
            name = new_lock_name_entry.get().strip()
            length = int(new_lock_length_entry.get().strip())
            offset_bottom = int(new_lock_offset_bottom_entry.get().strip())
            offset_top = int(new_lock_offset_top_entry.get().strip())
            if name:
                electric_locks[name] = {
                    "length": length,
                    "offset_bottom": offset_bottom,
                    "offset_top": offset_top
                }
                save_electric_locks(electric_locks)
                lock_window.destroy()
                self.entries["electric_lock_name"][1]['values'] = list(electric_locks.keys())
            else:
                messagebox.showerror("Error", "Electric lock data cannot be empty.")

        lock_window = tk.Toplevel(self.root)
        lock_window.title(translations[self.current_language]["add_electric_lock"])

        ttk.Label(lock_window, text=translations[self.current_language]["electriclockname"], font=("Helvetica", 13)).grid(row=0, column=0, sticky=tk.W)
        new_lock_name_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_name_entry.grid(row=0, column=1, sticky=tk.E)
        ttk.Label(lock_window, text=translations[self.current_language]["locklength"], font=("Helvetica", 13)).grid(row=1, column=0, sticky=tk.W)
        new_lock_length_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_length_entry.grid(row=1, column=1, sticky=tk.E)
        ttk.Label(lock_window, text=translations[self.current_language]["offsetbottom"], font=("Helvetica", 13)).grid(row=2, column=0, sticky=tk.W)
        new_lock_offset_bottom_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_offset_bottom_entry.grid(row=2, column=1, sticky=tk.E)
        ttk.Label(lock_window, text=translations[self.current_language]["offsettop"], font=("Helvetica", 13)).grid(row=3, column=0, sticky=tk.W)
        new_lock_offset_top_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_offset_top_entry.grid(row=3, column=1, sticky=tk.E)

        save_button = ttk.Button(lock_window, text=translations[self.current_language]["Save"], command=save_new_lock)
        save_button.grid(row=4, column=0, columnspan=2)

    def remove_electric_lock(self):
        def delete_lock():
            name = lock_to_remove_var.get().strip()
            if name in electric_locks:
                del electric_locks[name]
                save_electric_locks(electric_locks)
                remove_window.destroy()
                self.entries["electric_lock_name"][1]['values'] = list(electric_locks.keys())
            else:
                messagebox.showerror("Error", "Electric lock not found.")

        remove_window = tk.Toplevel(self.root)
        remove_window.title(translations[self.current_language]["remove_electric_lock"])

        ttk.Label(remove_window, text=translations[self.current_language]["removeelectric"], font=("Helvetica", 13)).grid(row=0, column=0, sticky=tk.W)
        lock_to_remove_var = tk.StringVar()
        # lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var)
        lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var, font=("Helvetica", 13))
        lock_to_remove_menu.grid(row=0, column=1, sticky=tk.E)
        lock_to_remove_menu['values'] = list(electric_locks.keys())


        delete_button = ttk.Button(remove_window, text=translations[self.current_language]["Delete"], command=delete_lock)
        delete_button.grid(row=1, column=0, columnspan=2)
        
    def add_box_lock(self):
        def save_new_lock():
            name = new_lock_name_entry.get().strip()
            length = int(new_lock_length_entry.get().strip())
            offset_bottom = int(new_lock_offset_bottom_entry.get().strip())
            offset_top = int(new_lock_offset_top_entry.get().strip())
            if name:
                box_locks[name] = {
                    "length": length,
                    "offset_bottom": offset_bottom,
                    "offset_top": offset_top
                }
                save_box_locks(box_locks)
                lock_window.destroy()
                self.entries["box_lock_name"][1]['values'] = list(box_locks.keys())
            else:
                messagebox.showerror("Error", "box lock data cannot be empty.")

        lock_window = tk.Toplevel(self.root)
        lock_window.title(translations[self.current_language]["add_box_lock"])

        ttk.Label(lock_window, text=translations[self.current_language]["boxlockname"], font=("Helvetica", 13)).grid(row=0, column=0, sticky=tk.W)
        new_lock_name_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_name_entry.grid(row=0, column=1, sticky=tk.E)
        ttk.Label(lock_window, text=translations[self.current_language]["locklength"], font=("Helvetica", 13)).grid(row=1, column=0, sticky=tk.W)
        new_lock_length_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_length_entry.grid(row=1, column=1, sticky=tk.E)
        ttk.Label(lock_window, text=translations[self.current_language]["offsetbottom"], font=("Helvetica", 13)).grid(row=2, column=0, sticky=tk.W)
        new_lock_offset_bottom_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_offset_bottom_entry.grid(row=2, column=1, sticky=tk.E)
        ttk.Label(lock_window, text=translations[self.current_language]["offsettop"], font=("Helvetica", 13)).grid(row=3, column=0, sticky=tk.W)
        new_lock_offset_top_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_offset_top_entry.grid(row=3, column=1, sticky=tk.E)

        save_button = ttk.Button(lock_window, text=translations[self.current_language]["Save"], command=save_new_lock)
        save_button.grid(row=4, column=0, columnspan=2)

    def remove_box_lock(self):
        def delete_lock():
            name = lock_to_remove_var.get().strip()
            if name in box_locks:
                del box_locks[name]
                save_box_locks(box_locks)
                remove_window.destroy()
                self.entries["box_lock_name"][1]['values'] = list(box_locks.keys())
            else:
                messagebox.showerror("Error", "box lock not found.")

        remove_window = tk.Toplevel(self.root)
        remove_window.title(translations[self.current_language]["remove_box_lock"])

        ttk.Label(remove_window, text=translations[self.current_language]["removebox"], font=("Helvetica", 13)).grid(row=0, column=0, sticky=tk.W)
        lock_to_remove_var = tk.StringVar()
        # lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var)
        lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var, font=("Helvetica", 13))
        lock_to_remove_menu.grid(row=0, column=1, sticky=tk.E)
        lock_to_remove_menu['values'] = list(box_locks.keys())


        delete_button = ttk.Button(remove_window, text=translations[self.current_language]["Delete"], command=delete_lock)
        delete_button.grid(row=1, column=0, columnspan=2)
        
    def add_concealed(self):
        def save_new_concealed():
            name = new_concealed_name_entry.get().strip()
            length = int(new_concealed_length_entry.get().strip())
            if name:
                concealeds[name] = {
                    "length": length,
                }
                save_concealed_door(concealeds)
                concealed_window.destroy()
                self.entries["concealed_door_closer_name"][1]['values'] = list(concealeds.keys())
            else:
                messagebox.showerror("Error", "Concealed door closer data cannot be empty.")

        concealed_window = tk.Toplevel(self.root)
        concealed_window.title(translations[self.current_language]["add_concealed"])

        ttk.Label(concealed_window, text=translations[self.current_language]["concealedname"], font=("Helvetica", 13)).grid(row=0, column=0, sticky=tk.W)
        new_concealed_name_entry = ttk.Entry(concealed_window, font=("Helvetica", 13))
        new_concealed_name_entry.grid(row=0, column=1, sticky=tk.E)
        ttk.Label(concealed_window, text=translations[self.current_language]["concealedlength"], font=("Helvetica", 13)).grid(row=1, column=0, sticky=tk.W)
        new_concealed_length_entry = ttk.Entry(concealed_window, font=("Helvetica", 13))
        new_concealed_length_entry.grid(row=1, column=1, sticky=tk.E)

        save_button = ttk.Button(concealed_window, text=translations[self.current_language]["Save"], command=save_new_concealed)
        save_button.grid(row=4, column=0, columnspan=2)

    def remove_concealed(self):
        def delete_concealed():
            name = concealed_to_remove_var.get().strip()
            if name in concealeds:
                del concealeds[name]
                save_concealed_door(concealeds)
                remove_window.destroy()
                self.entries["concealed_door_closer_name"][1]['values'] = list(concealeds.keys())
            else:
                messagebox.showerror("Error", "Concealed Door Closer not found.")

        remove_window = tk.Toplevel(self.root)
        remove_window.title(translations[self.current_language]["remove_concealed"])

        ttk.Label(remove_window, text=translations[self.current_language]["concealedremove"], font=("Helvetica", 13)).grid(row=0, column=0, sticky=tk.W)
        concealed_to_remove_var = tk.StringVar()
        # lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=concealed_to_remove_var)
        lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=concealed_to_remove_var, font=("Helvetica", 13))
        lock_to_remove_menu.grid(row=0, column=1, sticky=tk.E)
        lock_to_remove_menu['values'] = list(concealeds.keys())


        delete_button = ttk.Button(remove_window, text=translations[self.current_language]["Delete"], command=delete_concealed)
        delete_button.grid(row=1, column=0, columnspan=2)
        
    def simple_help(self):
        guidance_window = tk.Toplevel(self.root)
        guidance_window.title("Application Guidance")
        

        # Add a label for the title
        tk.Label(guidance_window, text="Step-by-Step Guide", font=("Helvetica", 16, "bold")).pack(pady=10)

        # # Load the image based on the current language
        # image_path = self.guidance_images_simple.get(self.current_language, self.guidance_images_simple["en"])  # Default to English if no match
        # self.original_image = Image.open(image_path)
        # self.image_display_size = (1200, 600)  # Initial display size
        
        # self.create_canvas(guidance_window)
        
        # self.display_image()  # Show the initial image

        # # Add further text or instructions if needed
        # # tk.Label(guidance_window, text="Follow the steps in the guide to complete the configuration.").pack(pady=5)
        # # Bind mouse scroll for zoom and dragging
        # guidance_window.bind("<MouseWheel>", self.zoom_image)
        # guidance_window.bind("<Button-4>", self.zoom_image)  # For Linux scroll up
        # guidance_window.bind("<Button-5>", self.zoom_image)  # For Linux scroll down
        # self.canvas.bind("<ButtonPress-1>", self.start_drag)
        # self.canvas.bind("<B1-Motion>", self.drag_image)
        
        # Local canvas for the help window
        help_canvas = tk.Canvas(guidance_window, width=600, height=400)
        help_canvas.pack(fill=tk.BOTH, expand=True)
     
        # Load the image based on the current language
        image_path = self.guidance_images_simple.get(self.current_language, self.guidance_images_simple["en"])
        original_image = Image.open(image_path)
        photo = ImageTk.PhotoImage(original_image)
     
        # Display the image on the local canvas
        help_canvas.create_image(0, 0, anchor="nw", image=photo)
        help_canvas.image = photo  # Keep a reference to prevent garbage collection
     
        # Bind scroll and drag events for this specific canvas
        # guidance_window.bind("<MouseWheel>", self.zoom_image)
        help_canvas.bind("<MouseWheel>", lambda event: self.zoom_image(event, help_canvas))
        help_canvas.bind("<ButtonPress-1>", self.start_drag)
        help_canvas.bind("<B1-Motion>", lambda event: self.drag_image(event, help_canvas))

        
              
        # Set guidance window reference to destroy tooltip if the window closes
        guidance_window.protocol("WM_DELETE_WINDOW", lambda: self.close_guidance(guidance_window))
              
    def ub_help(self):
        guidance_window = tk.Toplevel(self.root)
        guidance_window.title("Application Guidance")

        # Add a label for the title
        tk.Label(guidance_window, text="Step-by-Step Guide", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Local canvas for the help window
        help_canvas = tk.Canvas(guidance_window, width=600, height=400)
        help_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Load the image based on the current language
        image_path = self.guidance_images_ub.get(self.current_language, self.guidance_images_ub["en"])
        original_image = Image.open(image_path)
        photo = ImageTk.PhotoImage(original_image)
        
        # Display the image on the local canvas
        help_canvas.create_image(0, 0, anchor="nw", image=photo)
        help_canvas.image = photo  # Keep a reference to prevent garbage collection
        
        # Bind scroll and drag events for this specific canvas
        # guidance_window.bind("<MouseWheel>", self.zoom_image)
        help_canvas.bind("<MouseWheel>", lambda event: self.zoom_image(event, help_canvas))
        help_canvas.bind("<ButtonPress-1>", self.start_drag)
        help_canvas.bind("<B1-Motion>", lambda event: self.drag_image(event, help_canvas))
        
        # Set guidance window reference to destroy tooltip if the window closes
        guidance_window.protocol("WM_DELETE_WINDOW", lambda: self.close_guidance(guidance_window))
        
    def electric_lock_help(self):
        guidance_window = tk.Toplevel(self.root)
        guidance_window.title("Application Guidance")

        # Add a label for the title
        tk.Label(guidance_window, text="Step-by-Step Guide", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Local canvas for the help window
        help_canvas = tk.Canvas(guidance_window, width=600, height=400)
        help_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Load the image based on the current language
        image_path = self.guidance_images_electric.get(self.current_language, self.guidance_images_electric["en"])
        original_image = Image.open(image_path)
        photo = ImageTk.PhotoImage(original_image)
        
        # Display the image on the local canvas
        help_canvas.create_image(0, 0, anchor="nw", image=photo)
        help_canvas.image = photo  # Keep a reference to prevent garbage collection
        
        # Bind scroll and drag events for this specific canvas
        # guidance_window.bind("<MouseWheel>", self.zoom_image)
        help_canvas.bind("<MouseWheel>", lambda event: self.zoom_image(event, help_canvas))
        help_canvas.bind("<ButtonPress-1>", self.start_drag)
        help_canvas.bind("<B1-Motion>", lambda event: self.drag_image(event, help_canvas))
        
        # Set guidance window reference to destroy tooltip if the window closes
        guidance_window.protocol("WM_DELETE_WINDOW", lambda: self.close_guidance(guidance_window))
        
    def box_lock_help(self):
        guidance_window = tk.Toplevel(self.root)
        guidance_window.title("Application Guidance")

        # Add a label for the title
        tk.Label(guidance_window, text="Step-by-Step Guide", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Local canvas for the help window
        help_canvas = tk.Canvas(guidance_window, width=600, height=400)
        help_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Load the image based on the current language
        image_path = self.guidance_images_box.get(self.current_language, self.guidance_images_box["en"])
        original_image = Image.open(image_path)
        photo = ImageTk.PhotoImage(original_image)
        
        # Display the image on the local canvas
        help_canvas.create_image(0, 0, anchor="nw", image=photo)
        help_canvas.image = photo  # Keep a reference to prevent garbage collection
        
        # Bind scroll and drag events for this specific canvas
        # guidance_window.bind("<MouseWheel>", self.zoom_image)
        help_canvas.bind("<MouseWheel>", lambda event: self.zoom_image(event, help_canvas))
        help_canvas.bind("<ButtonPress-1>", self.start_drag)
        help_canvas.bind("<B1-Motion>", lambda event: self.drag_image(event, help_canvas))
        
        # Set guidance window reference to destroy tooltip if the window closes
        guidance_window.protocol("WM_DELETE_WINDOW", lambda: self.close_guidance(guidance_window))
        
    def toggle_tooltips(self):
        """Enable or disable tooltips based on user preference."""
        enabled = self.tooltips_enabled.get()
        for tooltip in self.tooltips.values():
            tooltip.enabled = enabled
    
    def create_canvas(self, window):
        """Create or reset the canvas for image display."""
        if self.canvas is None:
            self.canvas = tk.Canvas(window, width=600, height=400)
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _on_mousewheel_help(self, event, canvas):
        """Scroll the help canvas with the mouse wheel."""
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def close_guidance(self, window):
        """Handle the closure of the guidance window and clean up resources."""
        window.destroy()
        self.image_label = None  # Reset image label so it can be recreated next time
    
    def display_image(self, canvas):
        """Display image with the current display size."""
        # Resize the image and convert it to PhotoImage
        resized_image = self.original_image.resize(self.image_display_size)
        self.photo = ImageTk.PhotoImage(resized_image)
        
        # Clear any existing image and display the new image
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def zoom_image(self, event):
        """Zoom in or out on the image."""
        zoom_factor = 1.1 if event.delta > 0 else 0.9

        # Update size for zoom
        new_width = int(self.image_display_size[0] * zoom_factor)
        new_height = int(self.image_display_size[1] * zoom_factor)
        self.image_display_size = (new_width, new_height)

        # Update the displayed image
        self.display_image()
        
    def start_drag(self, event):
        """Start dragging the image."""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def drag_image(self, event, canvas):
        """Handle dragging the image within the canvas."""
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        
        canvas.move("all", delta_x, delta_y)
        
        # Update drag data
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
   
if __name__ == "__main__":
    root = tk.Tk()
    app = DoorFrameCalculator(root)
    app.update_language()  # Initialize with the correct language
    root.mainloop()
