import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import yaml
from PIL import Image, ImageTk

# Load configuration from YAML file
with open("resources/config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

# Extract configuration variables
WINDOW_WIDTH = config["window"]["width"]
WINDOW_HEIGHT = config["window"]["height"]
WINDOW_SIZE = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"

FONT = tuple(config["fonts"]["default"])
FONT_BOLD = tuple(config["fonts"]["bold"])
COLOR1 = config["colors"]["background"]
COLOR2 = config["colors"]["text"]
COLOR3 = config["colors"]["highlight"]
BARBELL_TYPES = config["barbell_types"]
IMAGE_ROUNDING = config["image"]["rounding"]
THEME_PATH = config["paths"]["theme"]
DEFAULT_PADDING = config["padding"]["default"]
DEFAULT_BUTTON_PADDING = config["padding"]["button"]

# Extract application metadata
APP_TITLE = config["app"]["title"]
APP_AUTHOR = config["app"]["author"]
APP_GITHUB_REPO = config["app"]["github_repo"]
APP_ICON_PATH = config["app"]["icon_path"]
APP_DESCRIPTION = config["app"]["description"]

class BarbellCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.iconbitmap(APP_ICON_PATH)
        self.geometry(WINDOW_SIZE)
        self.resizable(True, True)

        self.configure(bg=COLOR1)
        self.setup_header()
        self.setup_main_frame()
        self.setup_theme_controls()
        self.set_default_theme()

        self.exit_button = ttk.Button(self.frame, text="Exit", command=self.close_program, style="TButton")
        self.exit_button.grid(row=9, column=0, columnspan=3, pady=DEFAULT_PADDING * 2)

        self.bind("<Escape>", lambda event: self.close_program())

    def setup_header(self):
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(side=tk.TOP, fill=tk.X, pady=DEFAULT_PADDING)

        self.header_separator = ttk.Separator(self.header_frame, orient=tk.HORIZONTAL)
        self.header_separator.pack(side=tk.BOTTOM, fill=tk.X)

        self.author_label = ttk.Label(
            self.header_frame, 
            text=f"Author: {APP_AUTHOR}", 
            font=(FONT[0], 10), 
            background=COLOR1, 
            foreground=COLOR2
        )
        self.author_label.pack(side=tk.LEFT, padx=DEFAULT_PADDING)

        self.github_link = ttk.Label(
            self.header_frame, 
            text="GitHub Repository", 
            font=(FONT[0], 10, "underline"), 
            foreground="blue", 
            cursor="hand2", 
            background=COLOR1
        )
        self.github_link.pack(side=tk.RIGHT, padx=DEFAULT_PADDING)
        self.github_link.bind("<Button-1>", lambda e: self.open_github())

        self.message_label = ttk.Label(self, text="", font=(FONT[0], 12, "bold"), foreground="red", background=COLOR1)
        self.message_label.pack(pady=(DEFAULT_PADDING, 0))

    def setup_main_frame(self):
        self.frame = ttk.Frame(self, style="TFrame")
        self.frame.pack(pady=DEFAULT_PADDING * 4)

        first_barbell_type = list(BARBELL_TYPES.keys())[0]
        self.current_weight_lb, self.current_weight_kg = BARBELL_TYPES[first_barbell_type]
        self.current_weight_label = ttk.Label(
            self.frame, 
            text=f"{self.current_weight_lb} lbs / {self.current_weight_kg} kg", 
            font=(FONT[0], 16, "bold"),
            background=COLOR1, 
            foreground=COLOR2
        )
        self.current_weight_label.grid(row=2, column=1, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, sticky="n")

        self.conversion_label = ttk.Label(
            self.frame, 
            text="(Conversions: 3 st)", 
            font=FONT, 
            background=COLOR1, 
            foreground=COLOR2
        )
        self.conversion_label.grid(row=3, column=1, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, sticky="n")

        self.setup_weight_controls()
        self.setup_rounding_controls()
        self.setup_buttons()

    def setup_weight_controls(self):
        self.weight_unit_frame = ttk.LabelFrame(self.frame, text="Weight Units", padding=DEFAULT_PADDING)
        self.weight_unit_frame.grid(row=2, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, sticky="n")

        self.weight_unit_var = tk.StringVar(value="Pounds")
        self.kg_radio = ttk.Radiobutton(self.weight_unit_frame, text="Kgs", variable=self.weight_unit_var, value="Kilograms", command=self.update_weight_buttons)
        self.kg_radio.grid(row=0, column=0, padx=DEFAULT_PADDING // 2, pady=DEFAULT_PADDING // 2, sticky="n")

        self.lb_radio = ttk.Radiobutton(self.weight_unit_frame, text="Lbs", variable=self.weight_unit_var, value="Pounds", command=self.update_weight_buttons)
        self.lb_radio.grid(row=0, column=1, padx=DEFAULT_PADDING // 2, pady=DEFAULT_PADDING // 2, sticky="n")

        self.st_radio = ttk.Radiobutton(self.weight_unit_frame, text="St", variable=self.weight_unit_var, value="Stone", command=self.update_weight_buttons)
        self.st_radio.grid(row=0, column=2, padx=DEFAULT_PADDING // 2, pady=DEFAULT_PADDING // 2, sticky="n")

    def setup_rounding_controls(self):
        self.rounding_frame = ttk.LabelFrame(self.frame, text="Rounding Options", padding=DEFAULT_PADDING)
        self.rounding_frame.grid(row=2, column=2, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, sticky="n")

        self.rounding_var = tk.BooleanVar(value=False)
        self.rounding_checkbox = ttk.Checkbutton(
            self.rounding_frame, 
            text="Enable Rounding to 2.5", 
            variable=self.rounding_var, 
            command=self.update_weight
        )
        self.rounding_checkbox.pack(padx=DEFAULT_PADDING // 2, pady=DEFAULT_PADDING // 2)

    def setup_buttons(self):
        self.add_buttons_frame = ttk.Frame(self.frame)
        self.add_buttons_frame.grid(row=5, column=0, columnspan=3, pady=(DEFAULT_PADDING, DEFAULT_BUTTON_PADDING))

        self.subtract_buttons_frame = ttk.Frame(self.frame)
        self.subtract_buttons_frame.grid(row=6, column=0, columnspan=3, pady=(DEFAULT_BUTTON_PADDING, DEFAULT_PADDING))

        self.update_weight_buttons()

    def setup_theme_controls(self):
        self.example_image_label = ttk.Label(self.frame, background=COLOR1)
        self.example_image_label.grid(row=8, column=0, columnspan=3, pady=DEFAULT_PADDING * 2, sticky="n")

        self.theme_var = tk.StringVar(value="")

        self.theme_frame = ttk.LabelFrame(self.frame, text="Themes", padding=DEFAULT_PADDING)
        self.theme_frame.grid(row=7, column=0, columnspan=3, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, sticky="n")

        self.theme_radio_frame = ttk.Frame(self.theme_frame)
        self.theme_radio_frame.pack(padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)

        themes = self.get_theme_folders()
        self.lb_themes = [theme for theme in themes if theme.startswith("lb_")]
        self.kg_themes = [theme for theme in themes if theme.startswith("kg_")]
        self.other_themes = [theme for theme in themes if not (theme.startswith("lb_") or theme.startswith("kg_"))]

        self.theme_list_frame = ttk.LabelFrame(self.theme_radio_frame, text="Themes", padding=DEFAULT_PADDING)
        self.theme_filter_frame = ttk.LabelFrame(self.theme_radio_frame, text="Filter Themes", padding=DEFAULT_PADDING)

        self.theme_filter_frame.grid(row=0, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, sticky="n")
        self.theme_list_frame.grid(row=0, column=1, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, sticky="n")

        self.enlarge_button = ttk.Button(self.theme_filter_frame, text="Enlarge Image", command=self.open_image_in_window)
        self.enlarge_button.grid(row=4, column=0, padx=DEFAULT_PADDING // 2, pady=DEFAULT_PADDING // 2, sticky="w")

        self.theme_filter_entry = ttk.Entry(self.theme_list_frame)
        self.theme_filter_entry.pack(fill=tk.X, padx=DEFAULT_PADDING, pady=(0, DEFAULT_PADDING))
        self.theme_filter_entry.bind("<KeyRelease>", lambda event: self.filter_themes(self.theme_listbox, self.all_themes, self.theme_filter_entry, ""))

        self.theme_listbox = tk.Listbox(self.theme_list_frame, height=4, exportselection=False)
        self.theme_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.theme_listbox.config(selectbackground="darkred", highlightthickness=1)
        theme_scrollbar = ttk.Scrollbar(self.theme_list_frame, orient=tk.VERTICAL, command=self.theme_listbox.yview)
        theme_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.theme_listbox.config(yscrollcommand=theme_scrollbar.set)

        self.all_themes = self.lb_themes + self.kg_themes + self.other_themes
        for theme in self.all_themes:
            self.theme_listbox.insert(tk.END, theme)
        self.theme_listbox.bind("<<ListboxSelect>>", lambda event: self.on_theme_change_from_listbox(self.theme_listbox, ""))

        self.theme_filter_var = tk.StringVar(value="All")

        self.all_radio = ttk.Radiobutton(self.theme_filter_frame, text="All", variable=self.theme_filter_var, value="All", command=self.filter_themes_by_prefix)
        self.all_radio.grid(row=0, column=0, padx=DEFAULT_PADDING // 2, pady=DEFAULT_PADDING // 2, sticky="w")

        self.kg_radio = ttk.Radiobutton(self.theme_filter_frame, text="Kgs", variable=self.theme_filter_var, value="kg_", command=self.filter_themes_by_prefix)
        self.kg_radio.grid(row=1, column=0, padx=DEFAULT_PADDING // 2, pady=DEFAULT_PADDING // 2, sticky="w")

        self.lb_radio = ttk.Radiobutton(self.theme_filter_frame, text="Lbs", variable=self.theme_filter_var, value="lb_", command=self.filter_themes_by_prefix)
        self.lb_radio.grid(row=2, column=0, padx=DEFAULT_PADDING // 2, pady=DEFAULT_PADDING // 2, sticky="w")

        self.other_radio = ttk.Radiobutton(self.theme_filter_frame, text="Other", variable=self.theme_filter_var, value="Other", command=self.filter_themes_by_prefix)
        self.other_radio.grid(row=3, column=0, padx=DEFAULT_PADDING // 2, pady=DEFAULT_PADDING // 2, sticky="w")

    def open_image_in_window(self):
        if hasattr(self.example_image_label, "image") and self.example_image_label.image:
            top = tk.Toplevel(self)
            top.title("Enlarged Image")
            top.configure(bg=COLOR1)

            # Scale the image to 3x its size
            original_image = self.example_image_label.image._PhotoImage__photo.zoom(3, 3)

            enlarged_image_label = ttk.Label(top)
            enlarged_image_label.pack(expand=True)

            enlarged_image_label.config(image=original_image)
            enlarged_image_label.image = original_image
        else:
            self.display_message("No image available to enlarge.")

    def open_github(self):
        import webbrowser
        webbrowser.open(APP_GITHUB_REPO)

    def display_message(self, message):
        if message:
            self.message_label.config(text=message)
            self.message_label.pack_configure(pady=(DEFAULT_PADDING, 0))
        else:
            self.message_label.config(text="")
            self.message_label.pack_configure(pady=0)

    def get_theme_folders(self):
        base_path = os.path.dirname(__file__)
        theme_path = os.path.join(base_path, THEME_PATH)
        if os.path.exists(theme_path):
            return [folder for folder in os.listdir(theme_path) if os.path.isdir(os.path.join(theme_path, folder))]
        else:
            self.display_message(f"{THEME_PATH} folder not found.")
            return []

    def on_theme_change(self):
        selected_theme = self.theme_var.get()
        base_path = os.path.dirname(__file__)
        theme_path = os.path.abspath(os.path.join(base_path, THEME_PATH, selected_theme, f"{int(self.current_weight_lb)}.png"))
        if not os.path.exists(theme_path):
            self.display_message(f"Theme image not found for {selected_theme}.")
        self.update_example_image(theme_path)

    def on_theme_change_from_listbox(self, listbox, prefix):
        selected_index = listbox.curselection()
        if selected_index:
            selected_theme = listbox.get(selected_index[0])
            self.theme_var.set(selected_theme)
            self.on_theme_change()

    def set_default_theme(self):
        if self.all_themes:
            self.theme_listbox.selection_set(0)
            self.on_theme_change_from_listbox(self.theme_listbox, "")

    def update_barbell_weight(self, event):
        barbell_type = self.barbell_type_var.get()
        if barbell_type in BARBELL_TYPES:
            self.current_weight_lb, self.current_weight_kg = BARBELL_TYPES[barbell_type]
            self.update_weight()
        else:
            self.display_message("Error: Invalid barbell type selected.")
            self.current_weight_lb, self.current_weight_kg = BARBELL_TYPES["Standard"]
            self.update_weight()

    def update_weight_buttons(self):
        for widget in self.add_buttons_frame.winfo_children():
            widget.destroy()
        for widget in self.subtract_buttons_frame.winfo_children():
            widget.destroy()

        unit = self.weight_unit_var.get()
        if unit == "Pounds":
            increments = [1.75, 2.5, 5, 10, 25, 35, 45, 55]
        elif unit == "Kilograms":
            increments = [1, 2.5, 5, 10, 15, 20, 25]
        else:
            increments = []

        for increment in increments:
            button = ttk.Button(self.add_buttons_frame, text=f"+{increment}", command=lambda inc=increment: self.adjust_weight(inc))
            button.pack(side=tk.LEFT, padx=DEFAULT_BUTTON_PADDING)

        for increment in increments:
            button = ttk.Button(self.subtract_buttons_frame, text=f"-{increment}", command=lambda inc=increment: self.adjust_weight(-inc))
            button.pack(side=tk.LEFT, padx=DEFAULT_BUTTON_PADDING)

    def adjust_weight(self, amount):
        self.display_message("")
        unit = self.weight_unit_var.get()
        selected_theme = self.theme_var.get().lower()
        is_dumbbell_theme = "dumbell" in selected_theme or "dumbbell" in selected_theme

        if is_dumbbell_theme:
            self.rounding_var.set(True)

        effective_amount = amount if is_dumbbell_theme else amount * 2

        min_weight = 5 if is_dumbbell_theme else 45
        max_weight = 120 if is_dumbbell_theme else (900 if unit == "Pounds" else 855)

        if unit == "Pounds":
            self.current_weight_lb = round(self.current_weight_lb + effective_amount)
            if self.current_weight_lb < min_weight:
                self.current_weight_lb = min_weight
            elif self.current_weight_lb > max_weight:
                self.current_weight_lb = max_weight
            self.current_weight_kg = self.current_weight_lb / 2.20462
        elif unit == "Kilograms":
            self.current_weight_kg = round(self.current_weight_kg + effective_amount)
            self.current_weight_lb = self.current_weight_kg * 2.20462
            if self.current_weight_lb < min_weight:
                self.current_weight_lb = min_weight
                self.current_weight_kg = self.current_weight_lb / 2.20462
            elif self.current_weight_lb > max_weight:
                self.current_weight_lb = max_weight
                self.current_weight_kg = self.current_weight_lb / 2.20462
        self.update_weight()
        self.update_theme_photo(self.current_weight_lb)

    def update_theme_photo(self, weight_number):
        self.display_message("")
        rounded_weight = round(weight_number / (2.5 if self.rounding_var.get() else IMAGE_ROUNDING)) * (2.5 if self.rounding_var.get() else IMAGE_ROUNDING)
        rounded_weight_str = f"{int(rounded_weight)}" if rounded_weight.is_integer() else f"{rounded_weight:.1f}"
        selected_theme = self.theme_var.get()
        base_path = os.path.dirname(__file__)
        theme_folder = os.path.join(base_path, THEME_PATH, selected_theme)
        if os.path.exists(theme_folder):
            image_path = os.path.join(theme_folder, f"{rounded_weight_str}.png")
            if os.path.exists(image_path):
                self.update_example_image(image_path)
            else:
                fallback_image_path = os.path.join(theme_folder, "none.png")
                if os.path.exists(fallback_image_path):
                    self.update_example_image(fallback_image_path)
                else:
                    self.display_message(f"Image {rounded_weight_str}.png and fallback none.png not found in the selected theme folder.")
        else:
            self.display_message(f"Selected theme folder does not exist: {theme_folder}")

    def update_weight(self):
        self.display_message("")
        rounded_weight_lb = round(self.current_weight_lb / (2.5 if self.rounding_var.get() else IMAGE_ROUNDING)) * (2.5 if self.rounding_var.get() else IMAGE_ROUNDING)
        rounded_weight_kg = round(self.current_weight_kg / (2.5 if self.rounding_var.get() else IMAGE_ROUNDING)) * (2.5 if self.rounding_var.get() else IMAGE_ROUNDING)
        self.current_weight_label.config(
            text=f"{rounded_weight_lb:.1f} lbs / {rounded_weight_kg:.1f} kg"
        )
        self.calculate_weight()
        rounded_weight_str = f"{int(rounded_weight_lb)}" if rounded_weight_lb.is_integer() else f"{rounded_weight_lb:.1f}"
        self.update_example_image(f"{rounded_weight_str}.png")

    def calculate_weight(self):
        try:
            self.update_conversions(self.current_weight_kg)
        except Exception as e:
            self.display_message(f"An error occurred: {str(e)}")

    def update_conversions(self, weight_in_kg):
        stone = round(weight_in_kg / 6.35029)
        self.conversion_label.config(text=f"(Conversions: {stone} st)")

    def update_example_image(self, image_name):
        if os.path.exists(image_name):
            image = Image.open(image_name)
            image = image.resize((100, 100))

            inverted_image = image.transpose(Image.FLIP_LEFT_RIGHT)

            selected_theme = self.theme_var.get()
            base_path = os.path.dirname(__file__)
            static_image_path = os.path.join(base_path, THEME_PATH, selected_theme, "bar.png")
            if os.path.exists(static_image_path):
                static_image = Image.open(static_image_path)
                static_image = static_image.resize((150, 100))
            else:
                static_image = Image.new("RGBA", (0, 0), (255, 255, 255, 0))

            combined_width = image.width * 2 + static_image.width
            combined_image = Image.new("RGBA", (combined_width, image.height))
            combined_image.paste(image, (0, 0))
            combined_image.paste(static_image, (image.width, 0))
            combined_image.paste(inverted_image, (image.width + static_image.width, 0))

            photo = ImageTk.PhotoImage(combined_image)
            self.example_image_label.config(image=photo)
            self.example_image_label.image = photo
        else:
            selected_theme = self.theme_var.get()
            base_path = os.path.dirname(__file__)
            fallback_image_path = os.path.join(base_path, THEME_PATH, selected_theme, "none.png")
            if os.path.exists(fallback_image_path):
                fallback_image = Image.open(fallback_image_path)
                fallback_image = fallback_image.resize((100, 100))
                photo = ImageTk.PhotoImage(fallback_image)
                self.example_image_label.config(image=photo)
                self.example_image_label.image = photo
            else:
                self.example_image_label.config(image=None)
                self.example_image_label.image = None

    def filter_themes(self, listbox, themes, entry, prefix):
        filter_text = entry.get().lower()
        listbox.delete(0, tk.END)
        for theme in themes:
            if filter_text in theme.lower():
                listbox.insert(tk.END, theme)

    def filter_themes_by_prefix(self):
        prefix = self.theme_filter_var.get()
        if prefix == "All":
            filtered_themes = self.all_themes
        elif prefix == "Other":
            filtered_themes = self.other_themes
        else:
            filtered_themes = [theme for theme in self.all_themes if theme.startswith(prefix)]
        self.filter_themes(self.theme_listbox, filtered_themes, self.theme_filter_entry, "")

    def close_program(self):
        self.destroy()

if __name__ == "__main__":
    app = BarbellCalculator()
    app.mainloop()
