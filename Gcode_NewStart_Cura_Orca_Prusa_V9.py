import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from tkinter import ttk


# Function to get user input for nozzle temperature, bed temperature, fan speed, bed mesh, and pre-purge amount.
def get_user_input():
    global slicertype

    root = tk.Tk()
    root.withdraw()

    original_gcode = filedialog.askopenfilename(title="Select the original G-code file")
    slicertype=detect_slicer_type(original_gcode)
    nozzle_temp = float(simpledialog.askstring("Input", "Enter desired nozzle temperature (C): "))
    bed_temp = float(simpledialog.askstring("Input", "Enter desired bed temperature (C): "))
    fan_speed = int(simpledialog.askstring("Input", "Enter desired part cooling fan speed (%): "))
    load_bed_mesh = simpledialog.askstring("Input", "Load bed mesh from memory? (Y/N): ").strip().upper() == "Y"
    pre_purge_amount = float(simpledialog.askstring("Input", "Enter the pre-purge amount (mm): "))

    # Get a list of layer numbers and Z heights from the G-code file.
    layer_info = get_layer_info(original_gcode)
    selected_layers = []

    if layer_info:
        info_message = f"Slicer: {slicertype}\nLayer Count: {len(layer_info)}"
        messagebox.showinfo("Layer Information", info_message)
    else:
        messagebox.showerror("Error", "Could not retrieve layer information from the G-code file.")

    def ok_button_clicked():
        for layer_num, var in checkboxes:
            if var.get() == 1:
              selected_layers.append(layer_num)
        root.destroy()

    popup = tk.Toplevel()
    popup.title("Select the Layer to Restart From")

    ttk.Label(popup, text="Select the layer to restart from:").pack()

    canvas = tk.Canvas(popup, borderwidth=0)
    scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    checkboxes = []
    for i, (layer_num, z_height) in enumerate(layer_info, start=1):
        var = tk.IntVar(value=0)  # Initialize with 0 (unchecked)
        checkbox = ttk.Checkbutton(scrollable_frame, text=f"Layer {layer_num} (Z = {z_height:.2f} mm)", variable=var)
        checkbox.pack(anchor="w")
        checkboxes.append((layer_num, var))

    ok_button = ttk.Button(popup, text="OK", command=ok_button_clicked)
    ok_button.pack()

    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

    root.mainloop()

    if len(selected_layers) != 1:
        messagebox.showerror("Error", "Please select exactly one layer to restart from.")
        return None

    # Retrieve the selected layer from the checkboxes.
    selected_layer_num = selected_layers[0]

    return original_gcode, nozzle_temp, bed_temp, fan_speed, load_bed_mesh, pre_purge_amount, selected_layer_num, layer_info

def detect_slicer_type(gcode_file):
    with open(gcode_file, 'r') as f:
            for i, line in enumerate(f):
                if i > 50:  # Only check the first 50 lines to avoid reading the entire file
                    break
                lower_line = line.lower()  # Convert line to lowercase for case-insensitive comparison
                if "cura" in lower_line:
                    return "Cura"
                elif "orcaslicer" in lower_line:
                    return "Orca"
                elif "prusaslicer" in lower_line:
                    return "Prusa"
    return "Unknown"
# Function to parse the G-code file and retrieve layer information.
def get_layer_info(gcode_file):
    layer_info = []
    if slicertype == "Cura":
        with open(gcode_file, 'r') as f:
            z_height = None
            for line in f:
                if line.startswith(";LAYER:"):
                    if z_height is not None:
                        layer_info.append((int(line.split(":")[1]), z_height))
                elif line.startswith("G0"):
                    parts = line.split("Z")
                    if len(parts) > 1:
                        try:
                            next_z_height = float(parts[1].split()[0])
                            z_height = next_z_height
                        except (ValueError, IndexError):
                            messagebox.showerror("Error", "CURA - Error in making list of z height penis tag")                      
    elif slicertype =="Orca":
        with open(gcode_file, 'r') as f:
            current_layer_number = 0
            for line in f:
                if ";LAYER_CHANGE" in line:
                    current_layer_number += 1
                elif ";Z:" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            try:
                                z_height = float(parts[1].split()[0])
                                layer_info.append((current_layer_number, z_height))
                            except ValueError:
                                messagebox.showerror("Error", "Orca - Error in making list of z height in")
    elif slicertype =="Prusa":
        with open(gcode_file, 'r') as f:
            current_layer_number = 0
            for line in f:
                if ";LAYER_CHANGE" in line:
                    current_layer_number += 1
                elif ";Z:" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            try:
                                z_height = float(parts[1].split()[0])
                                layer_info.append((current_layer_number, z_height))
                            except ValueError:
                                messagebox.showerror("Error", "Prusa - Error in making list of z height in")
    else:
        messagebox.showerror("Error", "Cant get Z layers")
    return layer_info

# Function to edit the G-code file.
def edit_gcode(original_gcode, nozzle_temp, bed_temp, fan_speed, load_bed_mesh, pre_purge_amount, selected_layer, layer_info):
    with open(original_gcode, 'r') as f:
        gcode_lines = f.readlines()

    new_gcode = []

    # Get the correct Z height for the selected layer
    selected_layer_z = 0.0
    for layer_num, z_height in layer_info:
        if layer_num == selected_layer:
            selected_layer_z = z_height
            break

    new_gcode.append(f"G92 E0 ; Reset Extruder\n")
    new_gcode.append(f"M83 ; Set extruder to Relative\n")

    # Add G0 Z command with the correct Z height to the new G-code
    new_gcode.append(f"M104 S{nozzle_temp} ; Start preheating hotend\n")
    new_gcode.append(f"M140 S{bed_temp} ; Start preheating bed\n")
    if load_bed_mesh:
        new_gcode.append("M420 S1 ; Load bed mesh from memory\n")
    new_gcode.append(f"G0 Z{selected_layer_z + 5:.2f} ; Go 5mm above selected layer number\n")

    new_gcode.append(f"M190 S{bed_temp} ; Set bed temperature\n")
    new_gcode.append(f"M109 S{nozzle_temp} ; Set nozzle temperature\n")

    # Scale the user-provided fan_speed (0-100%) to M106 value (0-255)
    fan_speed_scaled = int(2.55 * fan_speed)
    new_gcode.append(f"M106 S{fan_speed_scaled} ; Set fan speed\n")

    new_gcode.append(f"G0 Z{selected_layer_z:.2f} ; Drop down to selected layer number\n")
    # Insert G1 F3600 EXX command with the user-provided pre-purge amount
    new_gcode.append(f"G1 F3600 E{pre_purge_amount:.2f} ; Pre-purge extruder\n")
    if slicertype=="Cura":
        new_gcode.append(f"M82 ; Set Extruder to Absolute\n")
    elif slicertype=="Orca":
        new_gcode.append(f"M83 ; Set extruder to Relative\n")
    elif slicertype=="Prusa":
        new_gcode.append(f"M83 ; Set extruder to Relative\n")

    # Flag to include lines starting from the selected_layer
    include_lines = False
    lineindex=0
    for line in gcode_lines:
        lineindex += 1
        if slicertype=="Cura":
            if line.startswith(f";LAYER:{selected_layer}"):
                include_lines = True
        elif slicertype=="Orca":
            if line.startswith(f";Z:{selected_layer_z}"):
                fakestring=gcode_lines[lineindex -2]
                if fakestring.startswith(f";LAYER_CHANGE"):
                    include_lines = True
        elif slicertype=="Prusa":
            if line.startswith(f";Z:{selected_layer_z}"):
                fakestring=gcode_lines[lineindex -2]
                if fakestring.startswith(f";LAYER_CHANGE"):
                    include_lines = True
        else:
            messagebox.showerror("I am Broke!")
        
        if include_lines:
            new_gcode.append(line)
        


    new_gcode_file = original_gcode.replace(".gcode", f"-NEWSTART-LAYER{selected_layer}.gcode")

    with open(new_gcode_file, 'w') as f:
        f.writelines(new_gcode)

    print(f"Modified G-code saved as {new_gcode_file}")



if __name__ == "__main__":
    user_input = get_user_input()

    if user_input is not None:
        original_gcode, nozzle_temp, bed_temp, fan_speed, load_bed_mesh, pre_purge_amount, selected_layer, layer_info = user_input
        edit_gcode(original_gcode, nozzle_temp, bed_temp, fan_speed, load_bed_mesh, pre_purge_amount, selected_layer, layer_info)
