import tkinter as tk
from tkinter import Menu, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import cv2
img_current: Image.Image | None = None
img_temp: Image.Image | None = None
coord_x: int = 0
coord_y: int = 0

current_r = 100
current_g = 100
current_b = 100

current_contrast = 100

exposure_value = 0
contrast_value = 0
shadow_value = 0
highlight_value = 0

def open_image() -> None:
    global img_current, img_temp, label_current, label_temp
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
    if file_path:
        img_current = Image.open(file_path)
        print(f">Image opened, mode: {img_current.mode}, size: {img_current.size}")
        if img_current.mode == 'RGB':
            img_current = img_current.convert('RGBA')
            print(">Added an alpha channel.")
        if img_current.size > (600, 600):
            img_current.thumbnail((600, 600), Image.Resampling.LANCZOS)
            print(f">Resized to {img_current.size}")

        img_temp = img_current.copy()
        display_image(img_current, label_current)
        display_image(img_temp, label_temp)
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
    global img_current, img_temp, label_temp
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
def open_contrast_window(root):
    EditContrastWindow(root)
    
class ResizeWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk) -> None:
        global img_current, img_temp
        super().__init__(parent)
        self.parent = parent

        self.title("Resize Image")
        self.geometry("300x200")

        # Initial dimensions
        self.base_width, self.base_height = img_current.size
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
            img_temp = img_current.resize((new_width, new_height), Image.Resampling.LANCZOS)
            display_image(img_temp, label_temp)

        except ValueError as e:
            print(f"Error in resize window: {e}")


class TransparencyWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        global img_current, img_temp
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


class PasteImageWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        global label_temp
        label_temp.bind("<Button-1>", lambda event: self.load_coords(event))

        super().__init__(parent)
        self.parent = parent
        self.geometry("400x150")
        self.overlay_img: Image.Image | None = None
        self.title("Paste Image")
        self.attributes("-topmost", True)

        # Open Image Button
        open_button = tk.Button(self, text="Open Image", command=self.open_image)
        open_button.pack(pady=2, side="top")
        # Paste Button
        paste_button = tk.Button(self, text="Paste", command=self.paste_image_onto_canvas)
        paste_button.pack(pady=10, side="bottom")
        # X Coordinate Field
        x_label = tk.Label(self, text="X Coordinate")
        x_label.pack(pady=5, side="left")
        self.x_entry = tk.Entry(self)
        self.x_entry.insert(0, "0")
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
        self.r_scale = tk.Scale(self, from_=10, to=200, orient="horizontal", label="Red", variable=self.r_value)
        self.r_scale.pack()
        # Green Scale
        self.g_scale = tk.Scale(self, from_=10, to=200, orient="horizontal", label="Green", variable=self.g_value)
        self.g_scale.pack()
        # Blue Scale
        self.b_scale = tk.Scale(self, from_=10, to=200, orient="horizontal", label="Blue", variable=self.b_value)
        self.b_scale.pack()
        
        self.reset_button = tk.Button(self, text="Reset", command=self.reset_color )
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
            img_temp = Image.merge("RGBA", (r_img, g_img, b_img,a))
            current_r = r
            current_g = g
            current_b = b
            display_image(img_temp, label_temp)
    def reset_color(self):
        self.r_scale.set(100)
        self.g_scale.set(100)
        self.b_scale.set(100)
        self.update_color(100,100,100)

class EditContrastWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Adjust Contrast Window")
        self.geometry("200x150")
        
        #Variable to keep track of contrast value
        self.contrast_value = tk.IntVar(value = current_contrast)
        
        # Contrast scale
        self.contrast_scale = tk.Scale(self, from_=10, to = 200, orient="horizontal", label= "Contrast", variable= self.contrast_value)
        self.contrast_scale.pack()
        
        self.reset_button = tk.Button(self, text="Reset", command=self.reset_contrast)
        self.reset_button.pack(pady=10)
        
        # Update color when scale values change
        def on_scale_change(event=None):
            self.update_contrast(self.contrast_value.get())

        # Bind scale changes to color update
        self.contrast_scale.bind("<ButtonRelease-1>", on_scale_change)
        
    def update_contrast(self, contrast_value):
        global current_contrast,img_temp, img_current
        img_cv = np.array(img_current)
        img_cv_abs = cv2.convertScaleAbs(img_cv, alpha= ( contrast_value/ 100), beta=0)
        img_temp = Image.fromarray(img_cv_abs)
        current_contrast = contrast_value
        display_image(img_temp, label_temp)
    def reset_contrast(self):
        self.contrast_scale.set(100)
        self.update_contrast(100)

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
            display_image(local_img_temp, label_temp1)


if __name__ == "__main__":
    app = tk.Tk()

    app.title("Image Editor")
    app.geometry("1200x800")
    app.state("zoomed")
    menu_bar = Menu(app)
    app.config(menu=menu_bar)

    file_menu = Menu(menu_bar, tearoff=0)
    edit_menu = Menu(menu_bar, tearoff=0)
    process_menu = Menu(menu_bar,tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)
    menu_bar.add_cascade(label="Process", menu=process_menu)
    file_menu.add_command(label="Open", command=open_image)
    file_menu.add_command(label="Exit", command=quit)
    edit_menu.add_command(label="Resize", command=lambda: open_resize_window(app))
    edit_menu.add_command(label="Change transparency", command=lambda: open_tpc_window(app))
    edit_menu.add_command(label="Paste image", command=lambda: open_paste_window(app))
    edit_menu.add_command(label="Crop image", command=lambda: open_crop_window(app))
    process_menu.add_command(label="Edit Color", command=lambda:open_color_window(app))
    process_menu.add_command(label="Contrast", command=lambda:open_contrast_window(app))
    process_menu.add_command(label="Invert Color", command=lambda:open_invert_window(app))
    
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
