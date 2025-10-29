import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import get_db
from typing import Optional

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
TIMESLOTS = ["Morning", "Afternoon", "Night"]


class TimetableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timetable Manager")
        self.db = get_db()
        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Teachers tab
        self.tab_teachers = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_teachers, text="Teachers")
        self._build_teachers_tab(self.tab_teachers)

        # Courses tab
        self.tab_courses = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_courses, text="Courses")
        self._build_courses_tab(self.tab_courses)

        # Units tab
        self.tab_units = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_units, text="Units")
        self._build_units_tab(self.tab_units)

        # Timetable tab
        self.tab_timetable = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_timetable, text="Timetable")
        self._build_timetable_tab(self.tab_timetable)

    # ---------------- Teachers Tab ----------------
    def _build_teachers_tab(self, parent):
        frame = ttk.Frame(parent, padding=8)
        frame.pack(fill="both", expand=True)

        top = ttk.Frame(frame)
        top.pack(fill="x")
        ttk.Label(top, text="Teacher Name:").pack(side="left")
        self.teacher_name_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.teacher_name_var).pack(side="left", padx=5)
        ttk.Button(top, text="Add Teacher", command=self.add_teacher).pack(side="left", padx=5)
        ttk.Button(top, text="Delete Selected", command=self.delete_selected_teacher).pack(side="left", padx=5)

        self.teachers_tree = ttk.Treeview(frame, columns=("id", "name"), show="headings", selectmode="browse")
        self.teachers_tree.heading("id", text="ID")
        self.teachers_tree.heading("name", text="Name")
        self.teachers_tree.column("id", width=50, anchor="center")
        self.teachers_tree.pack(fill="both", expand=True, pady=8)

    def add_teacher(self):
        name = self.teacher_name_var.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Teacher name cannot be empty.")
            return
        self.db.add_teacher(name)
        self.teacher_name_var.set("")
        self.refresh_teachers()
        self.refresh_timetable()

    def delete_selected_teacher(self):
        sel = self.teachers_tree.selection()
        if not sel:
            messagebox.showinfo("Delete Teacher", "Please select a teacher to delete.")
            return
        item = self.teachers_tree.item(sel[0])
        teacher_id = item["values"][0]
        if messagebox.askyesno("Confirm", f"Delete teacher '{item['values'][1]}'?"):
            self.db.delete_teacher(teacher_id)
            self.refresh_teachers()
            self.refresh_timetable()

    def refresh_teachers(self):
        for r in self.teachers_tree.get_children():
            self.teachers_tree.delete(r)
        for t in self.db.get_teachers():
            self.teachers_tree.insert("", "end", values=(t["id"], t["name"]))

    # ---------------- Courses Tab ----------------
    def _build_courses_tab(self, parent):
        frame = ttk.Frame(parent, padding=8)
        frame.pack(fill="both", expand=True)

        top = ttk.Frame(frame)
        top.pack(fill="x", pady=4)
        ttk.Label(top, text="Course Code:").pack(side="left")
        self.course_code_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.course_code_var, width=12).pack(side="left", padx=4)
        ttk.Label(top, text="Course Name:").pack(side="left")
        self.course_name_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.course_name_var).pack(side="left", padx=4)
        ttk.Button(top, text="Add Course", command=self.add_course).pack(side="left", padx=5)
        ttk.Button(top, text="Delete Selected", command=self.delete_selected_course).pack(side="left", padx=5)

        self.courses_tree = ttk.Treeview(frame, columns=("id", "code", "name"), show="headings", selectmode="browse")
        self.courses_tree.heading("id", text="ID")
        self.courses_tree.heading("code", text="Code")
        self.courses_tree.heading("name", text="Name")
        self.courses_tree.column("id", width=50, anchor="center")
        self.courses_tree.column("code", width=100, anchor="center")
        self.courses_tree.pack(fill="both", expand=True, pady=8)

    def add_course(self):
        name = self.course_name_var.get().strip()
        code = self.course_code_var.get().strip() or None
        if not name:
            messagebox.showwarning("Validation", "Course name cannot be empty.")
            return
        self.db.add_course(code, name)
        self.course_name_var.set("")
        self.course_code_var.set("")
        self.refresh_courses()
        self.refresh_units()

    def delete_selected_course(self):
        sel = self.courses_tree.selection()
        if not sel:
            messagebox.showinfo("Delete Course", "Please select a course to delete.")
            return
        item = self.courses_tree.item(sel[0])
        course_id = item["values"][0]
        if messagebox.askyesno("Confirm", f"Delete course '{item['values'][2]}'? This will also delete linked units."):
            self.db.delete_course(course_id)
            self.refresh_courses()
            self.refresh_units()
            self.refresh_timetable()

    def refresh_courses(self):
        for r in self.courses_tree.get_children():
            self.courses_tree.delete(r)
        for c in self.db.get_courses():
            self.courses_tree.insert("", "end", values=(c["id"], c["code"], c["name"]))

    # ---------------- Units Tab ----------------
    def _build_units_tab(self, parent):
        frame = ttk.Frame(parent, padding=8)
        frame.pack(fill="both", expand=True)

        top = ttk.Frame(frame)
        top.pack(fill="x", pady=4)
        ttk.Label(top, text="Unit Code:").pack(side="left")
        self.unit_code_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.unit_code_var, width=12).pack(side="left", padx=4)
        ttk.Label(top, text="Unit Name:").pack(side="left")
        self.unit_name_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.unit_name_var).pack(side="left", padx=4)
        ttk.Label(top, text="Course:").pack(side="left", padx=(8, 0))
        self.unit_course_var = tk.StringVar()
        self.unit_course_combo = ttk.Combobox(top, textvariable=self.unit_course_var, state="readonly", width=30)
        self.unit_course_combo.pack(side="left", padx=4)
        ttk.Button(top, text="Add Unit", command=self.add_unit).pack(side="left", padx=5)
        ttk.Button(top, text="Delete Selected", command=self.delete_selected_unit).pack(side="left", padx=5)

        self.units_tree = ttk.Treeview(frame, columns=("id", "code", "name", "course"), show="headings", selectmode="browse")
        self.units_tree.heading("id", text="ID")
        self.units_tree.heading("code", text="Code")
        self.units_tree.heading("name", text="Name")
        self.units_tree.heading("course", text="Course")
        self.units_tree.column("id", width=50, anchor="center")
        self.units_tree.pack(fill="both", expand=True, pady=8)

    def add_unit(self):
        name = self.unit_name_var.get().strip()
        code = self.unit_code_var.get().strip() or None
        course_selection = self.unit_course_var.get()
        course_id = None
        if course_selection:
            # combobox value formatted as "id - name" or "name"? We'll store mapping
            try:
                course_id = int(course_selection.split(":", 1)[0])
            except Exception:
                course_id = None
        if not name:
            messagebox.showwarning("Validation", "Unit name cannot be empty.")
            return
        self.db.add_unit(code, name, course_id)
        self.unit_name_var.set("")
        self.unit_code_var.set("")
        self.unit_course_var.set("")
        self.refresh_units()
        self.refresh_timetable()

    def delete_selected_unit(self):
        sel = self.units_tree.selection()
        if not sel:
            messagebox.showinfo("Delete Unit", "Please select a unit to delete.")
            return
        item = self.units_tree.item(sel[0])
        unit_id = item["values"][0]
        if messagebox.askyesno("Confirm", f"Delete unit '{item['values'][2]}'?"):
            self.db.delete_unit(unit_id)
            self.refresh_units()
            self.refresh_timetable()

    def refresh_units(self):
        # Update course combobox choices
        courses = self.db.get_courses()
        course_entries = []
        for c in courses:
            # use "id: name" format so we can parse id later
            course_entries.append(f"{c['id']}: {c['name']}")
        self.unit_course_combo["values"] = course_entries

        for r in self.units_tree.get_children():
            self.units_tree.delete(r)
        for u in self.db.get_units():
            course_name = u["course_name"] if u["course_name"] else ""
            self.units_tree.insert("", "end", values=(u["id"], u["code"] or "", u["name"], course_name))

    # ---------------- Timetable Tab ----------------
    def _build_timetable_tab(self, parent):
        frame = ttk.Frame(parent, padding=8)
        frame.pack(fill="both", expand=True)

        header = ttk.Frame(frame)
        header.pack(fill="x")
        ttk.Label(header, text="Right-click any cell to schedule or clear a class.", foreground="blue").pack(side="left")

        grid_frame = ttk.Frame(frame)
        grid_frame.pack(fill="both", expand=True, pady=8)

        # Build header row with day names
        ttk.Label(grid_frame, text="Time \\ Day", relief="ridge", width=18).grid(row=0, column=0, sticky="nsew")
        for c, day in enumerate(DAYS, start=1):
            lbl = ttk.Label(grid_frame, text=day, relief="ridge", width=24, anchor="center")
            lbl.grid(row=0, column=c, sticky="nsew")

        self.cell_widgets = {}  # (day, timeslot) -> Label widget

        for r, timeslot in enumerate(TIMESLOTS, start=1):
            # row label for timeslot
            lbl_row = ttk.Label(grid_frame, text=timeslot, relief="ridge", width=18, anchor="center")
            lbl_row.grid(row=r, column=0, sticky="nsew")
            for c, day in enumerate(DAYS, start=1):
                cell_frame = ttk.Frame(grid_frame, relief="ridge", borderwidth=1)
                cell_frame.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                cell_label = ttk.Label(cell_frame, text="", anchor="center", justify="center", width=24)
                cell_label.pack(fill="both", expand=True)
                # Bind right click to each cell
                cell_label.bind("<Button-3>", lambda ev, d=day, t=timeslot: self.on_cell_right_click(ev, d, t))
                # Also support macOS control-click
                cell_label.bind("<Control-Button-1>", lambda ev, d=day, t=timeslot: self.on_cell_right_click(ev, d, t))
                self.cell_widgets[(day, timeslot)] = cell_label

        # Make grid cells expand evenly
        for i in range(len(DAYS) + 1):
            grid_frame.columnconfigure(i, weight=1)
        for i in range(len(TIMESLOTS) + 1):
            grid_frame.rowconfigure(i, weight=1)

    def on_cell_right_click(self, event, day: str, timeslot: str):
        # Show schedule dialog
        self.open_schedule_dialog(day, timeslot)

    def open_schedule_dialog(self, day: str, timeslot: str):
        existing = self.db.get_schedule_cell(day, timeslot)

        dialog = tk.Toplevel(self.root)
        dialog.transient(self.root)
        dialog.title(f"Schedule: {day} - {timeslot}")
        dialog.grab_set()
        dialog.resizable(False, False)

        frm = ttk.Frame(dialog, padding=10)
        frm.pack(fill="both", expand=True)

        # Teacher combobox
        ttk.Label(frm, text="Teacher:").grid(row=0, column=0, sticky="w", pady=4)
        teachers = self.db.get_teachers()
        teacher_map = {f"{t['id']}: {t['name']}": t["id"] for t in teachers}
        teacher_values = list(teacher_map.keys())
        teacher_var = tk.StringVar()
        teacher_combo = ttk.Combobox(frm, textvariable=teacher_var, values=teacher_values, state="readonly", width=40)
        teacher_combo.grid(row=0, column=1, sticky="w", pady=4)

        # Unit combobox
        ttk.Label(frm, text="Unit:").grid(row=1, column=0, sticky="w", pady=4)
        units = self.db.get_units()
        unit_map = {}
        unit_values = []
        for u in units:
            display = f"{u['id']}: {u['name']} ({u['code'] or ''})"
            # attach course name if present
            if u["course_name"]:
                display += f" - {u['course_name']}"
            unit_map[display] = u["id"]
            unit_values.append(display)
        unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(frm, textvariable=unit_var, values=unit_values, state="readonly", width=60)
        unit_combo.grid(row=1, column=1, sticky="w", pady=4)

        # Room entry
        ttk.Label(frm, text="Room:").grid(row=2, column=0, sticky="w", pady=4)
        room_var = tk.StringVar()
        room_entry = ttk.Entry(frm, textvariable=room_var, width=30)
        room_entry.grid(row=2, column=1, sticky="w", pady=4)

        # Prepopulate if existing
        if existing:
            if existing["teacher_id"]:
                # find key by id
                for k, v in teacher_map.items():
                    if v == existing["teacher_id"]:
                        teacher_var.set(k)
                        break
            if existing["unit_id"]:
                for k, v in unit_map.items():
                    if v == existing["unit_id"]:
                        unit_var.set(k)
                        break
            room_var.set(existing["room"] or "")

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=8)

        def save_action():
            teacher_id = teacher_map.get(teacher_var.get())
            unit_id = unit_map.get(unit_var.get())
            room = room_var.get().strip() or None
            # allow scheduling with missing fields if desired; but at least unit or teacher should be set
            if teacher_id is None and unit_id is None and not room:
                if not messagebox.askyesno("Confirm", "You are saving an empty schedule entry. Continue?"):
                    return
            self.db.add_or_update_schedule(day, timeslot, teacher_id, unit_id, room)
            dialog.destroy()
            self.refresh_timetable()

        def clear_action():
            if messagebox.askyesno("Confirm", f"Clear schedule for {day} - {timeslot}?"):
                self.db.delete_schedule(day, timeslot)
                dialog.destroy()
                self.refresh_timetable()

        ttk.Button(btn_frame, text="Save", command=save_action).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear", command=clear_action).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

        # Center dialog over root
        self.root.update_idletasks()
        x = self.root.winfo_rootx() + self.root.winfo_width() // 2 - dialog.winfo_reqwidth() // 2
        y = self.root.winfo_rooty() + self.root.winfo_height() // 2 - dialog.winfo_reqheight() // 2
        dialog.geometry(f"+{x}+{y}")

    def refresh_timetable(self):
        # Clear all cells
        for (day, timeslot), widget in self.cell_widgets.items():
            widget.config(text="", foreground="black")

        # Fill with schedule entries
        for row in self.db.get_all_schedule():
            day = row["day"]
            timeslot = row["timeslot"]
            widget = self.cell_widgets.get((day, timeslot))
            if not widget:
                continue
            parts = []
            if row["unit_name"]:
                unit_text = row["unit_name"]
                if row["unit_code"]:
                    unit_text += f" ({row['unit_code']})"
                parts.append(unit_text)
            if row["teacher_name"]:
                parts.append(f"Teacher: {row['teacher_name']}")
            if row["room"]:
                parts.append(f"Room: {row['room']}")
            display = "\n".join(parts)
            widget.config(text=display)

    def refresh_all(self):
        self.refresh_teachers()
        self.refresh_courses()
        self.refresh_units()
        self.refresh_timetable()

    def on_close(self):
        try:
            self.db.close()
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.geometry("1000x600")
    root.mainloop()
