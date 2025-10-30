import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from database import get_db
from typing import Optional

# Import PDF generation library
try:
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
TIMESLOTS = [f"{h:02d}:00" for h in range(8, 22)]

class TimetableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timetable Manager")
        self.db = get_db()

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.style.configure("TLabel", font=("Helvetica", 11))
        self.style.configure("TButton", font=("Helvetica", 10))
        self.style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"))
        self.style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))

        self._build_ui()
        self.refresh_all_tabs()

    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        
        # ... (Tabs for Colleges, Teachers, Courses & Units will be built here) ...
        # For brevity, focusing on the Timetable tab where the change is.
        # Assume other build methods like _build_teachers_tab are defined elsewhere.
        
        self.tab_timetable = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_timetable, text="Timetable")
        self._build_timetable_tab(self.tab_timetable)
        
        self.tab_workload = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_workload, text="Workload")
        self._build_workload_tab(self.tab_workload)


    def _build_timetable_tab(self, parent):
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill="both", expand=True)

        top_bar = ttk.Frame(frame)
        top_bar.pack(fill="x", pady=(0, 10))
        
        ttk.Label(top_bar, text="Select College:", style="Header.TLabel").pack(side="left")
        self.college_var = tk.StringVar()
        self.college_combo = ttk.Combobox(top_bar, textvariable=self.college_var, state="readonly", width=20)
        self.college_combo.pack(side="left", padx=10)
        self.college_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_timetable())

        # Add Print to PDF button
        if REPORTLAB_AVAILABLE:
            pdf_button = ttk.Button(top_bar, text="Print to PDF", command=self.print_to_pdf)
            pdf_button.pack(side="right", padx=5)
        else:
            ttk.Label(top_bar, text="Install 'reportlab' for PDF export.", foreground="red").pack(side="right")

        # Canvas for scrollable grid
        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.grid_frame = ttk.Frame(canvas)

        self.grid_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Build grid
        self._build_timetable_grid(self.grid_frame)
    
    def _build_timetable_grid(self, parent):
        # Header row
        ttk.Label(parent, text="", relief="ridge").grid(row=0, column=0, sticky="nsew")
        for c, day in enumerate(DAYS, 1):
            ttk.Label(parent, text=day, relief="ridge", padding=5, anchor="center", style="Header.TLabel").grid(row=0, column=c, sticky="ew")

        self.cell_widgets = {}
        for r, timeslot in enumerate(TIMESLOTS, 1):
            ttk.Label(parent, text=timeslot, relief="ridge", padding=5).grid(row=r, column=0, sticky="ns")
            for c, day in enumerate(DAYS, 1):
                cell = ttk.Frame(parent, relief="solid", borderwidth=1)
                cell.grid(row=r, column=c, sticky="nsew")
                label = ttk.Label(cell, text="", anchor="center", padding=5, wraplength=150, justify="center")
                label.pack(expand=True, fill="both")

                for widget in [cell, label]:
                    widget.bind("<Button-3>", lambda e, d=day, t=timeslot: self.on_cell_right_click(e, d, t))
                    widget.bind("<Button-2>", lambda e, d=day, t=timeslot: self.on_cell_right_click(e, d, t))
                    widget.bind("<Control-Button-1>", lambda e, d=day, t=timeslot: self.on_cell_right_click(e, d, t))

                self.cell_widgets[(day, timeslot)] = label
        
        for i in range(len(DAYS) + 1):
            parent.columnconfigure(i, weight=1, uniform="grid")

    def print_to_pdf(self):
        college_name = self.college_var.get()
        if not college_name:
            messagebox.showwarning("PDF Export", "Please select a college first.")
            return

        college_id = self.college_map.get(college_name)
        schedule_data = self.db.get_schedule_for_college(college_id)

        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            title="Save Timetable as PDF",
            initialfile=f"{college_name}_Timetable.pdf"
        )
        if not file_path:
            return # User cancelled

        try:
            doc = SimpleDocTemplate(file_path, pagesize=landscape(letter))
            elements = []
            
            # Prepare data for the table
            data = [["Time"] + DAYS] # Header row
            schedule_map = {(item['day'], item['timeslot']): f"{item['unit_name'] or ''}\n{item['teacher_name'] or ''}\n{item['room'] or ''}".strip() for item in schedule_data}

            for timeslot in TIMESLOTS:
                row = [timeslot]
                for day in DAYS:
                    cell_content = schedule_map.get((day, timeslot), "")
                    row.append(cell_content)
                data.append(row)

            # Create and style the table
            table = Table(data, colWidths=[60] + [140]*len(DAYS))
            style = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR',(0,0),(-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (0,-1), colors.lightgrey),
                ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ])
            table.setStyle(style)
            
            elements.append(table)
            doc.build(elements)
            messagebox.showinfo("Success", f"PDF saved successfully to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {e}")

    # Dummy methods for other tabs to make the snippet runnable
    def _build_workload_tab(self, parent):
        ttk.Label(parent, text="Workload tracking will appear here.").pack(pady=20)
    def on_cell_right_click(self, e, d, t):
        print(f"Right-clicked {d} at {t}")
    def refresh_timetable(self):
        print("Refreshing timetable...")
    def refresh_all_tabs(self):
        # Mock college data for demonstration
        self.college_map = {"Moss Vale": 1, "Goulburn": 2, "Queanbeyan": 3}
        self.college_combo["values"] = list(self.college_map.keys())
        if self.college_combo["values"]:
            self.college_combo.current(0)
    def on_tab_change(self, event):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableApp(root)
    root.geometry("1400x900")
    root.mainloop()
