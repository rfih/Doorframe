import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import os
import sys
from PIL import Image, ImageTk, ImageDraw, ImageFont
import math
# from tkVideoPlayer import TkinterVideo 

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

def safe_int(value, default=0):
    """Convert a value to an integer, or return a default if conversion fails."""
    try:
        return int(value)
    except ValueError:
        return default


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
            label = tk.Label(self.tip_window, text=self.text, font=("Microsoft YaHei", 13),  background="#ffffe0", borderwidth=1)
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
        self.root.geometry("1400x820")
        self.current_language = "zh"
        self.entries = {}

        # Create a canvas and a scrollbar for the entire application
        self.canvas = tk.Canvas(root, width=1400, height=820)
        self.scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=self.canvas.xview)
        self.scrollbar_y = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.tooltips_enabled = tk.BooleanVar(value=False)
        self.canvas.create_window((10, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        
        self.canvas.pack(side="right", fill="both", expand=True)
        
        # Bind the scroll region configuration to the scrollable frame's size changes
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")) if self.canvas else None)
        
        # Initialize translated door type labels
        self.simple_label = translations[self.current_language]["simple"].lower()
        self.electric_lock_label = translations[self.current_language]["electric lock"].lower()
        self.ub_label = translations[self.current_language]["UB"].lower()
        self.box_lock_label = translations[self.current_language]["box lock"].lower()
        
        self.yipaiyikong_label = translations[self.current_language]["yipaiyikong"].lower()
        self.top_label = translations[self.current_language]["top"].lower()
        self.bottom_label = translations[self.current_language]["bottom"].lower()
        self.concealed_label = translations[self.current_language]["concealed door closer"].lower()
        self.fireproof_label = translations[self.current_language]["fireproof"].lower()
        self.non_fireproof_label = translations[self.current_language]["non_fireproof"].lower()
        self.honeycomb_paper_label = translations[self.current_language]["honeycomb_paper"].lower()
        self.honeycomb_board_label = translations[self.current_language]["honeycomb_board"].lower()
        
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
        frame.grid(row=0, column=2, sticky="ew", padx=(0,0), pady=0)
        
        # Create Entries Frame (left side)
        self.entries_frame = ttk.Frame(frame, width=1000)
        self.entries_frame.grid(row=0, column=0, sticky="nw", padx=(0, 0))
        
        # Create Results Frame (right side)
        self.results_frame = ttk.Frame(frame, width=10)  # Store it as an instance variable
        self.results_frame.grid(row=0, column=0, sticky="ew", padx=(550, 10))
        
        menu_font = font.Font(family="Microsoft YaHei", size=11)
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
                
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0, font=menu_font)
        self.menu_bar.add_cascade(label=translations[self.current_language]["edit_menu"], menu=self.edit_menu)
        self.edit_menu.add_command(label=translations[self.current_language]["add_electric_lock"], command=self.add_electric_lock)
        self.edit_menu.add_command(label=translations[self.current_language]["remove_electric_lock"], command=self.remove_electric_lock)
        self.edit_menu.add_command(label=translations[self.current_language]["add_box_lock"], command=self.add_box_lock)
        self.edit_menu.add_command(label=translations[self.current_language]["remove_box_lock"], command=self.remove_box_lock)
        self.edit_menu.add_command(label=translations[self.current_language]["add_concealed_door_closer"], command=self.add_concealed)
        self.edit_menu.add_command(label=translations[self.current_language]["remove_concealed_door_closer"], command=self.remove_concealed)

        self.language_menu = tk.Menu(self.menu_bar, tearoff=0, font=menu_font)
        self.menu_bar.add_cascade(label=translations[self.current_language]["language"], menu=self.language_menu)
        self.language_menu.add_command(label="English", command=lambda: self.change_language("en"))
        self.language_menu.add_command(label="中文", command=lambda: self.change_language("zh"))
        self.language_menu.add_command(label="Bahasa", command=lambda: self.change_language("id"))
        
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0, font=menu_font)
        self.menu_bar.add_cascade(label=translations[self.current_language]["help"], menu=self.help_menu)
        self.help_menu.add_command(label=translations[self.current_language]["app_help"], command=self.app_help)
        self.help_menu.add_command(label=translations[self.current_language]["simple_help"], command=self.simple_help)
        self.help_menu.add_command(label=translations[self.current_language]["ub_help"], command=self.ub_help)
        self.help_menu.add_command(label=translations[self.current_language]["electric_lock_help"], command=self.electric_lock_help)
        self.help_menu.add_command(label=translations[self.current_language]["box_lock_help"], command=self.box_lock_help)
        
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0, font=menu_font)
        self.menu_bar.add_cascade(label="Guidance", menu=self.view_menu)
        self.view_menu.add_checkbutton(label=translations[self.current_language]["Enable_"], variable=self.tooltips_enabled, command=self.toggle_tooltips)
        
        style = ttk.Style()
        style.configure("CustomLabel.TLabel", foreground="gray30")
        current_row = 0
        current_row = self.create_label_and_entry(self.entries_frame, "category", current_row, "category")
        self.entries["category"][1]['values'] = (
            translations[self.current_language]["fireproof"],
            translations[self.current_language]["non_fireproof"]
        )
        self.entries["category"][1].bind("<<ComboboxSelected>>", self.update_inputs)
        current_row += 1
        
        self.mode_selection_label = ttk.Label(
            self.entries_frame,
            text=translations[self.current_language]["mode_selection"],
            font=("Microsoft YaHei", 12),
            style="CustomLabel.TLabel"
        )
        self.mode_selection_label.grid(row=current_row, column=0, sticky="w")

        self.mode_selection = tk.StringVar(value="Normal")  # Default mode
        self.normal_mode_button = ttk.Radiobutton(
            self.entries_frame,
            text=translations[self.current_language]["normal_mode"],
            variable=self.mode_selection,
            value="Normal",
            command=self.update_inputs
        )
        self.ub_mode_button = ttk.Radiobutton(
            self.entries_frame,
            text=translations[self.current_language]["ub_mode"],
            variable=self.mode_selection,
            value="UB",
            command=self.update_inputs
        )
        
        self.normal_mode_button.grid(row=current_row, column=1, sticky="w", padx=50)
        self.ub_mode_button.grid(row=current_row, column=1, sticky="w", padx=120)
        current_row += 1
    
        # Structure Type Dropdown (for Non-Fireproof)
        current_row = self.create_label_and_entry(self.entries_frame, "structure_type", current_row, "structure_type")
        self.entries["structure_type"][1]['values'] = ("honeycomb_paper", "yipaiyikong", "honeycomb_board")

        self.entries["structure_type"][1].bind("<<ComboboxSelected>>", self.update_inputs)
    
        # Door Type Dropdown
        current_row = self.create_label_and_entry(self.entries_frame, "door_type", current_row, "door_type")
        self.entries["door_type"][1]['values'] = ("simple", "electric lock", "box lock")
        self.tooltips["door_type"] = ToolTip(self.entries["door_type"][1], translations[self.current_language]["tooltips"]["door_type"], self)
        self.entries["door_type"][1].bind("<<ComboboxSelected>>", self.update_inputs)

        current_row= self.create_label_and_entry(self.entries_frame, "num_doors", current_row, add_separator=True)
        self.tooltips["num_doors"] = ToolTip(self.entries["num_doors"][1], translations[self.current_language]["tooltips"]["num_doors"], self)
        current_row= self.create_label_and_entry(self.entries_frame, "right_vpiece_width", current_row)
        self.tooltips["right_vpiece_width"] = ToolTip(self.entries["right_vpiece_width"][1], translations[self.current_language]["tooltips"]["right_vpiece_width"], self)
        current_row= self.create_label_and_entry(self.entries_frame, "left_vpiece_width", current_row)
        self.tooltips["left_vpiece_width"] = ToolTip(self.entries["left_vpiece_width"][1], translations[self.current_language]["tooltips"]["left_vpiece_width"], self)
        current_row= self.create_label_and_entry(self.entries_frame, "upper_hpiece_width", current_row)
        self.tooltips["upper_hpiece_width"] = ToolTip(self.entries["upper_hpiece_width"][1], translations[self.current_language]["tooltips"]["upper_hpiece_width"], self)
        current_row= self.create_label_and_entry(self.entries_frame, "lower_hpiece_width", current_row, add_separator=True)
        self.tooltips["lower_hpiece_width"] = ToolTip(self.entries["lower_hpiece_width"][1], translations[self.current_language]["tooltips"]["lower_hpiece_width"], self)
        current_row= self.create_label_and_entry(self.entries_frame, "ub_wood_width", current_row, add_separator=True)
        self.tooltips["ub_wood_width"] = ToolTip(self.entries["ub_wood_width"][1], translations[self.current_language]["tooltips"]["ub_wood_width"], self)
        
        current_row= self.create_label_and_entry(self.entries_frame, "edge_sealing_type", current_row, "edge_sealing_type")
        self.entries["edge_sealing_type"][1]['values'] = ("6mm 實木", "4mm 白木", "6mm 鋁封邊", "1mm 鐡封邊 + 1mm 石墨片", "1mm 鐡封邊", "1mm 不織布", "0.8mm 美耐板", "0.5mm ABS", "1mm 鋁封邊")
        self.tooltips["edge_sealing_type"] = ToolTip(self.entries["edge_sealing_type"][1], translations[self.current_language]["tooltips"]["edge_sealing_type"], self)

        current_row= self.create_label_and_entry(self.entries_frame, "edge_sealing_thickness", current_row, add_separator=True)
        self.tooltips["edge_sealing_thickness"] = ToolTip(self.entries["edge_sealing_thickness"][1], translations[self.current_language]["tooltips"]["edge_sealing_thickness"], self)
        current_row= self.create_label_and_entry(self.entries_frame, "electric_lock_name", current_row, "electric_lock_name")
        self.entries["electric_lock_name"][1]['values'] = list(electric_locks.keys())
        self.tooltips["electric_lock_name"] = ToolTip(self.entries["electric_lock_name"][1], translations[self.current_language]["tooltips"]["electric_lock_name"], self)
        current_row= self.create_label_and_entry(self.entries_frame, "box_lock_name", current_row, "box_lock_name")
        self.entries["box_lock_name"][1]['values'] = list(box_locks.keys())
        self.tooltips["box_lock_name"] = ToolTip(self.entries["box_lock_name"][1], translations[self.current_language]["tooltips"]["box_lock_name"], self)

        current_row= self.create_label_and_entry(self.entries_frame, "lock_length", current_row)
        self.tooltips["lock_length"] = ToolTip(self.entries["lock_length"][1], translations[self.current_language]["tooltips"]["lock_length"], self)
        current_row= self.create_label_and_entry(self.entries_frame, "lock_height", current_row)
        self.tooltips["lock_height"] = ToolTip(self.entries["lock_height"][1], translations[self.current_language]["tooltips"]["lock_height"], self)
        current_row= self.create_label_and_entry(self.entries_frame, "lock_direction", current_row, "lock_direction", add_separator= True)
        self.entries["lock_direction"][1]['values'] = ("top", "bottom")
        self.tooltips["lock_direction"] = ToolTip(self.entries["lock_direction"][1], translations[self.current_language]["tooltips"]["lock_direction"], self)
        self.entries["lock_direction"][1].bind("<<ComboboxSelected>>", self.update_inputs)

        current_row= self.create_label_and_entry(self.entries_frame, "concealed_door_closer_name", current_row, "concealed_door_closer_name")
        self.entries["concealed_door_closer_name"][1]['values'] = list(concealeds.keys())
        self.tooltips["concealed_door_closer_name"] = ToolTip(self.entries["concealed_door_closer_name"][1], translations[self.current_language]["tooltips"]["concealed_door_closer_name"], self)
        current_row= self.create_label_and_entry(self.entries_frame, "concealed_wood_width", current_row, add_separator=True)
        self.tooltips["concealed_wood_width"] = ToolTip(self.entries["concealed_wood_width"][1], translations[self.current_language]["tooltips"]["concealed_wood_width"],self)

        current_row= self.create_label_and_entry(self.entries_frame, "slats_width", current_row)
        self.tooltips["slats_width"] = ToolTip(self.entries["slats_width"][1], translations[self.current_language]["tooltips"]["slats_width"], self)
        current_row= self.create_label_and_entry(self.entries_frame, "gap_width", current_row)
        self.tooltips["gap_width"] = ToolTip(self.entries["gap_width"][1], translations[self.current_language]["tooltips"]["gap_width"], self)
        # current_row= self.create_label_and_entry(self.entries_frame, "gap_wood_lock", current_row)
        # self.tooltips["gap_wood_lock"] = ToolTip(self.entries["gap_wood_lock"][1], translations[self.current_language]["tooltips"]["gap_wood_lock"],self)
        current_row= self.create_label_and_entry(self.entries_frame, "reinforce_wood", current_row)
        self.tooltips["reinforce_wood"] = ToolTip(self.entries["reinforce_wood"][1], translations[self.current_language]["tooltips"]["reinforce_wood"],self)
        
        current_row= self.create_label_and_entry(self.entries_frame, "max_height", current_row)
        self.tooltips["max_height"] = ToolTip(self.entries["max_height"][1], translations[self.current_language]["tooltips"]["max_height"], self)
        current_row= self.create_label_and_entry(self.entries_frame, "min_height", current_row, add_separator=True)
        self.tooltips["min_height"] = ToolTip(self.entries["min_height"][1], translations[self.current_language]["tooltips"]["min_height"], self)

        current_row= self.create_label_and_entry(self.entries_frame, "lock_offset_bottom", current_row)
        current_row= self.create_label_and_entry(self.entries_frame, "frame_height", current_row)
        self.tooltips["frame_height"] = ToolTip(self.entries["frame_height"][1], translations[self.current_language]["tooltips"]["frame_height"], self)
        current_row= self.create_label_and_entry(self.entries_frame, "frame_width", current_row)
        self.tooltips["frame_width"] = ToolTip(self.entries["frame_width"][1], translations[self.current_language]["tooltips"]["frame_width"], self)

        self.calculate_button = ttk.Button(self.entries_frame, text=translations[self.current_language]["calculate"], command=self.calculate_material)
        self.calculate_button.grid(row=current_row, column=0, columnspan=2, padx=(0, 500))
        current_row +=1
        
        scrollbar = ttk.Scrollbar(frame)
        # scrollbar.grid(row=current_row, column=2, sticky="nsew", padx=(0, 0), pady=(10, 10))
        
        # === Create Result Text (Left Side of Results Frame) ===
        self.result_text = tk.Text(self.results_frame, width=50, height=30, font=("Microsoft YaHei", 12), fg="dim gray", wrap="word", tabs="7c")
        self.result_text.grid(row=0, column=0, sticky="nsew", padx=(0, 0), pady=(5, 5))
        
        # === Create Result Image (Right Side of Results Frame) ===
        self.result_image = tk.Text(self.results_frame, width=40, height=30)
        self.result_image.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=(5, 5))
        
        # === Configure Layout Expansion ===
        self.root.grid_columnconfigure(0, weight=1)
        self.entries_frame.grid_columnconfigure(0, weight=0)
        self.entries_frame.grid_columnconfigure(1, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)  # Text takes more space
        self.results_frame.grid_columnconfigure(1, weight=2)  # Image takes less space
        
        scrollbar.config(command=self.result_text.yview)
        scrollbar.config(command=self.result_image.yview)
        trademark_label = ttk.Label(self.entries_frame, text="© 2024 HBB", font=("Microsoft YaHei", 8, "italic"))
        trademark_label.grid(row=current_row-1, column=0, columnspan=3, padx=(0, 1000))
        
        self.update_inputs()
            
    def create_label_and_entry(self, entries_frame, key, row, entry_type="entry", add_separator=False):
        style = ttk.Style()
        style.configure("CustomLabel.TLabel", foreground="gray30")
        label = ttk.Label(entries_frame, text=translations[self.current_language][key], font=("Microsoft YaHei", 12), width=35, anchor="w", style="CustomLabel.TLabel")
        label.grid(row=row, column=0, sticky="w", padx=(0, 0))
        if entry_type == "entry":
            entry = ttk.Entry(entries_frame, font=("Microsoft YaHei", 12))
        elif entry_type == "category" or entry_type == "structure_type" or entry_type == "door_type" or entry_type == "edge_sealing_type" or entry_type == "electric_lock_name"\
            or entry_type == "lock_direction" or entry_type == "concealed_door_closer_name" or entry_type == "box_lock_name":
            entry = ttk.Combobox(entries_frame, font=("Microsoft YaHei", 12))
        entry.grid(row=row, column=1, sticky="w", padx=(0, 0), pady=(0, 7))
        self.entries[key] = (label, entry)  
        # Add an optional separator after this row
        separator = None
        if add_separator:
            separator = ttk.Separator(entries_frame, orient="horizontal")
            separator.grid(row=row + 1, column=0, columnspan=2, sticky="nsew", padx=(0, 530), pady=5)
            self.entries[f"{key}_separator"] = separator  # Store separator in entries dictionary
    
        return row + (2 if add_separator else 1)  # Increment rows correctly

    def update_inputs(self, *args):
        
        all_fields = [
            "door_type", "structure_type", "slats_width", "gap_width", "left_vpiece_width",
            "electric_lock_name", "lock_length", "lock_height", "lock_direction",
            "lock_offset_bottom", "max_height", "min_height", "box_lock_name",
            "concealed_door_closer_name", "reinforce_wood", "ub_wood_width", "concealed_wood_width"
        ]
        self.show_entries(all_fields, False)
        
        category = self.entries["category"][1].get().strip().lower()
        structure_type = self.entries["structure_type"][1].get().strip().lower()
        door_type = self.entries["door_type"][1].get().strip().lower()
        lock_direction = self.entries["lock_direction"][1].get().strip().lower()
        mode = self.mode_selection.get()
        if category == self.fireproof_label:
            self.show_entries(["door_type"], True)
            self.show_entries(["structure_type"], False)
            self.entries["door_type"][1]['values'] = (
                self.simple_label,
                self.electric_lock_label,
                self.box_lock_label
            )
            self.ub_mode_button.grid()
            # self.entries["lock_direction"][1]['values'] = (
            #     self.top_label,
            #     self.bottom_label
            # )
            if mode == "UB":
                self.show_entries(["structure_type", "frame_height"], False)
                self.show_entries(["num_doors", "right_vpiece_width", "left_vpiece_width", "door_type", "max_height", "min_height", "ub_wood_width"], True)
                if door_type == self.simple_label:
                    self.show_entries(["left_vpiece_width"], True)
                elif door_type == self.electric_lock_label:
                    self.show_entries(["electric_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "concealed_wood_width"], True)
                    self.show_entries(["left_vpiece_width"], False)
                    if lock_direction == self.bottom_label:
                        self.show_entries(["concealed_door_closer_name", "concealed_wood_width"], False)
                        self.entries["concealed_door_closer_name"][1].delete(0, 'end')
                        self.entries["concealed_door_closer_name"][1].insert(0, '')
                        self.entries["concealed_wood_width"][1].delete(0, 'end')
                        self.entries["concealed_wood_width"][1].insert(0, '')
                    elif lock_direction == self.top_label:
                        self.show_entries(["concealed_door_closer_name", "concealed_wood_width"], True)
                elif door_type == self.box_lock_label:
                    self.show_entries(["box_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name"], True)
                    self.show_entries(["left_vpiece_width"], False)
                    if lock_direction == self.bottom_label:
                        self.show_entries(["concealed_door_closer_name", "concealed_wood_width"], False)
                        self.entries["concealed_door_closer_name"][1].delete(0, 'end')
                        self.entries["concealed_door_closer_name"][1].insert(0, '')
                        self.entries["concealed_wood_width"][1].delete(0, 'end')
                        self.entries["concealed_wood_width"][1].insert(0, '')
                    elif lock_direction == self.top_label:
                        self.show_entries(["concealed_door_closer_name", "concealed_wood_width"], True)
                else:
                    self.show_entries(["electric_lock_name", "lock_length", "lock_height", "lock_direction", "lock_offset_bottom",
                                       "box_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "reinforce_wood", "concealed_wood_width"], False)
                    
            else:
                self.show_entries(["structure_type", "door_type"], True)
                self.show_entries(["num_doors", "right_vpiece_width", "left_vpiece_width", "frame_height"], True)
                self.show_entries(["max_height", "min_height", "structure_type"], False)
                if door_type == self.simple_label:
                    self.show_entries(["left_vpiece_width"], True)
                elif door_type == self.electric_lock_label:
                    self.show_entries(["electric_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "concealed_wood_width"], True)
                    self.show_entries(["left_vpiece_width"], False)
                # elif door_type == self.ub_label:
                #     self.show_entries(["max_height", "min_height"], True)
                elif door_type == self.box_lock_label:
                    self.show_entries(["box_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "concealed_wood_width"], True)
                    self.show_entries(["left_vpiece_width"], False)
                else:
                    self.show_entries(["electric_lock_name", "lock_length", "lock_height", "lock_direction", "lock_offset_bottom",
                                        "max_height", "min_height", "box_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "reinforce_wood", "concealed_wood_width"], False)
            
            
        elif category == self.non_fireproof_label:
            self.show_entries(["door_type", "structure_type"], True)
            self.entries["door_type"][1]['values'] = (
                self.simple_label,
                self.electric_lock_label,
                self.box_lock_label
            )
            self.normal_mode_button.grid()
            self.ub_mode_button.grid_remove()
            self.mode_selection.set("Normal")
            if structure_type == self.yipaiyikong_label:
                self.show_entries(["slats_width", "gap_width"], True)
                if door_type == self.simple_label:
                    self.show_entries(["left_vpiece_width"], True)
                elif door_type == self.electric_lock_label:
                    self.show_entries(["electric_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "left_vpiece_width", "concealed_wood_width"], True)
                elif door_type == self.box_lock_label:
                    self.show_entries(["box_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "left_vpiece_width", "concealed_wood_width"], True)
                else:
                    self.show_entries(["electric_lock_name", "lock_length", "lock_height", "lock_direction", "lock_offset_bottom",
                                        "max_height", "min_height", "box_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "reinforce_wood", "concealed_wood_width"], False)
            elif structure_type == self.honeycomb_board_label:
                self.show_entries(["lock_height"], True)
                self.show_entries(["slats_width"], False)
                if door_type == self.simple_label:
                    self.show_entries(["left_vpiece_width", "lock_height", "reinforce_wood"], True)
                elif door_type == self.electric_lock_label:
                    self.show_entries(["electric_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "left_vpiece_width", "concealed_wood_width"], True)
                elif door_type == self.box_lock_label:
                    self.show_entries(["box_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "left_vpiece_width", "concealed_wood_width"], True)
                else:
                    self.show_entries(["electric_lock_name", "lock_length", "lock_height", "lock_direction", "lock_offset_bottom",
                                        "max_height", "min_height", "box_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "concealed_wood_width"], False)
            elif structure_type == self.honeycomb_paper_label:
                self.show_entries(["lock_height"], True)
                self.show_entries(["slats_width"], False)
                if door_type == self.simple_label:
                    self.show_entries(["left_vpiece_width", "lock_height", "reinforce_wood"], True)
                elif door_type == self.electric_lock_label:
                    self.show_entries(["electric_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "left_vpiece_width", "concealed_wood_width"], True)
                elif door_type == self.box_lock_label:
                    self.show_entries(["box_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "left_vpiece_width", "concealed_wood_width"], True)
                else:
                    self.show_entries(["electric_lock_name", "lock_length", "lock_height", "lock_direction", "lock_offset_bottom",
                                        "max_height", "min_height", "box_lock_name", "lock_height", "lock_direction", "concealed_door_closer_name", "concealed_wood_width"], False)
        

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
        self.fireproof_label = translations[self.current_language]["fireproof"].lower()
        self.non_fireproof_label = translations[self.current_language]["non_fireproof"].lower()
        self.honeycomb_paper_label = translations[self.current_language]["honeycomb_paper"].lower()
        self.honeycomb_board_label = translations[self.current_language]["honeycomb_board"].lower()

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
        self.help_menu.entryconfig(0, label=translations[self.current_language]["app_help"])
        self.help_menu.entryconfig(1, label=translations[self.current_language]["simple_help"])
        self.help_menu.entryconfig(2, label=translations[self.current_language]["ub_help"])
        self.help_menu.entryconfig(3, label=translations[self.current_language]["electric_lock_help"])
        self.help_menu.entryconfig(4, label=translations[self.current_language]["box_lock_help"])
        
        self.menu_bar.entryconfig(4, label=translations[self.current_language]["Guidance"])
        self.view_menu.entryconfig(0, label=translations[self.current_language]["Enable_"])
        
        self.calculate_button.config(text=translations[self.current_language]["calculate"])
        
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
                            
        self.entries["category"][1]['values'] = (
            translations[self.current_language]["fireproof"],
            translations[self.current_language]["non_fireproof"]
        )
        self.entries["structure_type"][1]['values'] = (
            translations[self.current_language]["honeycomb_paper"],
            translations[self.current_language]["yipaiyikong"],
            translations[self.current_language]["honeycomb_board"]
        )
        self.entries["door_type"][1]['values'] = (
        translations[self.current_language]["simple"],
        # translations[self.current_language]["UB"],
        translations[self.current_language]["electric lock"],
        translations[self.current_language]["box lock"]
        # translations[self.current_language]["yipaiyikong"]
        )
        self.entries["edge_sealing_type"][1]['values'] = ("6mm 實木", "4mm 白木", "6mm 鋁封邊", "1mm 鐡封邊 + 1mm 石墨片", "1mm 鐡封邊", "1mm 不織布", "0.8mm 美耐板", "0.5mm ABS", "1mm 鋁封邊")
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
        
        if hasattr(self, "normal_mode_button"):
            self.normal_mode_button.config(text=translations[self.current_language]["normal_mode"])
        if hasattr(self, "ub_mode_button"):
            self.ub_mode_button.config(text=translations[self.current_language]["ub_mode"])
        if hasattr(self, "mode_selection"):
            self.mode_selection_label.config(text=translations[self.current_language]["mode_selection"])
        
    def add_annotations(self, image_path, vertical_length, horizontal_length, door_type, outer_wood_upper, inner_wood_upper, outer_wood_bottom, 
                        inner_wood_bottom, concealed_length, very_upper_horizontal_piece_length, concealed_door_closer_name, slats_count,
                        category, gap_wood_lock_length, reinforce_wood, gap_length_bottom, gap_length_upper, gap_wood_lock, gap_length, mode, reinforce_concealed_wood_length):
        # Open the image file
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        structure_type = self.entries["structure_type"][1].get().strip().lower()
        
        # Define font and size
        font = ImageFont.truetype("DejaVuSans.ttf", 24)  # Ensure the font file is available
        
        if concealed_door_closer_name in concealeds:
            concealed_length = concealeds[concealed_door_closer_name]['length']
        else:
            # Set default values if no concealed door closer is selected
            concealed_length = 0

        # Annotation positions can be adjusted based on door_type
        '''################################################################### Fireproof!!!#########################################################'''
        
        if category == self.fireproof_label and mode != "UB" and door_type == self.simple_label:
            annotations = {
            "*mm (milimeter)": ((5, 5), "black"),
            f"{horizontal_length}": ((190, 35), "red"),   # Position and color for horizontal length
            f"{vertical_length}": ((40, 210), "mediumblue")     # Position and color for vertical length
        }
        elif category == self.fireproof_label and door_type == self.electric_lock_label and concealed_length > 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{very_upper_horizontal_piece_length}": ((160, 30), "magenta"),
                f"{outer_wood_upper}": ((45, 190), "limegreen"),
                f"{inner_wood_upper}": ((45, 80), "blueviolet"),
                f"{outer_wood_bottom}": ((45, 280), "orange"),
                f"{inner_wood_bottom}": ((45, 380), "saddlebrown"),
                f"{vertical_length}": ((400, 260), "mediumblue"),
                f"{horizontal_length}": ((200, 430), "red"),
                f"{concealed_length}": ((300, 20), "black")
            }
        elif category == self.fireproof_label and door_type == self.electric_lock_label and concealed_length == 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((160, 30), "red"),
                f"{outer_wood_upper}": ((45, 190), "limegreen"),
                f"{inner_wood_upper}": ((45, 80), "blueviolet"),
                f"{outer_wood_bottom}": ((45, 280), "orange"),
                f"{inner_wood_bottom}": ((45, 380), "saddlebrown"),
                f"{vertical_length}": ((400, 260), "mediumblue")
            }
        elif category == self.fireproof_label and door_type == self.box_lock_label and concealed_length > 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{very_upper_horizontal_piece_length}": ((160, 30), "fuchsia"),
                f"{outer_wood_upper}": ((45, 190), "limegreen"),
                f"{inner_wood_upper}": ((45, 80), "blueviolet"),
                f"{outer_wood_bottom}": ((45, 280), "orange"),
                f"{inner_wood_bottom}": ((45, 380), "saddlebrown"),
                f"{vertical_length}": ((400, 260), "mediumblue"),
                f"{horizontal_length}": ((200, 430), "red"),
                f"{concealed_length}": ((300, 20), "black")
            }
        elif category == self.fireproof_label and door_type == self.box_lock_label and concealed_length == 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((160, 30), "red"),
                f"{outer_wood_upper}": ((45, 190), "limegreen"),
                f"{inner_wood_upper}": ((45, 80), "blueviolet"),
                f"{outer_wood_bottom}": ((45, 280), "orange"),
                f"{inner_wood_bottom}": ((45, 380), "saddlebrown"),
                f"{vertical_length}": ((400, 260), "mediumblue")
            }
        elif category == self.fireproof_label and mode == "UB" and door_type == self.simple_label:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((120, 35), "red"),   # Position and color for horizontal length
                f"{vertical_length}": ((10, 210), "mediumblue")
                }
            
########################################## Non Fireproof!!##############################################
        elif category == self.non_fireproof_label and structure_type == self.honeycomb_board_label and door_type == self.simple_label:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((170, 40), "red"),
                f"{vertical_length}": ((40, 200), "mediumblue"),
                f"{reinforce_wood}": ((370, 190), "limegreen"),
                f"{gap_length_upper}": ((230,125), "saddlebrown"),
                f"{gap_length_bottom}": ((230,325), "saddlebrown")
                }
        elif category == self.non_fireproof_label and structure_type == self.honeycomb_board_label and door_type == self.electric_lock_label and concealed_length == 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((200, 33), "red"),
                f"{outer_wood_upper}": ((10, 130), "limegreen"),
                f"{outer_wood_bottom}": ((10, 320), "orange"),
                f"{gap_wood_lock_length}": ((50, 430), "fuchsia"),
                f"{vertical_length}": ((390, 200), "mediumblue"),
                f"一{gap_length}": ((230,125), "saddlebrown"),
                f"二{gap_length}": ((230,220), "saddlebrown"),
                f"三{gap_length}": ((230,325), "saddlebrown")
            }
        elif category == self.non_fireproof_label and structure_type == self.honeycomb_board_label and door_type == self.electric_lock_label and concealed_length > 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((300, 430), "red"),
                f"{outer_wood_upper}": ((10, 130), "limegreen"),
                f"{outer_wood_bottom}": ((10, 320), "orange"),
                f"{gap_wood_lock_length}": ((50, 430), "fuchsia"),
                f"{vertical_length}": ((390, 200), "mediumblue"),
                f"一{gap_length}": ((230,125), "saddlebrown"),
                f"二{gap_length}": ((230,220), "saddlebrown"),
                f"三{gap_length}": ((230,325), "saddlebrown"),
                f"{concealed_length}": ((280, 25), "black"),
                f"{very_upper_horizontal_piece_length}": ((150, 30), "fuchsia"),
                f"{reinforce_concealed_wood_length}": ((390, 65), "black")
            }
        elif category == self.non_fireproof_label and structure_type == self.honeycomb_board_label and door_type == self.box_lock_label and concealed_length == 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((200, 33), "red"),
                f"{outer_wood_upper}": ((10, 130), "limegreen"),
                f"{outer_wood_bottom}": ((10, 320), "orange"),
                f"{gap_wood_lock_length}": ((50, 430), "fuchsia"),
                f"{vertical_length}": ((390, 200), "mediumblue"),
                f"一{gap_length}": ((230,125), "saddlebrown"),
                f"二{gap_length}": ((230,220), "saddlebrown"),
                f"三{gap_length}": ((230,325), "saddlebrown")
            }
        elif category == self.non_fireproof_label and structure_type == self.honeycomb_board_label and door_type == self.box_lock_label and concealed_length > 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((300, 430), "red"),
                f"{outer_wood_upper}": ((10, 130), "limegreen"),
                f"{outer_wood_bottom}": ((10, 320), "orange"),
                f"{gap_wood_lock_length}": ((50, 430), "fuchsia"),
                f"{vertical_length}": ((390, 200), "mediumblue"),
                f"一{gap_length}": ((230,125), "saddlebrown"),
                f"二{gap_length}": ((230,220), "saddlebrown"),
                f"三{gap_length}": ((230,325), "saddlebrown"),
                f"{concealed_length}": ((280, 25), "black"),
                f"{very_upper_horizontal_piece_length}": ((150, 30), "fuchsia"),
                f"{reinforce_concealed_wood_length}": ((390,65), "black")
            }
######################################################################################
        elif category == self.non_fireproof_label and structure_type == self.honeycomb_paper_label and door_type == self.simple_label:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((180, 40), "red"),
                f"{vertical_length}": ((40, 200), "mediumblue"),
                f"{reinforce_wood}": ((370, 190), "limegreen"),
                f"一{gap_length_upper}": ((190,100), "saddlebrown"),
                f"二{gap_length_upper}": ((190,155), "saddlebrown"),
                f"三{gap_length_bottom}": ((190,300), "saddlebrown"),
                f"四{gap_length_bottom}": ((190,360), "saddlebrown")
                }
        elif category == self.non_fireproof_label and structure_type == self.honeycomb_paper_label and door_type == self.electric_lock_label and concealed_length == 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((200, 33), "red"),
                f"{outer_wood_upper}": ((10, 130), "limegreen"),
                f"{outer_wood_bottom}": ((10, 320), "orange"),
                f"{gap_wood_lock_length}": ((50, 430), "fuchsia"),
                f"{vertical_length}": ((390, 200), "mediumblue"),
                f"一{gap_length}": ((190,100), "saddlebrown"),
                f"二{gap_length}": ((190,155), "saddlebrown"),
                f"三{gap_length}": ((190,280), "saddlebrown"),
                f"四{gap_length}": ((190,360), "saddlebrown"),
                f"五{gap_length}": ((190,220), "saddlebrown")
            }
        elif category == self.non_fireproof_label and structure_type == self.honeycomb_paper_label and door_type == self.electric_lock_label and concealed_length > 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((300, 430), "red"),
                f"{outer_wood_upper}": ((10, 130), "limegreen"),
                f"{outer_wood_bottom}": ((10, 320), "orange"),
                f"{gap_wood_lock_length}": ((50, 430), "fuchsia"),
                f"{vertical_length}": ((390, 200), "mediumblue"),
                f"{vertical_length}": ((390, 200), "mediumblue"),
                f"一{gap_length}": ((190,125), "saddlebrown"),
                f"二{gap_length}": ((190,175), "saddlebrown"),
                f"三{gap_length}": ((190,300), "saddlebrown"),
                f"四{gap_length}": ((190,360), "saddlebrown"),
                f"五{gap_length}": ((190,230), "saddlebrown"),
                f"{concealed_length}": ((280, 25), "black"),
                f"{very_upper_horizontal_piece_length}": ((150, 30), "fuchsia"),
                f"{reinforce_concealed_wood_length}": ((390,65), "black")
            }
        elif category == self.non_fireproof_label and structure_type == self.honeycomb_paper_label and door_type == self.box_lock_label and concealed_length == 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((200, 33), "red"),
                f"{outer_wood_upper}": ((10, 130), "limegreen"),
                f"{outer_wood_bottom}": ((10, 320), "orange"),
                f"{gap_wood_lock_length}": ((50, 430), "fuchsia"),
                f"{vertical_length}": ((390, 200), "mediumblue"),
                f"一{gap_length}": ((190,100), "saddlebrown"),
                f"二{gap_length}": ((190,155), "saddlebrown"),
                f"三{gap_length}": ((190,280), "saddlebrown"),
                f"四{gap_length}": ((190,360), "saddlebrown"),
                f"五{gap_length}": ((190,220), "saddlebrown")
            }
        elif category == self.non_fireproof_label and structure_type == self.honeycomb_paper_label and door_type == self.box_lock_label and concealed_length > 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((300, 430), "red"),
                f"{outer_wood_upper}": ((10, 130), "limegreen"),
                f"{outer_wood_bottom}": ((10, 320), "orange"),
                f"{gap_wood_lock_length}": ((50, 430), "fuchsia"),
                f"{vertical_length}": ((390, 200), "mediumblue"),
                f"{vertical_length}": ((390, 200), "mediumblue"),
                f"一{gap_length}": ((190,125), "saddlebrown"),
                f"二{gap_length}": ((190,175), "saddlebrown"),
                f"三{gap_length}": ((190,300), "saddlebrown"),
                f"四{gap_length}": ((190,360), "saddlebrown"),
                f"五{gap_length}": ((190,230), "saddlebrown"),
                f"{concealed_length}": ((280, 25), "black"),
                f"{very_upper_horizontal_piece_length}": ((150, 30), "fuchsia"),
                f"{reinforce_concealed_wood_length}": ((390,65), "black")
            }
#####################################################################################
        elif category == self.non_fireproof_label and structure_type == self.yipaiyikong_label and door_type == self.simple_label:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((150, 30), "red"),   # Position and color for horizontal length
                f"{vertical_length}": ((15, 210), "mediumblue"),
                f"{slats_count} pcs": ((370, 260), "mediumturquoise")
                }
        elif category == self.non_fireproof_label and structure_type == self.yipaiyikong_label and door_type == self.electric_lock_label and concealed_length == 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((200, 33), "red"),
                f"{outer_wood_upper}": ((10, 130), "limegreen"),
                f"{outer_wood_bottom}": ((10, 320), "orange"),
                f"{gap_wood_lock_length}": ((50, 430), "fuchsia"),
                f"{vertical_length}": ((390, 190), "mediumblue"),
                f"{slats_count} pcs": ((390, 320), "mediumturquoise")
            }
        elif category == self.non_fireproof_label and structure_type == self.yipaiyikong_label and door_type == self.electric_lock_label and concealed_length > 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{very_upper_horizontal_piece_length}": ((150, 30), "fuchsia"),
                f"{outer_wood_upper}": ((10, 130), "limegreen"),
                f"{outer_wood_bottom}": ((10, 320), "orange"),
                f"{gap_wood_lock_length}": ((50, 430), "fuchsia"),
                f"{vertical_length}": ((390, 190), "mediumblue"),
                f"{horizontal_length}": ((300, 430), "red"),
                f"{concealed_length}": ((280, 20), "black"),
                f"{slats_count} pcs": ((390, 320), "mediumturquoise"),
                f"{reinforce_concealed_wood_length}": ((390,65), "black")
            }
        elif category == self.non_fireproof_label and structure_type == self.yipaiyikong_label and door_type == self.box_lock_label and concealed_length == 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{horizontal_length}": ((200, 33), "red"),
                f"{outer_wood_upper}": ((10, 130), "limegreen"),
                f"{outer_wood_bottom}": ((10, 320), "orange"),
                f"{gap_wood_lock_length}": ((50, 430), "fuchsia"),
                f"{vertical_length}": ((390, 190), "mediumblue"),
                f"{slats_count} pcs": ((390, 320), "mediumturquoise")
            }
        elif category == self.non_fireproof_label and structure_type == self.yipaiyikong_label and door_type == self.box_lock_label and concealed_length > 0:
            annotations = {
                "*mm (milimeter)": ((5, 5), "black"),
                f"{very_upper_horizontal_piece_length}": ((150, 30), "fuchsia"),
                f"{outer_wood_upper}": ((10, 130), "limegreen"),
                f"{outer_wood_bottom}": ((10, 320), "orange"),
                f"{gap_wood_lock_length}": ((50, 430), "fuchsia"),
                f"{vertical_length}": ((390, 190), "mediumblue"),
                f"{horizontal_length}": ((300, 430), "red"),
                f"{concealed_length}": ((280, 20), "black"),
                f"{slats_count} pcs": ((390, 320), "mediumturquoise"),
                f"{reinforce_concealed_wood_length}": ((390,65), "black")
            }

        for text, (position, color) in annotations.items():
            draw.text(position, text, fill=color, font=font)

        # Save the modified image
        annotated_image_path = image_path.replace(".png", "_annotated.png")
        image.save(annotated_image_path)
        
        return annotated_image_path

    def calculate_material(self):
        try:
            mode = self.mode_selection.get()
            # Initialize shared variables
            frame_height = frame_width = max_height = min_height = concealed_wood_piece_width = None
            
            self.validate_inputs()
            # Proceed with calculation if validation passes
            # self.perform_calculation()
        
     
            door_type = self.entries["door_type"][1].get().strip().lower()
            category = self.entries["category"][1].get().strip().lower()
            num_doors = safe_int(self.entries["num_doors"][1].get())
            structure_type = self.entries["structure_type"][1].get().strip().lower()
            category = self.entries["category"][1].get().strip().lower()
            

            right_vertical_piece_width = safe_int(self.entries["right_vpiece_width"][1].get())
            if category == self.fireproof_label:
                if door_type != self.electric_lock_label and door_type != self.box_lock_label:
                    left_vertical_piece_width = safe_int(self.entries["left_vpiece_width"][1].get())
                else:
                    left_vertical_piece_width = 70
            elif category == self.non_fireproof_label:
                if door_type == self.electric_lock_label or door_type == self.box_lock_label:
                    left_vertical_piece_width = safe_int(self.entries["left_vpiece_width"][1].get())
                else:
                    left_vertical_piece_width = safe_int(self.entries["left_vpiece_width"][1].get())

                
            upper_horizontal_piece_width = safe_int(self.entries["upper_hpiece_width"][1].get())
            lower_horizontal_piece_width = safe_int(self.entries["lower_hpiece_width"][1].get())
            ub_wood_piece_width = safe_int(self.entries["ub_wood_width"][1].get())
            

            
            edge_sealing_options = {
                "6mm 實木": 6,
                "6mm 鋁封邊": 6,
                "0.5mm ABS": 0.5,
                "1mm 鐡封邊 + 1mm 石墨片": 2,
                "1mm 鐡封邊": 1,
                "4mm 白木": 4,
                "0.8mm 美耐板": 0.8,
                "1mm 不織布": 1,
                "1mm 鋁封邊": 1
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
            # gap_wood_lock = 0
            reinforce_wood = 0
            lock_height = 0
            lock_length = 0

            if category == self.fireproof_label and mode != "UB":
                if door_type == self.box_lock_label:
                    box_lock_name = self.entries["box_lock_name"][1].get().strip()
                    concealed_door_closer_name = self.entries["concealed_door_closer_name"][1].get().strip()
                    if box_lock_name in box_locks:
                        lock_length = box_locks[box_lock_name]['length']
                        lock_offset_bottom = box_locks[box_lock_name]['offset_bottom']
                        lock_offset_top = box_locks[box_lock_name]['offset_top']
                    elif concealed_door_closer_name in concealeds:
                        concealed_length = concealeds[concealed_door_closer_name]['length']
                    else:
                        lock_length = safe_int(self.entries["lock_length"][1].get())
                        lock_offset_bottom = safe_int(self.entries["lock_offset_bottom"][1].get())
                        lock_offset_top = lock_length - lock_offset_bottom
                        # concealed_length = ""
                    box_lock_height = safe_int(self.entries["lock_height"][1].get())
                    lock_direction = self.entries["lock_direction"][1].get().strip().lower()
                    frame_height = safe_int(self.entries["frame_height"][1].get()) if frame_height is None else frame_height
                    frame_width = safe_int(self.entries["frame_width"][1].get()) if frame_width is None else frame_width
                    concealed_wood_piece_width = safe_int(self.entries["concealed_wood_width"][1].get()) if concealed_wood_piece_width is None else concealed_wood_piece_width
                elif door_type == self.electric_lock_label:
                    electric_lock_name = self.entries["electric_lock_name"][1].get().strip()
                    concealed_door_closer_name = self.entries["concealed_door_closer_name"][1].get().strip()
                    if electric_lock_name in electric_locks:
                        lock_length = electric_locks[electric_lock_name]['length']
                        lock_offset_bottom = electric_locks[electric_lock_name]['offset_bottom']
                        lock_offset_top = electric_locks[electric_lock_name]['offset_top']
                    elif concealed_door_closer_name in concealeds:
                        concealed_length = concealeds[concealed_door_closer_name]['length']
                    else:
                        lock_length = safe_int(self.entries["lock_length"][1].get())
                        lock_offset_bottom = safe_int(self.entries["lock_offset_bottom"][1].get())
                        lock_offset_top = lock_length - lock_offset_bottom
                    electric_lock_height = safe_int(self.entries["lock_height"][1].get())
                    lock_direction = self.entries["lock_direction"][1].get().strip().lower()
                    frame_height = safe_int(self.entries["frame_height"][1].get()) if frame_height is None else frame_height
                    frame_width = safe_int(self.entries["frame_width"][1].get()) if frame_width is None else frame_width
                    concealed_wood_piece_width = safe_int(self.entries["concealed_wood_width"][1].get()) if concealed_wood_piece_width is None else concealed_wood_piece_width
                else:
                    frame_height = safe_int(self.entries["frame_height"][1].get()) if frame_height is None else frame_height
                    frame_width = safe_int(self.entries["frame_width"][1].get()) if frame_width is None else frame_width
                        
            elif category == self.fireproof_label and mode == "UB":
                if door_type == self.box_lock_label:
                    box_lock_name = self.entries["box_lock_name"][1].get().strip()
                    concealed_door_closer_name = self.entries["concealed_door_closer_name"][1].get().strip()
                    if box_lock_name in box_locks:
                        lock_length = box_locks[box_lock_name]['length']
                        lock_offset_bottom = box_locks[box_lock_name]['offset_bottom']
                        lock_offset_top = box_locks[box_lock_name]['offset_top']
                    elif concealed_door_closer_name in concealeds:
                        concealed_length = concealeds[concealed_door_closer_name]['length']
                    else:
                        lock_length = safe_int(self.entries["lock_length"][1].get())
                        lock_offset_bottom = safe_int(self.entries["lock_offset_bottom"][1].get())
                        lock_offset_top = lock_length - lock_offset_bottom
                        # concealed_length = ""
                    box_lock_height = safe_int(self.entries["lock_height"][1].get())
                    lock_direction = self.entries["lock_direction"][1].get().strip().lower()
                    # frame_height = safe_int(self.entries["frame_height"][1].get()) if frame_height is None else frame_height
                    # frame_width = safe_int(self.entries["frame_width"][1].get()) if frame_width is None else frame_width
                    max_height = safe_int(self.entries["max_height"][1].get())
                    min_height = safe_int(self.entries["min_height"][1].get())
                    frame_width = safe_int(self.entries["frame_width"][1].get())
                    frame_height = max_height  # Frame height equals max height in UB mode
                    concealed_wood_piece_width = safe_int(self.entries["concealed_wood_width"][1].get()) if concealed_wood_piece_width is None else concealed_wood_piece_width
                    if max_height - min_height > safe_int(self.entries["ub_wood_width"][1].get()):
                        raise ValueError("the difference height should not exceed wood width\n 高度差異不應超過UB角材的寬度\n Perbedaan tinggi tidak boleh melebihi lebar kayu sisi")
                elif door_type == self.electric_lock_label:
                    electric_lock_name = self.entries["electric_lock_name"][1].get().strip()
                    concealed_door_closer_name = self.entries["concealed_door_closer_name"][1].get().strip()
                    if electric_lock_name in electric_locks:
                        lock_length = electric_locks[electric_lock_name]['length']
                        lock_offset_bottom = electric_locks[electric_lock_name]['offset_bottom']
                        lock_offset_top = electric_locks[electric_lock_name]['offset_top']
                    elif concealed_door_closer_name in concealeds:
                        concealed_length = concealeds[concealed_door_closer_name]['length']
                    else:
                        lock_length = safe_int(self.entries["lock_length"][1].get())
                        lock_offset_bottom = safe_int(self.entries["lock_offset_bottom"][1].get())
                        lock_offset_top = lock_length - lock_offset_bottom
                    electric_lock_height = safe_int(self.entries["lock_height"][1].get())
                    lock_direction = self.entries["lock_direction"][1].get().strip().lower()
                    # frame_height = safe_int(self.entries["frame_height"][1].get()) if frame_height is None else frame_height
                    # frame_width = safe_int(self.entries["frame_width"][1].get()) if frame_width is None else frame_width
                    max_height = safe_int(self.entries["max_height"][1].get())
                    min_height = safe_int(self.entries["min_height"][1].get())
                    frame_width = safe_int(self.entries["frame_width"][1].get())
                    frame_height = max_height  # Frame height equals max height in UB mode
                    concealed_wood_piece_width = safe_int(self.entries["concealed_wood_width"][1].get()) if concealed_wood_piece_width is None else concealed_wood_piece_width
                    if max_height - min_height > safe_int(self.entries["ub_wood_width"][1].get()):
                        raise ValueError("the difference height should not exceed wood width\n 高度差異不應超過UB角材的寬度\n Perbedaan tinggi tidak boleh melebihi lebar kayu sisi")
                else:
                    max_height = safe_int(self.entries["max_height"][1].get())
                    min_height = safe_int(self.entries["min_height"][1].get())
                    frame_height = max_height
                    frame_width = safe_int(self.entries["frame_width"][1].get())
                    if max_height - min_height > safe_int(self.entries["ub_wood_width"][1].get()):
                        raise ValueError("the difference height should not exceed wood width\n 高度差異不應超過UB角材的寬度\n Perbedaan tinggi tidak boleh melebihi lebar kayu sisi bagian atas")


            elif category == self.non_fireproof_label:            
                if structure_type == self.yipaiyikong_label:
                    if door_type == self.box_lock_label:
                        box_lock_name = self.entries["box_lock_name"][1].get().strip()
                        concealed_door_closer_name = self.entries["concealed_door_closer_name"][1].get().strip()
                        if box_lock_name in box_locks:
                            lock_length = box_locks[box_lock_name]['length']
                            lock_offset_bottom = box_locks[box_lock_name]['offset_bottom']
                            lock_offset_top = box_locks[box_lock_name]['offset_top']
                        elif concealed_door_closer_name in concealeds:
                            concealed_length = concealeds[concealed_door_closer_name]['length']
                        else:
                            lock_length = safe_int(self.entries["lock_length"][1].get())
                            lock_offset_bottom = safe_int(self.entries["lock_offset_bottom"][1].get())
                            lock_offset_top = lock_length - lock_offset_bottom
                            # concealed_length = ""
                        box_lock_height = safe_int(self.entries["lock_height"][1].get())
                        lock_direction = self.entries["lock_direction"][1].get().strip().lower()
                        frame_height = safe_int(self.entries["frame_height"][1].get()) if frame_height is None else frame_height
                        frame_width = safe_int(self.entries["frame_width"][1].get()) if frame_width is None else frame_width
                        gap_width = safe_int(self.entries["gap_width"][1].get())
                        slats_width = safe_int(self.entries["slats_width"][1].get())
                        concealed_wood_piece_width = safe_int(self.entries["concealed_wood_width"][1].get()) if concealed_wood_piece_width is None else concealed_wood_piece_width
                        # print("test4", gap_width)
                        # gap_wood_lock = safe_int(self.entries["gap_wood_lock"][1].get())
                    elif door_type == self.electric_lock_label:
                        electric_lock_name = self.entries["electric_lock_name"][1].get().strip()
                        concealed_door_closer_name = self.entries["concealed_door_closer_name"][1].get().strip()
                        if electric_lock_name in electric_locks:
                            lock_length = electric_locks[electric_lock_name]['length']
                            lock_offset_bottom = electric_locks[electric_lock_name]['offset_bottom']
                            lock_offset_top = electric_locks[electric_lock_name]['offset_top']
                        elif concealed_door_closer_name in concealeds:
                            concealed_length = concealeds[concealed_door_closer_name]['length']
                        else:
                            lock_length = safe_int(self.entries["lock_length"][1].get())
                            lock_offset_bottom = safe_int(self.entries["lock_offset_bottom"][1].get())
                            lock_offset_top = lock_length - lock_offset_bottom
                        electric_lock_height = safe_int(self.entries["lock_height"][1].get())
                        lock_direction = self.entries["lock_direction"][1].get().strip().lower()
                        frame_height = safe_int(self.entries["frame_height"][1].get()) if frame_height is None else frame_height
                        frame_width = safe_int(self.entries["frame_width"][1].get()) if frame_width is None else frame_width
                        slats_width = safe_int(self.entries["slats_width"][1].get())
                        gap_width = safe_int(self.entries["gap_width"][1].get())
                        concealed_wood_piece_width = safe_int(self.entries["concealed_wood_width"][1].get()) if concealed_wood_piece_width is None else concealed_wood_piece_width
                    else:
                        frame_height = safe_int(self.entries["frame_height"][1].get())
                        frame_width = safe_int(self.entries["frame_width"][1].get())
                        gap_width = safe_int(self.entries["gap_width"][1].get())

                else:
                    if door_type == self.box_lock_label:
                        box_lock_name = self.entries["box_lock_name"][1].get().strip()
                        concealed_door_closer_name = self.entries["concealed_door_closer_name"][1].get().strip()
                        if box_lock_name in box_locks:
                            lock_length = box_locks[box_lock_name]['length']
                            lock_offset_bottom = box_locks[box_lock_name]['offset_bottom']
                            lock_offset_top = box_locks[box_lock_name]['offset_top']
                        elif concealed_door_closer_name in concealeds:
                            concealed_length = concealeds[concealed_door_closer_name]['length']
                        else:
                            lock_length = safe_int(self.entries["lock_length"][1].get())
                            lock_offset_bottom = safe_int(self.entries["lock_offset_bottom"][1].get())
                            lock_offset_top = lock_length - lock_offset_bottom
                            # concealed_length = ""
                        box_lock_height = safe_int(self.entries["lock_height"][1].get())
                        lock_direction = self.entries["lock_direction"][1].get().strip().lower()
                        frame_height = safe_int(self.entries["frame_height"][1].get()) if frame_height is None else frame_height
                        frame_width = safe_int(self.entries["frame_width"][1].get()) if frame_width is None else frame_width
                        concealed_wood_piece_width = safe_int(self.entries["concealed_wood_width"][1].get()) if concealed_wood_piece_width is None else concealed_wood_piece_width
                        # lock_height = safe_int(self.entries["lock_height"][1].get()) if lock_height is None else lock_height
                    elif door_type == self.electric_lock_label:
                        electric_lock_name = self.entries["electric_lock_name"][1].get().strip()
                        concealed_door_closer_name = self.entries["concealed_door_closer_name"][1].get().strip()
                        if electric_lock_name in electric_locks:
                            lock_length = electric_locks[electric_lock_name]['length']
                            lock_offset_bottom = electric_locks[electric_lock_name]['offset_bottom']
                            lock_offset_top = electric_locks[electric_lock_name]['offset_top']
                        elif concealed_door_closer_name in concealeds:
                            concealed_length = concealeds[concealed_door_closer_name]['length']
                        else:
                            lock_length = safe_int(self.entries["lock_length"][1].get())
                            lock_offset_bottom = safe_int(self.entries["lock_offset_bottom"][1].get())
                            lock_offset_top = lock_length - lock_offset_bottom
                        electric_lock_height = safe_int(self.entries["lock_height"][1].get())
                        lock_direction = self.entries["lock_direction"][1].get().strip().lower()
                        frame_height = safe_int(self.entries["frame_height"][1].get()) if frame_height is None else frame_height
                        frame_width = safe_int(self.entries["frame_width"][1].get()) if frame_width is None else frame_width
                        concealed_wood_piece_width = safe_int(self.entries["concealed_wood_width"][1].get()) if concealed_wood_piece_width is None else concealed_wood_piece_width
                        # lock_height = safe_int(self.entries["lock_height"][1].get()) if lock_height is None else lock_height
                        # gap_wood_lock = safe_int(self.entries["gap_wood_lock"][1].get())
                    else:
                        frame_height = safe_int(self.entries["frame_height"][1].get())
                        frame_width = safe_int(self.entries["frame_width"][1].get())
                        lock_height = safe_int(self.entries["lock_height"][1].get())
                        reinforce_wood = safe_int(self.entries["reinforce_wood"][1].get())
                        
            if edge_sealing_type in ["1mm 鐡封邊 + 1mm 石墨片"]:
                electric_lock_height += 3
                box_lock_height += 3
                
            elif edge_sealing_type in ["1mm 鋁封邊"]:
                electric_lock_height += 2
                box_lock_height += 2
                
            elif edge_sealing_type in ["1mm 鐡封邊", "0.5mm ABS", "0.8mm 美耐板", "1mm 不織布"]:
                electric_lock_height += 4
                box_lock_height += 4
                    
            if edge_sealing_type in ["0.5mm ABS", "0.8mm 美耐板", "1mm 不織布"]:
                frame_height += 10
                frame_width += 10
            elif edge_sealing_type in ["1mm 鐡封邊 + 1mm 石墨片", "1mm 鐡封邊"]:
                frame_height += 5
                frame_width += 5
            elif edge_sealing_type in ["1mm 鋁封邊"]:
                frame_height += 3
                frame_width += 3

            inner_width, slats_length, plywood_width, plywood_height, total_length_all_doors, vertical_piece_length, \
                horizontal_pieces_length, frame_width, outer_wood_bottom, inner_wood_bottom, \
                outer_wood_upper, inner_wood_upper,very_upper_horizontal_piece_length, gap_width, slats_width,\
                    slats_count, total_blocks, gap_wood_lock, lock_height, reinforce_wood, gap_wood_lock_length,\
                    gap_length_bottom, gap_length_upper, gap_length, reinforce_concealed_wood_length = self.calculate_material_requirements(
                    door_type, num_doors, frame_height, right_vertical_piece_width, left_vertical_piece_width,
                    upper_horizontal_piece_width, lower_horizontal_piece_width, edge_sealing, max_height, min_height,
                    vertical_piece_width, horizontal_piece_width, frame_width, electric_lock_name, box_lock_name, lock_length,
                    electric_lock_height, box_lock_height, lock_direction, concealed_door_closer_name, concealed_length,
                    lock_offset_bottom, lock_offset_top, gap_width, slats_width, mode, category, structure_type, lock_height, reinforce_wood, ub_wood_piece_width, concealed_wood_piece_width)

            report = self.generate_report(door_type, num_doors, inner_width, slats_length, gap_width, slats_count, total_blocks, plywood_width, plywood_height, total_length_all_doors,
                                          vertical_piece_length, horizontal_pieces_length, right_vertical_piece_width,
                                          left_vertical_piece_width, upper_horizontal_piece_width, lower_horizontal_piece_width,
                                          edge_sealing, max_height, min_height, vertical_piece_width, horizontal_piece_width,
                                          electric_lock_name, box_lock_name, lock_length, electric_lock_height, box_lock_height, lock_direction, concealed_door_closer_name, concealed_length,
                                          outer_wood_bottom, inner_wood_bottom, outer_wood_upper, inner_wood_upper,very_upper_horizontal_piece_length,
                                          frame_width, mode, category, structure_type, reinforce_wood, gap_length_bottom, gap_length_upper, gap_length, gap_wood_lock,
                                          gap_wood_lock_length, ub_wood_piece_width, edge_sealing_type, concealed_wood_piece_width, reinforce_concealed_wood_length)
            
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
            
            if category == self.fireproof_label:
                if mode == "UB":
                    if door_type == self.simple_label:
                        image_path = os.path.join(application_path, 'UB.png')
                        
                    elif door_type in [self.electric_lock_label, self.box_lock_label]:
                        if lock_direction == self.top_label:
                            if concealed_length > 0:
                                image_path = os.path.join(application_path, 'UB_kunci_elektrik_menkongqi.png')
                            else:
                                image_path = os.path.join(application_path, 'UB_kunci_elektrik.png')
                        elif lock_direction == self.bottom_label:
                            image_path = os.path.join(application_path, 'UB_kunci_elektrik_bawah.png')
                        
                
                else:
                    if door_type == self.simple_label:
                        image_path = os.path.join(application_path, 'simple.png')
                    
                    elif door_type in [self.electric_lock_label, self.box_lock_label]:
                        if concealed_length > 0:
                            image_path = os.path.join(application_path, 'kunci menkongqi.png')
                        else:
                            image_path = os.path.join(application_path, 'kunci.png')
            
            elif category == self.non_fireproof_label:
                if structure_type == self.honeycomb_board_label:
                    if door_type == self.simple_label:
                        image_path = os.path.join(application_path, 'honeycomb_board_simple.png')
                    elif door_type in [self.electric_lock_label, self.box_lock_label]:
                        if concealed_length > 0:
                            image_path = os.path.join(application_path, 'honeycomb_board_kunci_elektrik_menkongqi.png')
                        else:
                            image_path = os.path.join(application_path, 'honeycomb_board_kunci_elektrik.png')
            
                elif structure_type == self.honeycomb_paper_label:
                    if door_type == self.simple_label:
                        image_path = os.path.join(application_path, 'honeycomb_paper_simple.png')
                    elif door_type in [self.electric_lock_label, self.box_lock_label]:
                        if concealed_length > 0:
                            image_path = os.path.join(application_path, 'honeycomb_paper_kunci_elektrik_menkongqi.png')
                        else:
                            image_path = os.path.join(application_path, 'honeycomb_paper_kunci_elektrik.png')
            
                elif structure_type == self.yipaiyikong_label:
                    if door_type == self.simple_label:
                        image_path = os.path.join(application_path, 'yipaiyikong_simple.png')
                    elif door_type in [self.electric_lock_label, self.box_lock_label]:
                        if concealed_length > 0:
                            image_path = os.path.join(application_path, 'yipaiyikong_kunci_elektrik_menkongqi.png')
                        else:
                            image_path = os.path.join(application_path, 'yipaiyikong_kunci_elektrik.png')

                        
            else:
                image_path = None
            if image_path and os.path.exists(image_path):
                image = Image.open(image_path)
            else:
                raise FileNotFoundError(f"Image file not found at {image_path}")
            
            # Annotate the image
            annotated_image_path = self.add_annotations(image_path, vertical_piece_length, horizontal_pieces_length, door_type, outer_wood_upper, inner_wood_upper,
                                                        outer_wood_bottom, inner_wood_bottom,concealed_length, very_upper_horizontal_piece_length, concealed_door_closer_name, slats_count,
                                                        category, gap_wood_lock_length, reinforce_wood, gap_length_bottom, gap_length_upper, gap_wood_lock, gap_length, mode, reinforce_concealed_wood_length)
            
            # Configure text tags for styling
            self.result_text.tag_configure("blackbold", foreground="black", font=("Microsoft YaHei", 14, "bold"))
            self.result_text.tag_configure("black", foreground="black", font=("Microsoft YaHei", 12))
            self.result_text.tag_configure("khaki", foreground="chocolate3", font=("Microsoft YaHei", 12))
            self.result_text.tag_configure("blue", foreground="medium blue", font=("Microsoft YaHei", 12))
            self.result_text.tag_configure("green", foreground="lime green", font=("Microsoft YaHei", 12))
            self.result_text.tag_configure("purple", foreground="blue violet", font=("Microsoft YaHei", 12))
            self.result_text.tag_configure("orange", foreground="orange", font=("Microsoft YaHei", 12))
            self.result_text.tag_configure("brown", foreground="saddle brown", font=("Microsoft YaHei", 12))
            self.result_text.tag_configure("red", foreground="red2", font=("Microsoft YaHei", 12))
            self.result_text.tag_configure("magenta", foreground="magenta3", font=("Microsoft YaHei", 12))
            self.result_text.tag_configure("slategray", foreground="medium turquoise", font=("Microsoft YaHei", 12))
            
            self.result_text.tag_configure("normal", font=("Microsoft YaHei", 12))
            
            lang = self.current_language
            # Use translated terms for checking content
            app_title_label = translations[lang]["app_title"]
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
            slats_count_label = translations[lang]["slats_count"]
            total_blocks = translations[lang]["total_blocks"]
            reinforce_wood = translations[lang]["reinforce_wood"]
            slats_length = translations[lang]["slats_length"]
            gap_length_bottom = translations[lang]["gap_length_bottom"]
            gap_length_upper = translations[lang]["gap_length_upper"]
            gap_length = translations[lang]["gap_length"]
            gap_wood_lock_length = translations[lang]["gap_wood_lock_length"]
            total_wood_label = translations[lang]["total_wood"]
            total_wood_length_label = translations[lang]["total_wood_length"]
            
        
            # Insert the report with different styles based on content
            lines = report.split('\n')
            for line in lines:
                if app_title_label in line:
                    self.result_text.insert(tk.END, line + "\n", "blackbold")
                elif door_type_label in line or electric_lock_label in line:
                    self.result_text.insert(tk.END, line + "\n", "black")  # Apply the "title" style
                elif plywood_dimensions_label in line:
                    self.result_text.insert(tk.END, line + "\n", "khaki")
                elif xisuangai_label in line:
                    self.result_text.insert(tk.END, line + "\n", "khaki")
                elif horizontal_length_label in line:
                    self.result_text.insert(tk.END, line + "\n", "red")
                elif vertical_length_label in line:
                    self.result_text.insert(tk.END, line + "\n", "blue")
                elif outer_wood_upper_label in line:
                    self.result_text.insert(tk.END, line + "\n", "green")
                elif inner_wood_upper_label in line:
                    self.result_text.insert(tk.END, line + "\n", "purple")
                elif outer_wood_bottom_label in line:
                    self.result_text.insert(tk.END, line + "\n", "orange")
                elif inner_wood_bottom_label in line:
                    self.result_text.insert(tk.END, line + "\n", "brown")
                elif very_upper_horizontal_piece_length_label in line:
                    self.result_text.insert(tk.END, line + "\n", "magenta")
                elif slats_count_label in line:
                    self.result_text.insert(tk.END, line + "\n", "slategray")
                elif reinforce_wood in line:
                    self.result_text.insert(tk.END, line + "\n", "green")
                elif slats_length in line:
                    self.result_text.insert(tk.END, line + "\n", "red")
                elif gap_length_bottom in line:
                    self.result_text.insert(tk.END, line + "\n", "brown")
                elif gap_length_upper in line or gap_length in line:
                    self.result_text.insert(tk.END, line + "\n", "brown")
                elif gap_wood_lock_length in line:
                    self.result_text.insert(tk.END, line + "\n", "magenta")
                elif total_wood_length_label in line or total_wood_label in line:
                    self.result_text.insert(tk.END, line + "\n", "black")
                else:
                    self.result_text.insert(tk.END, line + "\n", "normal")  # Default style
            
            # Display in Tkinter
            # self.result_text.delete("1.0", tk.END)
            
            # Create a frame within the result text area
            result_frame = ttk.Frame(self.result_text)
            # result_frame.pack(fill="both", expand=True)
            # result_frame.grid_columnconfigure(0, weight=1)  # Text column
            # result_frame.grid_columnconfigure(3, weight=3)  # Image column
            
            result_imageframe = ttk.Frame(self.result_image)
            
            # Insert the calculated text result into a Label inside the frame
            # text_result = tk.Label(result_frame, text=report, font=("Microsoft YaHei", 12), anchor="w", justify="left")
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
            


        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
            print("Input validation error:", ve)
        except TypeError as te:
            messagebox.showerror(
                "Calculation Error",
                "An error occurred during the calculation. Please check your inputs and try again.\n計算過程中出現錯誤。請檢查您的輸入並重試。\nTerdeteksi ada kesalahan, silahkan cek ulang perhitungan dan input lagi"
            )
            print("TypeError details:", te)
        except Exception as e:
            messagebox.showerror(
                "Unexpected Error",
                "An unexpected error occurred. Please restart the app or contact support.\n出現意外錯誤。請重新啟動應用程式或聯絡支援人員。\nTerjadi kesalahan tak terduga. Harap mulai ulang aplikasi atau hubungi dukungan."
            )
            print("Unexpected error details:", e)

    def calculate_material_requirements(self, door_type, num_doors, frame_height, right_vertical_piece_width,
                                        left_vertical_piece_width, upper_horizontal_piece_width, lower_horizontal_piece_width,
                                        edge_sealing, max_height, min_height, vertical_piece_width, horizontal_piece_width,
                                        frame_width, electric_lock_name, box_lock_name, lock_length, electric_lock_height, box_lock_height, lock_direction, concealed_door_closer_name, concealed_length, 
                                        lock_offset_bottom, lock_offset_top, gap_width, slats_width, mode, category, structure_type, lock_height, reinforce_wood, ub_wood_piece_width, concealed_wood_piece_width):
        slats_length = 0
        total_blocks = 0
        slats_count = 0
        gap_length_bottom = 0
        gap_length_upper = 0
        middle_length = 0
        inner_width = 0
        plywood_height = 0
        gap_wood_lock_length = 200
        gap_wood_lock = 70
        gap_length = 0  
        slats_width = 0
        reinforce_concealed_wood_length = 70
        # concealed_wood_piece_width = 100
        
        if concealed_door_closer_name in concealeds:
            concealed_length = concealeds[concealed_door_closer_name]['length']
        else:
            # Set default values if no concealed door closer is selected
            concealed_length = 0
      
        if category == self.fireproof_label:
            if mode == "UB":
                if door_type in [self.electric_lock_label, self.box_lock_label]:    
                    if concealed_length == 0:
                        inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2)
                        plywood_height = max_height - lower_horizontal_piece_width - upper_horizontal_piece_width - ub_wood_piece_width
                    else:
                        inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2)
                        plywood_height = frame_height - lower_horizontal_piece_width  - upper_horizontal_piece_width - concealed_wood_piece_width - ub_wood_piece_width
                else:
                    inner_width = frame_width - right_vertical_piece_width - left_vertical_piece_width
                    plywood_height = max_height - upper_horizontal_piece_width - lower_horizontal_piece_width - ub_wood_piece_width
            else:
                if door_type in [self.electric_lock_label, self.box_lock_label]:
                    if concealed_length == 0:
                        inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2)
                        plywood_height = frame_height - lower_horizontal_piece_width  - upper_horizontal_piece_width
                    else:
                        inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2)
                        plywood_height = frame_height - lower_horizontal_piece_width  - upper_horizontal_piece_width - concealed_wood_piece_width                    
                else:
                    inner_width = frame_width - right_vertical_piece_width - left_vertical_piece_width
                    plywood_height = frame_height - lower_horizontal_piece_width  - upper_horizontal_piece_width
            
        elif category == self.non_fireproof_label:
            if structure_type == self.yipaiyikong_label:
                if door_type in [self.electric_lock_label, self.box_lock_label]:
                    if concealed_length == 0:
                        plywood_height = frame_height - lower_horizontal_piece_width - upper_horizontal_piece_width
                        inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2) - gap_wood_lock
                        slats_length = inner_width
                        slats_width = lower_horizontal_piece_width
                        slats_count = plywood_height // (slats_width + gap_width)
                        total_blocks = slats_count + 4
                    else:
                        plywood_height = frame_height - lower_horizontal_piece_width  - upper_horizontal_piece_width - concealed_wood_piece_width
                        inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2) - gap_wood_lock
                        slats_length = inner_width
                        slats_width = lower_horizontal_piece_width
                        slats_count = plywood_height // (slats_width + gap_width)
                        total_blocks = slats_count + 4
                else:
                    plywood_height = frame_height - lower_horizontal_piece_width - upper_horizontal_piece_width
                    inner_width = frame_width - right_vertical_piece_width - left_vertical_piece_width
                    slats_length = inner_width
                    slats_width = lower_horizontal_piece_width
                    slats_count = plywood_height // (slats_width + gap_width)
                    total_blocks = slats_count + 4
            elif structure_type == self.honeycomb_board_label:
                # gap_width = 0
                if door_type in [self.electric_lock_label, self.box_lock_label]:
                    if concealed_length == 0:
                        inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2) - gap_wood_lock
                        # plywood_height = frame_height - lower_horizontal_piece_width - upper_horizontal_piece_width
                        slats_length = inner_width
                        slats_width = lower_horizontal_piece_width
                        gap_width = (frame_height - (slats_width * 4)) / 3
                        slats_count = 2
                        gap_length = math.ceil((frame_height - upper_horizontal_piece_width - lower_horizontal_piece_width - (slats_count*slats_width))/3)
                    else:
                        inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2) - gap_wood_lock
                        # plywood_height = frame_height - lower_horizontal_piece_width  - upper_horizontal_piece_width - concealed_wood_piece_width
                        slats_length = inner_width
                        slats_width = lower_horizontal_piece_width
                        gap_width = (frame_height - (slats_width * 3) - upper_horizontal_piece_width) / 3
                        slats_count = 2
                        gap_length = math.ceil((frame_height - (slats_count*slats_width) - upper_horizontal_piece_width - lower_horizontal_piece_width - concealed_wood_piece_width) / 3)
                    # slats_count = frame_height // (slats_width + gap_width)
                    # total_blocks = slats_count
                else:
                    slats_length = inner_width
                    slats_width = lower_horizontal_piece_width
                    inner_width = frame_width - right_vertical_piece_width - left_vertical_piece_width
                    middle_length = reinforce_wood + (slats_width * 2)
                    gap_length_bottom = lock_height - (middle_length / 2) - lower_horizontal_piece_width
                    gap_length_upper = frame_height - gap_length_bottom - middle_length - upper_horizontal_piece_width - lower_horizontal_piece_width
                    slats_count = 2
                    # total_blocks = slats_count
            elif structure_type == self.honeycomb_paper_label:
                # gap_width = 0
                if door_type in [self.electric_lock_label, self.box_lock_label]:
                    if concealed_length == 0:
                        inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2) - gap_wood_lock
                        # plywood_height = frame_height - lower_horizontal_piece_width - upper_horizontal_piece_width
                        slats_length = inner_width
                        slats_width = lower_horizontal_piece_width
                        gap_width = (frame_height - (slats_width * 6)) / 5
                        slats_count = 4
                        gap_length = (frame_height - upper_horizontal_piece_width - lower_horizontal_piece_width - (slats_count*slats_width))/5
                    else:
                        inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2) - gap_wood_lock
                        # plywood_height = frame_height - lower_horizontal_piece_width - upper_horizontal_piece_width
                        slats_length = inner_width
                        slats_width = lower_horizontal_piece_width
                        gap_width = (frame_height - (slats_width * 6) - concealed_wood_piece_width) / 5
                        slats_count = 4
                        gap_length = (frame_height - (slats_count*slats_width) - upper_horizontal_piece_width - lower_horizontal_piece_width - concealed_wood_piece_width) / 5
                else:
                    slats_length = inner_width
                    slats_width = lower_horizontal_piece_width
                    inner_width = frame_width - right_vertical_piece_width - left_vertical_piece_width
                    middle_length = reinforce_wood + (slats_width * 2)
                    gap_length_bottom = (lock_height - (middle_length / 2) - lower_horizontal_piece_width - slats_width) / 2
                    gap_length_upper = (frame_height - gap_length_bottom - middle_length - upper_horizontal_piece_width - lower_horizontal_piece_width - slats_width) / 2
                    slats_count = 4
        
        # gap_width = 0
        slats_length = inner_width
        plywood_width = inner_width
        vertical_piece_length = frame_height
        horizontal_pieces_length = inner_width
        # print("test3", plywood_height)
        very_upper_horizontal_piece_length = horizontal_pieces_length

        total_length_per_door = vertical_piece_length * 2 + horizontal_pieces_length * 2    ############# kayaknya masih salah #################
        total_length_all_doors = total_length_per_door * num_doors
        
        outer_wood_bottom = inner_wood_bottom = outer_wood_upper = inner_wood_upper = None
        if category == self.fireproof_label:
            if mode != "UB":
                if door_type == self.electric_lock_label:
                    if lock_direction == self.bottom_label:
                        outer_wood_bottom = electric_lock_height - lock_offset_bottom
                        inner_wood_bottom = outer_wood_bottom - 30
                        outer_wood_upper = frame_height - (outer_wood_bottom + lock_length)
                        inner_wood_upper = outer_wood_upper - 75
                    elif lock_direction == self.top_label:
                        outer_wood_upper = electric_lock_height - lock_offset_top
                        inner_wood_upper = outer_wood_upper - 75
                        outer_wood_bottom = frame_height - (outer_wood_upper + lock_length)
                        inner_wood_bottom = outer_wood_bottom - 30
                        
                    if concealed_door_closer_name in concealeds:
                        concealed_length = concealeds[concealed_door_closer_name]['length']
                        # concealed_wood_piece_width = 100
                        very_upper_horizontal_piece_length -= concealed_length
                        very_upper_horizontal_piece_length = horizontal_pieces_length - concealed_length
                    #     print(f"\nConcealed Length: {concealed_length}")
                    # print(f"\n222Very Upper Horizontal Piece Length: {very_upper_horizontal_piece_length}")
        
                    # if concealed_door_closer == "no":
                    #     concealed_wood_piece_width = 0
                    #     very_upper_horizontal_piece_length = 0
                        
                elif door_type == self.box_lock_label:
                    if lock_direction == self.bottom_label:
                        outer_wood_bottom = box_lock_height - lock_offset_bottom
                        inner_wood_bottom = outer_wood_bottom - 30
                        outer_wood_upper = frame_height - (outer_wood_bottom + lock_length)
                        inner_wood_upper = outer_wood_upper - 30
                    elif lock_direction == self.top_label:
                        outer_wood_upper = box_lock_height - lock_offset_top
                        inner_wood_upper = outer_wood_upper - 30
                        outer_wood_bottom = frame_height - (outer_wood_upper + lock_length)
                        inner_wood_bottom = outer_wood_bottom - 30
                        
                    if concealed_door_closer_name in concealeds:
                        concealed_length = concealeds[concealed_door_closer_name]['length']
                        # concealed_wood_piece_width = 100
                        very_upper_horizontal_piece_length -= concealed_length
                        very_upper_horizontal_piece_length = horizontal_pieces_length - concealed_length
            
            else:
                if door_type == self.electric_lock_label:
                    if lock_direction == self.bottom_label:
                        outer_wood_bottom = electric_lock_height - lock_offset_bottom
                        inner_wood_bottom = outer_wood_bottom - 30
                        outer_wood_upper = max_height - (outer_wood_bottom + lock_length)
                        inner_wood_upper = outer_wood_upper - 75
                    elif lock_direction == self.top_label:
                        outer_wood_upper = electric_lock_height - lock_offset_top
                        inner_wood_upper = outer_wood_upper - 75
                        outer_wood_bottom = max_height - (outer_wood_upper + lock_length)
                        inner_wood_bottom = outer_wood_bottom - 30
                        
                    if concealed_door_closer_name in concealeds:
                        concealed_length = concealeds[concealed_door_closer_name]['length']
                        # concealed_wood_piece_width = 100
                        very_upper_horizontal_piece_length -= concealed_length
                        very_upper_horizontal_piece_length = horizontal_pieces_length - concealed_length
                
                elif door_type == self.box_lock_label:
                    if lock_direction == self.bottom_label:
                        outer_wood_bottom = box_lock_height - lock_offset_bottom
                        inner_wood_bottom = outer_wood_bottom - 30
                        outer_wood_upper = max_height - (outer_wood_bottom + lock_length)
                        inner_wood_upper = outer_wood_upper - 30
                    elif lock_direction == self.top_label:
                        outer_wood_upper = box_lock_height - lock_offset_top
                        inner_wood_upper = outer_wood_upper - 30
                        outer_wood_bottom = max_height - (outer_wood_upper + lock_length)
                        inner_wood_bottom = outer_wood_bottom - 30
                        
                    if concealed_door_closer_name in concealeds:
                        concealed_length = concealeds[concealed_door_closer_name]['length']
                        # concealed_wood_piece_width = 100
                        very_upper_horizontal_piece_length -= concealed_length
                        very_upper_horizontal_piece_length = horizontal_pieces_length - concealed_length
                        
                    
        elif category == self.non_fireproof_label:
            if structure_type in [self.yipaiyikong_label, self.honeycomb_paper_label, self.honeycomb_board_label]:
                if door_type == self.electric_lock_label:
                    if lock_direction == self.bottom_label:
                        outer_wood_bottom = electric_lock_height - lock_offset_bottom
                        inner_wood_bottom = outer_wood_bottom - 30
                        outer_wood_upper = frame_height - (outer_wood_bottom + lock_length)
                        inner_wood_upper = outer_wood_upper - 75
                    elif lock_direction == self.top_label:
                        outer_wood_upper = electric_lock_height - lock_offset_top
                        inner_wood_upper = outer_wood_upper - 75
                        outer_wood_bottom = frame_height - (outer_wood_upper + lock_length)
                        inner_wood_bottom = outer_wood_bottom - 30
                    
                    if concealed_door_closer_name in concealeds:
                        concealed_length = concealeds[concealed_door_closer_name]['length']
                        # concealed_wood_piece_width = 100
                        very_upper_horizontal_piece_length -= concealed_length
                        very_upper_horizontal_piece_length = horizontal_pieces_length - concealed_length - reinforce_concealed_wood_length
                    
                elif door_type == self.box_lock_label:
                    if lock_direction == self.bottom_label:
                        outer_wood_bottom = box_lock_height - lock_offset_bottom
                        inner_wood_bottom = outer_wood_bottom - 30
                        outer_wood_upper = frame_height - (outer_wood_bottom + lock_length)
                        inner_wood_upper = outer_wood_upper - 30
                    elif lock_direction == self.top_label:
                        outer_wood_upper = box_lock_height - lock_offset_top
                        inner_wood_upper = outer_wood_upper - 30
                        outer_wood_bottom = frame_height - (outer_wood_upper + lock_length)
                        inner_wood_bottom = outer_wood_bottom - 30
                        
                    if concealed_door_closer_name in concealeds:
                        concealed_length = concealeds[concealed_door_closer_name]['length']
                        # concealed_wood_piece_width = 100
                        very_upper_horizontal_piece_length -= concealed_length
                        very_upper_horizontal_piece_length = horizontal_pieces_length - concealed_length - reinforce_concealed_wood_length
                        
                    # print("test4", slats_width)
        # print("test4", gap_width)

        return inner_width, slats_length, plywood_width, plywood_height, total_length_all_doors, vertical_piece_length, \
               horizontal_pieces_length, frame_width, outer_wood_bottom, inner_wood_bottom, outer_wood_upper, inner_wood_upper,\
               very_upper_horizontal_piece_length, gap_width, slats_width, slats_count, total_blocks, gap_wood_lock, lock_height, reinforce_wood, gap_wood_lock_length,\
               gap_length_bottom, gap_length_upper, gap_length, reinforce_concealed_wood_length


    def generate_report(self, door_type, num_doors, inner_width, slats_length, gap_width, slats_count, total_blocks, plywood_width, plywood_height, total_length_all_doors,
                        vertical_piece_length, horizontal_pieces_length, right_vertical_piece_width,
                        left_vertical_piece_width, upper_horizontal_piece_width, lower_horizontal_piece_width,
                        edge_sealing, max_height, min_height, vertical_piece_width, horizontal_piece_width,
                        electric_lock_name, box_lock_name, lock_length, electric_lock_height, box_lock_height, lock_direction, concealed_door_closer_name, concealed_length, outer_wood_bottom,
                        inner_wood_bottom, outer_wood_upper, inner_wood_upper,very_upper_horizontal_piece_length, frame_width,
                        mode, category, structure_type, reinforce_wood, gap_length_bottom, gap_length_upper, gap_length, gap_wood_lock, gap_wood_lock_length, ub_wood_piece_width, edge_sealing_type, concealed_wood_piece_width,
                        reinforce_concealed_wood_length):
        lang = self.current_language
        total_right_vertical_pieces = num_doors if right_vertical_piece_width else 0
        total_left_vertical_pieces = num_doors if left_vertical_piece_width else 0
        
        if category == self.fireproof_label:
            if mode == "UB" or mode != "UB":
                if (door_type == self.electric_lock_label or door_type == self.box_lock_label):
                    total_left_vertical_pieces = num_doors * 4

        total_horizontal_pieces = num_doors * sum(h is not None for h in [upper_horizontal_piece_width, lower_horizontal_piece_width])
        # total_horizontal_pieces_non_fireproof = num_doors * sum(h is not None for h in [upper_horizontal_piece_width, lower_horizontal_piece_width, slats_count])
        # print("test 3",slats_length)


        # if category == self.fireproof_label:
        #     if mode == "UB":
        #         total_horizontal_pieces += num_doors
        slats_list = [slats_length for _ in range(slats_count)]
        
        
        report = f"""                       {translations[lang]["app_title"]}
        """
        
        if category == self.fireproof_label:
            if mode != "UB":
                if door_type == self.electric_lock_label:
                    report += f"""
        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["plywood_dimensions"]}\t: {plywood_width} mm x {plywood_height} mm 
        ‣ {translations[lang]["xisuangai"]}\t: {frame_width} mm x {vertical_piece_length} mm 
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
                    
        ‣ {translations[lang]["electric_lock"]}\t: {electric_lock_name}
        ‣ {translations[lang]["electric_lock_height"]}\t: {electric_lock_height} mm
        ‣ {translations[lang]["direction"]}\t: {lock_direction.capitalize()}
        """
                    report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width} mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {vertical_piece_length*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil((vertical_piece_length*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width} mm):
          • {translations[lang]["outer_wood_upper_part"]}\t: {outer_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["inner_wood_upper_part"]}\t: {inner_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["outer_wood_bottom_part"]}\t: {outer_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["inner_wood_bottom_part"]}\t: {inner_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([outer_wood_upper, inner_wood_upper, outer_wood_bottom, inner_wood_bottom])}
          • {translations[lang]["total_wood_length"]}\t: {(outer_wood_upper + inner_wood_upper + outer_wood_bottom + inner_wood_bottom)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_upper + inner_wood_upper + outer_wood_bottom + inner_wood_bottom)*num_doors)/2400)}
                    """
                    if concealed_door_closer_name in concealeds and concealed_wood_piece_width > 0:
                        report += """
                        """
                        # Define dynamic widths
                        unique_horizontal_widths = {
                            concealed_wood_piece_width: {"length": very_upper_horizontal_piece_length},
                            upper_horizontal_piece_width: {"length": horizontal_pieces_length},
                        }
                        
                        # Add concealed wood width dynamically if concealed door closer is selected
                        if concealed_door_closer_name in concealeds and concealed_wood_piece_width:
                            unique_horizontal_widths[concealed_wood_piece_width] = {"length": very_upper_horizontal_piece_length}
                        
                        # Ensure only valid widths are kept (remove empty or None widths)
                        unique_horizontal_widths = {width: data for width, data in unique_horizontal_widths.items() if width}
                        
                        # Add horizontal pieces information to the report
                        for width, data in unique_horizontal_widths.items():
                            report += f"""    
        ‣ {translations[lang]["horizontal_pieces"]} ({width} mm)"""
                    
                            if concealed_door_closer_name in concealeds and width == concealed_wood_piece_width:
                                report += f"""
          • {translations[lang]["very_upper_horizontal_piece_length"]}\t: {very_upper_horizontal_piece_length} mm
          • {translations[lang]["concealed_door_closer"]}\t: {concealed_door_closer_name}
          • {translations[lang]["total_num_pieces"]}\t: {(len([very_upper_horizontal_piece_length])) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([very_upper_horizontal_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length)*num_doors)/2400)}
        """
                            else:
                                report += f"""
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_num_pieces"]}\t: {(len([inner_width, inner_width]))*num_doors}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
          
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length +(horizontal_pieces_length * 2))*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length +(horizontal_pieces_length * 2))*num_doors)/2400)}
                        """
                        report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {(outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length + (horizontal_pieces_length * 2)) * num_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length + (horizontal_pieces_length * 2)) * num_doors) / 2400)}
                """
                    else:
                        if horizontal_piece_width:
                            report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                            """
                        else:
                            report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
                    """
                              
                    report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {(outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + (horizontal_pieces_length * 2)) * num_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + (horizontal_pieces_length * 2)) * num_doors) / 2400)}
                """
                elif door_type == self.box_lock_label:
                    report += f"""
        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["plywood_dimensions"]}\t: {plywood_width} mm x {plywood_height} mm 
        ‣ {translations[lang]["xisuangai"]}\t: {frame_width} mm x {vertical_piece_length} mm 
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
                    
        ‣ {translations[lang]["box_lock"]}\t: {box_lock_name}
        ‣ {translations[lang]["box_lock_height"]}\t: {box_lock_height} mm
        ‣ {translations[lang]["direction"]}\t: {lock_direction.capitalize()}
        """
                    report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width} mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["total_wood_length"]}\t: {vertical_piece_length*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil((vertical_piece_length*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width} mm):
          • {translations[lang]["outer_wood_upper_part"]}\t: {outer_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["inner_wood_upper_part"]}\t: {inner_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["outer_wood_bottom_part"]}\t: {outer_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["inner_wood_bottom_part"]}\t: {inner_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([outer_wood_upper, inner_wood_upper, outer_wood_bottom, inner_wood_bottom])}
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["total_wood_length"]}\t: {(outer_wood_upper + inner_wood_upper + outer_wood_bottom + inner_wood_bottom)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_upper + inner_wood_upper + outer_wood_bottom + inner_wood_bottom)*num_doors)/2400)}
                    """
                    if concealed_door_closer_name in concealeds and concealed_wood_piece_width > 0:
                        report += """
                        """
                        # Define dynamic widths
                        unique_horizontal_widths = {
                            concealed_wood_piece_width: {"length": very_upper_horizontal_piece_length},
                            upper_horizontal_piece_width: {"length": horizontal_pieces_length},
                        }
                        
                        # Add concealed wood width dynamically if concealed door closer is selected
                        if concealed_door_closer_name in concealeds and concealed_wood_piece_width:
                            unique_horizontal_widths[concealed_wood_piece_width] = {"length": very_upper_horizontal_piece_length}
                        
                        # Ensure only valid widths are kept (remove empty or None widths)
                        unique_horizontal_widths = {width: data for width, data in unique_horizontal_widths.items() if width}
                        
                        # Add horizontal pieces information to the report
                        for width, data in unique_horizontal_widths.items():
                            report += f"""    
        ‣ {translations[lang]["horizontal_pieces"]} ({width} mm)"""
                    
                            if concealed_door_closer_name in concealeds and width == concealed_wood_piece_width:
                                report += f"""
          • {translations[lang]["very_upper_horizontal_piece_length"]}\t: {very_upper_horizontal_piece_length} mm
          • {translations[lang]["concealed_door_closer"]}\t: {concealed_door_closer_name}
          • {translations[lang]["total_num_pieces"]}\t: {(len([very_upper_horizontal_piece_length])) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([very_upper_horizontal_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length)*num_doors)/2400)}
        """
                            else:
                                report += f"""
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_num_pieces"]}\t: {(len([inner_width, inner_width]))*num_doors}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
          
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length +(horizontal_pieces_length * 2))*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length +(horizontal_pieces_length * 2))*num_doors)/2400)}
                        """
                        report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {(outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length + (horizontal_pieces_length * 2)) * num_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length + (horizontal_pieces_length * 2)) * num_doors) / 2400)}
                """
                    else:
                        if horizontal_piece_width:
                            report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                            """
                        else:
                            report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
                    """
                    report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {(outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + (horizontal_pieces_length * 2)) * num_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + (horizontal_pieces_length * 2)) * num_doors) / 2400)}
                """
                    
                else:
                    report += f"""
        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["plywood_dimensions"]}\t: {plywood_width} mm x {plywood_height} mm 
        ‣ {translations[lang]["xisuangai"]}\t: {frame_width} mm x {vertical_piece_length} mm 
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
                    """
                    if vertical_piece_width:
                        report += f"""
        ‣ {translations[lang]["vertical_pieces"]} ({vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {len([vertical_piece_length, vertical_piece_length]) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length, vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length + vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length + vertical_piece_length)*num_doors)/2400)}
                        """
                    else:
                        report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
                        """
                    if horizontal_piece_width:
                        report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
        
        ‣ {translations[lang]["total_wood_length"]}\t: {total_length_all_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil((total_length_all_doors)/2400)}
                            """
                    else:
                        report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
          
        ‣ {translations[lang]["total_wood_length"]}\t: {total_length_all_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil((total_length_all_doors)/2400)}
                            """
                            
            else:
                if door_type == self.electric_lock_label:
                    report += f"""
        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["plywood_dimensions"]}\t: {plywood_width} mm x {plywood_height} mm 
        ‣ {translations[lang]["xisuangai"]}\t: {frame_width} mm x {vertical_piece_length} mm 
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
                    
        ‣ {translations[lang]["electric_lock"]}\t: {electric_lock_name}
        ‣ {translations[lang]["electric_lock_height"]}\t: {electric_lock_height} mm
        ‣ {translations[lang]["direction"]}\t: {lock_direction.capitalize()}
                    """
                    report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width} mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {vertical_piece_length*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil((vertical_piece_length*num_doors)/2400)}
        
        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width} mm):
          • {translations[lang]["outer_wood_upper_part"]}\t: {outer_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["inner_wood_upper_part"]}\t: {inner_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["outer_wood_bottom_part"]}\t: {outer_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["inner_wood_bottom_part"]}\t: {inner_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([outer_wood_upper, inner_wood_upper, outer_wood_bottom, inner_wood_bottom])}
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["total_wood_length"]}\t: {(outer_wood_upper + inner_wood_upper + outer_wood_bottom + inner_wood_bottom)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_upper + inner_wood_upper + outer_wood_bottom + inner_wood_bottom)*num_doors)/2400)}
                    """
                    if concealed_door_closer_name in concealeds and concealed_wood_piece_width > 0:
                        report += """
                        """
                        # Define dynamic widths
                        unique_horizontal_widths = {
                            concealed_wood_piece_width: {"length": very_upper_horizontal_piece_length},
                            upper_horizontal_piece_width: {"length": horizontal_pieces_length},
                        }
                        
                        # Add concealed wood width dynamically if concealed door closer is selected
                        if concealed_door_closer_name in concealeds and concealed_wood_piece_width:
                            unique_horizontal_widths[concealed_wood_piece_width] = {"length": very_upper_horizontal_piece_length}
                        
                        # Ensure only valid widths are kept (remove empty or None widths)
                        unique_horizontal_widths = {width: data for width, data in unique_horizontal_widths.items() if width}
                        
                        # Add horizontal pieces information to the report
                        for width, data in unique_horizontal_widths.items():
                            report += f"""    
        ‣ {translations[lang]["horizontal_pieces"]} ({width} mm)"""
                    
                            if concealed_door_closer_name in concealeds and width == concealed_wood_piece_width:
                                report += f"""
          • {translations[lang]["very_upper_horizontal_piece_length"]}\t: {very_upper_horizontal_piece_length} mm
          • {translations[lang]["concealed_door_closer"]}\t: {concealed_door_closer_name}
          • {translations[lang]["total_num_pieces"]}\t: {(len([very_upper_horizontal_piece_length])) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([very_upper_horizontal_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length)*num_doors)/2400)}
        """
                            else:
                                report += f"""
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_num_pieces"]}\t: {(len([inner_width, inner_width]))*num_doors}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
          
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length +(horizontal_pieces_length * 2))*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length +(horizontal_pieces_length * 2))*num_doors)/2400)}
                        """
                        report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {(outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length + (horizontal_pieces_length * 2)) * num_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length + (horizontal_pieces_length * 2)) * num_doors) / 2400)}
                """
                    else:
                        if horizontal_piece_width:
                            report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}

                            """
                        else:
                            report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
          
                    """
                              
                    report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {(outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + (horizontal_pieces_length * 2)) * num_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + (horizontal_pieces_length * 2)) * num_doors) / 2400)}
                """
                elif door_type == self.box_lock_label:
                    report += f"""
        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["plywood_dimensions"]}\t: {plywood_width} mm x {plywood_height} mm 
        ‣ {translations[lang]["xisuangai"]}\t: {frame_width} mm x {vertical_piece_length} mm 
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
                    
        ‣ {translations[lang]["box_lock"]}\t: {box_lock_name}
        ‣ {translations[lang]["box_lock_height"]}\t: {box_lock_height} mm
        ‣ {translations[lang]["direction"]}\t: {lock_direction.capitalize()}
                    """
                    report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width} mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}\
          • {translations[lang]["total_wood_length"]}\t: {vertical_piece_length*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil((vertical_piece_length*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width} mm):
          • {translations[lang]["outer_wood_upper_part"]}\t: {outer_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["inner_wood_upper_part"]}\t: {inner_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["outer_wood_bottom_part"]}\t: {outer_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["inner_wood_bottom_part"]}\t: {inner_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([outer_wood_upper, inner_wood_upper, outer_wood_bottom, inner_wood_bottom])}
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["total_wood_length"]}\t: {(outer_wood_upper + inner_wood_upper + outer_wood_bottom + inner_wood_bottom)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_upper + inner_wood_upper + outer_wood_bottom + inner_wood_bottom)*num_doors)/2400)}
                    """
                    if concealed_door_closer_name in concealeds and concealed_wood_piece_width > 0:
                        report += """
                        """
                        # Define dynamic widths
                        unique_horizontal_widths = {
                            concealed_wood_piece_width: {"length": very_upper_horizontal_piece_length},
                            upper_horizontal_piece_width: {"length": horizontal_pieces_length},
                        }
                        
                        # Add concealed wood width dynamically if concealed door closer is selected
                        if concealed_door_closer_name in concealeds and concealed_wood_piece_width:
                            unique_horizontal_widths[concealed_wood_piece_width] = {"length": very_upper_horizontal_piece_length}
                        
                        # Ensure only valid widths are kept (remove empty or None widths)
                        unique_horizontal_widths = {width: data for width, data in unique_horizontal_widths.items() if width}
                        
                        # Add horizontal pieces information to the report
                        for width, data in unique_horizontal_widths.items():
                            report += f"""    
        ‣ {translations[lang]["horizontal_pieces"]} ({width} mm)"""
                    
                            if concealed_door_closer_name in concealeds and width == concealed_wood_piece_width:
                                report += f"""
          • {translations[lang]["very_upper_horizontal_piece_length"]}\t: {very_upper_horizontal_piece_length} mm
          • {translations[lang]["concealed_door_closer"]}\t: {concealed_door_closer_name}
          • {translations[lang]["total_num_pieces"]}\t: {(len([very_upper_horizontal_piece_length])) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([very_upper_horizontal_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length)*num_doors)/2400)}
        """
                            else:
                                report += f"""
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_num_pieces"]}\t: {(len([inner_width, inner_width]))*num_doors}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
          
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length +(horizontal_pieces_length * 2))*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length +(horizontal_pieces_length * 2))*num_doors)/2400)}
                        """
                        report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {(outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length + (horizontal_pieces_length * 2)) * num_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length + (horizontal_pieces_length * 2)) * num_doors) / 2400)}
                """
                    else:
                        if horizontal_piece_width:
                            report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
        
                            """
                        else:
                            report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
                              """
                              
                    report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {(outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + (horizontal_pieces_length * 2)) * num_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + (horizontal_pieces_length * 2)) * num_doors) / 2400)}
                """
                else:
                    report += f"""
        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["plywood_dimensions"]}\t: {plywood_width} mm x {plywood_height} mm 
        ‣ {translations[lang]["xisuangai"]}\t: {frame_width} mm x {vertical_piece_length} mm 
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
                    """
                    if vertical_piece_width:
                        report += f"""
        ‣ {translations[lang]["vertical_pieces"]} ({vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {len([vertical_piece_length, vertical_piece_length]) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length, vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length + vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length + vertical_piece_length)*num_doors)/2400)}
                        """
                    else:
                        report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
                        """
                    if horizontal_piece_width:
                        report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
        
        ‣ {translations[lang]["total_wood_length"]}\t: {total_length_all_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil((total_length_all_doors)/2400)}
                            """
                    else:
                        report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
          
        ‣ {translations[lang]["total_wood_length"]}\t: {total_length_all_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil((total_length_all_doors)/2400)}
                            """
                
#################################### NON-FIREPROOF!! #########################################                
        elif category == self.non_fireproof_label:
            if structure_type == self.honeycomb_board_label:
                if door_type == self.electric_lock_label:                    
                    report += f"""
        ‣ {translations[lang]["structure_type"]}\t: {structure_type}
        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
        
        ‣ {translations[lang]["electric_lock"]}\t: {electric_lock_name}
        ‣ {translations[lang]["electric_lock_height"]}\t: {electric_lock_height} mm
        ‣ {translations[lang]["direction"]}\t: {lock_direction.capitalize()}
                    """
                    
                    report += f"""
        ‣ {translations[lang]["gap_length"]}\t: {gap_length} mm
        ‣ {translations[lang]["slats_length"]}\t: {slats_length} mm 
          • {translations[lang]["total_num_pieces"]}\t: {slats_count * num_doors}
          • {translations[lang]["slats_count"]}\t: {slats_count} pcs
          • {translations[lang]["total_wood_length"]}\t: {(slats_length * slats_count)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((slats_length * slats_count)*num_doors)/2400)}
                    
        ‣ {translations[lang]["gap_wood_lock"]} ({gap_wood_lock} mm):
          • {translations[lang]["gap_wood_lock_length"]}\t: {gap_wood_lock_length} mm
          • {translations[lang]["total_wood"]}\t: 4
          """
                                
                    if vertical_piece_width:
                        report += f"""
        ‣ {translations[lang]["vertical_pieces"]} ({vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {len([vertical_piece_length, vertical_piece_length]) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length, vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length + vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length + vertical_piece_length)*num_doors)/2400)}
                        """
                    else:
                        report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
                  """
                    report += f"""
        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width} mm):
          • {translations[lang]["outer_wood_upper_part"]}\t: {outer_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["outer_wood_bottom_part"]}\t: {outer_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["total_num_pieces"]}\t: {(len([outer_wood_upper, outer_wood_bottom])) * total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([outer_wood_upper, outer_wood_bottom])}
          • {translations[lang]["total_wood_length"]}\t: {(outer_wood_upper + outer_wood_bottom)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_upper + outer_wood_bottom)*num_doors)/2400)}
                    """
                    if concealed_door_closer_name in concealeds and concealed_wood_piece_width > 0:
                        report += """
                        """
                        # Define dynamic widths
                        unique_horizontal_widths = {
                            concealed_wood_piece_width: {"length": very_upper_horizontal_piece_length},
                            upper_horizontal_piece_width: {"length": horizontal_pieces_length},
                        }
                        
                        # Add concealed wood width dynamically if concealed door closer is selected
                        if concealed_door_closer_name in concealeds and concealed_wood_piece_width:
                            unique_horizontal_widths[concealed_wood_piece_width] = {"length": very_upper_horizontal_piece_length}
                        
                        # Ensure only valid widths are kept (remove empty or None widths)
                        unique_horizontal_widths = {width: data for width, data in unique_horizontal_widths.items() if width}
                        
                        # Add horizontal pieces information to the report
                        for width, data in unique_horizontal_widths.items():
                            report += f"""    
        ‣ {translations[lang]["horizontal_pieces"]} ({width} mm)"""
                        
                            if concealed_door_closer_name in concealeds and width == concealed_wood_piece_width:
                                report += f"""
          • {translations[lang]["very_upper_horizontal_piece_length"]}\t: {very_upper_horizontal_piece_length} mm
          • {translations[lang]["concealed_door_closer"]}\t: {concealed_door_closer_name}
          • {translations[lang]["reinforce_concealed_wood_length"]}\t: {reinforce_concealed_wood_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {(len([very_upper_horizontal_piece_length, reinforce_concealed_wood_length])) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([very_upper_horizontal_piece_length, reinforce_concealed_wood_length])}
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length + reinforce_concealed_wood_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length + reinforce_concealed_wood_length)*num_doors)/2400)}
        """
                            else:
                                report += f"""
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_num_pieces"]}\t: {(len([inner_width, inner_width]))*num_doors}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                      """
                        report += f"""
         ‣ {translations[lang]["total_wood_length"]}\t: {outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) + very_upper_horizontal_piece_length + (gap_wood_lock_length*4) +(horizontal_pieces_length * 2) +(slats_length *slats_count) + reinforce_concealed_wood_length *num_doors:.2f} mm 
         ‣ {translations[lang]["total_wood"]}\t: {math.ceil((outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) + very_upper_horizontal_piece_length + (gap_wood_lock_length*4) +(horizontal_pieces_length * 2) +(slats_length *slats_count) + reinforce_concealed_wood_length *num_doors)/2400)}
                  """
                    else:
                        if horizontal_piece_width:
                            report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                            """
                        else:
                            report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
          """
                        report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) +(horizontal_pieces_length * 2) + (gap_wood_lock_length*4) +(slats_length *slats_count) *num_doors:.2f} mm 
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil((outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) +(horizontal_pieces_length * 2) + (gap_wood_lock_length*4) +(slats_length *slats_count) *num_doors)/2400)}
                    """
                elif door_type == self.box_lock_label:
                    report += f"""
        ‣ {translations[lang]["structure_type"]}\t: {structure_type}
        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
        
        ‣ {translations[lang]["box_lock"]}\t: {box_lock_name}
        ‣ {translations[lang]["box_lock_height"]}\t: {box_lock_height} mm
        ‣ {translations[lang]["direction"]}\t: {lock_direction.capitalize()}
                    """
                    
                    report += f"""
        ‣ {translations[lang]["gap_length"]}\t: {gap_length} mm
        ‣ {translations[lang]["slats_length"]}\t: {slats_length} mm 
          • {translations[lang]["total_num_pieces"]}\t: {slats_count * num_doors}
          • {translations[lang]["slats_count"]}\t: {slats_count} pcs
          • {translations[lang]["total_wood_length"]}\t: {(slats_length * slats_count)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((slats_length * slats_count)*num_doors)/2400)}
                    
        ‣ {translations[lang]["gap_wood_lock"]} ({gap_wood_lock} mm):
          • {translations[lang]["gap_wood_lock_length"]}\t: {gap_wood_lock_length} mm
          • {translations[lang]["total_wood"]}\t: 4
          """
                                
                    if vertical_piece_width:
                        report += f"""
        ‣ {translations[lang]["vertical_pieces"]} ({vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {len([vertical_piece_length, vertical_piece_length]) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length, vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length + vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length + vertical_piece_length)*num_doors)/2400)}
                        """
                    else:
                        report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
                  """
                    report += f"""
        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width} mm):
          • {translations[lang]["outer_wood_upper_part"]}\t: {outer_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["outer_wood_bottom_part"]}\t: {outer_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["total_num_pieces"]}\t: {(len([outer_wood_upper, outer_wood_bottom])) * total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([outer_wood_upper, outer_wood_bottom])}
          • {translations[lang]["total_wood_length"]}\t: {(outer_wood_upper + outer_wood_bottom)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_upper + outer_wood_bottom)*num_doors)/2400)}
                    """
                    if concealed_door_closer_name in concealeds and concealed_wood_piece_width > 0:
                        report += """
                        """
                        # Define dynamic widths
                        unique_horizontal_widths = {
                            concealed_wood_piece_width: {"length": very_upper_horizontal_piece_length},
                            upper_horizontal_piece_width: {"length": horizontal_pieces_length},
                        }
                        
                        # Add concealed wood width dynamically if concealed door closer is selected
                        if concealed_door_closer_name in concealeds and concealed_wood_piece_width:
                            unique_horizontal_widths[concealed_wood_piece_width] = {"length": very_upper_horizontal_piece_length}
                        
                        # Ensure only valid widths are kept (remove empty or None widths)
                        unique_horizontal_widths = {width: data for width, data in unique_horizontal_widths.items() if width}
                        
                        # Add horizontal pieces information to the report
                        for width, data in unique_horizontal_widths.items():
                            report += f"""    
        ‣ {translations[lang]["horizontal_pieces"]} ({width} mm)"""
                        
                            if concealed_door_closer_name in concealeds and width == concealed_wood_piece_width:
                                report += f"""
          • {translations[lang]["very_upper_horizontal_piece_length"]}\t: {very_upper_horizontal_piece_length} mm
          • {translations[lang]["concealed_door_closer"]}\t: {concealed_door_closer_name}
          • {translations[lang]["reinforce_concealed_wood_length"]}\t: {reinforce_concealed_wood_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {(len([very_upper_horizontal_piece_length, reinforce_concealed_wood_length])) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([very_upper_horizontal_piece_length, reinforce_concealed_wood_length])}
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length + reinforce_concealed_wood_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length + reinforce_concealed_wood_length)*num_doors)/2400)}
        """
                            else:
                                report += f"""
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_num_pieces"]}\t: {(len([inner_width, inner_width]))*num_doors}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                      """
                        report += f"""
         ‣ {translations[lang]["total_wood_length"]}\t: {outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) + very_upper_horizontal_piece_length + (gap_wood_lock_length*4) +(horizontal_pieces_length * 2) +(slats_length *slats_count) + reinforce_concealed_wood_length *num_doors:.2f} mm 
         ‣ {translations[lang]["total_wood"]}\t: {math.ceil((outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) + very_upper_horizontal_piece_length + (gap_wood_lock_length*4) +(horizontal_pieces_length * 2) +(slats_length *slats_count) + reinforce_concealed_wood_length *num_doors)/2400)}
                  """
                    else:
                        if horizontal_piece_width:
                            report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                            """
                        else:
                            report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
                    """
                        report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) +(horizontal_pieces_length * 2) + (gap_wood_lock_length*4) +(slats_length *slats_count) *num_doors:.2f} mm 
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil((outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) +(horizontal_pieces_length * 2) + (gap_wood_lock_length*4) +(slats_length *slats_count) *num_doors)/2400)}
                    """
                else:
                    report += f"""
        ‣ {translations[lang]["structure_type"]}\t: {structure_type}
        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
        
        ‣ {translations[lang]["reinforce_wood"]}\t: {reinforce_wood} mm
        ‣ {translations[lang]["gap_length_bottom"]}\t: {gap_length_bottom} mm
        ‣ {translations[lang]["gap_length_upper"]}\t: {gap_length_upper} mm
        
        ‣ {translations[lang]["slats_length"]}\t: {slats_length} mm 
          • {translations[lang]["total_num_pieces"]}\t: {slats_count * num_doors}
          • {translations[lang]["slats_count"]}\t: {slats_count} 
          • {translations[lang]["total_wood_length"]}\t: {(slats_length * slats_count)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((slats_length * slats_count)*num_doors)/2400)}
                    """  
                    if vertical_piece_width:
                        report += f"""
        ‣ {translations[lang]["vertical_pieces"]} ({vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {len([vertical_piece_length, vertical_piece_length]) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length, vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length + vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length + vertical_piece_length)*num_doors)/2400)}
                        """
                    else:
                        report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
                        """
                    if horizontal_piece_width:
                        report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
        
        ‣ {translations[lang]["total_wood_length"]}\t: {((inner_width * 2) + (slats_length * slats_count) + (vertical_piece_length * 2))*num_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil(((((inner_width * 2) + (slats_length * slats_count) + (vertical_piece_length * 2))*num_doors))/2400)}
                            """
                    else:
                        report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
          
        ‣ {translations[lang]["total_wood_length"]}\t: {((inner_width * 2) + (slats_length * slats_count) + (vertical_piece_length * 2))*num_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil(((((inner_width * 2) + (slats_length * slats_count) + (vertical_piece_length * 2))*num_doors))/2400)}
                            """
                    
            elif structure_type == self.honeycomb_paper_label:
                if door_type == self.electric_lock_label:
                    report += f"""
        ‣ {translations[lang]["structure_type"]}\t: {structure_type}
        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
        
        ‣ {translations[lang]["electric_lock"]}\t: {electric_lock_name}
        ‣ {translations[lang]["electric_lock_height"]}\t: {electric_lock_height} mm
        ‣ {translations[lang]["direction"]}\t: {lock_direction.capitalize()}
                    """
                    
                    report += f"""
        ‣ {translations[lang]["gap_length"]}\t: {gap_length} mm
        ‣ {translations[lang]["slats_length"]}\t: {slats_length} mm 
          • {translations[lang]["total_num_pieces"]}\t: {slats_count * num_doors}
          • {translations[lang]["slats_count"]}\t: {slats_count} pcs
          • {translations[lang]["total_wood_length"]}\t: {(slats_length * slats_count)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((slats_length * slats_count)*num_doors)/2400)}
                    
        ‣ {translations[lang]["gap_wood_lock"]} ({gap_wood_lock} mm):
          • {translations[lang]["gap_wood_lock_length"]}\t: {gap_wood_lock_length} mm
          • {translations[lang]["total_wood"]}\t: 4
          """
                                
                    if vertical_piece_width:
                        report += f"""
        ‣ {translations[lang]["vertical_pieces"]} ({vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {len([vertical_piece_length, vertical_piece_length]) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length, vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length + vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length + vertical_piece_length)*num_doors)/2400)}
                        """
                    else:
                        report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
                  """
                    report += f"""
        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width} mm):
          • {translations[lang]["outer_wood_upper_part"]}\t: {outer_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["outer_wood_bottom_part"]}\t: {outer_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["total_num_pieces"]}\t: {(len([outer_wood_upper, outer_wood_bottom])) * total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([outer_wood_upper, outer_wood_bottom])}
          • {translations[lang]["total_wood_length"]}\t: {(outer_wood_upper + outer_wood_bottom)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_upper + outer_wood_bottom)*num_doors)/2400)}
                    """
                    if concealed_door_closer_name in concealeds and concealed_wood_piece_width > 0:
                        report += """
                        """
                        # Define dynamic widths
                        unique_horizontal_widths = {
                            concealed_wood_piece_width: {"length": very_upper_horizontal_piece_length},
                            upper_horizontal_piece_width: {"length": horizontal_pieces_length},
                        }
                        
                        # Add concealed wood width dynamically if concealed door closer is selected
                        if concealed_door_closer_name in concealeds and concealed_wood_piece_width:
                            unique_horizontal_widths[concealed_wood_piece_width] = {"length": very_upper_horizontal_piece_length}
                        
                        # Ensure only valid widths are kept (remove empty or None widths)
                        unique_horizontal_widths = {width: data for width, data in unique_horizontal_widths.items() if width}
                        
                        # Add horizontal pieces information to the report
                        for width, data in unique_horizontal_widths.items():
                            report += f"""    
        ‣ {translations[lang]["horizontal_pieces"]} ({width} mm)"""
                        
                            if concealed_door_closer_name in concealeds and width == concealed_wood_piece_width:
                                report += f"""
          • {translations[lang]["very_upper_horizontal_piece_length"]}\t: {very_upper_horizontal_piece_length} mm
          • {translations[lang]["concealed_door_closer"]}\t: {concealed_door_closer_name}
          • {translations[lang]["reinforce_concealed_wood_length"]}\t: {reinforce_concealed_wood_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {(len([very_upper_horizontal_piece_length, reinforce_concealed_wood_length])) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([very_upper_horizontal_piece_length, reinforce_concealed_wood_length])}
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length + reinforce_concealed_wood_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length + reinforce_concealed_wood_length)*num_doors)/2400)}
        """
                            else:
                                report += f"""
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_num_pieces"]}\t: {(len([inner_width, inner_width]))*num_doors}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                      """
                        report += f"""
         ‣ {translations[lang]["total_wood_length"]}\t: {outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) + very_upper_horizontal_piece_length + (gap_wood_lock_length*4) +(horizontal_pieces_length * 2) +(slats_length *slats_count) + reinforce_concealed_wood_length *num_doors:.2f} mm 
         ‣ {translations[lang]["total_wood"]}\t: {math.ceil((outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) + very_upper_horizontal_piece_length + (gap_wood_lock_length*4) +(horizontal_pieces_length * 2) +(slats_length *slats_count) + reinforce_concealed_wood_length *num_doors)/2400)}
                  """
                    else:
                        if horizontal_piece_width:
                            report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                                """
                        else:
                            report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
                        """
                        report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) +(horizontal_pieces_length * 2) + (gap_wood_lock_length*4) +(slats_length *slats_count) *num_doors:.2f} mm 
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil((outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) +(horizontal_pieces_length * 2) + (gap_wood_lock_length*4) +(slats_length *slats_count) *num_doors)/2400)}
                    """
                elif door_type == self.box_lock_label:
                    report += f"""
        ‣ {translations[lang]["structure_type"]}\t: {structure_type}
        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
        
        ‣ {translations[lang]["box_lock"]}\t: {box_lock_name}
        ‣ {translations[lang]["box_lock_height"]}\t: {box_lock_height} mm
        ‣ {translations[lang]["direction"]}\t: {lock_direction.capitalize()}
                    """
                    
                    report += f"""
        ‣ {translations[lang]["gap_length"]}\t: {gap_length} mm
        ‣ {translations[lang]["slats_length"]}\t: {slats_length} mm 
          • {translations[lang]["total_num_pieces"]}\t: {slats_count * num_doors}
          • {translations[lang]["slats_count"]}\t: {slats_count} pcs
          • {translations[lang]["total_wood_length"]}\t: {(slats_length * slats_count)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((slats_length * slats_count)*num_doors)/2400)}
                    
        ‣ {translations[lang]["gap_wood_lock"]} ({gap_wood_lock} mm):
          • {translations[lang]["gap_wood_lock_length"]}\t: {gap_wood_lock_length} mm
          • {translations[lang]["total_wood"]}\t: 4
          """
                    
                    if vertical_piece_width:
                        report += f"""
        ‣ {translations[lang]["vertical_pieces"]} ({vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {len([vertical_piece_length, vertical_piece_length]) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length, vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length + vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length + vertical_piece_length)*num_doors)/2400)}
                        """
                    else:
                        report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
                  """
                    report += f"""
        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width} mm):
          • {translations[lang]["outer_wood_upper_part"]}\t: {outer_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["outer_wood_bottom_part"]}\t: {outer_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["total_num_pieces"]}\t: {(len([outer_wood_upper, outer_wood_bottom])) * total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([outer_wood_upper, outer_wood_bottom])}
          • {translations[lang]["total_wood_length"]}\t: {(outer_wood_upper + outer_wood_bottom)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_upper + outer_wood_bottom)*num_doors)/2400)}
                    """
                    if concealed_door_closer_name in concealeds and concealed_wood_piece_width > 0:
                        report += """
                        """
                        # Define dynamic widths
                        unique_horizontal_widths = {
                            concealed_wood_piece_width: {"length": very_upper_horizontal_piece_length},
                            upper_horizontal_piece_width: {"length": horizontal_pieces_length},
                        }
                        
                        # Add concealed wood width dynamically if concealed door closer is selected
                        if concealed_door_closer_name in concealeds and concealed_wood_piece_width:
                            unique_horizontal_widths[concealed_wood_piece_width] = {"length": very_upper_horizontal_piece_length}
                        
                        # Ensure only valid widths are kept (remove empty or None widths)
                        unique_horizontal_widths = {width: data for width, data in unique_horizontal_widths.items() if width}
                        
                        # Add horizontal pieces information to the report
                        for width, data in unique_horizontal_widths.items():
                            report += f"""    
        ‣ {translations[lang]["horizontal_pieces"]} ({width} mm)"""
                        
                            if concealed_door_closer_name in concealeds and width == concealed_wood_piece_width:
                                report += f"""
          • {translations[lang]["very_upper_horizontal_piece_length"]}\t: {very_upper_horizontal_piece_length} mm
          • {translations[lang]["concealed_door_closer"]}\t: {concealed_door_closer_name}
          • {translations[lang]["reinforce_concealed_wood_length"]}\t: {reinforce_concealed_wood_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {(len([very_upper_horizontal_piece_length, reinforce_concealed_wood_length])) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([very_upper_horizontal_piece_length, reinforce_concealed_wood_length])}
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length + reinforce_concealed_wood_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length + reinforce_concealed_wood_length)*num_doors)/2400)}
        """
                            else:
                                report += f"""
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_num_pieces"]}\t: {(len([inner_width, inner_width]))*num_doors}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
        
                      """
                        report += f"""
         ‣ {translations[lang]["total_wood_length"]}\t: {outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) + very_upper_horizontal_piece_length + (gap_wood_lock_length*4) +(horizontal_pieces_length * 2) +(slats_length *slats_count) + reinforce_concealed_wood_length *num_doors:.2f} mm 
         ‣ {translations[lang]["total_wood"]}\t: {math.ceil((outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) + very_upper_horizontal_piece_length + (gap_wood_lock_length*4) +(horizontal_pieces_length * 2) +(slats_length *slats_count) + reinforce_concealed_wood_length *num_doors)/2400)}
                   """
                    else:
                        if horizontal_piece_width:
                            report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                                """
                        else:
                            report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
                        """
                        report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) +(horizontal_pieces_length * 2) + (gap_wood_lock_length*4) +(slats_length *slats_count) *num_doors:.2f} mm 
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil((outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) +(horizontal_pieces_length * 2) + (gap_wood_lock_length*4) +(slats_length *slats_count) *num_doors)/2400)}
                        """
                    
                else:
                    report += f"""
        ‣ {translations[lang]["structure_type"]}\t: {structure_type}
        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
        
        ‣ {translations[lang]["reinforce_wood"]}\t: {reinforce_wood} mm
        ‣ {translations[lang]["gap_length_bottom"]}\t: {gap_length_bottom} mm
        ‣ {translations[lang]["gap_length_upper"]}\t: {gap_length_upper} mm
        
        ‣ {translations[lang]["slats_length"]}\t: {slats_length} mm 
          • {translations[lang]["total_num_pieces"]}\t: {slats_count * num_doors}
          • {translations[lang]["slats_count"]}\t: {slats_count} 
          • {translations[lang]["total_wood_length"]}\t: {(slats_length * slats_count)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((slats_length * slats_count)*num_doors)/2400)}
                    """  
                    if vertical_piece_width:
                        report += f"""
        ‣ {translations[lang]["vertical_pieces"]} ({vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {len([vertical_piece_length, vertical_piece_length]) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length, vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length + vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length + vertical_piece_length)*num_doors)/2400)}
                        """
                    else:
                        report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
                        """
                    if horizontal_piece_width:
                        report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                            """
                    else:
                        report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
          
        ‣ {translations[lang]["total_wood_length"]}\t: {((inner_width * 2) + (slats_length * slats_count) + (vertical_piece_length * 2))*num_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil(((((inner_width * 2) + (slats_length * slats_count) + (vertical_piece_length * 2))*num_doors))/2400)}
                            """
                    
            elif structure_type == self.yipaiyikong_label:
                if door_type == self.electric_lock_label:
                    report += f"""
        ‣ {translations[lang]["structure_type"]}\t: {structure_type}

        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
        
        ‣ {translations[lang]["electric_lock"]}\t: {electric_lock_name}
        ‣ {translations[lang]["electric_lock_height"]}\t: {electric_lock_height} mm
        ‣ {translations[lang]["direction"]}\t: {lock_direction.capitalize()}
        
        ‣ {translations[lang]["gap_width"]}\t: {gap_width}
        ‣ {translations[lang]["slats_length"]}\t: {slats_length} mm 
          • {translations[lang]["total_num_pieces"]}\t: {slats_count * num_doors}
          • {translations[lang]["slats_count"]}\t: {slats_count} pcs
          • {translations[lang]["total_wood_length"]}\t: {(slats_length * slats_count)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((slats_length * slats_count)*num_doors)/2400)}
        ‣ {translations[lang]["yipaiyikong_note"]}
        
        ‣ {translations[lang]["gap_wood_lock"]} ({gap_wood_lock} mm):
          • {translations[lang]["gap_wood_lock_length"]}\t: {gap_wood_lock_length} mm
          • {translations[lang]["total_wood"]}\t: 4
                    """
                    
                    if vertical_piece_width:
                        report += f"""
        ‣ {translations[lang]["vertical_pieces"]} ({vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {len([vertical_piece_length, vertical_piece_length]) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length, vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length + vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length + vertical_piece_length)*num_doors)/2400)}
                        """
                    else:
                        report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
                  """
                    report += f"""
        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width} mm):
          • {translations[lang]["outer_wood_upper_part"]}\t: {outer_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["outer_wood_bottom_part"]}\t: {outer_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["total_num_pieces"]}\t: {(len([outer_wood_upper, outer_wood_bottom])) * total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([outer_wood_upper, outer_wood_bottom])}
          • {translations[lang]["total_wood_length"]}\t: {(outer_wood_upper + outer_wood_bottom)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_upper + outer_wood_bottom)*num_doors)/2400)}
                    """
                    if concealed_door_closer_name in concealeds and concealed_wood_piece_width > 0:
                        report += """
                        """
                        # Define dynamic widths
                        unique_horizontal_widths = {
                            concealed_wood_piece_width: {"length": very_upper_horizontal_piece_length},
                            upper_horizontal_piece_width: {"length": horizontal_pieces_length},
                        }
                        
                        # Add concealed wood width dynamically if concealed door closer is selected
                        if concealed_door_closer_name in concealeds and concealed_wood_piece_width:
                            unique_horizontal_widths[concealed_wood_piece_width] = {"length": very_upper_horizontal_piece_length}
                        
                        # Ensure only valid widths are kept (remove empty or None widths)
                        unique_horizontal_widths = {width: data for width, data in unique_horizontal_widths.items() if width}
                        
                        # Add horizontal pieces information to the report
                        for width, data in unique_horizontal_widths.items():
                            report += f"""    
        ‣ {translations[lang]["horizontal_pieces"]} ({width} mm)"""
                        
                            if concealed_door_closer_name in concealeds and width == concealed_wood_piece_width:
                                report += f"""
          • {translations[lang]["very_upper_horizontal_piece_length"]}\t: {very_upper_horizontal_piece_length} mm
          • {translations[lang]["concealed_door_closer"]}\t: {concealed_door_closer_name}
          • {translations[lang]["reinforce_concealed_wood_length"]}\t: {reinforce_concealed_wood_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {(len([very_upper_horizontal_piece_length, reinforce_concealed_wood_length])) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([very_upper_horizontal_piece_length, reinforce_concealed_wood_length])}
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length + reinforce_concealed_wood_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length + reinforce_concealed_wood_length)*num_doors)/2400)}
        """
                            else:
                                report += f"""
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                      """
                        report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) + very_upper_horizontal_piece_length + (gap_wood_lock_length*4) +(horizontal_pieces_length * 2) +(slats_length *slats_count) + reinforce_concealed_wood_length *num_doors:.2f} mm 
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil((outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) + very_upper_horizontal_piece_length + (gap_wood_lock_length*4) +(horizontal_pieces_length * 2) +(slats_length *slats_count) + reinforce_concealed_wood_length *num_doors)/2400)}
                  """
                    else:
                        if horizontal_piece_width:
                            report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                                """
                        else:
                            report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
                        """
                        report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) +(horizontal_pieces_length * 2) + (gap_wood_lock_length*4) +(slats_length *slats_count) *num_doors:.2f} mm 
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil((outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) +(horizontal_pieces_length * 2) + (gap_wood_lock_length*4) +(slats_length *slats_count) *num_doors)/2400)}
                    """
                elif door_type == self.box_lock_label:
                    report += f"""
        ‣ {translations[lang]["structure_type"]}\t: {structure_type}

        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
        
        ‣ {translations[lang]["box_lock"]}\t: {box_lock_name}
        ‣ {translations[lang]["box_lock_height"]}\t: {box_lock_height} mm
        ‣ {translations[lang]["direction"]}\t: {lock_direction.capitalize()}
        
        ‣ {translations[lang]["gap_width"]}\t: {gap_width}
        ‣ {translations[lang]["slats_length"]}\t: {slats_length} mm 
          • {translations[lang]["total_num_pieces"]}\t: {slats_count * num_doors}
          • {translations[lang]["slats_count"]}\t: {slats_count} pcs
          • {translations[lang]["total_wood_length"]}\t: {(slats_length * slats_count)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((slats_length * slats_count)*num_doors)/2400)}
        ‣ {translations[lang]["yipaiyikong_note"]}
        
        ‣ {translations[lang]["gap_wood_lock"]} ({gap_wood_lock} mm):
          • {translations[lang]["gap_wood_lock_length"]}\t: {gap_wood_lock_length} mm
          • {translations[lang]["total_wood"]}\t: 4
                    """
                    
                    if vertical_piece_width:
                        report += f"""
        ‣ {translations[lang]["vertical_pieces"]} ({vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {len([vertical_piece_length, vertical_piece_length]) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length, vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length + vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length + vertical_piece_length)*num_doors)/2400)}
                        """
                    else:
                        report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
              """
                    report += f"""
        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width} mm):
          • {translations[lang]["outer_wood_upper_part"]}\t: {outer_wood_upper} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["outer_wood_bottom_part"]}\t: {outer_wood_bottom} mm
          • {translations[lang]["how_many"]}\t: {num_doors}
          • {translations[lang]["total_num_pieces"]}\t: {(len([outer_wood_upper, outer_wood_bottom])) * total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([outer_wood_upper, outer_wood_bottom])}
          • {translations[lang]["total_wood_length"]}\t: {(outer_wood_upper + outer_wood_bottom)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((outer_wood_upper + outer_wood_bottom)*num_doors)/2400)}
                    """
                    if concealed_door_closer_name in concealeds and concealed_wood_piece_width > 0:
                        report += """
                        """
                        # Define dynamic widths
                        unique_horizontal_widths = {
                            concealed_wood_piece_width: {"length": very_upper_horizontal_piece_length},
                            upper_horizontal_piece_width: {"length": horizontal_pieces_length},
                        }
                        
                        # Add concealed wood width dynamically if concealed door closer is selected
                        if concealed_door_closer_name in concealeds and concealed_wood_piece_width:
                            unique_horizontal_widths[concealed_wood_piece_width] = {"length": very_upper_horizontal_piece_length}
                        
                        # Ensure only valid widths are kept (remove empty or None widths)
                        unique_horizontal_widths = {width: data for width, data in unique_horizontal_widths.items() if width}
                        
                        # Add horizontal pieces information to the report
                        for width, data in unique_horizontal_widths.items():
                            report += f"""    
        ‣ {translations[lang]["horizontal_pieces"]} ({width} mm)"""
                        
                            if concealed_door_closer_name in concealeds and width == concealed_wood_piece_width:
                                report += f"""
          • {translations[lang]["very_upper_horizontal_piece_length"]}\t: {very_upper_horizontal_piece_length} mm
          • {translations[lang]["concealed_door_closer"]}\t: {concealed_door_closer_name}
          • {translations[lang]["reinforce_concealed_wood_length"]}\t: {reinforce_concealed_wood_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {(len([very_upper_horizontal_piece_length, reinforce_concealed_wood_length])) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([very_upper_horizontal_piece_length, reinforce_concealed_wood_length])}
          • {translations[lang]["total_wood_length"]}\t: {(very_upper_horizontal_piece_length + reinforce_concealed_wood_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((very_upper_horizontal_piece_length + reinforce_concealed_wood_length)*num_doors)/2400)}
        """
                            else:
                                report += f"""
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                      """
                        report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) + very_upper_horizontal_piece_length + (gap_wood_lock_length*4) +(horizontal_pieces_length * 2) +(slats_length *slats_count) + reinforce_concealed_wood_length *num_doors:.2f} mm 
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil((outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) + very_upper_horizontal_piece_length + (gap_wood_lock_length*4) +(horizontal_pieces_length * 2) +(slats_length *slats_count) + reinforce_concealed_wood_length *num_doors)/2400)}
                  """
                    else:
                        if horizontal_piece_width:
                            report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
                                """
                        else:
                            report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
                        """
                        report += f"""
        ‣ {translations[lang]["total_wood_length"]}\t: {outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) +(horizontal_pieces_length * 2) + (gap_wood_lock_length*4) +(slats_length *slats_count) *num_doors:.2f} mm 
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil((outer_wood_bottom + outer_wood_upper + (vertical_piece_length*2) +(horizontal_pieces_length * 2) + (gap_wood_lock_length*4) +(slats_length *slats_count) *num_doors)/2400)}
                    """
                else:
                    report += f"""
        ‣ {translations[lang]["door_type"]}\t: {door_type.upper()}
        ‣ {translations[lang]["num_doors"]}\t: {num_doors}
        ‣ {translations[lang]["edge_sealing"]}\t: {edge_sealing_type}
                
        ‣ {translations[lang]["gap_width"]}\t: {gap_width}
        ‣ {translations[lang]["slats_length"]}\t: {slats_length} mm 
          • {translations[lang]["total_num_pieces"]}\t: {slats_count * num_doors}
          • {translations[lang]["slats_count"]}\t: {slats_count} pcs
          • {translations[lang]["total_wood_length"]}\t: {(slats_length * slats_count)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((slats_length * slats_count)*num_doors)/2400)}
        ‣ {translations[lang]["yipaiyikong_note"]}

                    """
                    if vertical_piece_width:
                        report += f"""
        ‣ {translations[lang]["vertical_pieces"]} ({vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {len([vertical_piece_length, vertical_piece_length]) * num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length, vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length + vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length + vertical_piece_length)*num_doors)/2400)}
                        """
                    else:
                        report += f"""
        ‣ {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_right_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}

        ‣ {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
          • {translations[lang]["length_each_piecev"]}\t: {vertical_piece_length} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_left_vertical_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([vertical_piece_length])}
          • {translations[lang]["total_wood_length"]}\t: {(vertical_piece_length)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((vertical_piece_length)*num_doors)/2400)}
                        """
                    if horizontal_piece_width:
                        report += f"""
        ‣ {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {total_horizontal_pieces}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width, inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width + inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width + inner_width)*num_doors)/2400)}
        
        ‣ {translations[lang]["total_wood_length"]}\t: {((inner_width * 2) + (slats_length * slats_count) + (vertical_piece_length * 2))*num_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil(((((inner_width * 2) + (slats_length * slats_count) + (vertical_piece_length * 2))*num_doors))/2400)}
                            """
                    else:
                        report += f"""
        ‣ {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}

        ‣ {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
          • {translations[lang]["length_each_pieceh"]}\t: {inner_width} mm
          • {translations[lang]["total_num_pieces"]}\t: {num_doors}
          • {translations[lang]["num_pieces_per_door"]}\t: {len([inner_width])}
          • {translations[lang]["total_wood_length"]}\t: {(inner_width)*num_doors:.2f} mm
          • {translations[lang]["total_wood"]}\t: {math.ceil(((inner_width)*num_doors)/2400)}
          
        ‣ {translations[lang]["total_wood_length"]}\t: {((inner_width * 2) + (slats_length * slats_count) + (vertical_piece_length * 2))*num_doors:.2f} mm
        ‣ {translations[lang]["total_wood"]}\t: {math.ceil(((((inner_width * 2) + (slats_length * slats_count) + (vertical_piece_length * 2))*num_doors))/2400)}
                            """

        # if door_type == self.ub_label:
        #     report += f"""
        #     {translations[lang]["ub_note"]}
        #     """
            
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

        ttk.Label(lock_window, text=translations[self.current_language]["electriclockname"], font=("Microsoft YaHei", 13)).grid(row=0, column=0, sticky=tk.W)
        new_lock_name_entry = ttk.Entry(lock_window, font=("Microsoft YaHei", 13))
        new_lock_name_entry.grid(row=0, column=1, sticky=tk.E)
        ttk.Label(lock_window, text=translations[self.current_language]["locklength"], font=("Microsoft YaHei", 13)).grid(row=1, column=0, sticky=tk.W)
        new_lock_length_entry = ttk.Entry(lock_window, font=("Microsoft YaHei", 13))
        new_lock_length_entry.grid(row=1, column=1, sticky=tk.E)
        ttk.Label(lock_window, text=translations[self.current_language]["offsetbottom"], font=("Microsoft YaHei", 13)).grid(row=2, column=0, sticky=tk.W)
        new_lock_offset_bottom_entry = ttk.Entry(lock_window, font=("Microsoft YaHei", 13))
        new_lock_offset_bottom_entry.grid(row=2, column=1, sticky=tk.E)
        ttk.Label(lock_window, text=translations[self.current_language]["offsettop"], font=("Microsoft YaHei", 13)).grid(row=3, column=0, sticky=tk.W)
        new_lock_offset_top_entry = ttk.Entry(lock_window, font=("Microsoft YaHei", 13))
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

        ttk.Label(remove_window, text=translations[self.current_language]["removeelectric"], font=("Microsoft YaHei", 13)).grid(row=0, column=0, sticky=tk.W)
        lock_to_remove_var = tk.StringVar()
        # lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var)
        lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var, font=("Microsoft YaHei", 13))
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

        ttk.Label(lock_window, text=translations[self.current_language]["boxlockname"], font=("Microsoft YaHei", 13)).grid(row=0, column=0, sticky=tk.W)
        new_lock_name_entry = ttk.Entry(lock_window, font=("Microsoft YaHei", 13))
        new_lock_name_entry.grid(row=0, column=1, sticky=tk.E)
        ttk.Label(lock_window, text=translations[self.current_language]["locklength"], font=("Microsoft YaHei", 13)).grid(row=1, column=0, sticky=tk.W)
        new_lock_length_entry = ttk.Entry(lock_window, font=("Microsoft YaHei", 13))
        new_lock_length_entry.grid(row=1, column=1, sticky=tk.E)
        ttk.Label(lock_window, text=translations[self.current_language]["offsetbottom"], font=("Microsoft YaHei", 13)).grid(row=2, column=0, sticky=tk.W)
        new_lock_offset_bottom_entry = ttk.Entry(lock_window, font=("Microsoft YaHei", 13))
        new_lock_offset_bottom_entry.grid(row=2, column=1, sticky=tk.E)
        ttk.Label(lock_window, text=translations[self.current_language]["offsettop"], font=("Microsoft YaHei", 13)).grid(row=3, column=0, sticky=tk.W)
        new_lock_offset_top_entry = ttk.Entry(lock_window, font=("Microsoft YaHei", 13))
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

        ttk.Label(remove_window, text=translations[self.current_language]["removebox"], font=("Microsoft YaHei", 13)).grid(row=0, column=0, sticky=tk.W)
        lock_to_remove_var = tk.StringVar()
        # lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var)
        lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var, font=("Microsoft YaHei", 13))
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

        ttk.Label(concealed_window, text=translations[self.current_language]["concealedname"], font=("Microsoft YaHei", 13)).grid(row=0, column=0, sticky=tk.W)
        new_concealed_name_entry = ttk.Entry(concealed_window, font=("Microsoft YaHei", 13))
        new_concealed_name_entry.grid(row=0, column=1, sticky=tk.E)
        ttk.Label(concealed_window, text=translations[self.current_language]["concealedlength"], font=("Microsoft YaHei", 13)).grid(row=1, column=0, sticky=tk.W)
        new_concealed_length_entry = ttk.Entry(concealed_window, font=("Microsoft YaHei", 13))
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

        ttk.Label(remove_window, text=translations[self.current_language]["concealedremove"], font=("Microsoft YaHei", 13)).grid(row=0, column=0, sticky=tk.W)
        concealed_to_remove_var = tk.StringVar()
        # lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=concealed_to_remove_var)
        lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=concealed_to_remove_var, font=("Microsoft YaHei", 13))
        lock_to_remove_menu.grid(row=0, column=1, sticky=tk.E)
        lock_to_remove_menu['values'] = list(concealeds.keys())


        delete_button = ttk.Button(remove_window, text=translations[self.current_language]["Delete"], command=delete_concealed)
        delete_button.grid(row=1, column=0, columnspan=2)
        
    def simple_help(self):
        guidance_window = tk.Toplevel(self.root)
        guidance_window.title("Application Guidance")
        

        # Add a label for the title
        tk.Label(guidance_window, text="Step-by-Step Guide", font=("Microsoft YaHei", 16, "bold")).pack(pady=10)
        
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
        tk.Label(guidance_window, text="Step-by-Step Guide", font=("Microsoft YaHei", 16, "bold")).pack(pady=10)

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
        tk.Label(guidance_window, text="Step-by-Step Guide", font=("Microsoft YaHei", 16, "bold")).pack(pady=10)

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
        tk.Label(guidance_window, text="Step-by-Step Guide", font=("Microsoft YaHei", 16, "bold")).pack(pady=10)

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
        
    def app_help(self):
        guidance_window = tk.Toplevel(self.root)
        guidance_window.title("Application Guidance")
        
        # Add a title label
        tk.Label(guidance_window, text="Maaf belum diinput, ditunggu sebentar (還沒準備好，稍等一下哦)", font=("Microsoft YaHei", 16, "bold")).pack(pady=10)
        
        # # Frame for the video
        # video_frame = tk.Frame(guidance_window)
        # video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # # Get the directory where the script is located (for portability)
        # base_path = os.path.dirname(os.path.abspath(__file__))  # Gets the current script's directory
        
        # # Define relative video paths
        # video_files = {
        #     "en": os.path.join(base_path, "guide.mp4"),
        #     "zh": os.path.join(base_path, "guide.mp4"),
        #     "id": os.path.join(base_path, "guide.mp4"),
        # }
        
        # # Use the selected language's video or default to English
        # video_path = video_files.get(self.current_language, video_files["en"])
        
        # # Create the TkinterVideo widget
        # video_player = TkinterVideo(master=video_frame, scaled=True)
        # video_player.load(video_path)
        # video_player.pack(fill=tk.BOTH, expand=True)
        
        # # Seek Bar (Slider)
        # seek_bar = tk.Scale(guidance_window, from_=0, to=100, orient="horizontal", length=400, command=lambda pos: seek_video(pos))
        # seek_bar.pack(pady=5, fill="x")
    
        # # Play/Pause Buttons
        # button_frame = tk.Frame(guidance_window)
        # button_frame.pack(pady=5)
    
        # play_button = tk.Button(button_frame, text="Play", command=video_player.play)
        # play_button.pack(side="left", padx=5)
    
        # pause_button = tk.Button(button_frame, text="Pause", command=video_player.pause)
        # pause_button.pack(side="left", padx=5)
    
        # # Function to Update Slider in Real-time
        # def update_slider():
        #     if video_player.is_playing():
        #         current_pos = video_player.current_duration() / video_player.video_info()["duration"] * 100
        #         seek_bar.set(current_pos)
        #     guidance_window.after(1000, update_slider)  # Update every second
    
        # # Function to Seek (Drag to Change Video Position)
        # def seek_video(pos):
        #     duration = video_player.video_info()["duration"]
        #     new_time = (int(pos) / 100) * duration
        #     video_player.seek(int(new_time))  # Jump to the selected time
    
        # # Start Updating the Seek Bar
        # update_slider()
        
        # guidance_window.mainloop()
        
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
        
    def validate_inputs(self):
        # Define the required fields for each context
        required_text_fields = {
            "UB_simple": ["num_doors", "right_vpiece_width", "max_height", "min_height", "frame_width",
                          "left_vpiece_width", "upper_hpiece_width", "lower_hpiece_width", "ub_wood_width"],
            "UB_electric": ["num_doors", "right_vpiece_width", "lock_height", "max_height", "min_height", 
                            "upper_hpiece_width", "lower_hpiece_width", "ub_wood_width",
                            "lock_height"],
            "UB_box": ["num_doors", "right_vpiece_width", "lock_height", "max_height", "min_height", 
                            "upper_hpiece_width", "lower_hpiece_width", "ub_wood_width",
                              "lock_height"],
            
            "UB_electric_concealed": ["num_doors", "right_vpiece_width", "lock_height", "max_height", "min_height", 
                            "upper_hpiece_width", "lower_hpiece_width", "ub_wood_width",
                            "lock_height", "concealed_wood_width"],
            "UB_box_concealed": ["num_doors", "right_vpiece_width", "lock_height", "max_height", "min_height", 
                            "upper_hpiece_width", "lower_hpiece_width", "ub_wood_width",
                              "lock_height", "concealed_wood_width"],
            
            "non_UB_simple": ["num_doors", "left_vpiece_width", "frame_height", "frame_width", "upper_hpiece_width",
                              "lower_hpiece_width", "right_vpiece_width"],
            "non_UB_electric": ["num_doors", "lock_height", "frame_height", "frame_width", "upper_hpiece_width",
                                "lower_hpiece_width", "right_vpiece_width", "lock_height"],
            "non_UB_box": ["num_doors", "lock_height", "frame_height", "frame_width", "upper_hpiece_width",
                                "lower_hpiece_width", "right_vpiece_width", "lock_height"],
            
            "non_UB_electric_concealed": ["num_doors", "lock_height", "frame_height", "frame_width", "upper_hpiece_width",
                                "lower_hpiece_width", "right_vpiece_width", "lock_height", "concealed_wood_width"],
            "non_UB_box_concealed": ["num_doors", "lock_height", "frame_height", "frame_width", "upper_hpiece_width",
                                "lower_hpiece_width", "right_vpiece_width", "lock_height", "concealed_wood_width"],
            
            "non_fireproof_simple": ["num_doors", "right_vpiece_width", "frame_height", "frame_width", "frame_width", 
                                      "left_vpiece_width", "upper_hpiece_width", "lower_hpiece_width", "ub_wood_width",
                                      "lock_height", "reinforce_wood"],
            "non_fireproof_simple_yipaiyikong": ["num_doors", "right_vpiece_width", "frame_height", "frame_width", "frame_width", 
                                                  "left_vpiece_width", "upper_hpiece_width", "lower_hpiece_width", "ub_wood_width", "slats_width", "gap_width"],
            "non_fireproof_electric": ["num_doors", "lock_height", "frame_height", "frame_width", "upper_hpiece_width",
                                        "lower_hpiece_width", "right_vpiece_width", "lock_height"],
            "non_fireproof_electric_yipaiyikong": ["num_doors", "lock_height", "frame_height", "frame_width", "upper_hpiece_width",
                                                    "lower_hpiece_width", "right_vpiece_width", "lock_height", "slats_width", "gap_width"],
            "non_fireproof_box": ["num_doors", "lock_height", "frame_height", "frame_width", "upper_hpiece_width",
                                  "lower_hpiece_width", "right_vpiece_width", "lock_height"],
            "non_fireproof_box_yipaiyikong": ["num_doors", "lock_height", "frame_height", "frame_width", "upper_hpiece_width",
                                              "lower_hpiece_width", "right_vpiece_width", "lock_height", "slats_width", "gap_width"],
            
            "non_fireproof_electric_concealed": ["num_doors", "lock_height", "frame_height", "frame_width", "upper_hpiece_width",
                                        "lower_hpiece_width", "right_vpiece_width", "lock_height", "concealed_wood_width"],
            "non_fireproof_electric_yipaiyikong_concealed": ["num_doors", "lock_height", "frame_height", "frame_width", "upper_hpiece_width",
                                                    "lower_hpiece_width", "right_vpiece_width", "lock_height", "slats_width", "gap_width", "concealed_wood_width"],
            "non_fireproof_box_concealed": ["num_doors", "lock_height", "frame_height", "frame_width", "upper_hpiece_width",
                                  "lower_hpiece_width", "right_vpiece_width", "lock_height", "concealed_wood_width"],
            "non_fireproof_box_yipaiyikong_concealed": ["num_doors", "lock_height", "frame_height", "frame_width", "upper_hpiece_width",
                                              "lower_hpiece_width", "right_vpiece_width", "lock_height", "slats_width", "gap_width", "concealed_wood_width"]
        }
        
        required_dropdown_fields = ["category", "structure_type", "door_type", "edge_sealing_type"]
    
        # Determine the current mode and door type
        mode = self.mode_selection.get()
        door_type = self.entries["door_type"][1].get().strip().lower()
        category = self.entries["category"][1].get().strip().lower()
        structure_type = self.entries["structure_type"][1].get().strip().lower()
        concealed_door_closer_name = self.entries["concealed_door_closer_name"][1].get().strip()

    
        if concealed_door_closer_name in concealeds:
            concealed_length = concealeds[concealed_door_closer_name]['length']
        else:
            # Set default values if no concealed door closer is selected
            concealed_length = 0
            
        # Map context to required fields
        if mode == "UB" and door_type == self.simple_label:
            context = "UB_simple"
        elif mode == "UB" and door_type == self.electric_lock_label:
            if concealed_length == 0:
                context = "UB_electric"
            else:
                context = "UB_electric_concealed"
        elif mode == "UB" and door_type == self.box_lock_label:
            if concealed_length == 0:
                context = "UB_box"
            else:
                context = "UB_box_concealed"
        elif mode != "UB" and door_type == self.simple_label:
            context = "non_UB_simple"
        elif mode != "UB" and door_type == self.electric_lock_label:
            if concealed_length == 0:
                context = "non_UB_electric"
            else:
                context = "non_UB_electric_concealed"
        elif mode != "UB"and door_type == self.box_lock_label:
            if concealed_length ==0:
                context = "non_UB_box"
            else:
                context = "non_UB_box_concealed"
        elif category == self.fireproof_label and structure_type in [self.honeycomb_board_label, self.honeycomb_paper_label]:
            if door_type == self.simple_label:
                context = "non_fireproof_simple"
            elif door_type == self.electric_lock_label:
                if concealed_length == 0:
                    context = "non_fireproof_electric"
                else:
                    context = "non_fireproof_electric_concealed"
            else:
                if concealed_length == 0:
                    context = "non_fireproof_box"
                else:
                    context = "non_fireproof_box_concealed"
        elif category == self.non_fireproof_label and structure_type == self.yipaiyikong_label:
            if door_type == self.simple_label:
                context = "non_fireproof_simple_yipaiyikong"
            elif door_type == self.electric_lock_label:
                if concealed_length == 0:
                    context = "non_fireproof_electric_yipaiyikong"
                else:
                    context = "non_fireproof_electric_yipaiyikong_concealed"
            else:
                if concealed_length == 0:
                    context = "non_fireproof_box_yipaiyikong"
                else:
                    context = "non_fireproof_box_yipaiyikong_concealed"
        else:
            context = None

    
        # if not context:
        #     raise ValueError("無效的模式或門類型。\n Mode atau jenis pintu tidak valid.")
    
        # Validate the required fields
        if context in required_text_fields:
            for field in required_text_fields[context]:
                if field in self.entries and self.entries[field][0].winfo_ismapped():
                    value = self.entries[field][1].get().strip()
                    if not value.isdigit():
                        raise ValueError(f"請輸入有效的數字以 {translations[self.current_language][field]}\n"
                                         f"Silakan masukkan nomor yang valid untuk {translations[self.current_language][field]}")

        for dropdown in required_dropdown_fields:
            if dropdown in self.entries and self.entries[dropdown][0].winfo_ismapped():
                value = self.entries[dropdown][1].get().strip()
                if value == "":
                    raise ValueError(
                        f"{translations[self.current_language][dropdown]} 必須選擇一個選項。\n"
                        f"Harus memilih salah satu opsi untuk {translations[self.current_language][dropdown]}"
                    )
    
        if door_type == self.electric_lock_label:
            electric_lock_name = self.entries["electric_lock_name"][1].get().strip()
            if electric_lock_name not in electric_locks:
                raise ValueError(
                    f"{translations[self.current_language]['electric_lock_name']} 必須選擇有效的電鎖名稱。\n"
                    f"Harus memilih nama kunci listrik yang valid untuk {translations[self.current_language]['electric_lock_name']}"
                    )
                
        if door_type == self.box_lock_label:
            box_lock_name = self.entries["box_lock_name"][1].get().strip()
            if box_lock_name not in box_locks:
                raise ValueError(
                    f"{translations[self.current_language]['electric_lock_name']} 必須選擇有效的電鎖名稱。\n"
                    f"Harus memilih nama kunci kotak yang valid untuk {translations[self.current_language]['electric_lock_name']}"
                    )

   
if __name__ == "__main__":
    root = tk.Tk()
    app = DoorFrameCalculator(root)
    app.update_language()  # Initialize with the correct language
    root.mainloop()
    