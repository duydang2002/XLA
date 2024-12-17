import tkinter as tk
from tkinter import Menu, filedialog, messagebox, ttk
from typing import Dict
from PIL import Image, ImageTk
import numpy as np
import cv2
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


img_current: Image.Image | None = None
img_temp: Image.Image | None = None
coord_x: int = 0
coord_y: int = 0

current_r = 100
current_g = 100
current_b = 100

current_y = 100
current_u = 100
current_v = 100

current_c=100
current_m=100
current_y2=100
current_k=100

current_color_format = "RGB" 
current_brightness = 100

exposure_value = 0
contrast_value = 0
shadow_value = 0
highlight_value = 0


def open_image() -> None:
    global img_current, img_temp, label_current, label_temp, exposure_value, contrast_value, shadow_value, highlight_value, shadow_value
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
    if file_path:
        img_current = Image.open(file_path)
        print(f">Image opened, mode: {img_current.mode}, size: {img_current.size}")
        if img_current.mode != 'RGBA':
            print( img_current.mode )
            img_current = img_current.convert('RGBA')
            print(">Added an alpha channel.")
        if img_current.size > (600, 600):
            img_current.thumbnail((600, 600), Image.Resampling.LANCZOS)
            print(f">Resized to {img_current.size}")

        img_temp = img_current.copy()
        display_image(img_current, label_current)
        display_image(img_temp, label_temp)

        exposure_value = 0
        contrast_value = 0
        shadow_value = 0
        highlight_value = 0
    else:
        print("Error: cannot open image file")


def click_coords(event: tk.Event) -> None:
    global coord_x, coord_y
    coord_x, coord_y = event.x, event.y
    coords_label.config(text=f"Clicked at coordinates {coord_x} : {coord_y}")


def apply_button_click() -> None:
    global img_current, img_temp, label_current
    img_current = img_temp.copy()
    display_image(img_current, label_current)


def restore_button_click() -> None:
    global img_current, img_temp, label_temp, exposure_value, contrast_value, shadow_value, highlight_value, current_g, current_b, current_r, current_brightness
    current_g = 100
    current_b = 100
    current_r = 100
    current_brightness = 100
    exposure_value = 0
    contrast_value = 0
    shadow_value = 0
    highlight_value = 0
    img_temp = img_current.copy()
    display_image(img_temp, label_temp)


def open_resize_window(root):
    ResizeWindow(root)


def open_tpc_window(root):
    TransparencyWindow(root)


def open_paste_window(root):
    PasteImageWindow(root)


def open_crop_window(root):
    CropImageWindow(root)


def open_invert_window(root):
    InvertColorWindow(root)


def open_mouse_crop_window(root):
    MouseCropWindow(root)


def open_add_subtract_window(root):
    AddSubtractImageWindow(root)


def display_image(image: Image.Image | None, label: tk.Label) -> Image.Image | None:
    if image is None:
        print("Error: no image exist to display")
        return None

    print(f"sampling first pixel: {image.getpixel((0, 0))}")
    img_tk = ImageTk.PhotoImage(image)
    label.config(image=img_tk)
    label.image = img_tk
    return image


# Function to open the color adjustment

def open_color_window(root):
    EditColorWindow(root)

def open_color_window_hsv(root):
    EditHSVColorWindow(root)

def open_brightness_window(root):
    EditBrightnessWindow(root)

def open_histogram_window(root):
    EditHistogramWindow(root)

def open_color_window_yuv(root):
    EditYUVColorWindow(root)

def open_color_window_cmyk(root):
    EditCMYKColorWindow(root)

class ResizeWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk) -> None:
        global img_current, img_temp
        super().__init__(parent)
        self.parent = parent
        self.title("Resize Image")
        self.geometry("500x200")
        # Initial dimensions
        self.base_width, self.base_height = img_current.size
        self.aspect_ratio = self.base_width / self.base_height
        self.width_var = tk.IntVar(value=self.base_width)
        self.height_var = tk.IntVar(value=self.base_height)
        self.is_updating = False  # Flag to prevent circular updates

        # Width/Height entries
        width_frame = tk.Frame(self)
        width_frame.pack(side="top", pady=5)
        tk.Label(width_frame, text="Width:").pack(side="left")
        self.width_entry = tk.Entry(width_frame, textvariable=self.width_var)
        self.width_entry.pack(side="left")
        self.width_var.trace_add("write", self.on_width_change)

        height_frame = tk.Frame(self)
        height_frame.pack(side="top", pady=2)
        tk.Label(height_frame, text="Height:").pack(side="left")
        self.height_entry = tk.Entry(height_frame, textvariable=self.height_var)
        self.height_entry.pack(side="left")
        self.height_var.trace_add("write", self.on_height_change)
        # Aspect ratio checkbox
        self.aspect_ratio_var = tk.BooleanVar()
        self.aspect_ratio_checkbox = tk.Checkbutton(self, text="Maintain aspect ratio", variable=self.aspect_ratio_var)
        self.aspect_ratio_checkbox.pack(pady=5)
        img_temp.resize((10, 10), Image.Resampling.BOX)
        # Resampling dropdown options
        resamp_frame = tk.Frame(self)
        resamp_frame.pack(side="top", pady=5)
        tk.Label(resamp_frame, text="Choose a resampling option:").pack( side="left")
        self.resampling_option: Image.Resampling = Image.Resampling.BICUBIC
        self.resampling_dict: Dict[str, Image.Resampling] = {
            'nearest-neighbor interpolation': Image.Resampling.NEAREST,
            'box sampling': Image.Resampling.BOX,
            'bilinear interpolation': Image.Resampling.BILINEAR,
            'hamming interpolation': Image.Resampling.HAMMING,
            'bicubic interpolation': Image.Resampling.BICUBIC,
            'lanczos interpolation': Image.Resampling.LANCZOS,
        }
        selected_string = tk.StringVar()
        selected_string.set("--")
        dropdown = tk.OptionMenu(resamp_frame, selected_string, *list(self.resampling_dict.keys()), command=self.change_resampling)
        dropdown.pack(side="left")
        # Apply button
        apply_button = tk.Button(self, text="Apply", command=self.apply_resize)
        apply_button.pack(pady=10, padx=10, side="bottom", anchor="se")

    def on_width_change(self, *args):
        if self.aspect_ratio_var.get() and not self.is_updating:
            try:
                self.is_updating = True
                self.height_var.set(int(self.width_var.get() / self.aspect_ratio))
            except tk.TclError:
                pass  # Ignore invalid input during typing
            finally:
                self.is_updating = False

    def on_height_change(self, *args):
        if self.aspect_ratio_var.get() and not self.is_updating:
            try:
                self.is_updating = True
                self.width_var.set(int(self.height_var.get() * self.aspect_ratio))
            except tk.TclError:
                pass  # Ignore invalid input during typing
            finally:
                self.is_updating = False

    def apply_resize(self):
        global img_current, img_temp, label_temp
        # Cast to int
        try:
            new_width = int(self.width_entry.get())
            new_height = int(self.height_entry.get())
            if new_width <= 0 or new_height <= 0:
                raise ValueError("Dimensions must be positive integers.")
            if new_width > 600 or new_height > 600:
                raise ValueError("Dimensions too large.")

            # Update preview image
            img_temp = img_current.resize((new_width, new_height), self.resampling_option)
            display_image(img_temp, label_temp)

        except ValueError as e:
            print(f"Error in resize window: {e}")

    def change_resampling(self, resamp_txt):
        self.resampling_option = self.resampling_dict[resamp_txt]
        print("option selected: " + resamp_txt + ", resampling: " + str(self.resampling_option))


class TransparencyWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        global img_current, img_temp
        super().__init__(parent)
        self.parent = parent
        self.title("Change Image Transparency")
        self.geometry("250x300")

        self.abs_alpha = tk.IntVar()
        self.rel_alpha = 1.00
        self.toggle_abs = True
        self.abs_checked = tk.BooleanVar(value=self.toggle_abs)
        self.rel_checked = tk.BooleanVar(value=not self.toggle_abs)

        abs_label = tk.Label(self, text="Change absolute value")
        abs_label.pack(pady=5)
        abs_slider = tk.Scale(self, from_=0, to=255, orient="horizontal", variable=self.abs_alpha)
        if img_current.mode == "RGBA":
            abs_slider.set(img_current.getpixel((0, 0))[3])
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
        global img_current, img_temp, label_temp
        if self.toggle_abs:
            new_alpha = Image.new("L", img_current.size, self.abs_alpha.get())
            img_temp.putalpha(new_alpha)
            display_image(img_temp, label_temp)
        else:
            rel_mult = float(self.rel_entry.get())
            new_alpha = img_current.getchannel("A")
            new_alpha_pixels = new_alpha.load()
            for y in range(img_current.height):
                for x in range(img_current.width):
                    pixel = new_alpha_pixels[x, y]
                    new_alpha_pixels[x, y] = max(0, min(255, int(pixel * rel_mult)))
            img_temp.putalpha(new_alpha)
            display_image(img_temp, label_temp)


class MouseCropOverlayWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk, overlay_img: Image.Image, callback):
        super().__init__(parent)
        self.parent = parent
        self.overlay_img = overlay_img
        self.callback = callback
        self.title("Crop Overlay Image")
        self.geometry("800x600")
        self.state("zoomed")

        self.canvas = tk.Canvas(self, cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        self.img_tk = ImageTk.PhotoImage(self.overlay_img, )
        self.canvas.create_image(0, 0, anchor="nw", image=self.img_tk)

        self.rect = None
        self.start_x = None
        self.start_y = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        apply_button = tk.Button(self, text="Apply", command=self.apply_crop)
        apply_button.pack(pady=10)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_mouse_drag(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        pass

    def apply_crop(self):
        x0, y0, x1, y1 = self.canvas.coords(self.rect)
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        if x0 > x1: x0, x1 = x1, x0
        if y0 > y1: y0, y1 = y1, y0
        cropped_overlay_image = self.overlay_img.crop((x0, y0, x1, y1))
        self.callback(cropped_overlay_image)
        self.destroy()


class ResizeOverlayWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk, overlay_img: Image.Image, callback):
        super().__init__(parent)
        self.parent = parent
        self.overlay_img = overlay_img
        self.callback = callback
        self.title("Resize Overlay Image")
        self.geometry("400x300")
        self.state("zoomed")

        self.original_width, self.original_height = overlay_img.size
        self.aspect_ratio = self.original_width / self.original_height

        # Labels for original dimensions
        tk.Label(self, text=f"Original Dimensions: {self.original_width}x{self.original_height}").pack(pady=5)

        # Variables for new dimensions
        self.new_width_var = tk.IntVar(value=self.original_width)
        self.new_height_var = tk.IntVar(value=self.original_height)

        # Frame for new dimensions entry fields
        dimensions_frame = tk.Frame(self)
        dimensions_frame.pack(pady=5)

        # Entry fields for new dimensions
        tk.Label(dimensions_frame, text="New Width:").grid(row=0, column=0, padx=5)
        self.new_width_entry = tk.Entry(dimensions_frame, textvariable=self.new_width_var)
        self.new_width_entry.grid(row=0, column=1, padx=5)
        self.new_width_var.trace_add("write", self.on_width_change)

        tk.Label(dimensions_frame, text="New Height:").grid(row=0, column=2, padx=5)
        self.new_height_entry = tk.Entry(dimensions_frame, textvariable=self.new_height_var)
        self.new_height_entry.grid(row=0, column=3, padx=5)
        self.new_height_var.trace_add("write", self.on_height_change)

        # Aspect ratio checkbox
        self.aspect_ratio_var = tk.BooleanVar(value=True)
        self.aspect_ratio_checkbox = tk.Checkbutton(self, text="Maintain aspect ratio", variable=self.aspect_ratio_var)
        self.aspect_ratio_checkbox.pack(pady=5)

        # Canvas for preview
        self.preview_canvas = tk.Canvas(self, width=1000, height=600)
        self.preview_canvas.pack(pady=10)
        self.update_preview()

        # Apply button
        apply_button = tk.Button(self, text="Apply", command=self.apply_resize)
        apply_button.pack(pady=10)

    def on_width_change(self, *args):
        if self.aspect_ratio_var.get():
            try:
                new_width = self.new_width_var.get()
                new_height = int(new_width / self.aspect_ratio)
                self.new_height_var.set(new_height)
            except tk.TclError:
                pass  # Ignore invalid input during typing
        self.update_preview()

    def on_height_change(self, *args):
        if self.aspect_ratio_var.get():
            try:
                new_height = self.new_height_var.get()
                new_width = int(new_height * self.aspect_ratio)
                self.new_width_var.set(new_width)
            except tk.TclError:
                pass  # Ignore invalid input during typing
        self.update_preview()

    def update_preview(self):
        self.preview_canvas.delete("all")
        try:
            new_width = self.new_width_var.get()
            new_height = self.new_height_var.get()
            resized_img = self.overlay_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.img_tk = ImageTk.PhotoImage(resized_img)
            self.preview_canvas.create_image(500, 300, anchor="center", image=self.img_tk)
        except tk.TclError:
            pass  # Ignore invalid input during typing

    def apply_resize(self):
        try:
            new_width = int(self.new_width_entry.get())
            new_height = int(self.new_height_entry.get())
            if new_width <= 0 or new_height <= 0:
                raise ValueError("Dimensions must be positive integers.")
            resized_overlay_image = self.overlay_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.callback(resized_overlay_image)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")


class PasteImageWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        global label_temp
        label_temp.bind("<Button-1>", lambda event: self.load_coords(event))

        super().__init__(parent)
        self.parent = parent
        self.geometry("400x250")
        self.overlay_img: Image.Image | None = None
        self.title("Paste Image")
        self.attributes("-topmost", True)

        # Open Image Button and Text
        open_button = tk.Button(self, text="Open Image", command=self.open_image)
        open_button.pack(pady=2, side="top")
        self.path_str = tk.StringVar()
        path_label = tk.Label(self, textvariable=self.path_str, font=("Arial", 9))
        path_label.pack(pady=2, padx=5, side="top", expand=True)
        # Crop Button
        crop_button = tk.Button(self, text="Crop", command=self.open_crop_window)
        crop_button.pack(pady=2, side="top")
        # Resize Button
        resize_button = tk.Button(self, text="Resize", command=self.open_resize_window)
        resize_button.pack(pady=2, side="top")
        # Paste Button
        paste_button = tk.Button(self, text="Paste", command=self.paste_image_onto_canvas)
        paste_button.pack(pady=10, side="bottom")
        # Text hint
        hint_label = tk.Label(self, text="click on the right image to pick a coordinate")
        hint_label.pack(pady=5, side="top")
        # X Coordinate Field
        x_label = tk.Label(self, text="X Coordinate")
        x_label.pack(pady=2, side="left")
        self.x_entry = tk.Entry(self)
        self.x_entry.insert(0, "0")
        self.x_entry.pack(pady=2, side="left")
        # Y Coordinate Field
        y_label = tk.Label(self, text="Y Coordinate")
        y_label.pack(pady=2, side="left")
        self.y_entry = tk.Entry(self)
        self.y_entry.insert(0, "0")  # Default value
        self.y_entry.pack(pady=2, side="left")

    def open_image(self):
        file_path: str = filedialog.askopenfilename(
            title="Select Image to Paste",
            filetypes=([("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
        )
        if file_path:
            try:
                self.overlay_img = Image.open(file_path).convert("RGBA")
                # write to UI what image is opened
                self.path_str.set("Loaded image " + file_path[(file_path.rfind('/') + 1):])
            except Exception as e:
                print(f"Error opening image: {e}")

    def open_crop_window(self):
        if self.overlay_img:
            MouseCropOverlayWindow(self, self.overlay_img, self.set_overlay_img)

    def open_resize_window(self):
        if self.overlay_img:
            ResizeOverlayWindow(self, self.overlay_img, self.set_overlay_img)

    def set_overlay_img(self, img):
        self.overlay_img = img

    def load_coords(self, event: tk.Event):
        global coord_x, coord_y
        self.x_entry.delete(0, tk.END)
        self.y_entry.delete(0, tk.END)
        self.x_entry.insert(0, str(event.x))
        self.y_entry.insert(0, str(event.y))

    def paste_image_onto_canvas(self):
        global img_current, img_temp, label_temp
        x = int(self.x_entry.get())
        y = int(self.y_entry.get())
        if (self.overlay_img is None) \
                or (x < 0 or y < 0) \
                or ((x, y) > img_current.size):
            return
        # alpha mask of 255, overwrites all pixels
        mask = Image.new("L", self.overlay_img.size, 255)
        img_temp = img_current.copy()
        img_temp.paste(self.overlay_img, (x, y), mask)
        display_image(img_temp, label_temp)


class CropImageWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        global img_current
        super().__init__(parent)
        self.parent = parent
        self.image_width, self.image_height = img_current.size
        # canvas drawing offset, cant draw lines at canvas border
        self.offset: int = 5

        self.title("Crop Image")
        # Display image dimensions
        dimensions_label = tk.Label(self, text=f"Image dimensions: {self.image_width}x{self.image_height}")
        dimensions_label.pack(pady=5)
        # Grid frame for cropping coords
        coord_frame = tk.Frame(self)
        coord_frame.pack(pady=5)
        tk.Label(coord_frame, text="x0:").grid(row=0, column=0, padx=5, pady=2)
        tk.Label(coord_frame, text="y0:").grid(row=0, column=2, padx=5, pady=2)
        tk.Label(coord_frame, text="x1:").grid(row=1, column=0, padx=5, pady=2)
        tk.Label(coord_frame, text="y1:").grid(row=1, column=2, padx=5, pady=2)

        self.x0_entry = tk.Entry(coord_frame, width=5)
        self.x0_entry.grid(row=0, column=1, padx=5)
        self.y0_entry = tk.Entry(coord_frame, width=5)
        self.y0_entry.grid(row=0, column=3, padx=5)
        self.x1_entry = tk.Entry(coord_frame, width=5)
        self.x1_entry.grid(row=1, column=1, padx=5)
        self.y1_entry = tk.Entry(coord_frame, width=5)
        self.y1_entry.grid(row=1, column=3, padx=5)
        # Canvas for crop preview
        canvas_frame = tk.Frame(self)
        canvas_frame.pack(pady=5)
        self.canvas_width = 300
        self.canvas_height = int(self.image_height / self.image_width * self.canvas_width)
        self.preview_canvas = tk.Canvas(canvas_frame,
                                        width=(self.canvas_width + 2 * self.offset),
                                        height=(self.canvas_height + 2 * self.offset))
        self.preview_canvas.pack()

        # Initialize UI
        self.x0_entry.insert(0, "0")
        self.y0_entry.insert(0, "0")
        self.x1_entry.insert(0, str(self.image_width))
        self.y1_entry.insert(0, str(self.image_height))
        self.update_preview_canvas()
        # Update canvas when entries change
        for entry in [self.x0_entry, self.y0_entry, self.x1_entry, self.y1_entry]:
            entry.bind("<KeyRelease>", lambda e: self.update_preview_canvas())
        # Apply button
        apply_button = tk.Button(self, text="Apply Crop", command=self.apply_crop)
        apply_button.pack(pady=10)

    def update_preview_canvas(self):
        # Clear canvas
        self.preview_canvas.delete("all")
        # Draw border
        self.preview_canvas.create_rectangle(self.offset, self.offset,
                                             self.canvas_width + self.offset, self.canvas_height + self.offset,
                                             outline="black")
        try:
            # Get coordinates from entries
            x0 = int(self.x0_entry.get())
            y0 = int(self.y0_entry.get())
            x1 = int(self.x1_entry.get())
            y1 = int(self.y1_entry.get())
            # Scale coordinates to the canvas dimensions
            x0_scaled = x0 / self.image_width * self.canvas_width + self.offset
            y0_scaled = y0 / self.image_height * self.canvas_height + self.offset
            x1_scaled = x1 / self.image_width * self.canvas_width + self.offset
            y1_scaled = y1 / self.image_height * self.canvas_height + self.offset
            # Draw crop region to preview
            self.preview_canvas.create_rectangle(x0_scaled, y0_scaled, x1_scaled, y1_scaled, outline="red", width=2)
        except ValueError:
            # Do nothing if invalid input
            pass

    def apply_crop(self):
        global img_current, img_temp, label_temp
        try:
            # Get coordinates from entries
            x0 = int(self.x0_entry.get())
            y0 = int(self.y0_entry.get())
            x1 = int(self.x1_entry.get())
            y1 = int(self.y1_entry.get())
            if x0 > x1: x0, x1 = x1, x0
            if y0 > y1: y0, y1 = y1, y0
            # Validate coordinates
            if x0 < 0 or y0 < 0 or x1 > self.image_width or y1 > self.image_height:
                raise ValueError("Invalid crop coordinates.")

            # Crop the image
            img_temp = img_current.crop((x0, y0, x1, y1))
            display_image(img_temp, label_temp)
            messagebox.showinfo("Success", "Image cropped successfully.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")


class EditColorWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Adjust Colors")
        self.geometry("200x250")

        # Variables to track RGB values from scales
        self.r_value = tk.IntVar(value=current_r)
        self.g_value = tk.IntVar(value=current_g)
        self.b_value = tk.IntVar(value=current_b)

        # Red Scale
        self.r_scale = tk.Scale(self, from_=0, to=200, orient="horizontal", label="Red", variable=self.r_value)
        self.r_scale.pack()
        # Green Scale
        self.g_scale = tk.Scale(self, from_=0, to=200, orient="horizontal", label="Green", variable=self.g_value)
        self.g_scale.pack()
        # Blue Scale
        self.b_scale = tk.Scale(self, from_=0, to=200, orient="horizontal", label="Blue", variable=self.b_value)
        self.b_scale.pack()

        self.reset_button = tk.Button(self, text="Reset", command=self.reset_color)
        self.reset_button.pack(pady=10)

        # Update color when scale values change
        def on_scale_change(event=None):
            self.update_color(self.r_value.get(), self.g_value.get(), self.b_value.get())

        # Bind scale changes to color update
        self.r_scale.bind("<ButtonRelease-1>", on_scale_change)
        self.g_scale.bind("<ButtonRelease-1>", on_scale_change)
        self.b_scale.bind("<ButtonRelease-1>", on_scale_change)

    def update_color(self, r, g, b):
        global img_current, img_temp, current_r, current_g, current_b

        if img_temp:
            # Cập nhật giá trị RGB hiện tại

            # Điều chỉnh các kênh màu
            r_factor = r / 100
            g_factor = g / 100
            b_factor = b / 100

            # Tách hình ảnh thành các kênh màu R, G, B

            r_img, g_img, b_img, a = img_current.split()

            # Áp dụng các thay đổi dựa trên giá trị RGB đã lưu
            r_img = r_img.point(lambda i: i * r_factor)
            g_img = g_img.point(lambda i: i * g_factor)
            b_img = b_img.point(lambda i: i * b_factor)

            # Gộp các kênh màu và hiển thị
            img_temp = Image.merge("RGBA", (r_img, g_img, b_img, a))
            current_r = r
            current_g = g
            current_b = b
            display_image(img_temp, label_temp)

    def reset_color(self):
        self.r_scale.set(100)
        self.g_scale.set(100)
        self.b_scale.set(100)
        self.update_color(100, 100, 100)

class EditYUVColorWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Adjust Colors YUV")
        self.geometry("200x250")

        # Variables to track RGB values from scales
        self.y_value = tk.IntVar(value=current_y)
        self.u_value = tk.IntVar(value=current_u)
        self.v_value = tk.IntVar(value=current_v)

        # Red Scale
        self.y_scale = tk.Scale(self, from_=0, to=100, orient="horizontal", label="Y (Luminance)", variable=self.y_value, length= 200)
        self.y_scale.pack()
        # Green Scale
        self.u_scale = tk.Scale(self, from_=0, to=100, orient="horizontal", label="U (Chrominance - Blue difference)", variable=self.u_value, length=200)
        self.u_scale.pack()
        # Blue Scale
        self.v_scale = tk.Scale(self, from_=0, to=100, orient="horizontal", label="V (Chrominance - Red difference)", variable=self.v_value, length=200)
        self.v_scale.pack()

        self.reset_button = tk.Button(self, text="Reset", command=self.reset_color)
        self.reset_button.pack(pady=10)

        # Update color when scale values change
        def on_scale_change(event=None):
            self.update_color(self.y_value.get(), self.u_value.get(), self.v_value.get())

        # Bind scale changes to color update
        self.y_scale.bind("<ButtonRelease-1>", on_scale_change)
        self.u_scale.bind("<ButtonRelease-1>", on_scale_change)
        self.v_scale.bind("<ButtonRelease-1>", on_scale_change)

    def update_color(self, y, u, v):
        global img_current, img_temp, current_y, current_u, current_v

        if img_temp:

            y_factor = y / 100
            u_factor = u / 100
            v_factor = v / 100

            r, g, b, a = img_current.split()
            
            # Chuyển đổi RGB sang YUV
            y_img, u_img, v_img = self.rgb_to_yuv(r, g, b)

            # Áp dụng các thay đổi
            y_img *= y_factor
            u_img *= u_factor
            v_img *= v_factor

            current_y= y
            current_u= u
            current_v= v
            # Chuyển đổi YUV trở lại RGB
            r_img, g_img, b_img = self.yuv_to_rgb(y_img, u_img, v_img)

            img_temp = Image.merge("RGBA", (r_img, g_img, b_img, a))
            display_image(img_temp, label_temp)

    def reset_color(self):
        self.y_scale.set(100)
        self.u_scale.set(100)
        self.v_scale.set(100)
        self.update_color(100, 100, 100)


    def rgb_to_yuv(self, r_img, g_img, b_img):
        R = np.array(r_img, dtype=np.float32)
        G = np.array(g_img, dtype=np.float32)
        B = np.array(b_img, dtype=np.float32)

        Y = 0.299 * R + 0.587 * G + 0.114 * B
        U = R - Y
        V = B - Y

        return Y, U, V

    def yuv_to_rgb(self, y_img, u_img, v_img):
        Y = np.array(y_img, dtype=np.float32)
        U = np.array(u_img, dtype=np.float32)
        V = np.array(v_img, dtype=np.float32)

        R = Y + U
        B = Y + V
        G = (Y - 0.299 * R - 0.114 * B) / 0.587

        R = np.clip(R, 0, 255).astype(np.uint8)
        G = np.clip(G, 0, 255).astype(np.uint8)
        B = np.clip(B, 0, 255).astype(np.uint8)

        return Image.fromarray(R), Image.fromarray(G), Image.fromarray(B)

class EditHSVColorWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Adjust Colors HSV")
        self.geometry("500x300")
        colors = [
        ("Red", 0, 15),
        ("Orange", 15, 22.5),
        ("Yellow", 22.5, 45),
        ("Green", 45, 75),
        ("Cyan", 75, 112.5),
        ("Blue", 112.5, 135),
        ("Violet", 135, 142.5),
        ("Magenta", 142.5, 172.5)
        ]
        self.color_combobox = ttk.Combobox(self, values=[color[0] for color in colors])
        self.color_combobox.set("Red")
        self.color_combobox.pack(pady=10)

        self.slider_frame = tk.Frame(self)
        self.slider_frame.pack()
        # Lưu các slider
        self.sliders = {}
        for color, low, high in colors:
            self.hue_slider = tk.Scale(self.slider_frame, from_=-30, to=30, orient=tk.HORIZONTAL, length=300)
            self.sat_slider = tk.Scale(self.slider_frame, from_=0.0, to=200, orient=tk.HORIZONTAL, length=300)
            self.sat_slider.set(100)
            self.light_slider = tk.Scale(self.slider_frame, from_=0.0, to=200, orient=tk.HORIZONTAL, length=300)
            self.light_slider.set(100)
            self.sliders[color] = (self.hue_slider, self.sat_slider, self.light_slider, (low, high))

        self.update_sliders()
        self.color_combobox.bind("<<ComboboxSelected>>", self.update_sliders)

        # Nút áp dụng chỉnh sửa
        self.apply_button = tk.Button(self, text="Apply HSL Changes", command=self.apply_hsl_color_changes)
        self.apply_button.pack(pady=10)

    def update_sliders(self, _=None):
        selected_color = self.color_combobox.get()
        for widgets in self.slider_frame.winfo_children():
            widgets.pack_forget()

        hue_slider, sat_slider, light_slider, _ = self.sliders[selected_color]

        tk.Label(self.slider_frame, text=f"{selected_color} - Hue Shift").pack()
        hue_slider.pack()
        tk.Label(self.slider_frame, text=f"{selected_color} - Saturation Factor").pack()
        sat_slider.pack()
        tk.Label(self.slider_frame, text=f"{selected_color} - Lightness Factor").pack()
        light_slider.pack()

    def apply_hsl_color_changes(self):
        global img_current, img_temp
        if img_current is None:
            return
        print(img_current)
        # Tạo bản sao ảnh HSV
        hsv_image = cv2.cvtColor(np.array(img_current), cv2.COLOR_RGB2HSV).astype(np.float32)
        original_hue = hsv_image[..., 0]
        
        # Lấy thông tin màu đang chọn
        selected_color = self.color_combobox.get()
        hue_slider, sat_slider, light_slider, (low, high) = self.sliders[selected_color]
        hue_shift = hue_slider.get()
        saturation_factor = sat_slider.get()
        lightness_factor = light_slider.get()

        # Xác định vùng màu
        if selected_color == "Red":
            mask = ((original_hue >= low) & (original_hue < high)) | ((original_hue >= 172.5) & (original_hue < 180))
        else:
            mask = (original_hue >= low) & (original_hue < high)
        # Áp dụng thay đổi cho vùng màu đó
        hsv_image[..., 0][mask] = (hsv_image[..., 0][mask] + hue_shift) % 180
        hsv_image[..., 1][mask] = np.clip(hsv_image[..., 1][mask] * saturation_factor/100, 0, 255)
        hsv_image[..., 2][mask] = np.clip(hsv_image[..., 2][mask] * lightness_factor/100, 0, 255)

        # Chuyển lại sang BGR và hiển thị
        img_temp = cv2.cvtColor(hsv_image.astype(np.uint8), cv2.COLOR_HSV2RGB)
        img_temp = Image.fromarray(img_temp)
        display_image(img_temp,label_temp)

class EditCMYKColorWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Adjust Colors CMYK")
        self.geometry("200x250")


        self.c_value = tk.IntVar(value=current_c)
        self.m_value = tk.IntVar(value=current_m)
        self.y_value = tk.IntVar(value=current_y2)
        self.k_value = tk.IntVar(value=current_k)

        self.c_scale = tk.Scale(self, from_=0, to=100, orient="horizontal", label="Cyan", variable=self.c_value)
        self.c_scale.pack()

        self.m_scale = tk.Scale(self, from_=0, to=100, orient="horizontal", label="Magenta", variable=self.m_value)
        self.m_scale.pack()

        self.y_scale = tk.Scale(self, from_=0, to=100, orient="horizontal", label="Yellow", variable=self.y_value)
        self.y_scale.pack()

        self.k_scale = tk.Scale(self, from_=0, to=100, orient="horizontal", label="Black", variable=self.k_value)
        self.k_scale.pack()

        self.reset_button = tk.Button(self, text="Reset", command=self.reset_color)
        self.reset_button.pack(pady=10)

        # Update color when scale values change
        def on_scale_change(event=None):
            self.update_color(self.c_value.get(), self.m_value.get(), self.y_value.get(), self.k_value.get())

        # Bind scale changes to color update
        self.c_scale.bind("<ButtonRelease-1>", on_scale_change)
        self.m_scale.bind("<ButtonRelease-1>", on_scale_change)
        self.y_scale.bind("<ButtonRelease-1>", on_scale_change)
        self.k_scale.bind("<ButtonRelease-1>", on_scale_change)

    def update_color(self, c, m, y, k):
        global img_current, img_temp, current_c, current_m, current_y2, current_k

        if img_temp:

            c_factor = c / 100
            m_factor = m / 100
            y_factor = y / 100
            k_factor = k / 100
            
            r, g, b, a = img_current.split()

            img_rgb = Image.merge("RGB", (r, g, b))
            img_rgb = np.array(img_rgb)
            # Chuyển đổi RGB sang CMYK
            c_img, m_img, y_img, k_img = self.rgb_to_cmyk(img_rgb)
            print(k_img)
            # Áp dụng các thay đổi
            c_img *= c_factor
            m_img *= m_factor
            y_img *= y_factor
            k_img *= k_factor

            current_c= c
            current_m= m
            current_y2= y
            current_k= k

            # Chuyển đổi CMYK trở lại RGB
            
            r_img, g_img, b_img = self.cmyk_to_rgb(c_img, m_img, y_img,k_img)
            r_img = Image.fromarray(r_img.astype(np.uint8), mode="L")
            g_img = Image.fromarray(g_img.astype(np.uint8), mode="L")
            b_img = Image.fromarray(b_img.astype(np.uint8), mode="L")
            img_temp = Image.merge("RGBA", (r_img, g_img, b_img, a))
            display_image(img_temp, label_temp)

    def reset_color(self):
        self.c_scale.set(100)
        self.m_scale.set(100)
        self.y_scale.set(100)
        self.k_scale.set(100)
        self.update_color(100, 100, 100, 100)

    def rgb_to_cmyk(self, rgb_image):

        rgb_normalized = rgb_image / 255.0

        # Tính kênh K
        K = 1 - np.max(rgb_normalized, axis=-1)

        # Tránh chia cho 0
        K[K == 1] = 1 - 1e-10

        # Tính kênh C, M, Y
        C = (1 - rgb_normalized[..., 0] - K) / (1 - K)
        M = (1 - rgb_normalized[..., 1] - K) / (1 - K)
        Y = (1 - rgb_normalized[..., 2] - K) / (1 - K)

        return C,M,Y,K
    
    def cmyk_to_rgb(self, C, M, Y, K):
        # Tính kênh R, G, B
        R = (1 - C) * (1 - K) *255
        G = (1 - M) * (1 - K) *255
        B = (1 - Y) * (1 - K) *255
        return R,G,B

class EditBrightnessWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Adjust Brightness Window")
        self.geometry("200x150")

        # Variable to keep track of brightness value
        self.brightness_value = tk.IntVar(value=current_brightness)

        # brightness scale
        self.brightness_scale = tk.Scale(self, from_=10, to=200, orient="horizontal", label="Brightness", variable=self.brightness_value)
        self.brightness_scale.pack()

        self.reset_button = tk.Button(self, text="Reset", command=self.reset_brightness)
        self.reset_button.pack(pady=10)

        # Update color when scale values change
        def on_scale_change(event=None):
            self.update_brightness(self.brightness_value.get())

        # Bind scale changes to color update
        self.brightness_scale.bind("<ButtonRelease-1>", on_scale_change)

    def update_brightness(self, brightness_value):
        global current_brightness, img_temp, img_current
        img_cv = np.array(img_current)
        img_cv_abs = cv2.convertScaleAbs(img_cv, alpha=(brightness_value / 100), beta=0)
        img_temp = Image.fromarray(img_cv_abs)
        current_brightness = brightness_value
        display_image(img_temp, label_temp)

    def reset_brightness(self):
        self.brightness_scale.set(100)
        self.update_brightness(100)


class EditHistogramWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Histogram")
        self.geometry("600x700")

        # Images
        global img_current, img_temp
        self.baseline_image = self.convert_to_rgb(img_current)
        self.edited_image = self.convert_to_rgb(img_temp)

        # Sliders' initial values
        self.exposure_value = 0
        self.contrast_value = 0
        self.shadow_value = 0
        self.highlight_value = 0

        # Create the histogram window layout
        self.create_histogram_window()

    def convert_to_rgb(self, image):
        if image.mode == "RGBA":
            return image.convert("RGB")
        return image

    def is_gray_scale(self, image):
        if image.mode == "L":
            return True
        if image.mode == "RGBA":
            image = image.convert("RGB")
        w, h = image.size
        for i in range(w):
            for j in range(h):
                pixel = image.getpixel((i, j))
                if isinstance(pixel, tuple) and len(pixel) == 3:
                    r, g, b = pixel
                    if r != g or g != b:
                        return False
                else:
                    return True
        return True

    def create_histogram_window(self):
        # Histogram canvas
        bins = 256
        bar_width = 2
        canvas_width = bins * bar_width
        canvas_height = 200

        self.histogram_canvas = tk.Canvas(
            self, width=canvas_width, height=canvas_height, bg="white", highlightthickness=1, relief="solid"
        )
        self.histogram_canvas.pack(pady=10)

        # Sliders
        self.create_slider("Exposure", -255, 255, self.on_exposure_slider_change)
        # self.create_slider("Contrast", -100, 100, self.on_contrast_slider_change)
        self.create_slider("Highlights", -100, 100, self.on_highlights_slider_change)
        self.create_slider("Shadows", -100, 100, self.on_shadows_slider_change)

        # Equalize histogram button
        equalize_button = tk.Button(self, text="Equalize Histogram", command=self.equalize_histogram)
        equalize_button.pack(pady=10)

        # Draw the initial histogram
        self.update_histogram()

    def create_slider(self, label, from_, to, command):
        slider = tk.Scale(self, from_=from_, to=to, orient="horizontal", label=label, command=command)
        slider.set(0)
        slider.pack(pady=10)
        if label == "Exposure":
            global exposure_value
            slider.set(exposure_value)
        # elif label == "Contrast":
        #     global contrast_value
        #     slider.set(contrast_value)
        elif label == "Highlights":
            global highlight_value
            slider.set(highlight_value)
        elif label == "Shadows":
            global shadow_value
            slider.set(shadow_value)
        return slider

    def update_histogram(self):
        histogram_data = self.get_histogram_data(self.edited_image)
        self.draw_histogram(histogram_data)

    def get_histogram_data(self, image):
        if image is None:
            return None
        if image.mode == "RGB" and not self.is_gray_scale(image):
            r, g, b = image.split()
            return r.histogram()[:256], g.histogram()[:256], b.histogram()[:256]
        else:
            grayscale_img = image.convert("L")
            histogram = grayscale_img.histogram()[:256]
            return histogram, histogram, histogram

    def draw_histogram(self, data):
        self.histogram_canvas.delete("all")

        if data is None:
            return

        max_height = 200
        bar_width = 2
        total_pixels = self.baseline_image.width * self.baseline_image.height

        if self.is_gray_scale(self.baseline_image):
            channel_colors = ["black"]
            channel_offsets = [0]
        elif self.baseline_image.mode == 'RGB' and not self.is_gray_scale(self.baseline_image):
            channel_colors = ["red", "green", "blue"]
            channel_offsets = [-1, 0, 1]

        for channel, color in enumerate(channel_colors):
            for i in range(len(data[channel])):
                bar_height = int(data[channel][i] / (total_pixels / 25) * max_height)
                x0 = i * bar_width + channel_offsets[channel]
                y0 = max_height - bar_height
                x1 = x0 + bar_width - 2
                y1 = max_height
                self.histogram_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

    def adjust_highlights(self, img_array, highlight_value):
        grayscale_img = self.baseline_image.convert("L")
        hist = grayscale_img.histogram()[:256]
        mean_intensity = np.mean(img_array)
        mean_intensity = int(mean_intensity)
        brightest_peak = np.argmax(hist[mean_intensity:]) + mean_intensity
        print('brightest_peak', brightest_peak)

        highlight_range = 20
        lower_bound = max(0, brightest_peak - highlight_range)

        mask = (img_array >= lower_bound)

        max_value = max(255, np.max(img_array))
        min_value = min(0, np.min(img_array))

        if self.baseline_image.mode == 'RGB' and not self.is_gray_scale(self.baseline_image):
            # Handle RGB images
            for channel in range(3):
                channel_data = img_array[:, :, channel]
                channel_data[mask[:, :, channel]] += highlight_value / 4
                img_array[:, :, channel] = np.clip(channel_data, 0, 255)

                adjusted_values = channel_data[mask[:, :, channel]]
                mask_min_value, mask_max_value = None, None

                if adjusted_values.size > 0:
                    mask_min_value = min(254, adjusted_values.min())
                    mask_max_value = adjusted_values.max()
                if mask_min_value is not None or mask_max_value is not None:
                    if highlight_value > 0:
                        stretched_values = ((adjusted_values - mask_min_value) / (mask_max_value - mask_min_value)) * (
                                    255 - lower_bound) + lower_bound
                        channel_data[mask[:, :, channel]] = np.clip(stretched_values, 0, 255)
                    elif highlight_value < 0:
                        # compressed_values = ((img_array[:, :, channel] - min_value) / (max_value - min_value)) * 255
                        compressed_values = img_array[:, :, channel]
                        channel_data = np.clip(compressed_values, 0, 255)
                img_array[:, :, channel] = np.clip(channel_data, 0, 255)
        else:
            # Handle grayscale images
            img_array[mask] += highlight_value / 4
            img_array = np.clip(img_array, 0, 255)

            # Calculate min and max for the mask
            adjusted_values = img_array[mask]
            mask_min_value, mask_max_value = None, None

            if adjusted_values.size > 0:
                mask_min_value = min(254, adjusted_values.min())
                mask_max_value = adjusted_values.max()

            if mask_min_value is not None or mask_max_value is not None:
                if highlight_value > 0:
                    stretched_values = ((adjusted_values - mask_min_value) / (mask_max_value - mask_min_value)) * (255 - lower_bound) + lower_bound
                    img_array[mask] = np.clip(stretched_values, 0, 255)
                elif highlight_value < 0:
                    # compressed_values = ((img_array - min_value) / (max_value - min_value)) * 255
                    compressed_values = img_array
                    img_array = np.clip(compressed_values, 0, 255)

        img_array = np.clip(img_array, 0, 255).astype(np.uint8)

        return img_array

    def adjust_shadows(self, img_array, shadow_value):
        img_array = img_array.astype(np.float64)

        grayscale_img = self.baseline_image.convert("L")
        hist = grayscale_img.histogram()[:256]
        mean_intensity = np.mean(img_array)
        mean_intensity = int(mean_intensity)
        brightest_peak = np.argmax(hist[mean_intensity:]) + mean_intensity

        shadow_range = 20
        lower_bound = max(0, brightest_peak - shadow_range)

        mask = (img_array < lower_bound)

        max_value = np.max(img_array)
        min_value = min(np.min(img_array), 254)

        if self.baseline_image.mode == 'RGB' and not self.is_gray_scale(self.baseline_image):
            # Handle RGB images
            for channel in range(3):
                channel_data = img_array[:, :, channel]
                channel_data[mask[:, :, channel]] += shadow_value / 4
                img_array[:, :, channel] = np.clip(channel_data, 0, 255)

                adjusted_values = channel_data[mask[:, :, channel]]
                mask_min_value, mask_max_value = None, None

                if adjusted_values.size > 0:
                    mask_min_value = min(254, adjusted_values.min())
                    mask_max_value = adjusted_values.max()

                if mask_min_value is not None or mask_max_value is not None:
                    if shadow_value > 0:
                        # stretched_values = ((img_array[:, :, channel] - min_value) / (max_value - min_value)) * 255
                        stretched_values = img_array[:, :, channel]
                        channel_data = np.clip(stretched_values, 0, 255)
                    elif shadow_value < 0:
                        compressed_values = ((adjusted_values - mask_min_value) / (mask_max_value - mask_min_value)) * (lower_bound)
                        channel_data[mask[:, :, channel]] = np.clip(compressed_values, 0, 255)

                img_array[:, :, channel] = np.clip(channel_data, 0, 255)
        else:
            # Handle grayscale images
            img_array[mask] += shadow_value / 4
            img_array = np.clip(img_array, 0, 255)

            adjusted_values = img_array[mask]
            mask_min_value, mask_max_value = None, None

            if adjusted_values.size > 0:
                mask_min_value = min(254, adjusted_values.min())
                mask_max_value = adjusted_values.max()

            if mask_min_value is not None or mask_max_value is not None:
                if shadow_value > 0:
                    # stretched_values = ((img_array - min_value) / (max_value - min_value)) * 255
                    stretched_values = img_array
                    img_array = np.clip(stretched_values, 0, 255)
                elif shadow_value < 0:
                    compressed_values = ((adjusted_values - mask_min_value) / (mask_max_value - mask_min_value)) * (lower_bound)
                    img_array[mask] = compressed_values

            img_array = np.clip(img_array, 0, 255).astype(np.uint8)

        return img_array

    def apply_adjustments(self):
        global exposure_value, contrast_value, shadow_value, highlight_value
        img_array = np.array(self.baseline_image).astype(np.float32)

        # exposure
        img_array += exposure_value

        max_value = max(255, np.max(img_array))
        min_value = min(0, np.min(img_array))

        # contranst
        # if self.baseline_image.mode == 'RGB' and not self.is_gray_scale(self.baseline_image):
        #     # For RGB images
        #     mean_r = np.mean(img_array[:, :, 0])
        #     mean_g = np.mean(img_array[:, :, 1])
        #     mean_b = np.mean(img_array[:, :, 2])

        #     contrast_scale = 1 + (contrast_value / 170.0)

        #     img_array[:, :, 0] = (img_array[:, :, 0] - mean_r) * contrast_scale + mean_r
        #     img_array[:, :, 1] = (img_array[:, :, 1] - mean_g) * contrast_scale + mean_g
        #     img_array[:, :, 2] = (img_array[:, :, 2] - mean_b) * contrast_scale + mean_b

        # else:
        #     # For grayscale images
        #     mean = np.mean(img_array)
        #     contrast_scale = 1 + (contrast_value / 170.0)
        #     # img_array = (img_array - mean) * contrast_scale + mean
        #     img_array = ((img_array - min_value) / (max_value - min_value) * (contrast_scale * 255))

        # highlights
        img_array = self.adjust_highlights(img_array, highlight_value)

        # shadows
        img_array = self.adjust_shadows(img_array, shadow_value)

        # Clip and convert to uint8
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)

        # Update `edited_img`
        self.edited_image = Image.fromarray(img_array)

        # Update histogram
        display_image(self.edited_image, label_temp)
        updated_histogram_data = self.get_histogram_data(self.edited_image)
        self.draw_histogram(updated_histogram_data)

    def equalize_histogram(self):
        if self.baseline_image is None:
            return
        if self.baseline_image.mode == "RGB" and not self.is_gray_scale(self.baseline_image):
            img_array = np.array(self.baseline_image)
            for channel in range(3):
                img_array[:, :, channel] = cv2.equalizeHist(img_array[:, :, channel])
            self.edited_image = Image.fromarray(img_array)
        else:
            grayscale_img = cv2.cvtColor(np.array(self.baseline_image), cv2.COLOR_RGB2GRAY)
            equalized_img = cv2.equalizeHist(grayscale_img)
            self.edited_image = Image.fromarray(cv2.cvtColor(equalized_img, cv2.COLOR_GRAY2RGB))
        self.update_histogram()
        display_image(self.edited_image, label_temp)

    def on_exposure_slider_change(self, value):
        global exposure_value
        exposure_value = int(value)
        self.apply_adjustments()

    # def on_contrast_slider_change(self, value):
    #     global contrast_value
    #     contrast_value = int(value)
    #     self.apply_adjustments()

    def on_highlights_slider_change(self, value):
        global highlight_value
        highlight_value = int(value)
        self.apply_adjustments()

    def on_shadows_slider_change(self, value):
        global shadow_value
        shadow_value = int(value)
        self.apply_adjustments()


# A window for inverting color
class InvertColorWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Invert Colors")
        self.geometry("200x100")

        # Apply button to invert colors
        apply_button = tk.Button(self, text="Invert Colors", command=self.invert_colors)
        apply_button.pack(pady=20)

    def invert_colors(self):
        global img_current, img_temp, label_temp
        if img_temp:
            # Convert image to numpy array
            local_image_current = img_current.convert('RGB')
            img_np = np.array(local_image_current)
            # Invert colors
            img_np = 255 - img_np
            # Convert back to PIL image
            local_img_temp = Image.fromarray(img_np)
            # Update image_temp and display
            img_temp = local_img_temp.convert('RGBA')
            display_image(local_img_temp, label_temp)

# A window that allows cropping by mouse
class MouseCropWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        global img_current, img_temp
        super().__init__(parent)
        self.parent = parent
        self.title("Mouse Crop Image")
        self.geometry("800x600")

        self.canvas = tk.Canvas(self, cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        self.img_tk = ImageTk.PhotoImage(img_current)
        self.canvas.create_image(0, 0, anchor="nw", image=self.img_tk)

        self.rect = None
        self.start_x = None
        self.start_y = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        apply_button = tk.Button(self, text="Apply", command=self.apply_crop)
        apply_button.pack(pady=10)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_mouse_drag(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        pass

    def apply_crop(self):
        global img_current, img_temp, label_temp
        x0, y0, x1, y1 = self.canvas.coords(self.rect)
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        if x0 > x1: x0, x1 = x1, x0
        if y0 > y1: y0, y1 = y1, y0
        img_temp = img_current.crop((x0, y0, x1, y1))
        display_image(img_temp, label_temp)


# A function to save the current image
def save_image() -> None:
    global img_current
    if img_current.mode != "RGB":
        img_current = img_current.convert("RGB")
    if img_current is None:
        messagebox.showerror("Error", "No image to save.")
        return

    filetypes = [
        ("JPEG", "*.jpg;*.jpeg"),
        ("PNG", "*.png"),
        ("GIF", "*.gif"),
        ("BMP", "*.bmp"),
        ("TIFF", "*.tiff"),
    ]
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes)
    if file_path:
        try:
            img_current.save(file_path)
            messagebox.showinfo("Success", f"Image saved as {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")

def save_image_cmyk() -> None:
    """
    Lưu ảnh hiện tại ở chế độ CMYK với các định dạng hỗ trợ CMYK.
    """
    global img_current
    if img_current is None:
        messagebox.showerror("Error", "No image to save.")
        return

    if img_current.mode != "CMYK":
        img_current = img_current.convert("CMYK")
    
    # Các định dạng hỗ trợ CMYK
    filetypes = [
        ("TIFF", "*.tiff;*.tif"),
        ("JPEG", "*.jpg;*.jpeg"),
    ]

    file_path = filedialog.asksaveasfilename(defaultextension=".tiff", filetypes=filetypes)
    if file_path:
        try:
            img_current.save(file_path)
            messagebox.showinfo("Success", f"Image saved as {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")

class AddSubtractImageWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        global img_current
        super().__init__(parent)
        self.parent = parent
        self.title("Add/Subtract Image")
        self.geometry("800x800")
        self.attributes('-topmost', True)
        self.overlay_img: Image.Image | None = None

        # Open Image Button
        open_button = tk.Button(self, text="Open Image", command=self.open_image)
        open_button.pack(pady=10)

        # Canvas for preview
        self.preview_canvas = tk.Canvas(self, width=600, height=600, bg="white")
        self.preview_canvas.pack(pady=10)

        # Add and Subtract Buttons
        add_button = tk.Button(self, text="Add Image", command=self.add_image)
        add_button.pack(pady=5)
        subtract_button = tk.Button(self, text="Subtract Image", command=self.subtract_image)
        subtract_button.pack(pady=5)

    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")]
        )
        if file_path:
            try:
                self.overlay_img = Image.open(file_path).convert("RGBA")
                self.overlay_img = self.overlay_img.resize(img_current.size, Image.Resampling.LANCZOS)
                self.show_preview()
            except Exception as e:
                print(f"Error opening image: {e}")

    def show_preview(self):
        if self.overlay_img:
            self.preview_canvas.delete("all")
            img_tk = ImageTk.PhotoImage(self.overlay_img)
            self.preview_canvas.create_image(300, 300, anchor="center", image=img_tk)
            self.preview_canvas.image = img_tk

    def add_image(self):
        global img_temp, label_temp
        if self.overlay_img:
            img_np = np.array(img_temp.convert("RGBA"))
            overlay_np = np.array(self.overlay_img)
            result_np = cv2.add(img_np, overlay_np)
            img_temp = Image.fromarray(result_np)
            display_image(img_temp, label_temp)

    def subtract_image(self):
        global img_temp, label_temp
        if self.overlay_img:
            img_np = np.array(img_temp.convert("RGBA"))
            overlay_np = np.array(self.overlay_img)
            result_np = cv2.subtract(img_np, overlay_np)
            img_temp = Image.fromarray(result_np)
            display_image(img_temp, label_temp)


def open_identity_window(root):
    IdentityWindow(root)

def open_linear_window(root):
    LinearWindow(root)

def open_invert_window(root):
    InvertWindow(root)

def open_threshold_window(root):
    ThresholdWindow(root)

def open_log_window(root):
    LogWindow(root)

def open_inverse_log_window(root):
    InverseLogWindow(root)

def open_power_window(root):
    PowerWindow(root)

class IdentityWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Identity Transformation")
        self.geometry("600x600")

        # Label to show the mathematical function
        function_label = tk.Label(self, text="Identity Transformation: f(x) = x", font=("Helvetica", 16))
        function_label.pack(pady=20)

        # Create a plot for the identity function
        fig = Figure(figsize=(3, 3), dpi=100)
        ax = fig.add_subplot(111)
        x = [i for i in range(0, 256)]
        y = x
        ax.plot(x, y)
        ax.set_title("f(x) = x")
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")

        # Embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

        # Apply button to perform the identity transformation
        apply_button = tk.Button(self, text="Apply Identity Transformation", command=self.apply_identity)
        apply_button.pack(pady=20)

    def apply_identity(self):
        global img_temp, label_temp
        # Identity transformation does not change the image
        display_image(img_temp, label_temp)


class LinearWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Linear Transformation")
        self.geometry("600x600")

        # Variables for a and b
        self.a = tk.DoubleVar(value=1.0)
        self.b = tk.DoubleVar(value=0.0)

        # Entry fields for a and b
        a_label = tk.Label(self, text="a:", font=("Helvetica", 12))
        a_label.pack(pady=5)
        a_entry = tk.Entry(self, textvariable=self.a, font=("Helvetica", 12))
        a_entry.pack(pady=5)

        b_label = tk.Label(self, text="b:", font=("Helvetica", 12))
        b_label.pack(pady=5)
        b_entry = tk.Entry(self, textvariable=self.b, font=("Helvetica", 12))
        b_entry.pack(pady=5)

        # Button to update the plot
        update_button = tk.Button(self, text="Update Plot", command=self.update_plot)
        update_button.pack(pady=20)
        apply_button = tk.Button(self, text="Apply Linear Transformation", command=self.apply_linear)
        apply_button.pack(pady=20)

        # Create a plot for the linear function
        self.fig = Figure(figsize=(3, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=20)

        # Initial plot
        self.update_plot()

    def update_plot(self):
        a = self.a.get()
        b = self.b.get()
        x = [i for i in range(0, 256)]
        y = [a * i + b for i in range(0, 256)]
        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.set_xlim(0, 256)
        self.ax.set_ylim(0, 256)
        self.ax.set_title(f"f(x) = {a}x + {b}")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.canvas.draw()

    def apply_linear(self):
        global img_temp, label_temp
        a = self.a.get()
        b = self.b.get()
        img_array = np.array(img_temp)
        transformed_img_array = a * img_array + b
        transformed_img_array = np.clip(transformed_img_array, 0, 255).astype(np.uint8)
        transformed_img = Image.fromarray(transformed_img_array)
        display_image(transformed_img, label_temp)

class InvertWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Inverse Transformation")
        self.geometry("600x600")

        apply_button = tk.Button(self, text="Apply Inverse Transformation", command=self.apply_invert)
        apply_button.pack(pady=20)

        # Create a plot for the invert function
        self.fig = Figure(figsize=(3, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=20)

        # Initial plot
        self.update_plot()

    def update_plot(self):
        x = [i for i in range(0, 256)]
        y = [255 - i for i in range(0, 256)]
        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.set_xlim(0, 256)
        self.ax.set_ylim(0, 256)
        self.ax.set_title("f(x) = 255 - x")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.canvas.draw()

    def apply_invert(self):
        global img_temp, label_temp
        img_array = np.array(img_temp)
        transformed_img_array = 255 - img_array
        transformed_img = Image.fromarray(transformed_img_array)
        display_image(transformed_img, label_temp)

class ThresholdWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Threshold Transformation")
        self.geometry("600x600")

        self.threshold = tk.DoubleVar(value=128.0)

        threshold_label = tk.Label(self, text="Threshold:", font=("Helvetica", 12))
        threshold_label.pack(pady=5)
        threshold_entry = tk.Entry(self, textvariable=self.threshold, font=("Helvetica", 12))
        threshold_entry.pack(pady=5)

        update_button = tk.Button(self, text="Update Plot", command=self.update_plot)
        update_button.pack(pady=20)
        apply_button = tk.Button(self, text="Apply Threshold Transformation", command=self.apply_threshold)
        apply_button.pack(pady=20)

        # Create a plot for the threshold function
        self.fig = Figure(figsize=(3, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=20)

        # Initial plot
        self.update_plot()

    def update_plot(self):
        threshold = self.threshold.get()
        x = [i for i in range(0, 256)]
        y = [255 if i > threshold else 0 for i in range(0, 256)]
        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.set_xlim(0, 256)
        self.ax.set_ylim(0, 256)
        self.ax.set_title(f"f(x) = 255 if x > {threshold} else 0")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.canvas.draw()

    def apply_threshold(self):
        global img_temp, label_temp
        threshold = self.threshold.get()
        img_array = np.array(img_temp)
        transformed_img_array = (img_array > threshold) * 255
        transformed_img = Image.fromarray(transformed_img_array.astype(np.uint8))
        display_image(transformed_img, label_temp)

class LogWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Log Transformation")
        self.geometry("600x600")

        self.c = tk.DoubleVar(value=1.0)

        c_label = tk.Label(self, text="c: 255/log(256)", font=("Helvetica", 12))
        c_label.pack(pady=5)
        # c_entry = tk.Entry(self, textvariable=self.c, font=("Helvetica", 12))
        # c_entry.pack(pady=5)

        apply_button = tk.Button(self, text="Apply Log Transformation", command=self.apply_log)
        apply_button.pack(pady=20)

        # Create a plot for the log function
        self.fig = Figure(figsize=(3, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=20)

        # Initial plot
        self.update_plot()

    def update_plot(self):
        # c = self.c.get()
        c = 255 / np.log(256)
        x = [i for i in range(1, 256)]
        y = [c * np.log(1 + i) for i in range(1, 256)]
        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.set_xlim(0, 256)
        self.ax.set_ylim(0, 256)
        self.ax.set_title(f"f(x) = c * log(1 + x)")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.canvas.draw()

    def apply_log(self):
        global img_temp, label_temp
        # c = self.c.get()
        c = 255 / np.log(256)
        img_array = np.array(img_temp)
        transformed_img_array = c * np.log1p(img_array)
        transformed_img_array = np.clip(transformed_img_array, 0, 255).astype(np.uint8)
        transformed_img = Image.fromarray(transformed_img_array)
        display_image(transformed_img, label_temp)

class InverseLogWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Inverse Log Transformation")
        self.geometry("600x600")

        self.c = tk.DoubleVar(value=1.0)

        c_label = tk.Label(self, text="c: 255/log(256)", font=("Helvetica", 12))
        c_label.pack(pady=5)
        # c_entry = tk.Entry(self, textvariable=self.c, font=("Helvetica", 12))
        # c_entry.pack(pady=5)

        apply_button = tk.Button(self, text="Apply Inverse Log Transformation", command=self.apply_inverse_log)
        apply_button.pack(pady=20)

        # Create a plot for the inverse log function
        self.fig = Figure(figsize=(3, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=20)

        # Initial plot
        self.update_plot()

    def update_plot(self):
        # c = self.c.get()
        c = 255 / np.log(256)
        x = [i for i in range(0, 256)]
        y = [np.expm1(i / c) for i in range(0, 256)]
        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.set_xlim(0, 256)
        self.ax.set_ylim(0, 256)
        self.ax.set_title(f"f(x) = exp(x / c) - 1")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.canvas.draw()

    def apply_inverse_log(self):
        global img_temp, label_temp
        # c = self.c.get()
        c = 255 / np.log(256)
        img_array = np.array(img_temp)
        transformed_img_array = np.expm1(img_array / c)
        transformed_img_array = np.clip(transformed_img_array, 0, 255).astype(np.uint8)
        transformed_img = Image.fromarray(transformed_img_array)
        display_image(transformed_img, label_temp)

class PowerWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Power Transformation")
        self.geometry("600x600")

        self.c = tk.DoubleVar(value=1.0)
        self.gamma = tk.DoubleVar(value=1.0)

        c_label = tk.Label(self, text="c: 1", font=("Helvetica", 12))
        c_label.pack(pady=5)
        # c_entry = tk.Entry(self, textvariable=self.c, font=("Helvetica", 12))
        # c_entry.pack(pady=5)

        gamma_label = tk.Label(self, text="gamma:", font=("Helvetica", 12))
        gamma_label.pack(pady=5)
        gamma_entry = tk.Entry(self, textvariable=self.gamma, font=("Helvetica", 12))
        gamma_entry.pack(pady=5)

        update_button = tk.Button(self, text="Update Plot", command=self.update_plot)
        update_button.pack(pady=20)
        apply_button = tk.Button(self, text="Apply Power Transformation", command=self.apply_power)
        apply_button.pack(pady=20)
        
        # Create a plot for the power function
        self.fig = Figure(figsize=(3, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=20)

        # Initial plot
        self.update_plot()

    def update_plot(self):
        # c = self.c.get()
        c = 1
        gamma = self.gamma.get()
        x = [i for i in range(0, 256)]
        normalized_x = [i / 255 for i in range(0, 256)]
        y = [255 * c * np.power(i, gamma) for i in normalized_x]
        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.set_xlim(0, 256)
        self.ax.set_ylim(0, 256)
        self.ax.set_title(f"f(x) = {c} * x^{gamma}")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.canvas.draw()

    def apply_power(self):
        global img_temp, label_temp
        # c = self.c.get()
        c = 1
        gamma = self.gamma.get()
        img_array = np.array(img_temp)
        transformed_img_array = c * np.power(img_array, gamma)
        transformed_img_array = np.clip(transformed_img_array, 0, 255).astype(np.uint8)
        transformed_img = Image.fromarray(transformed_img_array)
        display_image(transformed_img, label_temp)


# this comment is just for git testing purpose 
if __name__ == "__main__":
    app = tk.Tk()

    app.title("Image Editor")
    app.geometry("1200x800")
    app.state("zoomed")
    menu_bar = Menu(app)
    app.config(menu=menu_bar)

    file_menu = Menu(menu_bar, tearoff=0)
    edit_menu = Menu(menu_bar, tearoff=0)
    color_menu = Menu(menu_bar,tearoff=0)
    histogram_menu = Menu(menu_bar, tearoff=0)
    contrast_menu = Menu(menu_bar, tearoff=0)

    menu_bar.add_cascade(label="File", menu=file_menu)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)
    menu_bar.add_cascade(label="Adjust Color", menu=color_menu)
    menu_bar.add_cascade(label="Adjust Contrast", menu=contrast_menu)
    menu_bar.add_cascade(label="Histogram", menu=histogram_menu)

    color_menu.add_command(label="RGB color space", command= lambda: open_color_window(app))
    color_menu.add_command(label="HSV color space", command= lambda: open_color_window_hsv(app))
    color_menu.add_command(label="YUV color space", command= lambda: open_color_window_yuv(app))
    color_menu.add_command(label="CMYK color space", command= lambda: open_color_window_cmyk(app))

    contrast_menu.add_command(label="Identity/Homogenous", command= lambda: open_identity_window(app))
    contrast_menu.add_command(label="Linear", command= lambda: open_linear_window(app))
    contrast_menu.add_command(label="Invert", command= lambda: open_invert_window(app))
    contrast_menu.add_command(label="Threshold", command= lambda: open_threshold_window(app))
    contrast_menu.add_command(label="Logarithmic", command= lambda: open_log_window(app))
    contrast_menu.add_command(label="Inverse Logarithmic", command= lambda: open_inverse_log_window(app))
    contrast_menu.add_command(label="Power", command= lambda: open_power_window(app))

    file_menu.add_command(label="Open", command=open_image)
    file_menu.add_command(label="Save", command=save_image)
    file_menu.add_command(label="Save CMYK mode", command=save_image_cmyk)
    file_menu.add_command(label="Exit", command=quit)
    edit_menu.add_command(label="Resize", command=lambda: open_resize_window(app))
    edit_menu.add_command(label="Change transparency", command=lambda: open_tpc_window(app))
    edit_menu.add_command(label="Paste image", command=lambda: open_paste_window(app))

    histogram_menu.add_command(label="Histogram", command=lambda: open_histogram_window(app))

    crop_menu = Menu(edit_menu, tearoff=0)
    edit_menu.add_cascade(label="Crop image", menu=crop_menu)
    crop_menu.add_command(label="Crop with mouse", command=lambda: open_mouse_crop_window(app))
    crop_menu.add_command(label="Crop with coordinate", command=lambda: open_crop_window(app))


    # Label to display label_current coordinates
    coords_label = tk.Label(app, text="Left click to see coordinates", font=("Helvetica", 14))
    coords_label.pack(side="top", padx=0, pady=0)
    # Button to save temporary image to current image
    frame_bottom = tk.Frame(app)
    frame_bottom.pack(side="bottom", fill="x", ipady=10)
    button_apply = tk.Button(frame_bottom, text="Apply", command=apply_button_click)
    button_apply.pack(side="right")
    button_restore = tk.Button(frame_bottom, text="Restore", command=restore_button_click)
    button_restore.pack(side="right")

    # Frame for image currently editing
    frame_current = tk.Frame(app, width=600, height=600, bg="white")
    frame_current.pack(side="left", fill="both", expand=True)
    label_current = tk.Label(frame_current, bg="white")
    label_current.place(x=10, y=50)
    label_current.bind("<Button-1>", lambda event: click_coords(event))

    # Frame to preview image before saving
    frame_temp = tk.Frame(app, width=600, height=600, bg="white")
    frame_temp.pack(side="right", fill="both", expand=True)
    label_temp = tk.Label(frame_temp, bg="white")
    label_temp.place(x=10, y=50)

    app.mainloop()
