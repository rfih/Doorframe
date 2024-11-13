import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Determine the path to the JSON files
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(__file__)

LOCK_FILE = os.path.join(application_path, 'electric_locks.json')
TRANSLATIONS_FILE = os.path.join(application_path, 'translations.json')
BOXLOCK_FILE = os.path.join(application_path, 'box_locks.json')


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

# Load translations from file
def load_translations():
    if os.path.exists(TRANSLATIONS_FILE):
        with open(TRANSLATIONS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def draw_door_frame(inner_width, frame_height, right_vertical_piece_width, left_vertical_piece_width,
               upper_horizontal_piece_width, lower_horizontal_piece_width, outer_wood_upper, inner_wood_upper,
               outer_wood_bottom, inner_wood_bottom, door_type):
    fig, axs = plt.subplots(1, 2, figsize=(10, 6))  # Create two subplots side by side

    # Draw the electric lock door (left)
    if (door_type == "electric lock" or door_type == "box lock"):
        ax = axs[0]
        # Outer frame
        outer_rect = patches.Rectangle((0, 0), inner_width + right_vertical_piece_width + left_vertical_piece_width, 
                                       frame_height + upper_horizontal_piece_width + lower_horizontal_piece_width, 
                                       linewidth=2, edgecolor='black', facecolor='none')
        # Inner frame
        inner_rect = patches.Rectangle((right_vertical_piece_width, lower_horizontal_piece_width), 
                                       inner_width, 
                                       frame_height, 
                                       linewidth=2, edgecolor='black', facecolor='lightgrey')

        # Top and bottom inner/outer parts
        top_outer = patches.Rectangle((right_vertical_piece_width, frame_height + lower_horizontal_piece_width), 
                                      inner_width, 
                                      outer_wood_upper, 
                                      linewidth=2, edgecolor='black', facecolor='none')
        
        bottom_outer = patches.Rectangle((right_vertical_piece_width, lower_horizontal_piece_width - outer_wood_bottom), 
                                         inner_width, 
                                         outer_wood_bottom, 
                                         linewidth=2, edgecolor='black', facecolor='none')

        ax.add_patch(outer_rect)
        ax.add_patch(inner_rect)
        ax.add_patch(top_outer)
        ax.add_patch(bottom_outer)

        ax.set_xlim(-left_vertical_piece_width-20, inner_width + right_vertical_piece_width + 20)
        ax.set_ylim(-lower_horizontal_piece_width-40, frame_height + upper_horizontal_piece_width + 40)
        ax.set_aspect('equal')
        ax.axis('off')

    # Draw the simple door (right)
    ax = axs[1]
    simple_outer_rect = patches.Rectangle((0, 0), inner_width + right_vertical_piece_width + left_vertical_piece_width, 
                                          frame_height + upper_horizontal_piece_width + lower_horizontal_piece_width, 
                                          linewidth=2, edgecolor='black', facecolor='none')
    simple_inner_rect = patches.Rectangle((right_vertical_piece_width, lower_horizontal_piece_width), 
                                          inner_width, 
                                          frame_height, 
                                          linewidth=2, edgecolor='black', facecolor='lightgrey')

    ax.add_patch(simple_outer_rect)
    ax.add_patch(simple_inner_rect)

    ax.set_xlim(-left_vertical_piece_width-20, inner_width + right_vertical_piece_width + 20)
    ax.set_ylim(-lower_horizontal_piece_width-40, frame_height + upper_horizontal_piece_width + 40)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.show()
    return fig

# Initialize electric locks and translations
electric_locks = load_electric_locks()
translations = load_translations()
box_locks = load_box_locks()

class DoorFrameCalculator:
    def __init__(self, root):
        self.root = root
        self.current_language = "en"
        self.entries = {}
        self.create_widgets()

    def create_widgets(self):
        self.root.title("Door Frame Material Calculator")

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=translations[self.current_language]["edit_menu"], menu=self.edit_menu)
        self.edit_menu.add_command(label=translations[self.current_language]["add_electric_lock"], command=self.add_electric_lock)
        self.edit_menu.add_command(label=translations[self.current_language]["remove_electric_lock"], command=self.remove_electric_lock)
        self.edit_menu.add_command(label=translations[self.current_language]["add_box_lock"], command=self.add_box_lock)
        self.edit_menu.add_command(label=translations[self.current_language]["remove_box_lock"], command=self.remove_box_lock)

        self.language_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=translations[self.current_language]["language"], menu=self.language_menu)
        self.language_menu.add_command(label="English", command=lambda: self.change_language("en"))
        self.language_menu.add_command(label="中文", command=lambda: self.change_language("zh"))
        self.language_menu.add_command(label="Bahasa", command=lambda: self.change_language("id"))

        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.create_label_and_entry(frame, "door_type", 0, "door_type")
        self.entries["door_type"][1]['values'] = ("simple", "UB", "electric lock", "box lock")
        self.entries["door_type"][1].bind("<<ComboboxSelected>>", self.update_inputs)

        self.create_label_and_entry(frame, "num_doors", 1)
        self.create_label_and_entry(frame, "right_vpiece_width", 2)
        self.create_label_and_entry(frame, "left_vpiece_width", 3)
        self.create_label_and_entry(frame, "upper_hpiece_width", 4)
        self.create_label_and_entry(frame, "lower_hpiece_width", 5)
        self.create_label_and_entry(frame, "edge_sealing_type", 6, "edge_sealing_type")
        self.entries["edge_sealing_type"][1]['values'] = ("實木", "白木 4 mm", "鋁封邊", "ABS", "鐡封邊+石墨片", "鐡封邊")

        self.create_label_and_entry(frame, "edge_sealing_thickness", 7)
        self.create_label_and_entry(frame, "max_height", 8)
        self.create_label_and_entry(frame, "min_height", 9)
        self.create_label_and_entry(frame, "electric_lock_name", 10, "electric_lock_name")
        self.entries["electric_lock_name"][1]['values'] = list(electric_locks.keys())
        self.create_label_and_entry(frame, "box_lock_name", 11, "box_lock_name")
        self.entries["box_lock_name"][1]['values'] = list(box_locks.keys())

        self.create_label_and_entry(frame, "lock_length", 12)
        self.create_label_and_entry(frame, "lock_height", 13)
        self.create_label_and_entry(frame, "lock_direction", 14, "lock_direction")
        self.entries["lock_direction"][1]['values'] = ("top", "bottom")
        self.create_label_and_entry(frame, "concealed_door_closer", 15, "concealed_door_closer")
        self.entries["concealed_door_closer"][1]['values'] = ("yes", "no")

        self.create_label_and_entry(frame, "lock_offset_bottom", 16)
        self.create_label_and_entry(frame, "frame_height", 17)
        self.create_label_and_entry(frame, "frame_width", 18)

        calculate_button = ttk.Button(frame, text=translations[self.current_language]["calculate"], command=self.calculate_material)
        calculate_button.grid(row=19, column=0, columnspan=2)

        self.result_text = tk.Text(frame, width=100, height=32, font=("Helvetica", 13))
        self.result_text.grid(row=20, column=0, columnspan=2)
        
        self.canvas_frame = ttk.Frame(frame)
        self.canvas_frame.grid(row=20, column=1, rowspan=20)  # Adjust placement as needed

        trademark_label = ttk.Label(frame, text="© 2024 HBB", font=("Helvetica", 8))
        trademark_label.grid(row=21, column=0, columnspan=2, pady=(10, 0))

        self.update_inputs()

    def create_label_and_entry(self, frame, key, row, entry_type="entry"):
        label = ttk.Label(frame, text=translations[self.current_language][key], font=("Helvetica", 13))
        label.grid(row=row, column=0, sticky=tk.W)
        if entry_type == "entry":
            entry = ttk.Entry(frame, font=("Helvetica", 13))
        elif entry_type == "door_type" or entry_type == "edge_sealing_type" or entry_type == "electric_lock_name" or entry_type == "lock_direction" or entry_type == "concealed_door_closer" or entry_type == "box_lock_name":
            entry = ttk.Combobox(frame, font=("Helvetica", 13))
        entry.grid(row=row, column=1, sticky=tk.E)
        self.entries[key] = (label, entry)  

    def update_inputs(self, *args):
        door_type = self.entries["door_type"][1].get().strip().lower()
        if door_type == "electric lock":
            self.show_entries(["left_vpiece_width"], False)
            self.show_entries(["electric_lock_name", "lock_height", "lock_direction", "concealed_door_closer"], True)
            self.show_entries(["max_height", "min_height", "box_lock_name"], False)
        elif door_type == "ub":
            self.show_entries(["left_vpiece_width", "electric_lock_name", "lock_length", "lock_height", "lock_direction", "lock_offset_bottom"], False)
            self.show_entries(["max_height", "min_height"], True)
        elif door_type == "box lock":
            self.show_entries(["left_vpiece_width"], False)
            self.show_entries(["box_lock_name", "lock_height", "lock_direction", "concealed_door_closer"], True)
            self.show_entries(["max_height", "min_height", "electric_lock_name"], False)
        else:
            self.show_entries(["left_vpiece_width"], True)
            self.show_entries(["electric_lock_name", "lock_length", "lock_height", "lock_direction", "lock_offset_bottom", "max_height", "min_height", "box_lock_name", "lock_height", "lock_direction", "concealed_door_closer"], False)

    def show_entries(self, keys, show):
        for key in keys:
            if show:
                self.entries[key][0].grid()
                self.entries[key][1].grid()
            else:
                self.entries[key][0].grid_remove()
                self.entries[key][1].grid_remove()

    def change_language(self, language):
        self.current_language = language
        self.update_language()

    def update_language(self):
        self.root.title(translations[self.current_language]["app_title"])
        self.menu_bar.entryconfig(1, label=translations[self.current_language]["edit_menu"])
        self.menu_bar.entryconfig(2, label=translations[self.current_language]["language"])
        for key, (label, entry) in self.entries.items():
            label.config(text=translations[self.current_language][key])
            
        self.entries["door_type"][1]['values'] = ("簡單", "UB", "電子鎖", "匣式鎖")
        self.entries["edge_sealing_type"][1]['values'] = ("實木", "白木 4 mm", "鋁封邊", "ABS", "鐡封邊+石墨片", "鐡封邊")
        self.entries["electric_lock_name"][1]['values'] = list(electric_locks.keys())
        self.entries["box_lock_name"][1]['values'] = list(box_locks.keys())
        self.entries["lock_direction"][1]['values'] = ("top", "bottom")
        self.entries["concealed_door_closer"][1]['values'] = ("yes", "no")
        self.language_menu.entryconfig(0, label="English")
        self.language_menu.entryconfig(1, label="中文")
        self.language_menu.entryconfig(2, label="Bahasa")

    def calculate_material(self):
        try:
            # for key in ["num_doors", "right_vpiece_width", "left_vpiece_width", "upper_hpiece_width", "lower_hpiece_width", "lock_height", "frame_height", "frame_width"]:
            #     if not self.entries[key][1].get().strip().isdigit():
            #         raise ValueError(f"Please enter a valid number for {translations[self.current_language][key]}")
            door_type = self.entries["door_type"][1].get().strip().lower()
            num_doors = int(self.entries["num_doors"][1].get())
    
            right_vertical_piece_width = int(self.entries["right_vpiece_width"][1].get())
    
            if door_type != "electric lock" and door_type != "box lock":
                left_vertical_piece_width = int(self.entries["left_vpiece_width"][1].get())
            else:
                left_vertical_piece_width = 70
    
            upper_horizontal_piece_width = int(self.entries["upper_hpiece_width"][1].get())
            lower_horizontal_piece_width = int(self.entries["lower_hpiece_width"][1].get())

            edge_sealing_options = {
                "實木": 6,
                "鋁封邊": 6,
                "ABS": 0.5,
                "鐡封邊+石墨片": 2,
                "鐡封邊": 1,
                "白木 4 mm":4
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
            concealed_door_closer = ""
            box_lock_name = ""
            box_lock_height = 0
            # frame_height = 0
            # frame_width = 0
            # inner_width = 0

            if door_type == "UB":
                max_height = int(self.entries["max_height"][1].get())
                min_height = int(self.entries["min_height"][1].get())
                frame_height = max_height
            elif door_type == "box lock":
                # for key in ["num_doors", "right_vpiece_width", "upper_hpiece_width", "lower_hpiece_width", "lock_height", "frame_height", "frame_width"]:
                #     if not self.entries[key][1].get().strip().isdigit():
                #         raise ValueError(f"Please enter a valid number for {translations[self.current_language][key]}")
                box_lock_name = self.entries["box_lock_name"][1].get().strip()
                if box_lock_name in box_locks:
                    lock_length = box_locks[box_lock_name]['length']
                    lock_offset_bottom = box_locks[box_lock_name]['offset_bottom']
                    lock_offset_top = box_locks[box_lock_name]['offset_top']
                else:
                    lock_length = int(self.entries["lock_length"][1].get())
                    lock_offset_bottom = int(self.entries["lock_offset_bottom"][1].get())
                    lock_offset_top = lock_length - lock_offset_bottom
                box_lock_height = int(self.entries["lock_height"][1].get())
                lock_direction = self.entries["lock_direction"][1].get().strip().lower()
                concealed_door_closer = self.entries["concealed_door_closer"][1].get().strip().lower()
                frame_height = int(self.entries["frame_height"][1].get())
                frame_width = int(self.entries["frame_width"][1].get())
            elif door_type == "electric lock":
                # for key in ["num_doors", "right_vpiece_width", "upper_hpiece_width", "lower_hpiece_width", "lock_height", "frame_height", "frame_width"]:
                #     if not self.entries[key][1].get().strip().isdigit():
                #         raise ValueError(f"Please enter a valid number for {translations[self.current_language][key]}")
                electric_lock_name = self.entries["electric_lock_name"][1].get().strip()
                if electric_lock_name in electric_locks:
                    lock_length = electric_locks[electric_lock_name]['length']
                    lock_offset_bottom = electric_locks[electric_lock_name]['offset_bottom']
                    lock_offset_top = electric_locks[electric_lock_name]['offset_top']
                else:
                    lock_length = int(self.entries["lock_length"][1].get())
                    lock_offset_bottom = int(self.entries["lock_offset_bottom"][1].get())
                    lock_offset_top = lock_length - lock_offset_bottom
                electric_lock_height = int(self.entries["lock_height"][1].get())
                lock_direction = self.entries["lock_direction"][1].get().strip().lower()
                concealed_door_closer = self.entries["concealed_door_closer"][1].get().strip().lower()
                frame_height = int(self.entries["frame_height"][1].get())
                frame_width = int(self.entries["frame_width"][1].get())

                if edge_sealing_type == "鐡封邊+石墨片" or "鐡封邊":
                    electric_lock_height += 3
                    box_lock_height += 3

            else:
                frame_height = int(self.entries["frame_height"][1].get())
                frame_width = int(self.entries["frame_width"][1].get())

            if edge_sealing_type == "ABS":
                frame_height += 10
                frame_width += 10
            elif edge_sealing_type in ["鐡封邊+石墨片", "鐡封邊", "白木 4 mm"]:
                frame_height += 5
                frame_width += 5

            inner_width, plywood_width, plywood_height, total_length_all_doors, vertical_piece_length, \
                horizontal_pieces_length, frame_width, outer_wood_bottom, inner_wood_bottom, \
                outer_wood_upper, inner_wood_upper,very_upper_horizontal_piece_width,very_upper_horizontal_piece_length = self.calculate_material_requirements(
                    door_type, num_doors, frame_height, right_vertical_piece_width, left_vertical_piece_width,
                    upper_horizontal_piece_width, lower_horizontal_piece_width, edge_sealing, max_height, min_height,
                    vertical_piece_width, horizontal_piece_width, frame_width, electric_lock_name, box_lock_name, lock_length,
                    electric_lock_height, box_lock_height, lock_direction, concealed_door_closer, lock_offset_bottom, lock_offset_top)
                
            fig = draw_door_frame(inner_width, frame_height, right_vertical_piece_width, left_vertical_piece_width,
                           upper_horizontal_piece_width, lower_horizontal_piece_width, outer_wood_upper, inner_wood_upper,
                           outer_wood_bottom, inner_wood_bottom, door_type)
            # Embed the figure in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0)

            report = self.generate_report(door_type, num_doors, inner_width, plywood_width, plywood_height, total_length_all_doors,
                                          vertical_piece_length, horizontal_pieces_length, right_vertical_piece_width,
                                          left_vertical_piece_width, upper_horizontal_piece_width, lower_horizontal_piece_width,
                                          edge_sealing, max_height, min_height, vertical_piece_width, horizontal_piece_width,
                                          electric_lock_name, box_lock_name, lock_length, electric_lock_height, box_lock_height, lock_direction, concealed_door_closer,
                                          outer_wood_bottom, inner_wood_bottom, outer_wood_upper, inner_wood_upper,very_upper_horizontal_piece_width,very_upper_horizontal_piece_length)
            
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, report)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def calculate_material_requirements(self, door_type, num_doors, frame_height, right_vertical_piece_width,
                                        left_vertical_piece_width, upper_horizontal_piece_width, lower_horizontal_piece_width,
                                        edge_sealing, max_height, min_height, vertical_piece_width, horizontal_piece_width,
                                        frame_width, electric_lock_name, box_lock_name, lock_length, electric_lock_height, box_lock_height, lock_direction, concealed_door_closer, 
                                        lock_offset_bottom, lock_offset_top):
        if door_type in ["electric lock", "box lock"]:
            inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2)
        else:
            inner_width = frame_width - right_vertical_piece_width - left_vertical_piece_width

        if door_type == "UB":
            plywood_height = max_height - (upper_horizontal_piece_width * 2) - lower_horizontal_piece_width
        else:
            plywood_height = frame_height - upper_horizontal_piece_width - lower_horizontal_piece_width
            

        plywood_width = inner_width
        vertical_piece_length = frame_height
        horizontal_pieces_length = inner_width
        # print("test3", horizontal_pieces_length)
        very_upper_horizontal_piece_width = 100
        very_upper_horizontal_piece_length = horizontal_pieces_length

        total_length_per_door = vertical_piece_length * 2 + horizontal_pieces_length * 2
        total_length_all_doors = total_length_per_door * num_doors

        outer_wood_bottom = inner_wood_bottom = outer_wood_upper = inner_wood_upper = None
        if door_type == "electric lock":
            if lock_direction == "bottom":
                outer_wood_bottom = electric_lock_height - lock_offset_bottom
                inner_wood_bottom = outer_wood_bottom - 30
                outer_wood_upper = frame_height - (outer_wood_bottom + lock_length)
                inner_wood_upper = outer_wood_upper - 30
            if lock_direction == "top":
                outer_wood_upper = electric_lock_height - lock_offset_top
                inner_wood_upper = outer_wood_upper - 75
                outer_wood_bottom = frame_height - (outer_wood_upper + lock_length)
                inner_wood_bottom = outer_wood_bottom - 30
                
            if concealed_door_closer == "yes":
                very_upper_horizontal_piece_width = 100
                very_upper_horizontal_piece_length = horizontal_pieces_length - 240
            if concealed_door_closer == "no":
                very_upper_horizontal_piece_width = 0
                very_upper_horizontal_piece_length = 0
                
        if door_type == "box lock":
            if lock_direction == "bottom":
                outer_wood_bottom = box_lock_height - lock_offset_bottom
                inner_wood_bottom = outer_wood_bottom - 30
                outer_wood_upper = frame_height - (outer_wood_bottom + lock_length)
                inner_wood_upper = outer_wood_upper - 30
            if lock_direction == "top":
                outer_wood_upper = box_lock_height - lock_offset_top
                inner_wood_upper = outer_wood_upper - 30
                outer_wood_bottom = frame_height - (outer_wood_upper + lock_length)
                inner_wood_bottom = outer_wood_bottom - 30
                
            if concealed_door_closer == "yes":
                very_upper_horizontal_piece_width = 100
                very_upper_horizontal_piece_length = horizontal_pieces_length - 240
            if concealed_door_closer == "no":
                very_upper_horizontal_piece_width = 0
                very_upper_horizontal_piece_length = 0
                
        if (door_type == "electric lock" or door_type == "box lock") and concealed_door_closer == "yes":
            inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2)
            plywood_height = frame_height - upper_horizontal_piece_width - lower_horizontal_piece_width - very_upper_horizontal_piece_width
            plywood_width = inner_width
            # print("test4", inner_width)

        return inner_width, plywood_width, plywood_height, total_length_all_doors, vertical_piece_length, \
               horizontal_pieces_length, frame_width, outer_wood_bottom, inner_wood_bottom, outer_wood_upper, inner_wood_upper, very_upper_horizontal_piece_width,\
               very_upper_horizontal_piece_length

    def generate_report(self, door_type, num_doors, inner_width, plywood_width, plywood_height, total_length_all_doors,
                        vertical_piece_length, horizontal_pieces_length, right_vertical_piece_width,
                        left_vertical_piece_width, upper_horizontal_piece_width, lower_horizontal_piece_width,
                        edge_sealing, max_height, min_height, vertical_piece_width, horizontal_piece_width,
                        electric_lock_name, box_lock_name, lock_length, electric_lock_height, box_lock_height, lock_direction, concealed_door_closer, outer_wood_bottom,
                        inner_wood_bottom, outer_wood_upper, inner_wood_upper,very_upper_horizontal_piece_width,very_upper_horizontal_piece_length):
        lang = self.current_language
        total_right_vertical_pieces = num_doors if right_vertical_piece_width else 0
        total_left_vertical_pieces = num_doors if left_vertical_piece_width else 0

        if (door_type == "electric lock" or door_type == "box lock"):
            total_left_vertical_pieces = num_doors * 4

        total_horizontal_pieces = num_doors * sum(h is not None for h in [upper_horizontal_piece_width, lower_horizontal_piece_width])
        # print("test 3",outer_wood_bottom)


        if door_type == "UB":
            total_horizontal_pieces += num_doors

        report = f"""
        {translations[lang]["app_title"]}

        {translations[lang]["door_type"]}: {door_type.upper()}
        {translations[lang]["num_doors"]}: {num_doors}
        {translations[lang]["inner_width"]}: {inner_width} mm
        {translations[lang]["plywood_dimensions"]}: {plywood_width} mm x {plywood_height} mm 
        {translations[lang]["edge_sealing"]}: {edge_sealing} mm
        """

        if door_type == "electric lock":
            report += f"""
            {translations[lang]["electric_lock"]}: {electric_lock_name}
            {translations[lang]["electric_lock_height"]}: {electric_lock_height} mm
            {translations[lang]["direction"]}: {lock_direction.capitalize()}

            {translations[lang]["total_wood_length"]}: {outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length +(horizontal_pieces_length * 2):.2f} mm
            {translations[lang]["total_wood"]}: {(outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length +(horizontal_pieces_length * 2))/2400}
            """
            report += f"""
            {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
              - {translations[lang]["length_each_piece"]}: {vertical_piece_length} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors}
              - {translations[lang]["total_num_pieces"]}: {total_right_vertical_pieces}

            {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
              - {translations[lang]["outer_wood_upper_part"]}: {outer_wood_upper} mm
              - {translations[lang]["inner_wood_upper_part"]}: {inner_wood_upper} mm
              - {translations[lang]["outer_wood_bottom_part"]}: {outer_wood_bottom} mm
              - {translations[lang]["inner_wood_bottom_part"]}: {inner_wood_bottom} mm
              - {translations[lang]["concealed_door_closer"]} : {very_upper_horizontal_piece_length}
              - {translations[lang]["num_pieces_per_door"]}: {num_doors * 4}
              - {translations[lang]["total_num_pieces"]}: {total_left_vertical_pieces}
            """
        elif door_type == "box lock":
            report += f"""
            {translations[lang]["box_lock"]}: {box_lock_name}
            {translations[lang]["box_lock_height"]}: {box_lock_height} mm
            {translations[lang]["direction"]}: {lock_direction.capitalize()}

            {translations[lang]["total_wood_length"]}: {outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length +(horizontal_pieces_length * 2):.2f} mm
            {translations[lang]["total_wood"]}: {(outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + very_upper_horizontal_piece_length +(horizontal_pieces_length * 2))/2400}
            """
            report += f"""
            {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
              - {translations[lang]["length_each_piece"]}: {vertical_piece_length} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors}
              - {translations[lang]["total_num_pieces"]}: {total_right_vertical_pieces}

            {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
              - {translations[lang]["outer_wood_upper_part"]}: {outer_wood_upper} mm
              - {translations[lang]["inner_wood_upper_part"]}: {inner_wood_upper} mm
              - {translations[lang]["outer_wood_bottom_part"]}: {outer_wood_bottom} mm
              - {translations[lang]["inner_wood_bottom_part"]}: {inner_wood_bottom} mm
              - {translations[lang]["concealed_door_closer"]} : {very_upper_horizontal_piece_length}
              - {translations[lang]["num_pieces_per_door"]}: {num_doors * 4}
              - {translations[lang]["total_num_pieces"]}: {total_left_vertical_pieces}
            """
        else:
            report += f"""
            {translations[lang]["total_wood_length"]}: {total_length_all_doors:.2f} mm
            {translations[lang]["total_wood"]}: {(total_length_all_doors)/2400}

            """
            if vertical_piece_width:
                report += f"""
            {translations[lang]["vertical_pieces"]} ({vertical_piece_width}mm):
              - {translations[lang]["length_each_piece"]}: {vertical_piece_length} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors * 2}
              - {translations[lang]["total_num_pieces"]}: {num_doors * 2}
                """
            else:
                report += f"""
            {translations[lang]["right_vertical_pieces"]} ({right_vertical_piece_width}mm):
              - {translations[lang]["length_each_piece"]}: {vertical_piece_length} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors}
              - {translations[lang]["total_num_pieces"]}: {total_right_vertical_pieces}

            {translations[lang]["left_vertical_pieces"]} ({left_vertical_piece_width}mm):
              - {translations[lang]["length_each_piece"]}: {vertical_piece_length} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors}
              - {translations[lang]["total_num_pieces"]}: {total_left_vertical_pieces}
                """
        if horizontal_piece_width:
            report += f"""
            {translations[lang]["horizontal_pieces"]} ({horizontal_piece_width}mm):
              - {translations[lang]["length_each_piece"]}: {inner_width} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors * 2}
              - {translations[lang]["total_num_pieces"]}: {total_horizontal_pieces}
                """
        else:
            report += f"""
            {translations[lang]["upper_horizontal_pieces"]} ({upper_horizontal_piece_width}mm):
              - {translations[lang]["length_each_piece"]}: {inner_width} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors}
              - {translations[lang]["total_num_pieces"]}: {num_doors}

            {translations[lang]["lower_horizontal_pieces"]} ({lower_horizontal_piece_width}mm):
              - {translations[lang]["length_each_piece"]}: {inner_width} mm
              - {translations[lang]["num_pieces_per_door"]}: {num_doors}
              - {translations[lang]["total_num_pieces"]}: {num_doors}
                """
        if door_type == "ub":
            report += f"""
            {translations[lang]["ub_note"]}
            """
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
                messagebox.showerror("Error", "Electric lock name cannot be empty.")

        lock_window = tk.Toplevel(self.root)
        lock_window.title("Add Electric Lock")

        ttk.Label(lock_window, text="Electric Lock Name:", font=("Helvetica", 13)).grid(row=0, column=0, sticky=tk.W)

        new_lock_name_entry = ttk.Entry(lock_window, font=("Helvetica", 13))

        new_lock_name_entry.grid(row=0, column=1, sticky=tk.E)

        ttk.Label(lock_window, text="Lock Length (mm):", font=("Helvetica", 13)).grid(row=1, column=0, sticky=tk.W)
        new_lock_length_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_length_entry.grid(row=1, column=1, sticky=tk.E)
        ttk.Label(lock_window, text="Offset Bottom (mm):", font=("Helvetica", 13)).grid(row=2, column=0, sticky=tk.W)
        new_lock_offset_bottom_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_offset_bottom_entry.grid(row=2, column=1, sticky=tk.E)
        ttk.Label(lock_window, text="Offset Top (mm):", font=("Helvetica", 13)).grid(row=3, column=0, sticky=tk.W)
        new_lock_offset_top_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_offset_top_entry.grid(row=3, column=1, sticky=tk.E)

        save_button = ttk.Button(lock_window, text="Save", command=save_new_lock)
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
        remove_window.title("Remove Electric Lock")

        ttk.Label(remove_window, text="Select Electric Lock to Remove:", font=("Helvetica", 13)).grid(row=0, column=0, sticky=tk.W)
        lock_to_remove_var = tk.StringVar()
        lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var)
        lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var, font=("Helvetica", 13))
        lock_to_remove_menu.grid(row=0, column=1, sticky=tk.E)
        lock_to_remove_menu['values'] = list(electric_locks.keys())


        delete_button = ttk.Button(remove_window, text="Delete", command=delete_lock)
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
                messagebox.showerror("Error", "box lock name cannot be empty.")

        lock_window = tk.Toplevel(self.root)
        lock_window.title("Add box Lock")

        ttk.Label(lock_window, text="box Lock Name:", font=("Helvetica", 13)).grid(row=0, column=0, sticky=tk.W)

        new_lock_name_entry = ttk.Entry(lock_window, font=("Helvetica", 13))

        new_lock_name_entry.grid(row=0, column=1, sticky=tk.E)

        ttk.Label(lock_window, text="Lock Length (mm):", font=("Helvetica", 13)).grid(row=1, column=0, sticky=tk.W)
        new_lock_length_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_length_entry.grid(row=1, column=1, sticky=tk.E)
        ttk.Label(lock_window, text="Offset Bottom (mm):", font=("Helvetica", 13)).grid(row=2, column=0, sticky=tk.W)
        new_lock_offset_bottom_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_offset_bottom_entry.grid(row=2, column=1, sticky=tk.E)
        ttk.Label(lock_window, text="Offset Top (mm):", font=("Helvetica", 13)).grid(row=3, column=0, sticky=tk.W)
        new_lock_offset_top_entry = ttk.Entry(lock_window, font=("Helvetica", 13))
        new_lock_offset_top_entry.grid(row=3, column=1, sticky=tk.E)

        save_button = ttk.Button(lock_window, text="Save", command=save_new_lock)
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
        remove_window.title("Remove box Lock")

        ttk.Label(remove_window, text="Select box Lock to Remove:", font=("Helvetica", 13)).grid(row=0, column=0, sticky=tk.W)
        lock_to_remove_var = tk.StringVar()
        lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var)
        lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var, font=("Helvetica", 13))
        lock_to_remove_menu.grid(row=0, column=1, sticky=tk.E)
        lock_to_remove_menu['values'] = list(box_locks.keys())


        delete_button = ttk.Button(remove_window, text="Delete", command=delete_lock)
        delete_button.grid(row=1, column=0, columnspan=2)
        

if __name__ == "__main__":
    root = tk.Tk()
    app = DoorFrameCalculator(root)
    root.mainloop()
