import tkinter as tk


class Window:
    def __init__(self, title="Canvas", width=800, height=600):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")

        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

    def run(self):
        self.root.mainloop()