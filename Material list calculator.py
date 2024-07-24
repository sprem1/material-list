from operator import lt
import os
import math
import time
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, StringVar, IntVar, Checkbutton, Scrollbar, Frame, LEFT, RIGHT, Y, BOTH, Canvas, VERTICAL
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas

material_dict = {
    "Shingle (CertainTeed or GAF)": {"conversion": 3, "shingle_multiplier": 3},
    "CT Swiftstart (Starter)": {"conversion": 116},
    "CT Ridge Vent (per linear foot)": {"conversion": 4},
    "Drip Edge F5": {"conversion": 10},
    "Drip edge F8": {"conversion": 10},
    "Shadow Hip/Ridge (Cap)": {"conversion": 28},
    "Roof Runner (underlayment)": {"conversion": 10},
    "Diamond Deck (underlayment)": {"conversion": 10},
    "Ice and Water/MFG 2 sq": {"conversion": 62},
    "Geocel/Vulkem (caulk)": {"conversion": 15},
    "Paint": {"1 per job"},
    "Apron": {"conversion": 10},
    "Pipe Collar": {},
    "Step Flashing": {"conversion": 25},
    "Snorkel Vent": {},
    "750 Vent": {},
    "Attic Vent": {},
    "Coil Nail (per SQ)": {"conversion": 15},
    "3⁄4 Coil Nail (per SQ)": {"1 per shed"},
    "3” Nail (per ridge)": {"conversion": 30},
    "Staple (per SQ)": {"conversion": 10},
    "Intake Vent Certain Teed": {"conversion": 4},
    "Intake Vent Generic": {"conversion": 3},
    "Skylight Velux - Deck Mount": {},
    "Skylight Velux - Curb Mount": {},
    "Skylight Velux - Custom": {},
}

class MaterialEntry:
    def __init__(self, master, material, row):
        self.master = master
        self.material = material
        self.row = row
        self.quantity_var = StringVar()
        self.waste_10_var = IntVar()
        self.waste_15_var = IntVar()
        self.waste_20_var = IntVar()

        self.frame = Frame(master)
        self.frame.grid(row=row, column=0, columnspan=2, pady=2)

        self.label = Label(self.frame, text=material)
        self.label.pack(side=LEFT, padx=5)

        self.quantity_entry = Entry(self.frame, textvariable=self.quantity_var)
        self.quantity_entry.pack(side=LEFT, padx=5)

        self.waste_10_checkbox = Checkbutton(self.frame, text="10%", variable=self.waste_10_var)
        self.waste_10_checkbox.pack(side=LEFT, padx=5)

        self.waste_15_checkbox = Checkbutton(self.frame, text="15%", variable=self.waste_15_var)
        self.waste_15_checkbox.pack(side=LEFT, padx=5)

        self.waste_20_checkbox = Checkbutton(self.frame, text="20%", variable=self.waste_20_var)
        self.waste_20_checkbox.pack(side=LEFT, padx=5)

    def get_quantity(self):
        try:
            quantity = float(self.quantity_var.get())
            return quantity
        except ValueError:
            return 0

    def get_waste_factor(self):
        waste_factor = 0
        if self.waste_10_var.get() == 1:
            waste_factor = 0.10
        elif self.waste_15_var.get() == 1:
            waste_factor = 0.15
        elif self.waste_20_var.get() == 1:
            waste_factor = 0.20
        return waste_factor
 
def calculate_cost(material, quantity, waste_factor, material_info):  
   """Calculates the total cost for a material based on quantity and waste factor."""  
   if material == "Shingle (CertainTeed or GAF)":  
      quantity *= material_info["shingle_multiplier"]  # Multiply by 3  
      quantity *= (1 + waste_factor)  # Apply waste factor  
      # Custom rounding logic: round down if decimal part is less than 0.5, round up if 0.5 or greater  
      if quantity - math.floor(quantity) < 0.5:  
        return math.floor(quantity)  
      else:  
        return math.ceil(quantity)  
   elif "conversion" in material_info:  
      return (quantity / material_info["conversion"]) * (1 + waste_factor)  
   else:  
      return quantity * (1 + waste_factor)  

def create_pdf(material_costs, client_info, logo_path, filename="estimate.pdf"):
    try:
        c = pdf_canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        # Add logo image
        if os.path.exists(logo_path):
            logo_width = 300  # Adjust width as needed
            logo_height = 150  # Adjust height as needed
            c.drawImage(logo_path, 30, height - 150, width=logo_width, height=logo_height)
        else:
            print(f"Warning: Logo file '{logo_path}' not found.")

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, height - 180, "Material List")

        # Client information
        c.setFont("Helvetica", 12)
        y = height - 210
        for key, value in client_info.items():
            c.drawString(30, y, f"{key}: {value.get()}")
            y -= 20

        # Material costs
        c.drawString(30, y, "Material Quantities:")
        y -= 20
        for material, cost in material_costs.items():
            rounded_cost = math.ceil(cost)  # Round the cost up to the nearest whole number
            c.drawString(30, y, f"{material}: {rounded_cost}")
            y -= 20
        c.save()
    except Exception as e:
        print(f"Error creating PDF: {e}")

def upload_png_image():
    file_path = filedialog.askopenfilename(title="Select PNG image", filetypes=[("PNG files", "*.png")])
    return file_path

def main():
    global root, material_entries, client_info
    root = Tk()
    root.title("Material list")

    client_info = {
        "Name": StringVar(),
        "Phone": StringVar(),
        "Address": StringVar(),
        "Delivery Date": StringVar(),
        "Time": StringVar(),
        "Shingle MFG/Line": StringVar()
    }

    main_frame = Frame(root)
    main_frame.pack(fill=BOTH, expand=True)

    canvas = Canvas(main_frame, bg="grey")
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

    frame = Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor='nw')

    row = 0
    for key in client_info.keys():
        label = Label(frame, text=key)
        label.grid(row=row, column=0, padx=5, pady=2)
        entry = Entry(frame, textvariable=client_info[key])
        entry.grid(row=row, column=1, padx=5, pady=2)
        row += 1

    material_entries = []
    for i, material in enumerate(material_dict.keys()):
        material_entry = MaterialEntry(frame, material, i + row)
        material_entries.append(material_entry)

    def calculate_and_create_pdf():
        material_costs = {}
        for material_entry in material_entries:
            material = material_entry.material
            quantity = material_entry.get_quantity()
            waste_factor = material_entry.get_waste_factor()
            material_info = material_dict[material]

            cost = calculate_cost(material, quantity, waste_factor, material_info)
            material_costs[material] = cost

        logo_path = upload_png_image()
        
        # Generate a unique filename based on the current timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"estimate_{timestamp}.pdf"
        
        create_pdf(material_costs, client_info, logo_path, filename=filename)
        messagebox.showinfo("PDF Created", f"PDF estimate created successfully! Filename: {filename}")

    calculate_and_create_pdf_button = Button(root, text="Create PDF", command=calculate_and_create_pdf)
    calculate_and_create_pdf_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
