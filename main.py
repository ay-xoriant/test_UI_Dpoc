from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageOps, ImageTk


SUPPORTED_FORMATS = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}


class ImageViewer:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Folder Image Viewer")
        self.root.geometry("1000x700")
        self.root.minsize(480, 360)

        self.image_paths: list[Path] = []
        self.current_index = 0
        self.current_image: Image.Image | None = None
        self.photo: ImageTk.PhotoImage | None = None
        self.folder_label = tk.StringVar(value="Choose a folder to view its images")
        self.status_label = tk.StringVar(value="No images loaded")

        self._build_ui()
        self.root.bind("<Left>", lambda _event: self.show_image(self.current_index - 1))
        self.root.bind("<Right>", lambda _event: self.show_image(self.current_index + 1))
        self.root.bind("<Configure>", self._on_resize)

    def _build_ui(self) -> None:
        toolbar = ttk.Frame(self.root, padding=(12, 10))
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="Open folder...", command=self.choose_folder).pack(side=tk.LEFT)
        ttk.Label(toolbar, textvariable=self.folder_label, anchor="w").pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(12, 0)
        )

        self.image_area = ttk.Frame(self.root)
        self.image_area.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))
        self.image_label = ttk.Label(self.image_area, anchor="center")
        self.image_label.pack(fill=tk.BOTH, expand=True)

        footer = ttk.Frame(self.root, padding=(12, 8))
        footer.pack(fill=tk.X)
        self.previous_button = ttk.Button(footer, text="Previous", command=self.previous_image, state=tk.DISABLED)
        self.previous_button.pack(side=tk.LEFT)
        self.next_button = ttk.Button(footer, text="Next", command=self.next_image, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(footer, textvariable=self.status_label, anchor="e").pack(side=tk.RIGHT, fill=tk.X, expand=True)

    def choose_folder(self) -> None:
        folder = filedialog.askdirectory(title="Choose an image folder")
        if folder:
            self.load_folder(Path(folder))

    def load_folder(self, folder: Path) -> None:
        self.image_paths = sorted(
            (path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_FORMATS),
            key=lambda path: path.name.casefold(),
        )
        self.current_index = 0
        self.folder_label.set(str(folder))

        if not self.image_paths:
            self.current_image = None
            self.image_label.configure(image="", text="No supported images found in this folder")
            self.status_label.set("No images found")
            self._update_navigation()
            return

        self.show_image(0)

    def show_image(self, index: int) -> None:
        if not self.image_paths:
            return

        self.current_index = index % len(self.image_paths)
        path = self.image_paths[self.current_index]
        try:
            with Image.open(path) as image:
                self.current_image = ImageOps.exif_transpose(image).convert("RGB")
        except (OSError, ValueError) as error:
            messagebox.showerror("Unable to open image", f"Could not display {path.name}:\n{error}")
            return

        self.folder_label.set(str(path.parent))
        self.status_label.set(f"{path.name}  |  {self.current_index + 1} of {len(self.image_paths)}")
        self._render_image()
        self._update_navigation()

    def _render_image(self) -> None:
        if self.current_image is None:
            return

        width = max(self.image_area.winfo_width(), 1)
        height = max(self.image_area.winfo_height(), 1)
        preview = self.current_image.copy()
        preview.thumbnail((width, height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(preview)
        self.image_label.configure(image=self.photo, text="")

    def _on_resize(self, event: tk.Event) -> None:
        if event.widget is self.root:
            self._render_image()

    def _update_navigation(self) -> None:
        state = tk.NORMAL if len(self.image_paths) > 1 else tk.DISABLED
        self.previous_button.configure(state=state)
        self.next_button.configure(state=state)

    def previous_image(self) -> None:
        self.show_image(self.current_index - 1)

    def next_image(self) -> None:
        self.show_image(self.current_index + 1)


def main() -> None:
    root = tk.Tk()
    ImageViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()