import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys

# Determine the path to the JSON file
if getattr(sys, 'frozen', False):
    # The application is frozen
    application_path = sys._MEIPASS
else:
    # The application is not frozen
    application_path = os.path.dirname(__file__)

LOCK_FILE = os.path.join(application_path, 'electric_locks.json')
TRANSLATION_FILE = os.path.join(application_path, 'translations.json')

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

# Load translations from file
def load_translations():
    if os.path.exists(TRANSLATION_FILE):
        with open(TRANSLATION_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# Initialize electric locks and translations
electric_locks = load_electric_locks()
translations = load_translations()

class DoorFrameCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Door Frame Material Calculator")

        self.current_language = "en"

        # Create menu
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)

        # Language menu
        self.language_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=translations[self.current_language]["language"], menu=self.language_menu)
        self.language_menu.add_command(label="English", command=lambda: self.change_language("en"))
        self.language_menu.add_command(label="中文", command=lambda: self.change_language("zh"))
        self.language_menu.add_command(label="Bahasa", command=lambda: self.change_language("id"))

        # Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=translations[self.current_language]["edit_menu"], menu=self.edit_menu)
        # self.edit_menu.add_command(label=translations[self.current_language]["add_electric_lock"], command=self.add_electric_lock)
        # self.edit_menu.add_command(label=translations[self.current_language]["remove_electric_lock"], command=self.remove_electric_lock)

        self.entries = {}
        self.create_widgets()

    def create_widgets(self):
        # Frame for inputs
        self.input_frame = ttk.Frame(self.root, padding="10")
        self.input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create label and entry for each input
        self.create_label_and_entry("door_type", row=0, values=["simple", "UB", "electric lock"], dropdown=True)
        self.create_label_and_entry("num_doors", row=1)
        self.create_label_and_entry("right_vpiece_width", row=2)
        self.create_label_and_entry("left_vpiece_width", row=3)
        self.create_label_and_entry("upper_hpiece_width", row=4)
        self.create_label_and_entry("lower_hpiece_width", row=5)
        self.create_label_and_entry("edge_sealing_type", row=6, values=["實木", "鋁封邊", "ABS", "鐡封邊+石墨片", "鐡封邊"], dropdown=True)
        self.create_label_and_entry("edge_sealing_thickness", row=7)
        self.create_label_and_entry("max_height", row=8)
        self.create_label_and_entry("min_height", row=9)
        self.create_label_and_entry("electric_lock_name", row=10, values=list(electric_locks.keys()) + ["Other"], dropdown=True)
        self.create_label_and_entry("lock_length", row=11)
        self.create_label_and_entry("lock_height", row=12)
        self.create_label_and_entry("lock_direction", row=13, values=["top", "bottom"], dropdown=True)
        self.create_label_and_entry("lock_offset_bottom", row=14)
        self.create_label_and_entry("frame_height", row=15)
        self.create_label_and_entry("frame_width", row=16)

        # Calculate button
        self.calculate_button = ttk.Button(self.input_frame, text=translations[self.current_language]["calculate"], command=self.calculate_material)
        self.calculate_button.grid(row=17, column=0, columnspan=2)

        # Result display
        self.result_text = tk.Text(self.input_frame, width=80, height=20)
        self.result_text.grid(row=18, column=0, columnspan=2)

        self.update_inputs()

    def create_label_and_entry(self, key, row, values=None, dropdown=False):
        label = ttk.Label(self.input_frame, text=translations[self.current_language][key] + ":")
        label.grid(row=row, column=0, sticky=tk.W)
        if dropdown:
            entry = ttk.Combobox(self.input_frame, values=values)
        else:
            entry = ttk.Entry(self.input_frame)
        entry.grid(row=row, column=1, sticky=tk.E)
        self.entries[key] = entry

    def change_language(self, language):
        self.current_language = language
        self.update_language()

    def update_language(self):
        self.root.title(translations[self.current_language]["result"])
        for key, entry in self.entries.items():
            label = self.input_frame.grid_slaves(row=self.entries[key].grid_info()['row'], column=0)[0]
            label.config(text=translations[self.current_language][key] + ":")

        self.calculate_button.config(text=translations[self.current_language]["calculate"])
        self.edit_menu.entryconfig(0, label=translations[self.current_language]["add_electric_lock"])
        self.edit_menu.entryconfig(1, label=translations[self.current_language]["remove_electric_lock"])
        self.language_menu.entryconfig(0, label="English")
        self.language_menu.entryconfig(1, label="中文")
        self.language_menu.entryconfig(2, label="Bahasa")

    def update_inputs(self, *args):
        door_type = self.entries["door_type"].get().strip().lower()
        if door_type == "electric lock":
            self.show_entries(["left_vpiece_width"], False)
            self.show_entries(["electric_lock_name", "lock_height", "lock_direction"], True)
            self.show_entries(["max_height", "min_height"], False)
        elif door_type == "ub":
            self.show_entries(["left_vpiece_width", "electric_lock_name", "lock_length", "lock_height", "lock_direction", "lock_offset_bottom"], False)
            self.show_entries(["max_height", "min_height"], True)
        else:
            self.show_entries(["left_vpiece_width"], True)
            self.show_entries(["electric_lock_name", "lock_length", "lock_height", "lock_direction", "lock_offset_bottom", "max_height", "min_height"], False)

    def show_entries(self, keys, show):
        for key in keys:
            label = self.input_frame.grid_slaves(row=self.entries[key].grid_info()['row'], column=0)[0]
            entry = self.entries[key]
            if show:
                label.grid()
                entry.grid()
            else:
                label.grid_remove()
                entry.grid_remove()

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
                self.entries["electric_lock_name"]['values'] = list(electric_locks.keys()) + ["Other"]
            else:
                messagebox.showerror("Error", "Electric lock name cannot be empty.")

        lock_window = tk.Toplevel(self.root)
        lock_window.title("Add Electric Lock")

        ttk.Label(lock_window, text="Electric Lock Name:").grid(row=0, column=0, sticky=tk.W)
        new_lock_name_entry = ttk.Entry(lock_window)
        new_lock_name_entry.grid(row=0, column=1, sticky=tk.E)

        ttk.Label(lock_window, text="Lock Length (mm):").grid(row=1, column=0, sticky=tk.W)
        new_lock_length_entry = ttk.Entry(lock_window)
        new_lock_length_entry.grid(row=1, column=1, sticky=tk.E)

        ttk.Label(lock_window, text="Offset Bottom (mm):").grid(row=2, column=0, sticky=tk.W)
        new_lock_offset_bottom_entry = ttk.Entry(lock_window)
        new_lock_offset_bottom_entry.grid(row=2, column=1, sticky=tk.E)

        ttk.Label(lock_window, text="Offset Top (mm):").grid(row=3, column=0, sticky=tk.W)
        new_lock_offset_top_entry = ttk.Entry(lock_window)
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
                self.entries["electric_lock_name"]['values'] = list(electric_locks.keys()) + ["Other"]
            else:
                messagebox.showerror("Error", "Electric lock not found.")

        remove_window = tk.Toplevel(self.root)
        remove_window.title("Remove Electric Lock")

        ttk.Label(remove_window, text="Select Electric Lock to Remove:").grid(row=0, column=0, sticky=tk.W)
        lock_to_remove_var = tk.StringVar()
        lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var)
        lock_to_remove_menu['values'] = list(electric_locks.keys())
        lock_to_remove_menu.grid(row=0, column=1, sticky=tk.E)

        delete_button = ttk.Button(remove_window, text="Delete", command=delete_lock)
        delete_button.grid(row=1, column=0, columnspan=2)

    def calculate_material(self):
        try:
            door_type = self.entries["door_type"].get().strip().lower()
            num_doors = int(self.entries["num_doors"].get())

            right_vertical_piece_width = int(self.entries["right_vpiece_width"].get())

            if door_type != "electric lock":
                left_vertical_piece_width = int(self.entries["left_vpiece_width"].get())
            else:
                left_vertical_piece_width = 70

            upper_horizontal_piece_width = int(self.entries["upper_hpiece_width"].get())
            lower_horizontal_piece_width = int(self.entries["lower_hpiece_width"].get())

            edge_sealing_options = {
                "實木": 6,
                "鋁封邊": 6,
                "ABS": 0.5,
                "鐡封邊+石墨片": 2,  # 1 mm each
                "鐡封邊": 1
            }

            edge_sealing_type = self.entries["edge_sealing_type"].get().strip()
            edge_sealing = edge_sealing_options.get(edge_sealing_type, None)

            if edge_sealing is None:
                edge_sealing = float(self.entries["edge_sealing_thickness"].get())

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

            if door_type == "ub":
                max_height = int(self.entries["max_height"].get())
                min_height = int(self.entries["min_height"].get())
                frame_height = max_height
            elif door_type == "electric lock":
                electric_lock_name = self.entries["electric_lock_name"].get().strip()
                if electric_lock_name in electric_locks:
                    lock_length = electric_locks[electric_lock_name]['length']
                    lock_offset_bottom = electric_locks[electric_lock_name]['offset_bottom']
                    lock_offset_top = electric_locks[electric_lock_name]['offset_top']
                else:
                    lock_length = int(self.entries["lock_length"].get())
                    lock_offset_bottom = int(self.entries["lock_offset_bottom"].get())
                    lock_offset_top = lock_length - lock_offset_bottom
                electric_lock_height = int(self.entries["lock_height"].get())
                lock_direction = self.entries["lock_direction"].get().strip().lower()

                if edge_sealing_type == "鐡封邊+石墨片":
                    electric_lock_height += 3

                frame_height = int(self.entries["frame_height"].get())
                frame_width = int(self.entries["frame_width"].get())
            else:
                frame_height = int(self.entries["frame_height"].get())
                frame_width = int(self.entries["frame_width"].get())

            # Adjust frame height and width based on edge sealing type
            if edge_sealing_type == "ABS":
                frame_height += 10
                frame_width += 10
            elif edge_sealing_type in ["鐡封邊+石墨片", "鐡封邊"]:
                frame_height += 5
                frame_width += 5

            (inner_width, plywood_width, plywood_height, total_length_all_doors, vertical_piece_length,
             horizontal_pieces_length, frame_width, outer_wood_bottom, inner_wood_bottom,
             outer_wood_upper, inner_wood_upper) = self.calculate_material_requirements(
                door_type, num_doors, frame_height, right_vertical_piece_width, left_vertical_piece_width,
                upper_horizontal_piece_width, lower_horizontal_piece_width, edge_sealing, max_height, min_height,
                vertical_piece_width, horizontal_piece_width, frame_width, electric_lock_name, lock_length,
                electric_lock_height, lock_direction, lock_offset_bottom, lock_offset_top)

            report = self.generate_report(door_type, num_doors, inner_width, plywood_width, plywood_height, total_length_all_doors,
                                     vertical_piece_length, horizontal_pieces_length, right_vertical_piece_width,
                                     left_vertical_piece_width, upper_horizontal_piece_width, lower_horizontal_piece_width,
                                     edge_sealing, max_height, min_height, vertical_piece_width, horizontal_piece_width,
                                     electric_lock_name, lock_length, electric_lock_height, lock_direction,
                                     outer_wood_bottom, inner_wood_bottom, outer_wood_upper, inner_wood_upper)

            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, report)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def calculate_material_requirements(self, door_type, num_doors, frame_height, right_vertical_piece_width,
                                        left_vertical_piece_width, upper_horizontal_piece_width, lower_horizontal_piece_width,
                                        edge_sealing, max_height, min_height, vertical_piece_width, horizontal_piece_width,
                                        frame_width, electric_lock_name, lock_length, electric_lock_height, lock_direction,
                                        lock_offset_bottom, lock_offset_top):
        # Calculate inner width
        if door_type == "electric lock":
            inner_width = frame_width - right_vertical_piece_width - (left_vertical_piece_width * 2)
        else:
            inner_width = frame_width - right_vertical_piece_width - left_vertical_piece_width

        # Plywood dimensions
        if door_type == "ub":
            # Adjust for "U" shape, plywood height will be maximum height minus the horizontal piece width (to form the "U" shape)
            plywood_height = max_height - (upper_horizontal_piece_width * 2) - lower_horizontal_piece_width
        else:
            plywood_height = frame_height - upper_horizontal_piece_width - lower_horizontal_piece_width  # considering the same width for top and bottom

        plywood_width = inner_width

        # Total wood length calculations
        vertical_piece_length = frame_height
        horizontal_pieces_length = inner_width  # Adjust for "U" shape

        total_length_per_door = vertical_piece_length * 2 + horizontal_pieces_length * 2

        total_length_all_doors = total_length_per_door * num_doors

        # Electric lock adjustments if door type is electric lock
        outer_wood_bottom = inner_wood_bottom = outer_wood_upper = inner_wood_upper = None
        if door_type == "electric lock":
            if lock_direction == "bottom":
                outer_wood_bottom = electric_lock_height - lock_offset_bottom
            else:
                outer_wood_bottom = frame_height - electric_lock_height - lock_length

            inner_wood_bottom = outer_wood_bottom - 30
            outer_wood_upper = frame_height - (outer_wood_bottom + lock_length)
            inner_wood_upper = outer_wood_upper - 30

            if lock_direction == "top":
                outer_wood_upper = electric_lock_height - lock_offset_top
            else:
                outer_wood_upper = frame_height - electric_lock_height - lock_length

            inner_wood_upper = outer_wood_upper - 75
            outer_wood_bottom = frame_height - (outer_wood_upper + lock_length)
            inner_wood_bottom = outer_wood_bottom - 30

        return (inner_width, plywood_width, plywood_height, total_length_all_doors, vertical_piece_length,
                horizontal_pieces_length, frame_width, outer_wood_bottom, inner_wood_bottom,
                outer_wood_upper, inner_wood_upper)

    def generate_report(self, door_type, num_doors, inner_width, plywood_width, plywood_height, total_length_all_doors,
                        vertical_piece_length, horizontal_pieces_length, right_vertical_piece_width,
                        left_vertical_piece_width, upper_horizontal_piece_width, lower_horizontal_piece_width,
                        edge_sealing, max_height, min_height, vertical_piece_width, horizontal_piece_width,
                        electric_lock_name, lock_length, electric_lock_height, lock_direction, outer_wood_bottom,
                        inner_wood_bottom, outer_wood_upper, inner_wood_upper):

        # Sum the total number of vertical pieces dynamically
        total_right_vertical_pieces = num_doors if right_vertical_piece_width else 0
        total_left_vertical_pieces = num_doors if left_vertical_piece_width else 0

        # For electric lock, add 4 pieces for left vertical pieces
        if door_type == "electric lock":
            total_left_vertical_pieces = num_doors * 4

        # Sum the total number of horizontal pieces dynamically
        total_horizontal_pieces = num_doors * sum(h is not None for h in [upper_horizontal_piece_width, lower_horizontal_piece_width])

        if door_type == "ub":
            total_horizontal_pieces += num_doors  # UB frame includes an extra horizontal piece per door

        if door_type == "electric lock":
            report = f"""
            Door Frame Material Requirements:

            Door Type: {door_type.upper()}
            Number of doors: {num_doors}
            Inner Width: {inner_width} mm
            Plywood Dimensions: {plywood_width} mm x {plywood_height} mm 
            Edge Sealing: {edge_sealing} mm

            Electric Lock: {electric_lock_name}
            Electric Lock Height: {electric_lock_height} mm
            Direction: {lock_direction.capitalize()}

            Total Wood Length Required: {outer_wood_bottom + inner_wood_bottom + outer_wood_upper + inner_wood_upper + vertical_piece_length + (horizontal_pieces_length * 2):.2f} mm
            """
            report += f"""
            Right Vertical Pieces ({right_vertical_piece_width}mm):
              - Length of each piece: {vertical_piece_length} mm
              - Number of pieces per door: {num_doors}
              - Total number of pieces: {total_right_vertical_pieces}

            Left Vertical Pieces ({left_vertical_piece_width}mm):
              - Outer Wood Bottom Part: {outer_wood_bottom} mm
              - Inner Wood Bottom Part: {inner_wood_bottom} mm
              - Outer Wood Upper Part: {outer_wood_upper} mm
              - Inner Wood Upper Part: {inner_wood_upper} mm
              - Number of pieces per door: {num_doors * 4}
              - Total number of pieces: {total_left_vertical_pieces}
            """
        else:
            report = f"""
            Door Frame Material Requirements:

            Door Type: {door_type.upper()}
            Number of doors: {num_doors}
            Inner Width: {inner_width} mm
            Plywood Dimensions: {plywood_width} mm x {plywood_height} mm 
            Minimum Height: {min_height} mm
            Maximum Height: {max_height} mm
            Edge Sealing: {edge_sealing} mm

            Total Wood Length Required: {total_length_all_doors:.2f} mm
            """
            if vertical_piece_width:
                report += f"""
            Vertical Pieces ({vertical_piece_width}mm):
              - Length of each piece: {vertical_piece_length} mm
              - Number of pieces per door: {num_doors * 2}
              - Total number of pieces: {num_doors * 2}
                """
            else:
                report += f"""
            Right Vertical Pieces ({right_vertical_piece_width}mm):
              - Length of each piece: {vertical_piece_length} mm
              - Number of pieces per door: {num_doors}
              - Total number of pieces: {total_right_vertical_pieces}

            Left Vertical Pieces ({left_vertical_piece_width}mm):
              - Length of each piece: {vertical_piece_length} mm
              - Number of pieces per door: {num_doors}
              - Total number of pieces: {total_left_vertical_pieces}
                """
        if horizontal_piece_width:
            report += f"""
            Horizontal Pieces ({horizontal_piece_width}mm):
              - Length of each piece: {inner_width} mm
              - Number of pieces per door: {num_doors * 2}
              - Total number of pieces: {total_horizontal_pieces}
                """
        else:
            report += f"""
            Upper Horizontal Pieces ({upper_horizontal_piece_width}mm):
              - Length of each piece: {inner_width} mm
              - Number of pieces per door: {num_doors}
              - Total number of pieces: {num_doors}

            Lower Horizontal Pieces ({lower_horizontal_piece_width}mm):
              - Length of each piece: {inner_width} mm
              - Number of pieces per door: {num_doors}
              - Total number of pieces: {num_doors}
                """
        if door_type == "ub":
            report += f"""
            For UB Door, the horizontal piece can be adjusted or cut to fit the exact height during the installation process.
            """
        return report


if __name__ == "__main__":
    root = tk.Tk()
    app = DoorFrameCalculator(root)
    root.mainloop()
