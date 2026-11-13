
import tkinter as tk
from tkinter import ttk, messagebox
import ast
import operator
import math
import datetime
import calendar
import json
import urllib.request
import threading
import os

# =====================================================
# ADVANCED CALCULATOR - PYTHON TKINTER
# =====================================================

root = tk.Tk()
root.title("Advanced Calculator")
root.geometry("430x820")
root.minsize(400, 700)

DARK = {
    "bg": "#171923",
    "display": "#252A3A",
    "button": "#343B50",
    "text": "#FFFFFF",
    "accent": "#16A085",
    "history": "#B8C7E0"
}

LIGHT = {
    "bg": "#F0F2F5",
    "display": "#FFFFFF",
    "button": "#DCE3EE",
    "text": "#171923",
    "accent": "#16A085",
    "history": "#343B50"
}

theme = "dark"
expression = ""
memory_value = 0.0
history = []
history_file = "calculator_history.json"
all_windows = []

display = tk.StringVar()

# =====================================================
# SAFE SCIENTIFIC MATHEMATICAL EVALUATOR
# =====================================================

operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
}

# Trigonometric functions use degrees.
functions = {
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    "asin": lambda x: math.degrees(math.asin(x)),
    "acos": lambda x: math.degrees(math.acos(x)),
    "atan": lambda x: math.degrees(math.atan(x)),
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "factorial": math.factorial,
    "abs": abs,
    "exp": math.exp
}

constants = {
    "pi": math.pi,
    "e": math.e
}


def calculate(node, depth=0):

    if depth > 50:
        raise ValueError("Expression too complex")

    if isinstance(node, ast.Constant):
        if type(node.value) in (int, float):
            return node.value
        raise ValueError("Invalid number")

    if isinstance(node, ast.Name):
        if node.id in constants:
            return constants[node.id]
        raise ValueError("Unknown constant")

    if isinstance(node, ast.BinOp) and type(node.op) in operators:

        left = calculate(node.left, depth + 1)
        right = calculate(node.right, depth + 1)

        if isinstance(node.op, ast.Pow):
            if abs(right) > 100 or abs(left) > 1e100:
                raise ValueError("Power too large")

        result = operators[type(node.op)](left, right)

        if isinstance(result, complex):
            raise ValueError("Complex numbers not supported")

        if not math.isfinite(result):
            raise ValueError("Invalid result")

        return result

    if isinstance(node, ast.UnaryOp) and type(node.op) in operators:
        return operators[type(node.op)](
            calculate(node.operand, depth + 1)
        )

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Invalid function")

        name = node.func.id

        if name not in functions or node.keywords:
            raise ValueError("Invalid function")

        if len(node.args) != 1:
            raise ValueError("Function needs one argument")

        value = calculate(node.args[0], depth + 1)

        if name == "factorial":
            if value < 0 or not value.is_integer() if isinstance(value, float) else False:
                raise ValueError("Factorial needs a non-negative integer")
            if value > 170:
                raise ValueError("Number too large")

        result = functions[name](value)

        if isinstance(result, complex) or not math.isfinite(result):
            raise ValueError("Invalid result")

        return result

    raise ValueError("Invalid expression")


def safe_evaluate(text):
    if not text.strip():
        raise ValueError("Enter an expression")

    if len(text) > 300:
        raise ValueError("Expression too long")

    tree = ast.parse(text, mode="eval")
    return calculate(tree.body)


def format_result(value):
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


# =====================================================
# HISTORY
# =====================================================

def load_history():

    global history

    try:
        with open(history_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            history = [str(item) for item in data[-500:]]

    except (FileNotFoundError, json.JSONDecodeError, OSError):
        history = []


def save_history():

    try:
        with open(history_file, "w", encoding="utf-8") as file:
            json.dump(history[-500:], file, indent=4)

    except OSError:
        messagebox.showwarning("History", "Could not save history.")


def add_history(item):

    history.append(item)
    history[:] = history[-500:]

    save_history()
    update_history()


def update_history():

    history_box.config(state="normal")
    history_box.delete("1.0", tk.END)

    for item in history[-8:]:
        history_box.insert(tk.END, item + "\n")

    history_box.config(state="disabled")


def show_full_history():

    win = tk.Toplevel(root)
    win.title("Calculation History")
    win.geometry("450x500")
    register_window(win)

    tk.Label(
        win,
        text="CALCULATION HISTORY",
        font=("Arial", 16, "bold"),
        bg=colors()["bg"],
        fg="#61DAFB"
    ).pack(pady=12)

    box = tk.Text(
        win,
        font=("Arial", 12),
        bg=colors()["display"],
        fg=colors()["text"],
        bd=0
    )
    box.pack(fill="both", expand=True, padx=12, pady=10)

    for item in history:
        box.insert(tk.END, item + "\n")

    box.config(state="disabled")

    def clear_history():

        if messagebox.askyesno("History", "Delete all history?"):
            history.clear()
            save_history()
            update_history()
            win.destroy()

    tk.Button(
        win,
        text="Clear History",
        command=clear_history,
        bg="#E74C3C",
        fg="white"
    ).pack(pady=10)


# =====================================================
# MAIN CALCULATOR FUNCTIONS
# =====================================================

def press(value):

    global expression

    if display.get() == "Error":
        expression = ""

    expression += str(value)
    display.set(expression)


def equal():

    global expression

    try:
        old_expression = expression
        result = safe_evaluate(expression)

        expression = format_result(result)
        display.set(expression)

        add_history(f"{old_expression} = {expression}")

    except Exception:
        expression = ""
        display.set("Error")


def clear():

    global expression

    expression = ""
    display.set("")


def backspace():

    global expression

    expression = expression[:-1]
    display.set(expression)


def square():
    press("**2")


def square_root():
    press("sqrt(")


def reciprocal():

    global expression

    expression = f"1/({expression})"
    display.set(expression)


def percentage():

    global expression

    expression += "/100"
    display.set(expression)


def copy_result():

    value = display.get()

    if value and value != "Error":
        root.clipboard_clear()
        root.clipboard_append(value)
        root.update()


def paste_value():

    global expression

    try:
        value = root.clipboard_get()
        if all(c in "0123456789.+-*/()% " for c in value):
            expression += value
            display.set(expression)
    except tk.TclError:
        pass


# =====================================================
# MEMORY FUNCTIONS
# =====================================================

def current_number():

    try:
        return float(safe_evaluate(display.get()))
    except Exception:
        return 0.0


def memory_clear():

    global memory_value

    memory_value = 0.0


def memory_recall():

    global expression

    expression = format_result(memory_value)
    display.set(expression)


def memory_add():

    global memory_value

    memory_value += current_number()


def memory_subtract():

    global memory_value

    memory_value -= current_number()


# =====================================================
# THEME
# =====================================================

def colors():

    return DARK if theme == "dark" else LIGHT


def register_window(win):
    if win not in all_windows:
        all_windows.append(win)


def apply_theme(widget):

    c = colors()

    try:
        if isinstance(widget, tk.Toplevel) or widget == root:
            widget.configure(bg=c["bg"])

        elif isinstance(widget, tk.Label):
            widget.configure(bg=c["bg"], fg=c["text"])

        elif isinstance(widget, tk.Entry):
            widget.configure(
                bg=c["display"],
                fg=c["text"],
                insertbackground=c["text"]
            )

        elif isinstance(widget, tk.Text):
            widget.configure(
                bg=c["display"],
                fg=c["text"]
            )

        elif isinstance(widget, tk.Button):
            if widget not in special_buttons:
                widget.configure(
                    bg=c["button"],
                    fg=c["text"],
                    activeforeground=c["text"]
                )

    except tk.TclError:
        pass

    for child in widget.winfo_children():
        apply_theme(child)


special_buttons = []


def toggle_theme():

    global theme

    theme = "light" if theme == "dark" else "dark"

    apply_theme(root)

    for win in list(all_windows):
        try:
            if win.winfo_exists():
                apply_theme(win)
        except tk.TclError:
            pass


# =====================================================
# COMMON WINDOW DESIGN
# =====================================================

def new_window(title, geometry):

    win = tk.Toplevel(root)
    win.title(title)
    win.geometry(geometry)
    win.configure(bg=colors()["bg"])
    register_window(win)

    return win


def window_title(win, text):

    tk.Label(
        win,
        text=text,
        font=("Arial", 16, "bold"),
        bg=colors()["bg"],
        fg="#61DAFB"
    ).pack(pady=15)


def tool_button(parent, text, command, color="#343B50"):

    btn = tk.Button(
        parent,
        text=text,
        font=("Arial", 12, "bold"),
        bg=color,
        fg="white",
        activebackground="#6474A1",
        activeforeground="white",
        bd=0,
        command=command,
        cursor="hand2"
    )

    btn.pack(fill="x", padx=20, pady=5, ipady=8)

    return btn


# =====================================================
# SCIENTIFIC BUTTONS
# =====================================================

def scientific_input(value):

    press(value)


# =====================================================
# GST CALCULATOR
# =====================================================

def gst_calculator():

    win = new_window("GST Calculator", "380x400")
    window_title(win, "GST CALCULATOR")

    tk.Label(
        win, text="Original Amount",
        bg=colors()["bg"], fg=colors()["text"]
    ).pack()

    amount = tk.Entry(win, font=("Arial", 13))
    amount.pack(pady=6)

    tk.Label(
        win, text="GST Rate (%)",
        bg=colors()["bg"], fg=colors()["text"]
    ).pack()

    rate = ttk.Combobox(
        win,
        values=["0", "5", "12", "18", "28"],
        state="readonly"
    )
    rate.set("18")
    rate.pack(pady=6)

    result = tk.Label(
        win, text="GST: 0 | Total: 0",
        font=("Arial", 12, "bold"),
        bg=colors()["bg"],
        fg="#2ECC71"
    )
    result.pack(pady=20)

    def calculate_gst():

        try:
            a = float(amount.get())
            r = float(rate.get())

            if a < 0:
                raise ValueError

            gst = a * r / 100
            total = a + gst

            result.config(
                text=f"GST Amount: {gst:.2f}\nTotal Amount: {total:.2f}"
            )

        except ValueError:
            messagebox.showerror("Error", "Enter valid values.")

    tool_button(win, "Calculate GST", calculate_gst, "#16A085")


# =====================================================
# PERCENTAGE CALCULATOR
# =====================================================

def percentage_calculator():

    win = new_window("Percentage Calculator", "380x370")
    window_title(win, "PERCENTAGE CALCULATOR")

    tk.Label(
        win, text="Total Value",
        bg=colors()["bg"], fg=colors()["text"]
    ).pack()

    total = tk.Entry(win, font=("Arial", 13))
    total.pack(pady=6)

    tk.Label(
        win, text="Percentage (%)",
        bg=colors()["bg"], fg=colors()["text"]
    ).pack()

    percent = tk.Entry(win, font=("Arial", 13))
    percent.pack(pady=6)

    output = tk.Label(
        win, text="Result: ",
        font=("Arial", 13, "bold"),
        bg=colors()["bg"], fg="#2ECC71"
    )
    output.pack(pady=20)

    def calculate_percent():

        try:
            a = float(total.get())
            b = float(percent.get())

            result = a * b / 100

            output.config(text=f"Result: {result:g}")

        except ValueError:
            messagebox.showerror("Error", "Enter valid numbers.")

    tool_button(win, "Calculate", calculate_percent, "#16A085")


# =====================================================
# AGE CALCULATOR
# =====================================================

def age_calculator():

    win = new_window("Age Calculator", "400x320")
    window_title(win, "AGE CALCULATOR")

    tk.Label(
        win,
        text="Date of Birth (YYYY-MM-DD)",
        bg=colors()["bg"],
        fg=colors()["text"]
    ).pack()

    dob = tk.Entry(win, font=("Arial", 13), justify="center")
    dob.pack(pady=12)

    output = tk.Label(
        win, text="Your Age:",
        font=("Arial", 12, "bold"),
        bg=colors()["bg"],
        fg="#2ECC71"
    )
    output.pack(pady=15)

    def calculate_age():

        try:
            birth = datetime.date.fromisoformat(dob.get())
            today = datetime.date.today()

            if birth > today:
                raise ValueError

            years = today.year - birth.year
            months = today.month - birth.month
            days = today.day - birth.day

            if days < 0:
                months -= 1
                previous_month = today.month - 1 or 12
                previous_year = today.year if today.month > 1 else today.year - 1

                days += calendar.monthrange(
                    previous_year, previous_month
                )[1]

            if months < 0:
                years -= 1
                months += 12

            output.config(
                text=f"{years} Years, {months} Months, {days} Days"
            )

        except ValueError:
            messagebox.showerror(
                "Error",
                "Enter a valid past date in YYYY-MM-DD format."
            )

    tool_button(win, "Calculate Age", calculate_age, "#16A085")


# =====================================================
# UNIT CONVERTER
# =====================================================

def unit_converter():

    win = new_window("Unit Converter", "400x480")
    window_title(win, "UNIT CONVERTER")

    units = {
        "Length": {
            "Meter": 1,
            "Kilometer": 1000,
            "Centimeter": 0.01,
            "Millimeter": 0.001,
            "Mile": 1609.344,
            "Foot": 0.3048,
            "Inch": 0.0254
        },
        "Weight": {
            "Kilogram": 1,
            "Gram": 0.001,
            "Milligram": 0.000001,
            "Pound": 0.45359237,
            "Ounce": 0.0283495,
            "Tonne": 1000
        },
        "Temperature": {
            "Celsius": 1,
            "Fahrenheit": 1,
            "Kelvin": 1
        }
    }

    category = tk.StringVar(value="Length")
    source = tk.StringVar(value="Meter")
    target = tk.StringVar(value="Kilometer")

    def add_combo(label, variable, values):

        tk.Label(
            win, text=label,
            bg=colors()["bg"], fg=colors()["text"]
        ).pack()

        combo = ttk.Combobox(
            win,
            textvariable=variable,
            values=values,
            state="readonly"
        )
        combo.pack(pady=7)

        return combo

    category_combo = add_combo(
        "Category", category, list(units.keys())
    )

    source_combo = add_combo(
        "From Unit", source, list(units["Length"].keys())
    )

    target_combo = add_combo(
        "To Unit", target, list(units["Length"].keys())
    )

    tk.Label(
        win, text="Enter Value",
        bg=colors()["bg"], fg=colors()["text"]
    ).pack()

    value = tk.Entry(win, font=("Arial", 13))
    value.pack(pady=8)

    output = tk.Label(
        win, text="Result:",
        bg=colors()["bg"],
        fg="#2ECC71",
        font=("Arial", 12, "bold")
    )
    output.pack(pady=15)

    def update_units(event=None):

        available = list(units[category.get()].keys())

        source_combo["values"] = available
        target_combo["values"] = available

        source.set(available[0])
        target.set(available[1] if len(available) > 1 else available[0])

    def convert():

        try:
            number = float(value.get())
            a = source.get()
            b = target.get()

            if category.get() == "Temperature":

                if a == "Celsius":
                    c = number
                elif a == "Fahrenheit":
                    c = (number - 32) * 5 / 9
                else:
                    c = number - 273.15

                if b == "Celsius":
                    answer = c
                elif b == "Fahrenheit":
                    answer = c * 9 / 5 + 32
                else:
                    answer = c + 273.15

            else:
                answer = (
                    number * units[category.get()][a]
                    / units[category.get()][b]
                )

            output.config(text=f"Result: {answer:.8g} {b}")

        except (ValueError, ZeroDivisionError):
            messagebox.showerror("Error", "Enter a valid number.")

    category_combo.bind("<<ComboboxSelected>>", update_units)

    tool_button(win, "Convert", convert, "#16A085")


# =====================================================
# LIVE CURRENCY CONVERTER
# =====================================================

def currency_converter():

    win = new_window("Currency Converter", "400x430")
    window_title(win, "CURRENCY CONVERTER")

    tk.Label(
        win, text="Amount",
        bg=colors()["bg"], fg=colors()["text"]
    ).pack()

    amount = tk.Entry(win, font=("Arial", 13))
    amount.pack(pady=7)

    tk.Label(
        win, text="From Currency (USD, INR, EUR)",
        bg=colors()["bg"], fg=colors()["text"]
    ).pack()

    source = tk.Entry(win, font=("Arial", 13))
    source.insert(0, "USD")
    source.pack(pady=7)

    tk.Label(
        win, text="To Currency",
        bg=colors()["bg"], fg=colors()["text"]
    ).pack()

    target = tk.Entry(win, font=("Arial", 13))
    target.insert(0, "INR")
    target.pack(pady=7)

    output = tk.Label(
        win, text="Converted Amount:",
        bg=colors()["bg"],
        fg="#2ECC71",
        font=("Arial", 12, "bold")
    )
    output.pack(pady=15)

    def convert():

        try:
            number = float(amount.get())
            src = source.get().strip().upper()
            dst = target.get().strip().upper()

            if number <= 0:
                raise ValueError("Amount must be positive.")

            if len(src) != 3 or not src.isalpha():
                raise ValueError("Invalid source currency.")

            if len(dst) != 3 or not dst.isalpha():
                raise ValueError("Invalid target currency.")

        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        convert_button.config(state="disabled")
        output.config(text="Converting...")

        def worker():

            try:
                url = (
                    f"https://api.frankfurter.app/latest"
                    f"?amount={number}&from={src}&to={dst}"
                )

                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": "AdvancedCalculator/1.0"}
                )

                with urllib.request.urlopen(
                    request, timeout=12
                ) as response:
                    data = json.loads(response.read().decode())

                result = data["rates"][dst]

                win.after(
                    0,
                    lambda: output.config(
                        text=f"{number:g} {src} = {result:.4f} {dst}"
                    )
                )

            except Exception:
                win.after(
                    0,
                    lambda: output.config(
                        text="Conversion failed. Check internet/code."
                    )
                )

            finally:
                win.after(
                    0,
                    lambda: convert_button.config(state="normal")
                )

        threading.Thread(target=worker, daemon=True).start()

    convert_button = tool_button(
        win, "Convert Currency", convert, "#16A085"
    )


# =====================================================
# SECOND WINDOW - ALL ADDITIONAL TOOLS
# =====================================================

def open_tools_window():

    win = new_window("Calculator Tools", "400x690")
    window_title(win, "ADVANCED CALCULATOR TOOLS")

    tool_button(win, "1. GST Calculator", gst_calculator, "#2874A6")
    tool_button(win, "2. Unit Converter", unit_converter, "#2874A6")
    tool_button(win, "3. Percentage Calculator", percentage_calculator, "#8E44AD")
    tool_button(win, "4. Age Calculator", age_calculator, "#16A085")
    tool_button(win, "5. Currency Converter", currency_converter, "#2874A6")
    tool_button(win, "6. Dark / Light Mode", toggle_theme, "#596780")
    tool_button(win, "7. Memory Clear (MC)", memory_clear)
    tool_button(win, "8. Memory Recall (MR)", memory_recall)
    tool_button(win, "9. Memory Add (M+)", memory_add)
    tool_button(win, "10. Memory Subtract (M-)", memory_subtract)
    tool_button(win, "11. Copy Result", copy_result, "#16A085")
    tool_button(win, "12. Full Calculation History", show_full_history, "#8E44AD")


# =====================================================
# MAIN WINDOW DESIGN
# =====================================================

root.configure(bg=DARK["bg"])

entry = tk.Entry(
    root,
    textvariable=display,
    font=("Arial", 25, "bold"),
    bg=DARK["display"],
    fg="white",
    insertbackground="white",
    justify="right",
    bd=0
)

entry.grid(
    row=0,
    column=0,
    columnspan=5,
    padx=12,
    pady=15,
    ipady=20,
    sticky="nsew"
)


def create_button(text, row, col, color, command=None):

    if command is None:
        command = lambda x=text: press(x)

    btn = tk.Button(
        root,
        text=text,
        font=("Arial", 12, "bold"),
        bg=color,
        fg="white",
        activebackground="#6474A1",
        activeforeground="white",
        bd=0,
        relief="flat",
        command=command,
        cursor="hand2"
    )

    btn.grid(
        row=row,
        column=col,
        padx=4,
        pady=4,
        ipadx=2,
        ipady=12,
        sticky="nsew"
    )

    return btn


# =====================================================
# SCIENTIFIC AND BASIC BUTTONS
# =====================================================

buttons = [
    ("sin", "sin(", "#0EC70E"),
    ("cos", "cos(", "#0EC70E"),
    ("tan", "tan(", "#0EC70E"),
    ("log", "log(", "#0EC70E"),
    ("ln", "ln(", "#0EC70E"),

    ("C", None, "#E74C3C"),
    ("⌫", None, "#E67E22"),
    ("(", "(", "#596780"),
    (")", ")", "#596780"),
    ("√", "sqrt(", "#8E44AD"),

    ("7", "7", "#343B50"),
    ("8", "8", "#343B50"),
    ("9", "9", "#343B50"),
    ("/", "/", "#2874A6"),
    ("x²", "**2", "#8E44AD"),

    ("4", "4", "#343B50"),
    ("5", "5", "#343B50"),
    ("6", "6", "#343B50"),
    ("*", "*", "#2874A6"),
    ("1/x", None, "#8E44AD"),

    ("1", "1", "#343B50"),
    ("2", "2", "#343B50"),
    ("3", "3", "#343B50"),
    ("-", "-", "#2874A6"),
    ("π", "pi", "#8E44AD"),

    ("0", "0", "#343B50"),
    (".", ".", "#343B50"),
    ("%", None, "#8E44AD"),
    ("+", "+", "#2874A6"),
    ("e", "e", "#8E44AD"),

    ("^", "**", "#8E44AD"),
    ("!", None, "#8E44AD"),
    ("=", None, "#3416A0"),
    ("TOOLS", None, "#8E44AD"),
    ("HISTORY", None, "#596780")
]

for index, (label, value, color) in enumerate(buttons):

    row = 1 + index // 5
    col = index % 5

    command = None

    if label == "C":
        command = clear
    elif label == "⌫":
        command = backspace
    elif label == "=":
        command = equal
    elif label == "TOOLS":
        command = open_tools_window
    elif label == "HISTORY":
        command = show_full_history
    elif label == "1/x":
        command = reciprocal
    elif label == "%":
        command = percentage
    elif label == "!":
        command = lambda: press("factorial(")
    else:
        command = lambda v=value: press(v)

    create_button(label, row, col, color, command)


# =====================================================
# MEMORY AND QUICK ACTION BUTTONS
# =====================================================

quick_buttons = [
    ("MC", memory_clear),
    ("MR", memory_recall),
    ("M+", memory_add),
    ("M-", memory_subtract),
    ("COPY", copy_result)
]

for col, (label, command) in enumerate(quick_buttons):

    create_button(
        label,
        9,
        col,
        "#596780",
        command
    )


# =====================================================
# HISTORY DISPLAY
# =====================================================

tk.Label(
    root,
    text="CALCULATION HISTORY",
    font=("Arial", 11, "bold"),
    bg="#171923",
    fg="#61DAFB"
).grid(
    row=10,
    column=0,
    columnspan=5,
    pady=7
)

history_box = tk.Text(
    root,
    height=5,
    bg="#252A3A",
    fg="#B8C7E0",
    font=("Arial", 10),
    bd=0,
    state="disabled"
)

history_box.grid(
    row=11,
    column=0,
    columnspan=5,
    padx=12,
    pady=5,
    sticky="nsew"
)

load_history()
update_history()


# =====================================================
# KEYBOARD SUPPORT
# =====================================================

def keyboard(event):

    if event.keysym == "Return":
        equal()
        return "break"

    elif event.keysym == "BackSpace":
        backspace()
        return "break"

    elif event.keysym == "Escape":
        clear()
        return "break"

    elif event.keysym == "c" and event.state & 0x4:
        copy_result()
        return "break"

    elif event.keysym == "v" and event.state & 0x4:
        paste_value()
        return "break"

    elif event.char in "0123456789+-*/().%":
        press(event.char)
        return "break"


root.bind("<Key>", keyboard)

# =====================================================
# GRID SETTINGS
# =====================================================

for i in range(5):
    root.grid_columnconfigure(i, weight=1)

root.mainloop()

