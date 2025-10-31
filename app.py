
import tkinter as tk
from tkinter import ttk

from database import get_db

# --- Constants ---
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
TIME_SLOTS = [f"{h:02d}:{m:02d}" for h in range(8, 22) for m in (0, 30)]
CELL_HEIGHT = 25  # Height for a 30-min slot
HEADER_BG = "#2c3e50"
HEADER_FG = "white"
GRID_BG = "#ecf0f1"
GRID_LINE_COLOR = "#bdc3c7"

class TimetableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TAFE Timetabling Application")
        self.root.geometry("1600x1000")
        self.db = get_db()

        # --- Styling ---
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TNotebook.Tab", font=("Helvetica", 11, "bold"))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 11, "bold"), background=HEADER_BG, foreground=HEADER_FG)

        self._build_main_layout()
        self._build_management_panel()
        self._build_unscheduled_units_panel()
        self._build_timetable_panel()

        self.refresh_all()

    def _build_main_layout(self):
        # Main layout with a resizable pane
        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        # Left panel for management and unscheduled units
        self.left_panel = ttk.Notebook(self.main_pane)
        self.main_pane.add(self.left_panel, weight=1)

        # Right panel for the timetable grid
        self.right_panel = ttk.Frame(self.main_pane)
        self.main_pane.add(self.right_panel, weight=4)

    def _build_management_panel(self):
        # This notebook will contain tabs for Teachers, Courses, Rooms
        self.mgmt_notebook = ttk.Notebook(self.left_panel)
        self.left_panel.add(self.mgmt_notebook, text="Management")

        # Create the individual tabs
        self.teachers_tab = ttk.Frame(self.mgmt_notebook)
        self.courses_tab = ttk.Frame(self.mgmt_notebook)
        self.rooms_tab = ttk.Frame(self.mgmt_notebook)

        self.mgmt_notebook.add(self.teachers_tab, text="Teachers")
        self.mgmt_notebook.add(self.courses_tab, text="Courses & Units")
        self.mgmt_notebook.add(self.rooms_tab, text="Rooms")
        
        # Populate the tabs (basic placeholder for now)
        ttk.Label(self.teachers_tab, text="Teacher Management UI goes here.").pack(pady=20)
        ttk.Label(self.courses_tab, text="Course & Unit Management UI goes here.").pack(pady=20)
        ttk.Label(self.rooms_tab, text="Room Management UI goes here.").pack(pady=20)

    def _build_unscheduled_units_panel(self):
        unscheduled_frame = ttk.Frame(self.left_panel)
        self.left_panel.add(unscheduled_frame, text="Unscheduled Units")

        ttk.Label(unscheduled_frame, text="Units to be Scheduled", font=("Helvetica", 12, "bold")).pack(pady=5)
        
        cols = ("course", "unit", "required", "scheduled")
        self.units_bank_tree = ttk.Treeview(unscheduled_frame, columns=cols, show="headings")
        
        self.units_bank_tree.heading("course", text="Course")
        self.units_bank_tree.heading("unit", text="Unit")
        self.units_bank_tree.heading("required", text="Required (h)")
        self.units_bank_tree.heading("scheduled", text="Scheduled (h)")

        self.units_bank_tree.column("required", width=80, anchor=tk.CENTER)
        self.units_bank_tree.column("scheduled", width=80, anchor=tk.CENTER)

        self.units_bank_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _build_timetable_panel(self):
        # --- Top Filter Bar ---
        filter_bar = ttk.Frame(self.right_panel)
        filter_bar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_bar, text="View by Campus:").pack(side=tk.LEFT, padx=(0, 5))
        self.campus_filter = ttk.Combobox(filter_bar, state="readonly", width=15)
        self.campus_filter.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_bar, text="Teacher:").pack(side=tk.LEFT, padx=(15, 5))
        self.teacher_filter = ttk.Combobox(filter_bar, state="readonly", width=20)
        self.teacher_filter.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_bar, text="Course:").pack(side=tk.LEFT, padx=(15, 5))
        self.course_filter = ttk.Combobox(filter_bar, state="readonly", width=25)
        self.course_filter.pack(side=tk.LEFT, padx=5)
        
        # --- Timetable Grid Canvas ---
        self.grid_canvas = tk.Canvas(self.right_panel, bg=GRID_BG, highlightthickness=0)
        
        v_scroll = ttk.Scrollbar(self.right_panel, orient=tk.VERTICAL, command=self.grid_canvas.yview)
        self.grid_canvas.configure(yscrollcommand=v_scroll.set)

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.grid_canvas.pack(fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))

        self.grid_canvas.bind("<Configure>", self._draw_grid)
        
    def _draw_grid(self, event=None):
        self.grid_canvas.delete("all")
        width = self.grid_canvas.winfo_width()
        height = len(TIME_SLOTS) * CELL_HEIGHT

        self.grid_canvas.config(scrollregion=(0, 0, width, height + 50))

        # --- Draw Header ---
        header_height = 30
        self.grid_canvas.create_rectangle(0, 0, width, header_height, fill=HEADER_BG, outline=GRID_LINE_COLOR)
        
        time_col_width = 80
        day_col_width = (width - time_col_width) / len(DAYS)

        # Header Text
        self.grid_canvas.create_text(time_col_width / 2, header_height / 2, text="Time", fill=HEADER_FG, font=("Helvetica", 11, "bold"))
        for i, day in enumerate(DAYS):
            x = time_col_width + (i * day_col_width) + (day_col_width / 2)
            self.grid_canvas.create_text(x, header_height / 2, text=day, fill=HEADER_FG, font=("Helvetica", 11, "bold"))
            
        # --- Draw Grid Lines & Time Slots ---
        for i, time in enumerate(TIME_SLOTS):
            y = header_height + (i * CELL_HEIGHT)
            
            # Horizontal line
            self.grid_canvas.create_line(0, y, width, y, fill=GRID_LINE_COLOR)

            # Time slot text (only for full hours)
            if time.endswith(":00"):
                self.grid_canvas.create_text(time_col_width / 2, y + (CELL_HEIGHT / 2), text=time, anchor=tk.CENTER, font=("Helvetica", 9))

        # Vertical lines
        self.grid_canvas.create_line(time_col_width, 0, time_col_width, height + header_height, fill=GRID_LINE_COLOR)
        for i in range(len(DAYS)):
            x = time_col_width + (i * day_col_width)
            self.grid_canvas.create_line(x, header_height, x, height + header_height, fill=GRID_LINE_COLOR)
            
    def refresh_unscheduled_units(self):
        for item in self.units_bank_tree.get_children():
            self.units_bank_tree.delete(item)
        
        units = self.db.get_unscheduled_units_summary()
        for unit in units:
            self.units_bank_tree.insert("", "end", values=(
                unit["course_name"],
                unit["name"],
                f'{unit["required_hours"]:.1f}',
                f'{unit["scheduled_hours"]:.1f}'
            ))
            
    def refresh_filters(self):
        colleges = [c['name'] for c in self.db.get_colleges()]
        self.campus_filter['values'] = ["All"] + colleges
        self.campus_filter.set("All")
        
        teachers = [t['name'] for t in self.db.get_teachers()]
        self.teacher_filter['values'] = ["All"] + teachers
        self.teacher_filter.set("All")

        courses = [c['name'] for c in self.db.get_courses()]
        self.course_filter['values'] = ["All"] + courses
        self.course_filter.set("All")

    def refresh_all(self):
        self.refresh_unscheduled_units()
        self.refresh_filters()
        # In future phases, this will also refresh the timetable display itself

    def on_close(self):
        self.db.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

