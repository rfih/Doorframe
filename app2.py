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

# Initialize electric locks
electric_locks = load_electric_locks()

# # File to store electric lock types
# LOCK_FILE = 'electric_locks.json'

# # Load electric lock types from file
# def load_electric_locks():
#     if os.path.exists(LOCK_FILE):
#         with open(LOCK_FILE, 'r', encoding='utf-8') as file:
#             return json.load(file)
#     return {}

# # Save electric lock types to file
# def save_electric_locks(electric_locks):
#     with open(LOCK_FILE, 'w', encoding='utf-8') as file:
#         json.dump(electric_locks, file, ensure_ascii=False, indent=4)

# Initialize electric lock types
electric_locks = load_electric_locks()

def get_user_input():
    def calculate_material():
        try:
            door_type = door_type_var.get().strip().lower()
            num_doors = int(num_doors_entry.get())

            right_vertical_piece_width = int(right_vertical_piece_width_entry.get())

            if door_type != "electric lock":
                left_vertical_piece_width = int(left_vertical_piece_width_entry.get())
            else:
                left_vertical_piece_width = 70

            upper_horizontal_piece_width = int(upper_horizontal_piece_width_entry.get())
            lower_horizontal_piece_width = int(lower_horizontal_piece_width_entry.get())

            edge_sealing_options = {
                "實木": 6,
                "鋁封邊": 6,
                "ABS": 0.5,
                "鐡封邊+石墨片": 2,  # 1 mm each
                "鐡封邊": 1
            }

            edge_sealing_type = edge_sealing_var.get().strip()
            edge_sealing = edge_sealing_options.get(edge_sealing_type, None)

            if edge_sealing is None:
                edge_sealing = float(edge_sealing_entry.get())

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
                max_height = int(max_height_entry.get())
                min_height = int(min_height_entry.get())
                frame_height = max_height
            elif door_type == "electric lock":
                electric_lock_name = electric_lock_var.get().strip()
                if electric_lock_name in electric_locks:
                    lock_length = electric_locks[electric_lock_name]['length']
                    lock_offset_bottom = electric_locks[electric_lock_name]['offset_bottom']
                    lock_offset_top = electric_locks[electric_lock_name]['offset_top']
                else:
                    lock_length = int(lock_length_entry.get())
                    lock_offset_bottom = int(lock_offset_bottom_entry.get())
                    lock_offset_top = lock_length - lock_offset_bottom
                electric_lock_height = int(electric_lock_height_entry.get())
                lock_direction = lock_direction_var.get().strip().lower()

                if edge_sealing_type == "鐡封邊+石墨片":
                    electric_lock_height += 3

                frame_height = int(frame_height_entry.get())
                frame_width = int(frame_width_entry.get())
            else:
                frame_height = int(frame_height_entry.get())
                frame_width = int(frame_width_entry.get())

            # Adjust frame height and width based on edge sealing type
            if edge_sealing_type == "ABS":
                frame_height += 10
                frame_width += 10
            elif edge_sealing_type in ["鐡封邊+石墨片", "鐡封邊"]:
                frame_height += 5
                frame_width += 5

            (inner_width, plywood_width, plywood_height, total_length_all_doors, vertical_piece_length,
             horizontal_pieces_length, frame_width, outer_wood_bottom, inner_wood_bottom,
             outer_wood_upper, inner_wood_upper) = calculate_material_requirements(
                door_type, num_doors, frame_height, right_vertical_piece_width, left_vertical_piece_width,
                upper_horizontal_piece_width, lower_horizontal_piece_width, edge_sealing, max_height, min_height,
                vertical_piece_width, horizontal_piece_width, frame_width, electric_lock_name, lock_length,
                electric_lock_height, lock_direction, lock_offset_bottom, lock_offset_top)

            report = generate_report(door_type, num_doors, inner_width, plywood_width, plywood_height, total_length_all_doors,
                                     vertical_piece_length, horizontal_pieces_length, right_vertical_piece_width,
                                     left_vertical_piece_width, upper_horizontal_piece_width, lower_horizontal_piece_width,
                                     edge_sealing, max_height, min_height, vertical_piece_width, horizontal_piece_width,
                                     electric_lock_name, lock_length, electric_lock_height, lock_direction,
                                     outer_wood_bottom, inner_wood_bottom, outer_wood_upper, inner_wood_upper)

            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, report)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def calculate_material_requirements(door_type, num_doors, frame_height, right_vertical_piece_width,
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

    def generate_report(door_type, num_doors, inner_width, plywood_width, plywood_height, total_length_all_doors,
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

    def update_inputs(*args):
        door_type = door_type_var.get().strip().lower()
        if door_type == "electric lock":
            left_vertical_piece_width_label.grid_remove()
            left_vertical_piece_width_entry.grid_remove()
            electric_lock_label.grid()
            electric_lock_menu.grid()
            electric_lock_height_label.grid()
            electric_lock_height_entry.grid()
            lock_direction_label.grid()
            lock_direction_menu.grid()
            lock_length_label.grid()
            lock_length_entry.grid()
            lock_offset_bottom_label.grid()
            lock_offset_bottom_entry.grid()
            max_height_label.grid_remove()
            max_height_entry.grid_remove()
            min_height_label.grid_remove()
            min_height_entry.grid_remove()
        elif door_type == "ub":
            left_vertical_piece_width_label.grid()
            left_vertical_piece_width_entry.grid()
            electric_lock_label.grid_remove()
            electric_lock_menu.grid_remove()
            electric_lock_height_label.grid_remove()
            electric_lock_height_entry.grid_remove()
            lock_direction_label.grid_remove()
            lock_direction_menu.grid_remove()
            lock_length_label.grid_remove()
            lock_length_entry.grid_remove()
            lock_offset_bottom_label.grid_remove()
            lock_offset_bottom_entry.grid_remove()
            max_height_label.grid()
            max_height_entry.grid()
            min_height_label.grid()
            min_height_entry.grid()
        else:
            left_vertical_piece_width_label.grid()
            left_vertical_piece_width_entry.grid()
            electric_lock_label.grid_remove()
            electric_lock_menu.grid_remove()
            electric_lock_height_label.grid_remove()
            electric_lock_height_entry.grid_remove()
            lock_direction_label.grid_remove()
            lock_direction_menu.grid_remove()
            lock_length_label.grid_remove()
            lock_length_entry.grid_remove()
            lock_offset_bottom_label.grid_remove()
            lock_offset_bottom_entry.grid_remove()
            max_height_label.grid_remove()
            max_height_entry.grid_remove()
            min_height_label.grid_remove()
            min_height_entry.grid_remove()

    def add_electric_lock():
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
                electric_lock_menu['values'] = list(electric_locks.keys()) + ["Other"]
            else:
                messagebox.showerror("Error", "Electric lock name cannot be empty.")

        lock_window = tk.Toplevel(root)
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

    def remove_electric_lock():
        def delete_lock():
            name = lock_to_remove_var.get().strip()
            if name in electric_locks:
                del electric_locks[name]
                save_electric_locks(electric_locks)
                remove_window.destroy()
                electric_lock_menu['values'] = list(electric_locks.keys()) + ["Other"]
            else:
                messagebox.showerror("Error", "Electric lock not found.")

        remove_window = tk.Toplevel(root)
        remove_window.title("Remove Electric Lock")

        ttk.Label(remove_window, text="Select Electric Lock to Remove:").grid(row=0, column=0, sticky=tk.W)
        lock_to_remove_var = tk.StringVar()
        lock_to_remove_menu = ttk.Combobox(remove_window, textvariable=lock_to_remove_var)
        lock_to_remove_menu['values'] = list(electric_locks.keys())
        lock_to_remove_menu.grid(row=0, column=1, sticky=tk.E)

        delete_button = ttk.Button(remove_window, text="Delete", command=delete_lock)
        delete_button.grid(row=1, column=0, columnspan=2)

    # Tkinter GUI setup
    root = tk.Tk()
    root.title("Door Frame Material Calculator")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Menu bar
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    edit_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Add Electric Lock Type", command=add_electric_lock)
    edit_menu.add_command(label="Remove Electric Lock Type", command=remove_electric_lock)

    # Door type dropdown
    ttk.Label(frame, text="Door Type:").grid(row=0, column=0, sticky=tk.W)
    door_type_var = tk.StringVar()
    door_type_var.trace("w", update_inputs)
    door_type_menu = ttk.Combobox(frame, textvariable=door_type_var)
    door_type_menu['values'] = ("simple", "UB", "electric lock")
    door_type_menu.grid(row=0, column=1, sticky=tk.E)

    # Number of doors
    ttk.Label(frame, text="Number of doors:").grid(row=1, column=0, sticky=tk.W)
    num_doors_entry = ttk.Entry(frame)
    num_doors_entry.grid(row=1, column=1, sticky=tk.E)

    # Right vertical piece width
    ttk.Label(frame, text="Right Vertical Piece Width:").grid(row=2, column=0, sticky=tk.W)
    right_vertical_piece_width_entry = ttk.Entry(frame)
    right_vertical_piece_width_entry.grid(row=2, column=1, sticky=tk.E)

    # Left vertical piece width
    left_vertical_piece_width_label = ttk.Label(frame, text="Left Vertical Piece Width:")
    left_vertical_piece_width_label.grid(row=3, column=0, sticky=tk.W)
    left_vertical_piece_width_entry = ttk.Entry(frame)
    left_vertical_piece_width_entry.grid(row=3, column=1, sticky=tk.E)

    # Upper horizontal piece width
    ttk.Label(frame, text="Upper Horizontal Piece Width:").grid(row=4, column=0, sticky=tk.W)
    upper_horizontal_piece_width_entry = ttk.Entry(frame)
    upper_horizontal_piece_width_entry.grid(row=4, column=1, sticky=tk.E)

    # Lower horizontal piece width
    ttk.Label(frame, text="Lower Horizontal Piece Width:").grid(row=5, column=0, sticky=tk.W)
    lower_horizontal_piece_width_entry = ttk.Entry(frame)
    lower_horizontal_piece_width_entry.grid(row=5, column=1, sticky=tk.E)

    # Edge sealing dropdown
    ttk.Label(frame, text="Edge Sealing Type:").grid(row=6, column=0, sticky=tk.W)
    edge_sealing_var = tk.StringVar()
    edge_sealing_menu = ttk.Combobox(frame, textvariable=edge_sealing_var)
    edge_sealing_menu['values'] = ("實木", "鋁封邊", "ABS", "鐡封邊+石墨片", "鐡封邊")
    edge_sealing_menu.grid(row=6, column=1, sticky=tk.E)

    # Edge sealing thickness (manual input)
    ttk.Label(frame, text="Edge Sealing Thickness (mm):").grid(row=7, column=0, sticky=tk.W)
    edge_sealing_entry = ttk.Entry(frame)
    edge_sealing_entry.grid(row=7, column=1, sticky=tk.E)

    # UB specific inputs
    max_height_label = ttk.Label(frame, text="Max Height (UB only):")
    max_height_label.grid(row=8, column=0, sticky=tk.W)
    max_height_entry = ttk.Entry(frame)
    max_height_entry.grid(row=8, column=1, sticky=tk.E)

    min_height_label = ttk.Label(frame, text="Min Height (UB only):")
    min_height_label.grid(row=9, column=0, sticky=tk.W)
    min_height_entry = ttk.Entry(frame)
    min_height_entry.grid(row=9, column=1, sticky=tk.E)

    # Electric lock specific inputs
    electric_lock_label = ttk.Label(frame, text="Electric Lock Type:")
    electric_lock_label.grid(row=10, column=0, sticky=tk.W)
    electric_lock_var = tk.StringVar()
    electric_lock_menu = ttk.Combobox(frame, textvariable=electric_lock_var)
    electric_lock_menu['values'] = list(electric_locks.keys()) + ["Other"]
    electric_lock_menu.grid(row=10, column=1, sticky=tk.E)

    lock_length_label = ttk.Label(frame, text="Lock Length (mm) (use if no selection):")
    lock_length_label.grid(row=11, column=0, sticky=tk.W)
    lock_length_entry = ttk.Entry(frame)
    lock_length_entry.grid(row=11, column=1, sticky=tk.E)

    electric_lock_height_label = ttk.Label(frame, text="Electric Lock Height (mm):")
    electric_lock_height_label.grid(row=12, column=0, sticky=tk.W)
    electric_lock_height_entry = ttk.Entry(frame)
    electric_lock_height_entry.grid(row=12, column=1, sticky=tk.E)

    lock_direction_label = ttk.Label(frame, text="Lock Direction (top/bottom):")
    lock_direction_label.grid(row=13, column=0, sticky=tk.W)
    lock_direction_var = tk.StringVar()
    lock_direction_menu = ttk.Combobox(frame, textvariable=lock_direction_var)
    lock_direction_menu['values'] = ("top", "bottom")
    lock_direction_menu.grid(row=13, column=1, sticky=tk.E)

    lock_offset_bottom_label = ttk.Label(frame, text="Lock Offset Bottom (mm) (use if no selection):")
    lock_offset_bottom_label.grid(row=14, column=0, sticky=tk.W)
    lock_offset_bottom_entry = ttk.Entry(frame)
    lock_offset_bottom_entry.grid(row=14, column=1, sticky=tk.E)

    # Frame height and width
    ttk.Label(frame, text="Frame Height (mm):").grid(row=15, column=0, sticky=tk.W)
    frame_height_entry = ttk.Entry(frame)
    frame_height_entry.grid(row=15, column=1, sticky=tk.E)

    ttk.Label(frame, text="Frame Width (mm):").grid(row=16, column=0, sticky=tk.W)
    frame_width_entry = ttk.Entry(frame)
    frame_width_entry.grid(row=16, column=1, sticky=tk.E)

    # Calculate button
    calculate_button = ttk.Button(frame, text="Calculate", command=calculate_material)
    calculate_button.grid(row=17, column=0, columnspan=2)

    # Result display
    result_text = tk.Text(frame, width=80, height=20)
    result_text.grid(row=18, column=0, columnspan=2)

    update_inputs()
    root.mainloop()

if __name__ == "__main__":
    get_user_input()
