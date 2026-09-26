"""
gui.py
Tkinter desktop interface for the Scholarship Application System.
Wraps the existing backend (models/validation/storage/search/eligibility/
seed_data) with no changes to that logic - this file is purely presentation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from models import (
    Applicant, AcademicBackground, FinancialProfile, ScholarshipProgram,
    Application, Gender, SchoolType, EmploymentStatus, ScholarshipType,
    ApplicationStatus,
)
from validation import (
    validate_name, validate_email, validate_mobile_number, validate_date_of_birth,
    validate_gwa, validate_income, validate_evaluation_score, validate_required_text,
    validate_application_for_submission,
)
from storage import DataStore, NotFoundError, DuplicateIDError
from search import (
    search_by_name, search_by_status, search_by_scholarship_type,
    search_by_gwa_range,
)
from eligibility import list_eligible_programs
from seed_data import seed_programs

# ---------------------------------------------------------------------------
# Theme constants (Mapua palette: red/maroon, gold, black, grey)
# ---------------------------------------------------------------------------

BG_COLOR = "#f2f2f2"
CARD_COLOR = "#ffffff"
PRIMARY_COLOR = "#a6192e"      # Mapua red/maroon
ACCENT_COLOR = "#ffc72c"       # gold/yellow
ACCENT_HOVER = "#e6b325"       # darker gold, for button hover
TEXT_COLOR = "#1a1a1a"         # near-black
SUBTLE_TEXT = "#595959"        # grey
BORDER_COLOR = "#cccccc"       # grey
STRIPE_COLOR = "#f5f5f5"       # light grey (zebra striping)

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_HEADING = ("Segoe UI", 12, "bold")
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SUBTITLE = ("Segoe UI", 9)


def parse_date(text):
    text = text.strip()
    if not text:
        return None
    return datetime.strptime(text, "%Y-%m-%d").date()


def zebra_tags(tree):
    tree.tag_configure("oddrow", background=STRIPE_COLOR)
    tree.tag_configure("evenrow", background=CARD_COLOR)


class ScrollableFrame(ttk.Frame):
    """A vertically scrollable container. Use .inner as the parent for
    widgets placed inside it. Pack this with fill='both', expand=True and
    it will stretch to fill whatever space its parent gives it, while still
    scrolling if the inner content is taller than that space."""

    def __init__(self, parent, height=1, **kwargs):
        super().__init__(parent, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, height=height, bg=CARD_COLOR)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.inner = ttk.Frame(canvas)

        self.inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window_id = canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            delta = event.delta if event.delta else (120 if event.num == 4 else -120)
            canvas.yview_scroll(int(-1 * (delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: (
            canvas.bind_all("<MouseWheel>", _on_mousewheel),
            canvas.bind_all("<Button-4>", _on_mousewheel),
            canvas.bind_all("<Button-5>", _on_mousewheel),
        ))
        canvas.bind("<Leave>", lambda e: (
            canvas.unbind_all("<MouseWheel>"),
            canvas.unbind_all("<Button-4>"),
            canvas.unbind_all("<Button-5>"),
        ))


class ScholarshipApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scholarship Application System")
        self.geometry("1100x800")
        self.minsize(960, 640)
        self.configure(bg=BG_COLOR)

        self.store = DataStore()
        seed_programs(self.store)

        self._configure_styles()
        self._build_header()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=14, pady=(10, 4))

        self.applicants_tab = ApplicantsTab(notebook, self.store)
        self.programs_tab = ProgramsTab(notebook, self.store)
        self.applications_tab = ApplicationsTab(notebook, self.store, on_change=self.refresh_all)
        self.search_tab = SearchTab(notebook, self.store)

        notebook.add(self.applicants_tab, text="  Applicants  ")
        notebook.add(self.programs_tab, text="  Scholarship Programs  ")
        notebook.add(self.applications_tab, text="  Applications  ")
        notebook.add(self.search_tab, text="  Search  ")

        notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh_all())

        self._build_status_bar()
        self.refresh_all()

    def _configure_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=BG_COLOR, foreground=TEXT_COLOR, font=FONT)
        style.configure("TFrame", background=BG_COLOR)
        style.configure("Card.TFrame", background=CARD_COLOR)

        style.configure("TLabelframe", background=CARD_COLOR, bordercolor=BORDER_COLOR,
                         relief="solid", borderwidth=1)
        style.configure("TLabelframe.Label", background=CARD_COLOR, foreground=PRIMARY_COLOR,
                         font=FONT_HEADING)
        style.configure("TLabel", background=CARD_COLOR, foreground=TEXT_COLOR, font=FONT)
        style.configure("Hint.TLabel", background=CARD_COLOR, foreground=SUBTLE_TEXT,
                         font=FONT_SUBTITLE)

        style.configure("Header.TLabel", background=PRIMARY_COLOR, foreground="white", font=FONT_TITLE)
        style.configure("SubHeader.TLabel", background=PRIMARY_COLOR, foreground="#ffe6a8",
                         font=FONT_SUBTITLE)
        style.configure("Status.TLabel", background=BG_COLOR, foreground=SUBTLE_TEXT, font=FONT_SUBTITLE)

        style.configure("TButton", font=FONT, padding=6)
        style.configure("Accent.TButton", background=ACCENT_COLOR, foreground="#1a1a1a", font=FONT_BOLD)
        style.map("Accent.TButton", background=[("active", ACCENT_HOVER)])

        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", font=FONT_BOLD, padding=(16, 8),
                         background="#d9d9d9", foreground=SUBTLE_TEXT)
        style.map("TNotebook.Tab",
                  background=[("selected", CARD_COLOR)],
                  foreground=[("selected", PRIMARY_COLOR)])

        style.configure("Treeview", background=CARD_COLOR, fieldbackground=CARD_COLOR,
                         rowheight=26, font=FONT, bordercolor=BORDER_COLOR)
        style.configure("Treeview.Heading", font=FONT_BOLD, background="#e6e6e6",
                         foreground=PRIMARY_COLOR, relief="flat")
        style.map("Treeview", background=[("selected", PRIMARY_COLOR)], foreground=[("selected", "white")])

        style.configure("TCombobox", padding=4)
        style.configure("TEntry", padding=4)

    def _build_header(self):
        header = tk.Frame(self, bg=PRIMARY_COLOR)
        header.pack(fill="x")
        text_frame = tk.Frame(header, bg=PRIMARY_COLOR)
        text_frame.pack(side="left", padx=20, pady=14)
        ttk.Label(text_frame, text="Scholarship Application System", style="Header.TLabel").pack(anchor="w")
        ttk.Label(text_frame, text="Applicant records, scholarship grants, and eligibility matching",
                  style="SubHeader.TLabel").pack(anchor="w", pady=(2, 0))

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="")
        bar = ttk.Label(self, textvariable=self.status_var, style="Status.TLabel", anchor="w")
        bar.pack(fill="x", padx=16, pady=(0, 8))

    def refresh_all(self):
        self.applicants_tab.refresh()
        self.programs_tab.refresh()
        self.applications_tab.refresh()
        self.status_var.set(
            f"  Applicants: {len(self.store.list_applicants())}    |    "
            f"Programs: {len(self.store.list_programs())}    |    "
            f"Applications: {len(self.store.list_applications())}    |    "
            f"Tip: scroll within a tab if content runs below the window"
        )


# ---------------------------------------------------------------------------
# Applicants tab
# ---------------------------------------------------------------------------

class ApplicantsTab(ttk.Frame):
    def __init__(self, parent, store):
        super().__init__(parent)
        self.store = store

        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True)
        self.content = scroll.inner

        self._build_form()
        self._build_list()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self.content, text="Register New Applicant")
        form.pack(fill="x", padx=12, pady=12)

        self.vars = {
            "first_name": tk.StringVar(), "middle_name": tk.StringVar(),
            "last_name": tk.StringVar(), "suffix": tk.StringVar(),
            "email": tk.StringVar(), "mobile": tk.StringVar(),
            "dob": tk.StringVar(), "address": tk.StringVar(),
        }
        self.gender_var = tk.StringVar(value=Gender.MALE.value)

        fields = [
            ("First Name*", "first_name"), ("Middle Name", "middle_name"),
            ("Last Name*", "last_name"), ("Suffix (Jr./III)", "suffix"),
            ("Email*", "email"), ("Mobile (09XXXXXXXXX)*", "mobile"),
            ("Date of Birth (YYYY-MM-DD)*", "dob"), ("Permanent Address*", "address"),
        ]
        for i, (label, key) in enumerate(fields):
            row, col = divmod(i, 2)
            ttk.Label(form, text=label).grid(row=row * 2, column=col, sticky="w", padx=10, pady=(8, 0))
            ttk.Entry(form, textvariable=self.vars[key], width=34).grid(
                row=row * 2 + 1, column=col, sticky="we", padx=10, pady=(0, 6)
            )

        gender_row = ((len(fields) + 1) // 2) * 2
        ttk.Label(form, text="Gender*").grid(row=gender_row, column=0, sticky="w", padx=10, pady=(8, 0))
        ttk.Combobox(
            form, textvariable=self.gender_var, values=[g.value for g in Gender],
            state="readonly", width=31,
        ).grid(row=gender_row + 1, column=0, sticky="we", padx=10, pady=(0, 10))

        ttk.Button(form, text="+ Register Applicant", style="Accent.TButton",
                   command=self._on_register).grid(row=gender_row + 1, column=1, sticky="e", padx=10, pady=(0, 10))
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

    def _build_list(self):
        list_frame = ttk.LabelFrame(self.content, text="Registered Applicants")
        list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        columns = ("id", "name", "email", "mobile")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        for col, label, width in [
            ("id", "Applicant ID", 100), ("name", "Full Name", 260),
            ("email", "Email", 220), ("mobile", "Mobile", 140),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        zebra_tags(self.tree)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def _on_register(self):
        checks = [
            validate_name(self.vars["first_name"].get(), "First name"),
            validate_name(self.vars["last_name"].get(), "Last name"),
            validate_email(self.vars["email"].get()),
            validate_mobile_number(self.vars["mobile"].get()),
            validate_required_text(self.vars["address"].get(), "Address"),
        ]
        try:
            dob = parse_date(self.vars["dob"].get())
        except ValueError:
            messagebox.showerror("Invalid input", "Date of birth must be in YYYY-MM-DD format.")
            return
        checks.append(validate_date_of_birth(dob))

        errors = [msg for is_valid, msg in checks if not is_valid]
        if errors:
            messagebox.showerror("Invalid input", "\n".join(errors))
            return

        applicant_id = self.store.generate_applicant_id()
        applicant = Applicant(
            applicant_id=applicant_id,
            first_name=self.vars["first_name"].get().strip(),
            middle_name=self.vars["middle_name"].get().strip(),
            last_name=self.vars["last_name"].get().strip(),
            suffix=self.vars["suffix"].get().strip(),
            email=self.vars["email"].get().strip(),
            mobile_number=self.vars["mobile"].get().strip(),
            date_of_birth=dob,
            gender=Gender(self.gender_var.get()),
            permanent_address=self.vars["address"].get().strip(),
        )
        try:
            self.store.add_applicant(applicant)
        except DuplicateIDError as e:
            messagebox.showerror("Error", str(e))
            return

        messagebox.showinfo("Success", f"Applicant registered with ID: {applicant_id}")
        for var in self.vars.values():
            var.set("")
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, a in enumerate(self.store.list_applicants()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(a.applicant_id, a.full_name(), a.email, a.mobile_number),
                              tags=(tag,))


# ---------------------------------------------------------------------------
# Scholarship Programs tab
# ---------------------------------------------------------------------------

class ProgramsTab(ttk.Frame):
    def __init__(self, parent, store):
        super().__init__(parent)
        self.store = store

        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True)
        self.content = scroll.inner

        self._build_list()
        self._build_detail()
        self._build_form()
        self.refresh()

    def _build_list(self):
        list_frame = ttk.LabelFrame(self.content, text="Scholarship Programs")
        list_frame.pack(fill="both", expand=False, padx=12, pady=12)

        columns = ("id", "name", "provider", "type")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        for col, label, width in [
            ("id", "Program ID", 90), ("name", "Grant Name", 300),
            ("provider", "Provider", 220), ("type", "Type", 150),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        zebra_tags(self.tree)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _build_detail(self):
        detail_frame = ttk.LabelFrame(self.content, text="Program Details  (select a row above)")
        detail_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.detail_text = tk.Text(detail_frame, height=10, wrap="word", state="disabled",
                                    bg=CARD_COLOR, fg=TEXT_COLOR, font=FONT, relief="flat",
                                    padx=8, pady=8)
        self.detail_text.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_form(self):
        form = ttk.LabelFrame(self.content, text="Register New Scholarship Program")
        form.pack(fill="x", padx=12, pady=(0, 12))

        self.vars = {
            "name": tk.StringVar(), "provider": tk.StringVar(),
            "tuition": tk.StringVar(value="0"), "stipend": tk.StringVar(value="0"),
            "book": tk.StringVar(value="0"),
        }
        self.type_var = tk.StringVar(value=ScholarshipType.ACADEMIC_MERIT.value)

        ttk.Label(form, text="Grant Name*").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))
        ttk.Entry(form, textvariable=self.vars["name"], width=28).grid(row=1, column=0, sticky="we", padx=10)
        ttk.Label(form, text="Provider*").grid(row=0, column=1, sticky="w", padx=10, pady=(8, 0))
        ttk.Entry(form, textvariable=self.vars["provider"], width=28).grid(row=1, column=1, sticky="we", padx=10)
        ttk.Label(form, text="Type*").grid(row=0, column=2, sticky="w", padx=10, pady=(8, 0))
        ttk.Combobox(
            form, textvariable=self.type_var, values=[t.value for t in ScholarshipType],
            state="readonly", width=20,
        ).grid(row=1, column=2, sticky="we", padx=10)

        ttk.Label(form, text="Tuition Allowance").grid(row=2, column=0, sticky="w", padx=10, pady=(8, 0))
        ttk.Entry(form, textvariable=self.vars["tuition"], width=28).grid(row=3, column=0, sticky="we", padx=10)
        ttk.Label(form, text="Monthly Stipend").grid(row=2, column=1, sticky="w", padx=10, pady=(8, 0))
        ttk.Entry(form, textvariable=self.vars["stipend"], width=28).grid(row=3, column=1, sticky="we", padx=10)
        ttk.Label(form, text="Book Allowance").grid(row=2, column=2, sticky="w", padx=10, pady=(8, 0))
        ttk.Entry(form, textvariable=self.vars["book"], width=28).grid(row=3, column=2, sticky="we", padx=10)

        ttk.Button(form, text="+ Register Program", style="Accent.TButton", command=self._on_register).grid(
            row=4, column=2, sticky="e", padx=10, pady=10
        )
        for i in range(3):
            form.columnconfigure(i, weight=1)

    def _on_register(self):
        errors = []
        is_valid, msg = validate_required_text(self.vars["name"].get(), "Grant name")
        if not is_valid:
            errors.append(msg)
        is_valid, msg = validate_required_text(self.vars["provider"].get(), "Provider")
        if not is_valid:
            errors.append(msg)

        amounts = {}
        for key, label in [("tuition", "Tuition allowance"), ("stipend", "Monthly stipend"),
                            ("book", "Book allowance")]:
            try:
                value = float(self.vars[key].get())
                if value < 0:
                    raise ValueError
                amounts[key] = value
            except ValueError:
                errors.append(f"{label} must be a non-negative number.")

        if errors:
            messagebox.showerror("Invalid input", "\n".join(errors))
            return

        program_id = self.store.generate_program_id()
        program = ScholarshipProgram(
            program_id=program_id,
            grant_name=self.vars["name"].get().strip(),
            provider=self.vars["provider"].get().strip(),
            scholarship_type=ScholarshipType(self.type_var.get()),
            tuition_allowance=amounts["tuition"],
            monthly_stipend=amounts["stipend"],
            book_allowance=amounts["book"],
        )
        try:
            self.store.add_program(program)
        except DuplicateIDError as e:
            messagebox.showerror("Error", str(e))
            return

        messagebox.showinfo("Success", f"Program registered with ID: {program_id}")
        self.vars["name"].set("")
        self.vars["provider"].set("")
        self.vars["tuition"].set("0")
        self.vars["stipend"].set("0")
        self.vars["book"].set("0")
        self.refresh()

    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        program_id = self.tree.item(selection[0], "values")[0]
        program = self.store.get_program(program_id)
        lines = [
            f"{program.grant_name}  ({program.provider})",
            f"Type: {program.scholarship_type.value}",
            f"Total modeled coverage: Php {program.total_coverage():,.2f}", "",
        ]
        for title, items in [
            ("Benefits", program.benefits_description),
            ("Eligibility criteria", program.eligibility_criteria),
            ("Required documents", program.required_documents),
            ("Application period / process", program.application_period_notes),
            ("Responsibilities of grantees", program.grantee_responsibilities),
        ]:
            if items:
                lines.append(f"{title}:")
                lines.extend(f"  -  {item}" for item in items)
                lines.append("")
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", "\n".join(lines))
        self.detail_text.configure(state="disabled")

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, p in enumerate(self.store.list_programs()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(p.program_id, p.grant_name, p.provider,
                                                 p.scholarship_type.value), tags=(tag,))


# ---------------------------------------------------------------------------
# Applications tab
# ---------------------------------------------------------------------------

class ApplicationsTab(ttk.Frame):
    def __init__(self, parent, store, on_change=None):
        super().__init__(parent)
        self.store = store
        self.on_change = on_change or (lambda: None)
        self.editing_application_id = None

        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True)
        self.content = scroll.inner

        self._build_form()
        self._build_list()
        self.refresh()

    def _build_form(self):
        form_frame = ttk.LabelFrame(self.content, text="Create / Update Application")
        form_frame.pack(fill="x", padx=12, pady=12)

        inner_scroll = ScrollableFrame(form_frame, height=320)
        inner_scroll.pack(fill="both", expand=True, padx=6, pady=6)
        form = inner_scroll.inner

        self.applicant_var = tk.StringVar()
        self.program_var = tk.StringVar()
        self.applicant_combo = ttk.Combobox(form, textvariable=self.applicant_var, state="readonly", width=40)
        self.program_combo = ttk.Combobox(form, textvariable=self.program_var, state="readonly", width=40)

        ttk.Label(form, text="Applicant*").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))
        self.applicant_combo.grid(row=1, column=0, sticky="we", padx=10)
        ttk.Label(form, text="Scholarship Program*").grid(row=0, column=1, sticky="w", padx=10, pady=(8, 0))
        self.program_combo.grid(row=1, column=1, sticky="we", padx=10)

        self.vars = {
            "year_level": tk.StringVar(), "program_name": tk.StringVar(), "school_name": tk.StringVar(),
            "gwa": tk.StringVar(), "tor_path": tk.StringVar(),
            "income": tk.StringVar(), "father_name": tk.StringVar(), "father_occ": tk.StringVar(),
            "mother_name": tk.StringVar(), "mother_occ": tk.StringVar(), "guardian_name": tk.StringVar(),
            "doc_path": tk.StringVar(), "opening_date": tk.StringVar(), "deadline": tk.StringVar(),
        }
        self.school_type_var = tk.StringVar(value=SchoolType.PRIVATE.value)
        self.father_status_var = tk.StringVar(value=EmploymentStatus.EMPLOYED.value)
        self.mother_status_var = tk.StringVar(value=EmploymentStatus.UNEMPLOYED.value)

        ttk.Label(form, text="Academic Background", style="Hint.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(14, 0)
        )

        fields = [
            ("Year/Grade Level*", "year_level"), ("Enrolled Program/Strand*", "program_name"),
            ("School Name*", "school_name"), ("GWA (1.0-5.0)*", "gwa"),
            ("TOR/Form 138 file path", "tor_path"), ("Household Monthly Income*", "income"),
            ("Father's Name", "father_name"), ("Father's Occupation", "father_occ"),
            ("Mother's Name", "mother_name"), ("Mother's Occupation", "mother_occ"),
            ("Guardian's Name", "guardian_name"), ("Supporting Doc path (ITR/Indigency)", "doc_path"),
            ("Opening Date (YYYY-MM-DD)", "opening_date"), ("Deadline (YYYY-MM-DD)", "deadline"),
        ]
        for i, (label, key) in enumerate(fields):
            row, col = divmod(i, 2)
            base = 3 + row * 2
            ttk.Label(form, text=label).grid(row=base, column=col, sticky="w", padx=10, pady=(8, 0))
            ttk.Entry(form, textvariable=self.vars[key], width=40).grid(row=base + 1, column=col, sticky="we", padx=10)

        combo_row = 3 + ((len(fields) + 1) // 2) * 2
        ttk.Label(form, text="School Type*").grid(row=combo_row, column=0, sticky="w", padx=10, pady=(8, 0))
        ttk.Combobox(form, textvariable=self.school_type_var, values=[t.value for t in SchoolType],
                     state="readonly", width=37).grid(row=combo_row + 1, column=0, sticky="we", padx=10)
        ttk.Label(form, text="Father's Employment Status").grid(row=combo_row, column=1, sticky="w", padx=10, pady=(8, 0))
        ttk.Combobox(form, textvariable=self.father_status_var, values=[s.value for s in EmploymentStatus],
                     state="readonly", width=37).grid(row=combo_row + 1, column=1, sticky="we", padx=10)
        ttk.Label(form, text="Mother's Employment Status").grid(row=combo_row + 2, column=0, sticky="w", padx=10, pady=(8, 0))
        ttk.Combobox(form, textvariable=self.mother_status_var, values=[s.value for s in EmploymentStatus],
                     state="readonly", width=37).grid(row=combo_row + 3, column=0, sticky="we", padx=10, pady=(0, 10))

        for i in range(2):
            form.columnconfigure(i, weight=1)

        button_bar = ttk.Frame(form_frame)
        button_bar.pack(fill="x", padx=10, pady=(0, 10))
        self.submit_button = ttk.Button(button_bar, text="+ Create Application", style="Accent.TButton",
                                         command=self._on_create)
        self.submit_button.pack(side="right")
        ttk.Button(button_bar, text="Clear Form / New Application", command=self._on_clear_form).pack(
            side="right", padx=(0, 8)
        )
        self.editing_label = ttk.Label(button_bar, text="", style="Hint.TLabel")
        self.editing_label.pack(side="left")

    def _refresh_combos(self):
        applicants = self.store.list_applicants()
        programs = self.store.list_programs()
        self._applicant_map = {f"{a.applicant_id} - {a.full_name()}": a.applicant_id for a in applicants}
        self._program_map = {f"{p.program_id} - {p.grant_name}": p.program_id for p in programs}
        self.applicant_combo["values"] = list(self._applicant_map.keys())
        self.program_combo["values"] = list(self._program_map.keys())

    def _load_application_into_form(self, application):
        self.editing_application_id = application.application_id
        self.applicant_var.set(f"{application.applicant.applicant_id} - {application.applicant.full_name()}")
        self.program_var.set(f"{application.program.program_id} - {application.program.grant_name}")

        academic = application.academic_background
        financial = application.financial_profile

        self.vars["year_level"].set(academic.year_level)
        self.vars["program_name"].set(academic.program)
        self.vars["school_name"].set(academic.school_name)
        self.vars["gwa"].set("" if academic.gwa is None else str(academic.gwa))
        self.vars["tor_path"].set(academic.tor_file_path)
        self.school_type_var.set(academic.school_type.value if academic.school_type else SchoolType.PRIVATE.value)

        self.vars["income"].set(
            "" if financial.household_monthly_income is None else str(financial.household_monthly_income)
        )
        self.vars["father_name"].set(financial.father_name)
        self.vars["father_occ"].set(financial.father_occupation)
        self.father_status_var.set(
            financial.father_employment_status.value if financial.father_employment_status
            else EmploymentStatus.EMPLOYED.value
        )
        self.vars["mother_name"].set(financial.mother_name)
        self.vars["mother_occ"].set(financial.mother_occupation)
        self.mother_status_var.set(
            financial.mother_employment_status.value if financial.mother_employment_status
            else EmploymentStatus.UNEMPLOYED.value
        )
        self.vars["guardian_name"].set(financial.guardian_name)
        self.vars["doc_path"].set(
            financial.supporting_document_paths[0] if financial.supporting_document_paths else ""
        )
        self.vars["opening_date"].set(application.opening_date.isoformat() if application.opening_date else "")
        self.vars["deadline"].set(
            application.submission_deadline.isoformat() if application.submission_deadline else ""
        )

        self.submit_button.configure(text="Update Application")
        self.editing_label.configure(text=f"Editing: {application.application_id}")

    def _on_clear_form(self):
        self.editing_application_id = None
        self.applicant_var.set("")
        self.program_var.set("")
        for var in self.vars.values():
            var.set("")
        self.school_type_var.set(SchoolType.PRIVATE.value)
        self.father_status_var.set(EmploymentStatus.EMPLOYED.value)
        self.mother_status_var.set(EmploymentStatus.UNEMPLOYED.value)
        self.submit_button.configure(text="+ Create Application")
        self.editing_label.configure(text="")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def _on_create(self):
        if not self.applicant_var.get() or not self.program_var.get():
            messagebox.showerror("Missing selection", "Please select both an applicant and a program.")
            return
        applicant_id = self._applicant_map.get(self.applicant_var.get())
        program_id = self._program_map.get(self.program_var.get())
        if applicant_id is None or program_id is None:
            messagebox.showerror("Invalid selection", "Selected applicant or program no longer exists.")
            return

        errors = []
        for key, label in [("year_level", "Year/grade level"), ("program_name", "Enrolled program/strand"),
                            ("school_name", "School name")]:
            is_valid, msg = validate_required_text(self.vars[key].get(), label)
            if not is_valid:
                errors.append(msg)

        try:
            gwa = float(self.vars["gwa"].get())
        except ValueError:
            gwa = None
        is_valid, msg = validate_gwa(gwa)
        if not is_valid:
            errors.append(msg)

        try:
            income = float(self.vars["income"].get())
        except ValueError:
            income = None
        is_valid, msg = validate_income(income)
        if not is_valid:
            errors.append(msg)

        opening_date = deadline = None
        try:
            opening_date = parse_date(self.vars["opening_date"].get())
            deadline = parse_date(self.vars["deadline"].get())
        except ValueError:
            errors.append("Opening date / deadline must be in YYYY-MM-DD format.")

        if errors:
            messagebox.showerror("Invalid input", "\n".join(errors))
            return

        applicant = self.store.get_applicant(applicant_id)
        program = self.store.get_program(program_id)

        academic = AcademicBackground(
            year_level=self.vars["year_level"].get().strip(),
            program=self.vars["program_name"].get().strip(),
            school_name=self.vars["school_name"].get().strip(),
            school_type=SchoolType(self.school_type_var.get()),
            gwa=gwa, tor_file_path=self.vars["tor_path"].get().strip(),
        )
        financial = FinancialProfile(
            household_monthly_income=income,
            father_name=self.vars["father_name"].get().strip(),
            father_occupation=self.vars["father_occ"].get().strip(),
            father_employment_status=EmploymentStatus(self.father_status_var.get()),
            mother_name=self.vars["mother_name"].get().strip(),
            mother_occupation=self.vars["mother_occ"].get().strip(),
            mother_employment_status=EmploymentStatus(self.mother_status_var.get()),
            guardian_name=self.vars["guardian_name"].get().strip(),
            supporting_document_paths=(
                [self.vars["doc_path"].get().strip()] if self.vars["doc_path"].get().strip() else []
            ),
        )

        if self.editing_application_id:
            application = self.store.get_application(self.editing_application_id)
            application.applicant = applicant
            application.program = program
            application.academic_background = academic
            application.financial_profile = financial
            application.opening_date = opening_date
            application.submission_deadline = deadline
            messagebox.showinfo("Updated", f"Application {self.editing_application_id} updated.")
        else:
            application_id = self.store.generate_application_id()
            application = Application(
                application_id=application_id, applicant=applicant, academic_background=academic,
                financial_profile=financial, program=program,
                opening_date=opening_date, submission_deadline=deadline,
            )
            try:
                self.store.add_application(application)
            except DuplicateIDError as e:
                messagebox.showerror("Error", str(e))
                return
            messagebox.showinfo("Success", f"Application created with ID: {application_id}")

        self._on_clear_form()
        self.refresh()
        self.on_change()

    def _build_list(self):
        list_frame = ttk.LabelFrame(self.content, text="Applications  (select a row to edit or act on it)")
        list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        columns = ("id", "applicant", "program", "status", "score")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        for col, label, width in [
            ("id", "Application ID", 100), ("applicant", "Applicant", 220),
            ("program", "Program", 260), ("status", "Status", 220), ("score", "Score", 80),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        zebra_tags(self.tree)
        self.tree.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        self.tree.bind("<<TreeviewSelect>>", self._on_select_from_list)

        button_bar = ttk.Frame(list_frame)
        button_bar.pack(fill="x", padx=10, pady=10)
        ttk.Button(button_bar, text="Submit Application", style="Accent.TButton",
                   command=self._on_submit).pack(side="left", padx=(0, 6))
        ttk.Button(button_bar, text="Update Status", command=self._on_update_status).pack(side="left", padx=6)
        ttk.Button(button_bar, text="Log Evaluation Score", command=self._on_log_score).pack(side="left", padx=6)
        ttk.Button(button_bar, text="Check Eligibility", command=self._on_check_eligibility).pack(side="left", padx=6)

    def _on_select_from_list(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        application_id = self.tree.item(selection[0], "values")[0]
        application = self.store.get_application(application_id)
        self._load_application_into_form(application)

    def _selected_application(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No selection", "Select an application from the list first.")
            return None
        application_id = self.tree.item(selection[0], "values")[0]
        return self.store.get_application(application_id)

    def _on_submit(self):
        application = self._selected_application()
        if not application:
            return
        is_valid, errors = validate_application_for_submission(application)
        if not is_valid:
            messagebox.showerror("Cannot submit", "\n".join(errors))
            return
        application.submitted_at = datetime.now()
        self.store.update_application_status(application.application_id, ApplicationStatus.SUBMITTED)
        messagebox.showinfo("Submitted", f"Application {application.application_id} submitted.")
        self.refresh()

    def _on_update_status(self):
        application = self._selected_application()
        if not application:
            return
        new_status = self._ask_choice("Update Status", "New status:", [s.value for s in ApplicationStatus])
        if not new_status:
            return
        self.store.update_application_status(application.application_id, ApplicationStatus(new_status))
        self.refresh()

    def _on_log_score(self):
        application = self._selected_application()
        if not application:
            return
        score_str = self._ask_text("Log Score", "Evaluation score (0-100):")
        if score_str is None:
            return
        try:
            score = float(score_str)
        except ValueError:
            messagebox.showerror("Invalid input", "Score must be numeric.")
            return
        is_valid, msg = validate_evaluation_score(score)
        if not is_valid:
            messagebox.showerror("Invalid input", msg)
            return
        self.store.update_evaluation_score(application.application_id, score)
        self.refresh()

    def _on_check_eligibility(self):
        application = self._selected_application()
        if not application:
            return
        results = list_eligible_programs(self.store, application)
        lines = [f"Eligibility for {application.applicant.full_name()} ({application.application_id}):", ""]
        for program, is_eligible, reasons in results:
            verdict = "ELIGIBLE" if is_eligible else "NOT ELIGIBLE"
            lines.append(f"[{verdict}] {program.grant_name}")
            for r in reasons:
                lines.append(f"    - {r}")
            if not reasons:
                lines.append("    (no unmet machine-checkable criteria)")
            lines.append("")
        self._show_report("Eligibility Results", "\n".join(lines))

    def _ask_choice(self, title, prompt, options):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.configure(bg=CARD_COLOR)
        dialog.grab_set()
        ttk.Label(dialog, text=prompt).pack(padx=16, pady=(16, 6))
        var = tk.StringVar(value=options[0])
        ttk.Combobox(dialog, textvariable=var, values=options, state="readonly", width=40).pack(padx=16, pady=4)
        result = {"value": None}

        def confirm():
            result["value"] = var.get()
            dialog.destroy()

        ttk.Button(dialog, text="OK", style="Accent.TButton", command=confirm).pack(pady=16)
        dialog.wait_window()
        return result["value"]

    def _ask_text(self, title, prompt):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.configure(bg=CARD_COLOR)
        dialog.grab_set()
        ttk.Label(dialog, text=prompt).pack(padx=16, pady=(16, 6))
        var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=var, width=30)
        entry.pack(padx=16, pady=4)
        entry.focus_set()
        result = {"value": None}

        def confirm():
            result["value"] = var.get()
            dialog.destroy()

        ttk.Button(dialog, text="OK", style="Accent.TButton", command=confirm).pack(pady=16)
        dialog.wait_window()
        return result["value"]

    def _show_report(self, title, text):
        window = tk.Toplevel(self)
        window.title(title)
        window.configure(bg=CARD_COLOR)
        window.geometry("540x440")
        text_widget = tk.Text(window, wrap="word", bg=CARD_COLOR, fg=TEXT_COLOR, font=FONT,
                               relief="flat", padx=10, pady=10)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", text)
        text_widget.configure(state="disabled")

    def refresh(self):
        self._refresh_combos()
        self.tree.delete(*self.tree.get_children())
        for i, a in enumerate(self.store.list_applications()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(
                a.application_id, a.applicant.full_name(), a.program.grant_name,
                a.status.value, a.evaluation_score if a.evaluation_score is not None else "",
            ), tags=(tag,))


# ---------------------------------------------------------------------------
# Search tab
# ---------------------------------------------------------------------------

class SearchTab(ttk.Frame):
    def __init__(self, parent, store):
        super().__init__(parent)
        self.store = store

        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True)
        self.content = scroll.inner

        self._build_controls()
        self._build_results()

    def _build_controls(self):
        controls = ttk.LabelFrame(self.content, text="Search Applications")
        controls.pack(fill="x", padx=12, pady=12)

        ttk.Label(controls, text="Name keyword").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.name_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.name_var, width=20).grid(row=0, column=1, padx=10)
        ttk.Button(controls, text="Search by Name", style="Accent.TButton",
                   command=self._search_by_name).grid(row=0, column=2, padx=10)

        ttk.Label(controls, text="Status").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.status_var = tk.StringVar(value=ApplicationStatus.SUBMITTED.value)
        ttk.Combobox(controls, textvariable=self.status_var, values=[s.value for s in ApplicationStatus],
                     state="readonly", width=18).grid(row=1, column=1, padx=10)
        ttk.Button(controls, text="Search by Status", command=self._search_by_status).grid(row=1, column=2, padx=10)

        ttk.Label(controls, text="Scholarship type").grid(row=2, column=0, sticky="w", padx=10, pady=8)
        self.type_var = tk.StringVar(value=ScholarshipType.ACADEMIC_MERIT.value)
        ttk.Combobox(controls, textvariable=self.type_var, values=[t.value for t in ScholarshipType],
                     state="readonly", width=18).grid(row=2, column=1, padx=10)
        ttk.Button(controls, text="Search by Type", command=self._search_by_type).grid(row=2, column=2, padx=10)

        ttk.Label(controls, text="GWA range").grid(row=3, column=0, sticky="w", padx=10, pady=8)
        self.min_gwa_var = tk.StringVar(value="1.0")
        self.max_gwa_var = tk.StringVar(value="5.0")
        gwa_frame = ttk.Frame(controls)
        gwa_frame.grid(row=3, column=1, padx=10)
        ttk.Entry(gwa_frame, textvariable=self.min_gwa_var, width=8).pack(side="left")
        ttk.Label(gwa_frame, text=" to ").pack(side="left")
        ttk.Entry(gwa_frame, textvariable=self.max_gwa_var, width=8).pack(side="left")
        ttk.Button(controls, text="Search by GWA", command=self._search_by_gwa).grid(row=3, column=2, padx=10)

        ttk.Button(controls, text="Show All", command=self._show_all).grid(
            row=4, column=2, padx=10, pady=(8, 10), sticky="e"
        )

    def _build_results(self):
        results_frame = ttk.LabelFrame(self.content, text="Results")
        results_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        columns = ("id", "applicant", "program", "status", "gwa")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=12)
        for col, label, width in [
            ("id", "Application ID", 100), ("applicant", "Applicant", 220),
            ("program", "Program", 260), ("status", "Status", 220), ("gwa", "GWA", 70),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        zebra_tags(self.tree)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def _populate(self, results):
        self.tree.delete(*self.tree.get_children())
        for i, a in enumerate(results):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(
                a.application_id, a.applicant.full_name(), a.program.grant_name,
                a.status.value, a.academic_background.gwa,
            ), tags=(tag,))

    def _search_by_name(self):
        self._populate(search_by_name(self.store, self.name_var.get()))

    def _search_by_status(self):
        self._populate(search_by_status(self.store, ApplicationStatus(self.status_var.get())))

    def _search_by_type(self):
        self._populate(search_by_scholarship_type(self.store, ScholarshipType(self.type_var.get())))

    def _search_by_gwa(self):
        try:
            min_gwa = float(self.min_gwa_var.get())
            max_gwa = float(self.max_gwa_var.get())
        except ValueError:
            messagebox.showerror("Invalid input", "GWA range must be numeric.")
            return
        self._populate(search_by_gwa_range(self.store, min_gwa, max_gwa))

    def _show_all(self):
        self._populate(self.store.list_applications())


if __name__ == "__main__":
    app = ScholarshipApp()
    app.mainloop()