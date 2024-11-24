import tkinter as tk
from tkinter import Menu, filedialog, messagebox
from PIL import Image, ImageTk


class Scion(tk.Tk):
    img_current: Image.Image = None
    img_temp: Image.Image = None
    coord_x: int = 0
    coord_y: int = 0

    def __init__(self):
        super().__init__()

        self.title("Image Editor")
        self.geometry("1200x800")
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)

        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        self.file_menu.add_command(label="Open", command=self.open_image)
        self.file_menu.add_command(label="Exit", command=self.quit)
        self.edit_menu.add_command(label="Resize", command=self.open_resize_window)
        self.edit_menu.add_command(label="Change transparency", command=self.open_tpc_window)
        self.edit_menu.add_command(label="Paste image", command=self.open_paste_image_window)

        # Label to display label_current coordinates
        self.coords_label = tk.Label(self, text="Left click to see coordinates", font=("Helvetica", 14))
        self.coords_label.pack(side="top", padx=0, pady=0)
        # Button to save temporary image to current image
        self.frame_bottom = tk.Frame(self)
        self.frame_bottom.pack(side="bottom", fill="x", ipady=10)
        self.button_apply = tk.Button(self.frame_bottom, text="Apply", command=self.apply_button_click)
        self.button_apply.pack(side="right")
        self.button_restore = tk.Button(self.frame_bottom, text="Restore", command=self.restore_button_click)
        self.button_restore.pack(side="right")

        # Frame for image currently editing
        self.frame_current = tk.Frame(self, width=600, height=600, bg="white")
        self.frame_current.pack(side="left", fill="both", expand=True)
        self.label_current = tk.Label(self.frame_current, bg="white")
        self.label_current.place(x=10, y=50)
        self.label_current.bind("<Button-1>", lambda event: self.click_coords(event))

        # Frame to preview image before saving
        self.frame_temp = tk.Frame(self, width=600, height=600, bg="white")
        self.frame_temp.pack(side="right", fill="both", expand=True)
        self.label_temp = tk.Label(self.frame_temp, bg="white")
        self.label_temp.place(x=10, y=50)

    def open_image(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
        if file_path:
            Scion.img_current = Image.open(file_path)
            print(f">Image opened, mode: {Scion.img_current.mode}, size: {Scion.img_current.size}")
            if Scion.img_current.mode == 'RGB':
                Scion.img_current = Scion.img_current.convert('RGBA')
                print(">Added an alpha channel.")
            if Scion.img_current.size > (600, 600):
                Scion.img_current.thumbnail((600, 600), Image.Resampling.LANCZOS)
                print(f">Resized to {Scion.img_current.size}")

            Scion.img_temp = Scion.img_current.copy()
            self.display_image(Scion.img_current, self.label_current)
            self.display_image(Scion.img_temp, self.label_temp)
        else:
            print("Error: cannot open image file")

    def click_coords(self, event: tk.Event) -> None:
        coord_x, coord_y = event.x, event.y
        self.coords_label.config(text=f"Clicked at coordinates {coord_x} : {coord_y}")

    def apply_button_click(self) -> None:
        Scion.img_current = Scion.img_temp.copy()
        Scion.display_image(Scion.img_current, self.label_current)

    def restore_button_click(self) -> None:
        Scion.img_temp = Scion.img_current.copy()
        Scion.display_image(Scion.img_temp, self.label_temp)

    def open_resize_window(self):
        ResizeWindow(self)

    def open_tpc_window(self):
        TransparencyWindow(self)

    def open_paste_image_window(self):
        PasteImageWindow(self)

    @staticmethod
    def display_image(image: Image.Image | None, label: tk.Label) -> Image.Image | None:
        if image is None:
            print("Error: no image exist to display")
            return None

        print(f"sampling first pixel: {image.getpixel((0, 0))}")
        img_tk = ImageTk.PhotoImage(image)
        label.config(image=img_tk)
        label.image = img_tk
        return image


class ResizeWindow(tk.Toplevel):
    def __init__(self, parent: Scion) -> None:
        super().__init__(parent)
        self.parent = parent

        self.title("Resize Image")
        self.geometry("300x200")

        # Initial dimensions
        self.base_width, self.base_height = Scion.img_current.size
        self.aspect_ratio = self.base_width / self.base_height
        self.width_var = tk.IntVar(value=self.base_width)
        self.height_var = tk.IntVar(value=self.base_height)

        # Labels
        tk.Label(self, text="Width:").pack(pady=5)
        self.width_entry = tk.Entry(self, textvariable=self.width_var)
        self.width_entry.pack(pady=5)
        self.width_var.trace_add("write", self.on_width_change)

        tk.Label(self, text="Height:").pack(pady=5)
        self.height_entry = tk.Entry(self, textvariable=self.height_var)
        self.height_entry.pack(pady=5)
        self.height_var.trace_add("write", self.on_height_change)

        # Aspect ratio checkbox
        self.aspect_ratio_var = tk.BooleanVar()
        self.aspect_ratio_checkbox = tk.Checkbutton(self, text="Maintain aspect ratio", variable=self.aspect_ratio_var)
        self.aspect_ratio_checkbox.pack(pady=5)

        # Apply button
        apply_button = tk.Button(self, text="Apply", command=self.apply_resize)
        apply_button.pack(pady=10)

    def on_width_change(self, *args):
        if self.aspect_ratio_var.get():
            try:
                self.height_var.set(int(self.width_var.get() / self.aspect_ratio))
            except tk.TclError:
                pass  # Ignore invalid input during typing

    def on_height_change(self, *args):
        if self.aspect_ratio_var.get():
            try:
                self.width_var.set(int(self.height_var.get() * self.aspect_ratio))
            except tk.TclError:
                pass  # Ignore invalid input during typing

    def apply_resize(self):
        # Cast to int
        try:
            new_width = int(self.width_entry.get())
            new_height = int(self.height_entry.get())

            # if self.aspect_ratio_var.get():
            #     new_height = int(new_width / self.aspect_ratio)

            if new_width <= 0 or new_height <= 0:
                raise ValueError("Dimensions must be positive integers.")
            if new_width >= 600 or new_height > 600:
                raise ValueError("Dimensions too large.")

            # Update preview image
            Scion.img_temp = Scion.img_current.resize((new_width, new_height), Image.Resampling.LANCZOS)
            Scion.display_image(Scion.img_temp, self.parent.label_temp)

        except ValueError as e:
            print(f"Error in resize window: {e}")


class TransparencyWindow(tk.Toplevel):
    def __init__(self, parent: Scion):
        super().__init__(parent)
        self.parent = parent
        self.title("Change Image Transparency")

        self.abs_alpha = tk.IntVar()
        self.rel_alpha = 1.00
        self.toggle_abs = True
        self.abs_checked = tk.BooleanVar(value=self.toggle_abs)
        self.rel_checked = tk.BooleanVar(value=not self.toggle_abs)

        abs_label = tk.Label(self, text="Change absolute value")
        abs_label.pack(pady=5)
        abs_slider = tk.Scale(self, from_=0, to=255, orient="horizontal", variable=self.abs_alpha)
        if Scion.img_current.mode == "RGBA":
            abs_slider.set(Scion.img_current.getpixel((0, 0))[3])
        abs_slider.pack(pady=5)

        # Text field for relative value (default 1.00)
        rel_label = tk.Label(self, text="Change relative value")
        rel_label.pack(pady=5)
        self.rel_entry = tk.Entry(self)
        self.rel_entry.insert(0, str(self.rel_alpha))
        self.rel_entry.pack(pady=5)

        # Checkboxes to toggle between absolute and relative modes
        abs_checkbox = tk.Checkbutton(self, text="Use absolute value", variable=self.abs_checked, command=self.toggle_checkboxes)
        abs_checkbox.pack(pady=5)

        rel_checkbox = tk.Checkbutton(self, text="Use relative value", variable=self.rel_checked, command=self.toggle_checkboxes)
        rel_checkbox.pack(pady=5)

        # Apply button to process the transparency change
        apply_button = tk.Button(self, text="Apply", command=self.apply_transparency)
        apply_button.pack(pady=10)

    def toggle_checkboxes(self):
        self.toggle_abs = not self.toggle_abs
        self.abs_checked.set(self.toggle_abs)
        self.rel_checked.set(not self.toggle_abs)

    def apply_transparency(self):
        if self.toggle_abs:
            new_alpha = Image.new("L", Scion.img_current.size, self.abs_alpha.get())
            Scion.img_temp.putalpha(new_alpha)
            Scion.display_image(Scion.img_temp, self.parent.label_temp)
        else:
            rel_mult = float(self.rel_entry.get())
            new_alpha = Scion.img_current.getchannel("A")
            new_alpha_pixels = new_alpha.load()
            for y in range(Scion.img_current.height):
                for x in range(Scion.img_current.width):
                    pixel = new_alpha_pixels[x, y]
                    new_alpha_pixels[x, y] = max(0, min(255, int(pixel * rel_mult)))
            Scion.img_temp.putalpha(new_alpha)
            Scion.display_image(Scion.img_temp, self.parent.label_temp)


class PasteImageWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.geometry("400x150")
        self.overlay_img: Image.Image | None = None
        self.title("Paste Image")

        # Open Image Button
        open_button = tk.Button(self, text="Open Image", command=self.open_image)
        open_button.pack(pady=5)

        # Paste Button
        paste_button = tk.Button(self, text="Paste", command=self.paste_image_onto_canvas)
        paste_button.pack(pady=10, side="bottom")
        # X Coordinate Field
        x_label = tk.Label(self, text="X Coordinate")
        x_label.pack(pady=5, side="left")
        self.x_entry = tk.Entry(self)
        self.x_entry.insert(0, "0")  # Default value
        self.x_entry.pack(pady=5, side="left")

        # Y Coordinate Field
        y_label = tk.Label(self, text="Y Coordinate")
        y_label.pack(pady=5, side="left")
        self.y_entry = tk.Entry(self)
        self.y_entry.insert(0, "0")  # Default value
        self.y_entry.pack(pady=5, side="left")

    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image to Paste",
            filetypes=([("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
        )
        if file_path:
            try:
                self.overlay_img = Image.open(file_path).convert("RGBA")
                messagebox.showinfo("Success", "Image loaded successfully.")
            except Exception as e:
                print(f"Error opening image: {e}")

    def paste_image_onto_canvas(self):
        x = int(self.x_entry.get())
        y = int(self.y_entry.get())
        if (self.overlay_img is None) \
                or (x < 0 or y < 0) \
                or ((x, y) > Scion.img_current.size):
            return
        # alpha mask of 255, overwrites all pixels
        mask = Image.new("L", self.overlay_img.size, 255)
        Scion.img_temp = Scion.img_current.copy()
        Scion.img_temp.paste(self.overlay_img, (x, y), mask)
        Scion.display_image(Scion.img_temp, self.parent.label_temp)


if __name__ == "__main__":
    app = Scion()
    app.mainloop()
