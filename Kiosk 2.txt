import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from datetime import datetime
import random
import os
import zlib  # Native library used to compress text structures into valid PDFs
import json  # Used for reliable local file persistence of logs and inventories
import urllib.request  # Used to download the requested image links
import io              # Used to handle image bytes in memory
from PIL import Image, ImageTk  # Standard library for handling images in Tkinter

# ─────────────────────────────────────────────
#  COLOUR PALETTE  (McDonald's brand)
# ─────────────────────────────────────────────
C = {
    "red":        "#DA291C",
    "red_dark":   "#B31C11",
    "yellow":     "#FFC72C",
    "dark":       "#27251F",
    "white":      "#FFFFFF",
    "gray_bg":    "#F5F5F0",
    "gray_light": "#FAFAFA",
    "border":     "#E0D8CC",
    "green":      "#1A6E35",
    "blue":       "#1565C0",
    "purple":     "#6A1B9A",
    "text_muted": "#888888",
    "text_light": "#AAAAAA",
}

# ─────────────────────────────────────────────
#  MENU DATA
# ─────────────────────────────────────────────
MENU = [
    # id,  name,                          category,     price,  emoji
    ("B01", "Big Mac",                    "Burgers",     196,   "🍔"),
    ("B02", "Double Cheeseburger",        "Burgers",     154,   "🍔"),
    ("B03", "Quarter Pounder w/ Cheese",  "Burgers",     196,   "🍔"),
    ("B04", "Cheeseburger",               "Burgers",      95,   "🍔"),
    ("B05", "Burger McDo",                "Burgers",      52,   "🍔"),
    ("C01", "1pc. Chicken McDo w/ Rice",  "Chicken",      96,   "🍗"),
    ("C02", "McNuggets 6pc",              "Chicken",     120,   "🍗"),
    ("C03", "McNuggets 10pc",             "Chicken",     195,   "🍗"),
    ("C04", "Crispy Chicken Fillet w/ Rice", "Chicken",    88,   "🥪"),
    ("C05", "2pc. Chicken McDo w/ Rice",  "Chicken",     191,   "🍝"),
    ("F01", "Regular Fries",              "Sides",        72,   "🍟"),
    ("F02", "Medium Fries",               "Sides",        95,   "🍟"),
    ("F03", "Large Fries",                "Sides",       114,   "🍟"),
    ("F04", "Apple Pie",                  "Sides",        47,   "🥧"),
    ("F05", "Corn Cup",                   "Sides",        43,   "🌽"),
    ("D01", "Coke Medium",                "Drinks",       77,   "🥤"),
    ("D02", "Coke Large",                 "Drinks",       87,   "🥤"),
    ("D03", "Iced Coffee",                "Drinks",       83,   "☕"),
    ("D04", "Orange Juice",               "Drinks",       85,   "🍊"),
    ("D05", "McFloat",                    "Drinks",       58,   "🥤"),
    ("M01", "McFlurry Oreo",              "Desserts",     72,   "🍦"),
    ("M02", "Sundae Cone",                "Desserts",     20,   "🍦"),
    ("M03", "Hot Fudge Sundae",           "Desserts",     59,   "🍨"),
    ("M04", "Hot Caramel Sundae",         "Desserts",     59,   "🥧"),
    ("V01", "Big Mac Meal",               "Value Meals", 296,   "🎁"),
    ("V02", "McChicken Meal",             "Value Meals", 169,   "🎁"),
    ("V03", "McNuggets 6pc Meal",         "Value Meals", 185,   "🎁"),
    ("V04", "Crispy Chicken Fillet Meal", "Value Meals", 121,   "🎁"),
]

CATEGORIES = ["All"] + list(dict.fromkeys(item[2] for item in MENU))

SALES_FILE = "sales_history.json"
INVENTORY_FILE = "inventory.json"


def fmt(amount: float) -> str:
    """Format number as Philippine Peso string."""
    return f"₱{amount:,.2f}"


def load_sales_history():
    if os.path.exists(SALES_FILE):
        try:
            with open(SALES_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []


def save_sales_history(history):
    with open(SALES_FILE, "w") as f:
        json.dump(history, f, indent=4)


def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        try:
            with open(INVENTORY_FILE, "r") as f:
                inv = json.load(f)
                for m in MENU:
                    if m[0] not in inv:
                        inv[m[0]] = 100
                return inv
        except:
            pass
    return {m[0]: 100 for m in MENU}


def save_inventory(inv):
    with open(INVENTORY_FILE, "w") as f:
        json.dump(inv, f, indent=4)


# ─────────────────────────────────────────────────────────────────
#  NATIVE PDF EXPORTER UTILITY
# ─────────────────────────────────────────────────────────────────
def export_txt_to_pdf(lines, output_filename="receipt.pdf"):
    """Generates a realistic 3-inch (80mm) thermal tape receipt layout."""
    pdf_content = []

    # Paper Settings: Width expanded to 260 points to guarantee layout padding
    paper_width = 260
    line_height = 12

    # Calculate estimated height matching lines count buffer size bounds safely
    estimated_height = max(350, (len(lines) * line_height) + 60)
    y_pos = estimated_height - 30

    # Approximate width of Courier text at 8 points size
    char_width_pts = 4.8

    for line in lines:
        # Sanitize and convert non-ASCII layout entities into standard printable PDF font equivalents
        clean_line = line.replace("🍔", "").replace(
            "🍟", "").replace("🥤", "").replace("🍗", "")
        clean_line = clean_line.replace("🥪", "").replace(
            "🍝", "").replace("🥧", "").replace("🌽", "")
        clean_line = clean_line.replace("☕", "").replace(
            "🍊", "").replace("🍦", "").replace("🍨", "")
        clean_line = clean_line.replace("🎁", "").replace(
            "👴", "").replace("♿", "").replace("✓", "")
        clean_line = clean_line.replace(
            "🛒", "").replace("💳", "").replace("💛", "")

        # Convert problematic symbols that fail character map lookups in standard PDF text objects
        clean_line = clean_line.replace("₱", "Php ")
        clean_line = clean_line.replace("·", "|")
        clean_line = clean_line.replace("─", "-")
        clean_line = clean_line.replace("═", "=")

        # Escape parenthesis just in case
        clean_line = clean_line.replace("(", "\\(").replace(")", "\\)")

        # Format layout adjustments to constraint widths gracefully inside bounds
        if len(clean_line) > 46:
            clean_line = clean_line[:46]

        # Dynamically center text by shifting the X position coordinate matching string bounds
        line_length_pts = len(clean_line) * char_width_pts
        margin_left = max(12, (paper_width - line_length_pts) / 2)

        pdf_content.append(
            f"BT /F1 8 Tf {line_height} Tl {margin_left:.1f} {y_pos} Td ({clean_line}) Tj ET")
        y_pos -= line_height
        if y_pos < 15:
            break

    stream_data = "\n".join(pdf_content).encode('utf-8')
    objects = []

    def add_object(content):
        objects.append(content)
        return len(objects)

    add_object(b"<< /Type /Catalog /Pages 2 0 R >>")
    add_object(b"<< /Type /Pages /Kids [ 3 0 R ] /Count 1 >>")
    add_object(
        f"<< /Type /Page /Parent 2 0 R /MediaBox [ 0 0 {paper_width} {estimated_height} ] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>".encode('ascii'))
    add_object(b"<< /Length " + str(len(stream_data)).encode('ascii') +
               b" >>\nstream\n" + stream_data + b"\nendstream")
    add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")

    with open(output_filename, "wb") as f:
        f.write(b"%PDF-1.4\n")
        offsets = []
        for idx, obj in enumerate(objects, 1):
            offsets.append(f.tell())
            f.write(f"{idx} 0 obj\n".encode('ascii') + obj +
                    b"\nobj\n" if b"endobj" in obj else f"{idx} 0 obj\n".encode('ascii') + obj + b"\nendobj\n")

        xref_pos = f.tell()
        f.write(b"xref\n")
        f.write(f"0 {len(objects) + 1}\n".encode('ascii'))
        f.write(b"0000000000 65535 f \n")
        for offset in offsets:
            f.write(f"{offset:010d} 00000 n \n".encode('ascii'))

        f.write(b"trailer\n")
        f.write(b"<< /Size " + str(len(objects) +
                1).encode('ascii') + b" /Root 1 0 R >>\n")
        f.write(b"startxref\n")
        f.write(str(xref_pos).encode('ascii') + b"\n")
        f.write(b"%%EOF\n")


# ─────────────────────────────────────────────────────────────────
#  VECTOR ART COMPONENTS
# ─────────────────────────────────────────────────────────────────
class McDonaldsLogo(tk.Canvas):
    """Draws a mathematically accurate, scalable vector McDonald's Golden Arches Logo."""

    def __init__(self, parent, size=120, bg=C["red"], **kwargs):
        super().__init__(parent, width=size, height=size,
                         bg=bg, highlightthickness=0, **kwargs)
        self.size = size
        self.bg = bg
        self.draw_logo()

    def draw_logo(self):
        self.delete("all")
        s = self.size
        paths = [
            # Left Arch
            [(0.12*s, 0.85*s), (0.13*s, 0.22*s), (0.33*s, 0.12*s), (0.50*s, 0.42*s),
             (0.50*s, 0.85*s), (0.43*s, 0.85*s), (0.43*s, 0.48*s), (0.33*s, 0.25*s),
             (0.21*s, 0.32*s), (0.21*s, 0.85*s)],
            # Right Arch
            [(0.50*s, 0.85*s), (0.50*s, 0.42*s), (0.67*s, 0.12*s), (0.87*s, 0.22*s),
             (0.88*s, 0.85*s), (0.79*s, 0.85*s), (0.79*s, 0.32*s), (0.67*s, 0.25*s),
             (0.57*s, 0.48*s), (0.57*s, 0.85*s)]
        ]
        for path in paths:
            flat_coords = []
            for pt in path:
                flat_coords.extend(pt)
            self.create_polygon(
                flat_coords, fill=C["yellow"], outline=C["yellow"], smooth=True, splinesteps=36)


class RoundedButton(tk.Canvas):
    """A canvas-based button with rounded corners and hover effects."""

    def __init__(self, parent, text, command, bg=C["red"], fg=C["white"],
                 hover_bg=C["red_dark"], radius=10, width=160, height=42,
                 font_size=13, font_weight="bold", state="normal", **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=parent.cget("bg"), highlightthickness=0, **kwargs)
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.fg = fg
        self.radius = radius
        self.w = width
        self.h = height
        self.text_str = text
        self.font_size = font_size
        self.font_weight = font_weight
        self.state = state
        self._draw(bg if state == "normal" else "#cccccc")

        if state == "normal":
            self.bind("<Enter>", lambda e: self._draw(hover_bg))
            self.bind("<Leave>", lambda e: self._draw(bg))
            self.bind("<Button-1>", lambda e: self._click())

    def _draw(self, color):
        self.delete("all")
        r = self.radius
        w, h = self.w, self.h
        self.create_polygon(
            r, 0, w - r, 0, w, 0, w, r, w, h - r, w, h,
            w - r, h, r, h, 0, h, 0, h - r, 0, r, 0, 0, r, 0,
            smooth=True, fill=color, outline=color
        )
        display_fg = self.fg if self.state == "normal" else "#888888"
        self.create_text(
            w // 2, h // 2, text=self.text_str, fill=display_fg,
            font=("Arial", self.font_size, self.font_weight), justify="center"
        )

    def _click(self):
        if self.state != "normal":
            return
        self._draw(self.hover_bg)
        self.after(100, lambda: self._draw(self.bg))
        if self.command:
            self.command()

    def config(self, **kwargs):
        if "state" in kwargs:
            self.state = kwargs["state"]
            if self.state == "disabled":
                self._draw("#cccccc")
                self.unbind("<Enter>")
                self.unbind("<Leave>")
                self.unbind("<Button-1>")
            else:
                self._draw(self.bg)
                self.bind("<Enter>", lambda e: self._draw(self.hover_bg))
                self.bind("<Leave>", lambda e: self._draw(self.bg))
                self.bind("<Button-1>", lambda e: self._click())


class ScrollableFrame(tk.Frame):
    """A vertically scrollable frame."""

    def __init__(self, parent, bg=C["gray_bg"], **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)

        self.inner.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all(
            "<MouseWheel>", lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))

    def _on_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)


# ─────────────────────────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────
class McDonaldsKiosk(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("McDonald's Kiosk System")
        self.geometry("1024x768")
        self.minsize(950, 700)
        self.configure(bg=C["dark"])

        # ── State ──────────────────────────────
        self.cart: dict[str, dict] = {}
        self.disc_type: str | None = None
        self.order_type: str | None = None
        self.cur_cat = "All"
        self.grand_total = 0.0
        self.current_receipt_lines = []

        self.inventory = load_inventory()

        # ── Image Storage Dictionary ───────────
        self.menu_photos = {}
        self._load_menu_images()

        # ── Build UI ───────────────────────────
        self._build_header()
        self._build_pages()
        self._show_page("welcome")
        self._tick_clock()

    def _load_menu_images(self):
        """Downloads the unique product image URLs and falls back to Big Mac image if item is omitted."""
        urls = {
            "B01": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-03-06/65e82c80d0140/Menu_Burgers_500x500_BigMac-500.jpg",
            "B02": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-03-06/65e830b48e43b/Menu_Burgers_500x500_DoubleCheeseburger-500.jpg",
            "B03": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-03-06/65e82ef5b45f6/Menu_Burgers_500x500_QPC-500.jpg",
            "B04": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-03-06/65e82ef5b45f6/Menu_Burgers_500x500_QPC-500.jpg",
            "B05": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-03-06/65e82d1f2017d/Menu_Burgers_500x500_BurgerMcDo-500.jpg",
            "C01": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-03-07/65e90d86862ba/Menu_Chicken_500x500_1pcChickenMcDo_Plus_Rice-500.jpg",
            "C02": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSjvNeSWo9C69amMwMDgVsKywISklbsKoXU1eKnMKGHvcqrkNl8Df65E00&s=10",
            "C03": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxOk90P2IWaFqqqKlfLfuFgTsXrw9KeQ0FqMbDzXOxB3ZjBGMFc2_7RgTJ&s=10",
            "C04": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-03-07/65e92d3852167/Menu_Chicken_500x500_1pcChickenFillet_Plus_Rice-500.jpg",
            "C05": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-03-07/65e90c6a6f036/Menu_Chicken_500x500_2pcChickenMcDo_Plus_Rice-500.jpg",
            "F01": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoKMfdZ-BNRMAgRkkfeNLns02ks1b79vPF9Ed0Jg93YQ&s=10",
            "F02": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-03-07/65e934e80364e/Menu_Fries_500x500_FriesMedium-500.jpg",
            "F03": "https://s7d1.scene7.com/is/image/mcdonalds/DC_202002_6053_LargeFries_1564x1564-1:nutrition-calculator-tile?resmode=sharp2",
            "F04": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-06-03/665d89e7153d5/Menu_Desserts_500x500_ApplePie-500-500.jpg",
            "F05": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcuIYkJMIHJnl4JrVSQQ75pZ6QCIy19LxGvMpNnMY1QQ&s=10",
            "D01": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-06-03/665d882937bd9/COKE-500x500px-500-500.jpg",
            "D02": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-06-03/665d886fe3fd1/Menu_Drinks_500x500_CokeZero-500-500.jpg",
            "D03": "https://d3bjzufjcawald.cloudfront.net/public/web/2019-03-07/ceddf4fae63034b1df0a688468431e2b/McCafe-IcedAmericano-500.jpeg",
            "D04": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-06-03/665d8abc293de/Menu_Drinks_500x500_OrangeJuice-500-500.jpg",
            "D05": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-06-03/665d88b1a8571/Menu_Drinks_500x500_McFloatCoke-500-500.jpg",
            "M01": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-06-03/665d88e649b59/Desserts500x500_McFlurryOreo_Mondelez-500-500.jpg",
            "M02": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-06-03/665d8982dd930/Menu_Desserts_500x500_VanillaSundaeCone-500-500.jpg",
            "M03": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-06-03/665d8916d709e/Menu_Desserts_500x500_SundaeHotFudge-500.jpg",
            "M04": "https://d3bjzufjcawald.cloudfront.net/public/web/2024-06-03/665d894a0c0ac/Menu_Desserts_500x500_SundaeCaramel-500-500.jpg",
            "V01": "https://s7d1.scene7.com/is/image/mcdonalds/DC_202409_8936_EVM_M_BigMac_Coke_Glassv26_1564x1564:product-header-mobile?wid=1313&hei=1313&dpr=off",
            "V02": "https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcRub1tNznl9GsHmbgAs7KPcACGHp0u8a74OGJ96MXEy5_PnVlaW",
            "V03": "https://pinoycupidgifts.com/wp-content/uploads/2022/08/6-pc.-Chicken-McNuggets-with-Fries-Meal.jpg",
            "V04": "https://mcdomenuprices.com.ph/wp-content/uploads/2025/08/mcdo-sulit-busog-meals-03.webp",
        }

        # Base fallback image link if not specified in individual keys
        default_url = "https://d3bjzufjcawald.cloudfront.net/public/web/2024-03-06/65e82c80d0140/Menu_Burgers_500x500_BigMac-500.jpg"

        for item in MENU:
            pid = item[0]
            url = urls.get(pid, default_url)
            try:
                req = urllib.request.Request(
                    url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    img_data = response.read()

                pil_img = Image.open(io.BytesIO(img_data))
                pil_img_resized = pil_img.resize(
                    (80, 80), Image.Resampling.LANCZOS)
                self.menu_photos[pid] = ImageTk.PhotoImage(pil_img_resized)
            except Exception as e:
                print(
                    f"Error downloading image for {pid}, using fallback: {e}")
                self.menu_photos[pid] = None

    def _build_header(self):
        self.hdr = tk.Frame(self, bg=C["dark"], height=60)
        self.hdr.pack(fill="x")
        self.hdr.pack_propagate(False)

        self.hdr_left = tk.Frame(self.hdr, bg=C["dark"])
        self.hdr_left.pack(side="left", padx=16, pady=4)

        # Embedded Header Return Button
        self.btn_hdr_back = RoundedButton(self.hdr_left, text="← Cart", command=lambda: self._show_page("cart"),
                                          bg="#444444", fg="white", hover_bg="#555555", radius=6, width=80, height=34, font_size=11)

        self.lbl_hdr_title = tk.Label(
            self.hdr_left, text="💳  Payment", bg=C["dark"], fg=C["yellow"], font=("Arial", 14, "bold"))
        self.lbl_hdr_title.pack(side="left", padx=10)

        self.lbl_time = tk.Label(self.hdr, bg=C["dark"], fg="white",
                                 font=("Arial", 9), justify="right", cursor="hand2")
        self.lbl_time.pack(side="right", padx=16)
        self.lbl_time.bind("<Button-1>", lambda e: self._prompt_admin_login())

    def _tick_clock(self):
        now = datetime.now()
        self.lbl_time.config(text=now.strftime(
            "%a, %b %d %Y\n%I:%M:%S %p\n🔒 ADMIN LOGIN"))
        self.after(1000, self._tick_clock)

    def _build_pages(self):
        self.container = tk.Frame(self, bg=C["gray_bg"])
        self.container.pack(fill="both", expand=True)

        self.pages: dict[str, tk.Frame] = {}
        for name in ("welcome", "order_type", "menu", "cart", "payment", "receipt", "admin_dashboard"):
            frm = tk.Frame(self.container, bg=C["gray_bg"])
            frm.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.pages[name] = frm

        self._build_welcome()
        self._build_order_type_page()
        self._build_menu_page()
        self._build_cart_page()
        self._build_payment_page()
        self._build_receipt_page()
        self._build_admin_dashboard_page()

    def _show_page(self, name: str):
        self.pages[name].lift()

        # Dynamically modulate header states matching custom navigation bounds
        if name in ("welcome", "order_type", "admin_dashboard"):
            self.hdr.pack_forget()
        else:
            self.hdr.pack(fill="x", before=self.container)

        if name == "payment":
            self.hdr.config(bg=C["dark"])
            self.hdr_left.config(bg=C["dark"])
            self.lbl_hdr_title.config(
                text="💳  Payment", bg=C["dark"], fg=C["yellow"])
            self.btn_hdr_back.pack(side="left", padx=(0, 10))
        elif name == "cart":
            self.hdr.config(bg=C["dark"])
            self.hdr_left.config(bg=C["dark"])
            self.lbl_hdr_title.config(
                text="🛒  Your Order", bg=C["dark"], fg=C["yellow"])
            self.btn_hdr_back.pack_forget()
        else:
            self.hdr.config(bg=C["red"])
            self.hdr_left.config(bg=C["red"])
            self.lbl_hdr_title.config(
                text="McDonald's", bg=C["red"], fg="white")
            self.btn_hdr_back.pack_forget()

        if name == "cart":
            self._refresh_cart()
        elif name == "payment":
            self._setup_payment()
        elif name == "menu":
            self._refresh_menu_badges()
        elif name == "admin_dashboard":
            self._refresh_admin_data()

    def _build_welcome(self):
        pg = self.pages["welcome"]
        pg.configure(bg=C["red"])

        center_frame = tk.Frame(pg, bg=C["red"])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        large_logo = McDonaldsLogo(center_frame, size=180, bg=C["red"])
        large_logo.pack(pady=(0, 10))

        tk.Label(center_frame, text="Welcome to McDonald's!", bg=C["red"], fg="white",
                 font=("Arial", 32, "bold")).pack()
        tk.Label(center_frame, text="Order your favorites in seconds",
                 bg=C["red"], fg="#ffcccc", font=("Arial", 14)).pack(pady=4)

        btn = RoundedButton(center_frame, text="TAP TO ORDER",
                            command=lambda: self._show_page("order_type"),
                            bg=C["yellow"], fg=C["dark"],
                            hover_bg="#e6b020", radius=28,
                            width=260, height=60, font_size=18)
        btn.pack(pady=35)

    def _build_order_type_page(self):
        pg = self.pages["order_type"]
        pg.configure(bg=C["gray_bg"])

        top_banner = tk.Frame(pg, bg=C["red"], height=140)
        top_banner.pack(fill="x", side="top")
        top_banner.pack_propagate(False)

        banner_logo = McDonaldsLogo(top_banner, size=100, bg=C["red"])
        banner_logo.place(relx=0.5, rely=0.5, anchor="center")

        center_frame = tk.Frame(pg, bg=C["gray_bg"])
        center_frame.place(relx=0.5, rely=0.55, anchor="center")

        tk.Label(center_frame, text="Where will you be eating today?", bg=C["gray_bg"], fg=C["dark"],
                 font=("Arial", 26, "bold")).pack(pady=(0, 35))

        buttons_row = tk.Frame(center_frame, bg=C["gray_bg"])
        buttons_row.pack()

        def select_type(type_str):
            self.order_type = type_str
            self._show_page("menu")

        dine_card = tk.Frame(buttons_row, bg="white", highlightthickness=1,
                             highlightbackground=C["border"], padx=15, pady=15)
        dine_card.pack(side="left", padx=25)
        tk.Label(dine_card, text="🍽️", bg="white",
                 font=("Arial", 50)).pack(pady=5)
        tk.Label(dine_card, text="DINE IN", bg="white",
                 fg=C["dark"], font=("Arial", 16, "bold")).pack()
        tk.Label(dine_card, text="Eat inside the restaurant", bg="white",
                 fg=C["text_muted"], font=("Arial", 10)).pack(pady=(2, 12))
        RoundedButton(dine_card, text="SELECT", command=lambda: select_type("Dine In"),
                      bg=C["red"], fg="white", hover_bg=C["red_dark"], radius=12, width=170, height=40, font_size=12).pack()

        take_card = tk.Frame(buttons_row, bg="white", highlightthickness=1,
                             highlightbackground=C["border"], padx=15, pady=15)
        take_card.pack(side="left", padx=25)
        tk.Label(take_card, text="🛍️", bg="white",
                 font=("Arial", 50)).pack(pady=5)
        tk.Label(take_card, text="TAKE OUT", bg="white",
                 fg=C["dark"], font=("Arial", 16, "bold")).pack()
        tk.Label(take_card, text="Packaged to take away", bg="white",
                 fg=C["text_muted"], font=("Arial", 10)).pack(pady=(2, 12))
        RoundedButton(take_card, text="SELECT", command=lambda: select_type("Take Out"),
                      bg=C["red"], fg="white", hover_bg=C["red_dark"], radius=12, width=170, height=40, font_size=12).pack()

        RoundedButton(center_frame, text="← Cancel Order", command=self._cancel_and_reset,
                      bg="#dddddd", fg=C["dark"], hover_bg="#cccccc", radius=10, width=140, height=36, font_size=11).pack(pady=(50, 0))

    def _build_menu_page(self):
        pg = self.pages["menu"]
        pg.configure(bg=C["gray_bg"])

        self.cat_frame = tk.Frame(pg, bg=C["dark"], height=48)
        self.cat_frame.pack(fill="x")
        self.cat_frame.pack_propagate(False)
        self._build_cat_bar()

        outer_grid_container = tk.Frame(pg, bg=C["gray_bg"])
        outer_grid_container.pack(fill="both", expand=True)

        self.menu_scroll = ScrollableFrame(
            outer_grid_container, bg=C["gray_bg"])
        self.menu_scroll.pack(side="top", fill="both", expand=True)
        self.menu_grid_frame = self.menu_scroll.inner

        cart_bar = tk.Frame(pg, bg="white", height=64,
                            highlightthickness=1, highlightbackground=C["border"])
        cart_bar.pack(fill="x", side="bottom")
        cart_bar.pack_propagate(False)

        self.lbl_preview_count = tk.Label(
            cart_bar, text="", bg="white", fg=C["text_muted"], font=("Arial", 10))
        self.lbl_preview_count.pack(side="left", padx=14)
        self.lbl_preview_amt = tk.Label(
            cart_bar, text="", bg="white", fg=C["dark"], font=("Arial", 13, "bold"))
        self.lbl_preview_amt.pack(side="left")

        actions_bar = tk.Frame(cart_bar, bg="white")
        actions_bar.pack(side="right", padx=14, pady=10)

        self.btn_cancel_menu = RoundedButton(
            actions_bar, text="❌ Cancel Order", command=self._cancel_and_reset,
            bg="#e0e0e0", fg=C["dark"], hover_bg="#d2d2d2", radius=10, width=150, height=42, font_size=12)
        self.btn_cancel_menu.pack(side="left", padx=6)

        self.btn_view_cart = RoundedButton(
            actions_bar, text="🛒  View Cart", command=lambda: self._show_page("cart"),
            bg=C["red"], fg="white", hover_bg=C["red_dark"], radius=10, width=160, height=42, font_size=13)
        self.btn_view_cart.pack(side="left", padx=6)

        self._render_menu()

    def _build_cat_bar(self):
        for w in self.cat_frame.winfo_children():
            w.destroy()
        for cat in CATEGORIES:
            active = (cat == self.cur_cat)
            fg = C["yellow"] if active else "#aaaaaa"
            lbl = tk.Label(self.cat_frame, text=cat, bg=C["dark"], fg=fg,
                           font=("Arial", 10, "bold"), padx=14, pady=12, cursor="hand2")
            lbl.pack(side="left")
            lbl.bind("<Button-1>", lambda e, c=cat: self._select_cat(c))
            lbl.bind("<Enter>", lambda e, l=lbl,
                     a=active: l.config(fg=C["yellow"]))
            lbl.bind("<Leave>", lambda e, l=lbl, a=active: l.config(
                fg=C["yellow"] if a else "#aaaaaa"))

    def _select_cat(self, cat: str):
        self.cur_cat = cat
        self._build_cat_bar()
        self._render_menu()

    def _render_menu(self):
        for w in self.menu_grid_frame.winfo_children():
            w.destroy()

        items = MENU if self.cur_cat == "All" else [
            m for m in MENU if m[2] == self.cur_cat]
        COLS = 4

        for i in range(COLS):
            self.menu_grid_frame.columnconfigure(
                i, weight=1, uniform="menu_cols")

        last_cat = None
        col = 0
        row = 0

        for pid, name, cat, price, emoji in items:
            if self.cur_cat == "All" and cat != last_cat:
                last_cat = cat
                col = 0
                if row > 0:
                    row += 1
                hdr = tk.Label(self.menu_grid_frame, text=cat.upper(), bg=C["gray_bg"], fg=C["text_light"],
                               font=("Arial", 11, "bold"), anchor="w", padx=16, pady=8)
                hdr.grid(row=row, column=0, columnspan=COLS, sticky="ew")
                row += 1

            card = self._make_product_card(
                self.menu_grid_frame, pid, name, price, emoji)
            card.grid(row=row, column=col, padx=14, pady=14, sticky="nsew")

            col += 1
            if col >= COLS:
                col = 0
                row += 1

    def _make_product_card(self, parent_frame, pid, name, price, emoji):
        qty_in_cart = self.cart.get(pid, {}).get("qty", 0)
        stock = self.inventory.get(pid, 0)

        frame = tk.Frame(parent_frame, bg="white", relief="flat", bd=0,
                         highlightthickness=1, highlightbackground=C["border"], cursor="hand2", width=170, height=225)
        frame.pack_propagate(False)

        emoji_frame = tk.Frame(frame, bg="#FFF8EE", height=80)
        emoji_frame.pack(fill="x")
        emoji_frame.pack_propagate(False)

        # Display individual photo image cache or fallback text logic natively
        photo_img = self.menu_photos.get(pid)
        if photo_img:
            img_lbl = tk.Label(emoji_frame, image=photo_img, bg="#FFF8EE")
            img_lbl.pack(expand=True)
        else:
            img_lbl = tk.Label(emoji_frame, text=emoji,
                               bg="#FFF8EE", font=("Arial", 36))
            img_lbl.pack(expand=True)

        if qty_in_cart > 0:
            badge = tk.Label(emoji_frame, text=str(qty_in_cart), bg=C["red"], fg="white",
                             font=("Arial", 9, "bold"), padx=5, pady=1)
            badge.place(relx=1.0, rely=0, anchor="ne", x=-4, y=4)

        info = tk.Frame(frame, bg="white", padx=8, pady=6)
        info.pack(fill="both", expand=True)
        tk.Label(info, text=f"#{pid}", bg="white", fg=C["text_light"], font=(
            "Arial", 8)).pack(anchor="w")
        tk.Label(info, text=name, bg="white", fg=C["dark"], font=(
            "Arial", 11, "bold"), wraplength=140, justify="left").pack(anchor="w")

        stock_text = f"Stock: {stock}" if stock > 0 else "OUT OF STOCK"
        stock_fg = C["text_muted"] if stock > 5 else (
            C["red"] if stock == 0 else "#D2691E")
        tk.Label(info, text=stock_text, bg="white", fg=stock_fg,
                 font=("Arial", 9, "italic")).pack(anchor="w")

        tk.Label(info, text=fmt(price), bg="white", fg=C["red"], font=(
            "Arial", 13, "bold")).pack(anchor="w", side="bottom", pady=(2, 0))

        if stock > 0:
            def on_enter(e): frame.config(highlightbackground=C["yellow"])
            def on_leave(e): frame.config(highlightbackground=C["border"])
            def on_click(e): self._open_qty_dialog(pid, name, price, emoji)
            for w in [frame, emoji_frame, img_lbl, info] + info.winfo_children():
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.bind("<Button-1>", on_click)
        else:
            frame.config(bg=C["gray_bg"])
            info.config(bg=C["gray_bg"])
            for w in info.winfo_children():
                w.config(bg=C["gray_bg"])

        return frame

    def _refresh_menu_badges(self):
        self._render_menu()
        self._update_fab()

    def _update_fab(self):
        total_items = sum(v["qty"] for v in self.cart.values())
        total_amt = sum(v["price"] * v["qty"] for v in self.cart.values())
        if total_items > 0:
            self.lbl_preview_count.config(
                text=f"{total_items} item{'s' if total_items != 1 else ''}")
            self.lbl_preview_amt.config(text=fmt(total_amt))
        else:
            self.lbl_preview_count.config(text="")
            self.lbl_preview_amt.config(text="")

    def _open_qty_dialog(self, pid, name, price, emoji):
        max_stock = self.inventory.get(pid, 0)
        if max_stock == 0:
            messagebox.showerror(
                "Unavailable", "Item is currently out of stock.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Add to Order")
        dlg.resizable(False, False)
        dlg.configure(bg="white")
        dlg.grab_set()

        dlg.update_idletasks()
        pw, ph = 340, 310
        x = self.winfo_x() + (self.winfo_width() - pw) // 2
        y = self.winfo_y() + (self.winfo_height() - ph) // 2
        dlg.geometry(f"{pw}x{ph}+{x}+{y}")

        qty = tk.IntVar(value=1)
        top = tk.Frame(dlg, bg="white", pady=16, padx=20)
        top.pack(fill="x")

        photo_img = self.menu_photos.get(pid)
        if photo_img:
            tk.Label(top, image=photo_img, bg="#FFF8EE", relief="flat",
                     highlightthickness=1, highlightbackground=C["border"]).pack(side="left", padx=(0, 14))
        else:
            tk.Label(top, text=emoji, bg="#FFF8EE", font=("Arial", 44), width=3, relief="flat",
                     highlightthickness=1, highlightbackground=C["border"]).pack(side="left", padx=(0, 14))

        txt = tk.Frame(top, bg="white")
        txt.pack(side="left")
        tk.Label(txt, text=name, bg="white", fg=C["dark"], font=(
            "Arial", 14, "bold"), wraplength=200, justify="left").pack(anchor="w")
        tk.Label(txt, text=f"{fmt(price)} each", bg="white", fg=C["red"], font=(
            "Arial", 12, "bold")).pack(anchor="w")

        mid = tk.Frame(dlg, bg="white")
        mid.pack(pady=10)

        def dec():
            if qty.get() > 1:
                qty.set(qty.get() - 1)
                upd()

        def inc():
            if qty.get() < min(20, max_stock):
                qty.set(qty.get() + 1)
                upd()

        def upd():
            lbl_qty = mid.winfo_children()[1]
            lbl_qty.config(text=str(qty.get()))
            lbl_sub.config(text=f"Subtotal: {fmt(price * qty.get())}")

        tk.Button(mid, text="−", bg=C["dark"], fg="white", font=(
            "Arial", 18, "bold"), width=3, relief="flat", command=dec, cursor="hand2").pack(side="left", padx=8)
        lbl_qty = tk.Label(mid, text="1", bg="white",
                           fg=C["dark"], font=("Arial", 36, "bold"), width=3)
        lbl_qty.pack(side="left")
        tk.Button(mid, text="+", bg=C["dark"], fg="white", font=("Arial", 18, "bold"),
                  width=3, relief="flat", command=inc, cursor="hand2").pack(side="left", padx=8)

        lbl_sub = tk.Label(
            dlg, text=f"Subtotal: {fmt(price)}", bg="white", fg=C["text_muted"], font=("Arial", 11))
        lbl_sub.pack()

        def confirm():
            q = qty.get()
            if pid in self.cart:
                if self.cart[pid]["qty"] + q > max_stock:
                    messagebox.showerror(
                        "Stock Error", "Cannot add requested amount. Exceeds available stock.")
                    return
                self.cart[pid]["qty"] += q
            else:
                self.cart[pid] = {"id": pid, "name": name, "cat": "",
                                  "price": price, "emoji": emoji, "qty": q}
            dlg.destroy()
            self._update_fab()
            self._render_menu()

        btn_frame = tk.Frame(dlg, bg="white", pady=14, padx=20)
        btn_frame.pack(fill="x")
        RoundedButton(btn_frame, text="ADD TO ORDER", command=confirm,
                      bg=C["red"], fg="white", hover_bg=C["red_dark"], radius=10, width=290, height=44, font_size=14).pack()
        tk.Button(btn_frame, text="Cancel", bg="white", fg=C["text_muted"], relief="flat", font=(
            "Arial", 10), command=dlg.destroy, cursor="hand2").pack(pady=(6, 0))

    def _build_cart_page(self):
        pg = self.pages["cart"]
        pg.configure(bg=C["gray_bg"])

        self.cart_scroll = ScrollableFrame(pg, bg=C["gray_bg"])
        self.cart_scroll.pack(fill="both", expand=True)
        self.cart_inner = self.cart_scroll.inner

    def _refresh_cart(self):
        for w in self.cart_inner.winfo_children():
            w.destroy()

        clear_bar = tk.Frame(self.cart_inner, bg=C["gray_bg"])
        clear_bar.pack(fill="x", padx=12, pady=(10, 0))
        tk.Button(clear_bar, text="🗑️ Clear All Items", bg="#e0e0e0", fg=C["dark"], font=(
            "Arial", 9), relief="flat", command=self._clear_cart, cursor="hand2", padx=10, pady=4).pack(side="right")

        items_box = tk.LabelFrame(self.cart_inner, text=" Order Items ", bg="white", fg=C["dark"], font=(
            "Arial", 10, "bold"), labelanchor="n", padx=8, pady=6)
        items_box.pack(fill="x", padx=12, pady=(5, 6))

        if not self.cart:
            tk.Label(items_box, text="🍟\nYour cart is empty.\nGo back and add some items!",
                     bg="white", fg=C["text_light"], font=("Arial", 12), pady=24).pack()
        else:
            hdr = tk.Frame(items_box, bg=C["dark"])
            hdr.pack(fill="x", pady=(0, 4))
            for txt, w, anchor in [("Item", 0, "w"), ("Qty", 80, "center"), ("Subtotal", 90, "e")]:
                tk.Label(hdr, text=txt, bg=C["dark"], fg=C["yellow"], font=(
                    "Arial", 9, "bold"), width=w if w else 0, anchor=anchor, padx=8, pady=4).pack(side="left", fill="x", expand=(w == 0))
            for pid, item in self.cart.items():
                self._make_cart_row(items_box, pid, item)

        disc_box = tk.LabelFrame(self.cart_inner, text=" Discount / Privilege Card ", bg="white",
                                 fg=C["dark"], font=("Arial", 10, "bold"), labelanchor="n", padx=10, pady=8)
        disc_box.pack(fill="x", padx=12, pady=6)

        disc_row = tk.Frame(disc_box, bg="white")
        disc_row.pack(fill="x", pady=4)
        disc_row.columnconfigure(0, weight=1)
        disc_row.columnconfigure(1, weight=1)
        self._make_disc_card(disc_row, "senior", "👴", "Senior Citizen", 0)
        self._make_disc_card(disc_row, "pwd", "♿", "PWD Discount", 1)

        self.disc_status_lbl = tk.Label(
            disc_box, text="", bg="white", font=("Arial", 10, "bold"), pady=4)
        self.disc_status_lbl.pack()
        self._update_disc_label()

        bill_box = tk.LabelFrame(self.cart_inner, text=" Billing Summary ", bg="white", fg=C["dark"], font=(
            "Arial", 10, "bold"), labelanchor="n", padx=14, pady=10)
        bill_box.pack(fill="x", padx=12, pady=6)

        self.bill_labels: dict[str, tk.Label] = {}
        rows = [("subtotal", "Subtotal", C["dark"]), ("discount", "Discount (20%)", C["green"]),
                ("after_disc", "After Discount", C["dark"]), ("vat", "VAT (12%)", C["dark"])]
        for key, lbl_txt, fg in rows:
            r = tk.Frame(bill_box, bg="white")
            r.pack(fill="x", pady=2)
            tk.Label(r, text=lbl_txt, bg="white", fg=fg,
                     font=("Arial", 11)).pack(side="left")
            v = tk.Label(r, text="₱0.00", bg="white",
                         fg=fg, font=("Arial", 11, "bold"))
            v.pack(side="right")
            self.bill_labels[key] = v

        ttk.Separator(bill_box, orient="horizontal").pack(fill="x", pady=6)
        grand_row = tk.Frame(bill_box, bg="white")
        grand_row.pack(fill="x")
        tk.Label(grand_row, text="Grand Total", bg="white",
                 fg=C["dark"], font=("Arial", 14, "bold")).pack(side="left")
        self.bill_labels["grand"] = tk.Label(
            grand_row, text="₱0.00", bg="white", fg=C["red"], font=("Arial", 18, "bold"))
        self.bill_labels["grand"].pack(side="right")

        # Central Button Action Triggers Panel Block
        btn_action_panel = tk.Frame(bill_box, bg="white")
        btn_action_panel.pack(pady=(12, 0))

        self.proceed_btn = RoundedButton(btn_action_panel, text="PROCEED TO PAYMENT →", command=lambda: self._show_page(
            "payment"), bg=C["red"], fg="white", hover_bg=C["red_dark"], radius=10, width=400, height=46, font_size=14)
        self.proceed_btn.pack(pady=4)

        self.back_to_menu_btn = RoundedButton(btn_action_panel, text="← BACK TO MENU", command=lambda: self._show_page(
            "menu"), bg="#444444", fg="white", hover_bg="#555555", radius=10, width=400, height=38, font_size=12)
        self.back_to_menu_btn.pack(pady=4)

        if not self.cart:
            self.proceed_btn.config(state="disabled")
        self._update_billing()

    def _make_cart_row(self, parent, pid: str, item: dict):
        max_stock = self.inventory.get(pid, 0)
        row = tk.Frame(parent, bg="white", highlightthickness=1,
                       highlightbackground="#f0f0f0")
        row.pack(fill="x", pady=1)

        photo_img = self.menu_photos.get(pid)
        if photo_img:
            tk.Label(row, image=photo_img, bg="white").pack(
                side="left", padx=6)
        else:
            tk.Label(row, text=item["emoji"], bg="white", font=(
                "Arial", 22)).pack(side="left", padx=6)

        info = tk.Frame(row, bg="white")
        info.pack(side="left", fill="both", expand=True, pady=6)
        tk.Label(info, text=item["name"], bg="white", fg=C["dark"], font=(
            "Arial", 11, "bold"), anchor="w").pack(anchor="w")
        tk.Label(info, text=f"{fmt(item['price'])} each", bg="white",
                 fg=C["text_light"], font=("Arial", 9)).pack(anchor="w")

        qf = tk.Frame(info, bg="white")
        qf.pack(anchor="w", pady=2)
        lbl_q = tk.Label(qf, text=str(item["qty"]), bg="white", fg=C["dark"], font=(
            "Arial", 12, "bold"), width=3)

        def dec(p=pid):
            if self.cart[p]["qty"] > 1:
                self.cart[p]["qty"] -= 1
            else:
                del self.cart[p]
            self._update_fab()
            self._refresh_cart()

        def inc(p=pid):
            if self.cart[p]["qty"] < max_stock:
                self.cart[p]["qty"] += 1
            else:
                messagebox.showwarning(
                    "Stock Alert", "Cannot add more. Reached max inventory limit.")
            self._update_fab()
            self._refresh_cart()

        tk.Button(qf, text="−", bg=C["gray_bg"], fg=C["dark"], font=(
            "Arial", 12, "bold"), relief="flat", width=2, command=dec, cursor="hand2").pack(side="left")
        lbl_q.pack(side="left")
        tk.Button(qf, text="+", bg=C["gray_bg"], fg=C["dark"], font=("Arial", 12, "bold"),
                  relief="flat", width=2, command=inc, cursor="hand2").pack(side="left")

        tk.Label(row, text=fmt(item["price"] * item["qty"]), bg="white",
                 fg=C["red"], font=("Arial", 13, "bold"), padx=10).pack(side="right")

    def _make_disc_card(self, parent, dtype, emoji, label, col):
        is_sel = (self.disc_type == dtype)
        sel_bg, sel_bd = ("#E3F2FD", C["blue"]) if dtype == "senior" else (
            "#F3E5F5", C["purple"])
        bg = sel_bg if is_sel else "white"
        bd = sel_bd if is_sel else C["border"]
        fg = sel_bd if is_sel else C["dark"]

        card = tk.Frame(parent, bg=bg, highlightthickness=2,
                        highlightbackground=bd, cursor="hand2")
        card.grid(row=0, column=col, padx=5, pady=4, sticky="ew")
        tk.Label(card, text=emoji, bg=bg, font=("Arial", 26)).pack(pady=(8, 2))
        tk.Label(card, text=label, bg=bg, fg=fg,
                 font=("Arial", 11, "bold")).pack()
        tk.Label(card, text="20% off", bg=bg,
                 fg=C["text_muted"], font=("Arial", 9)).pack(pady=(0, 8))

        if is_sel:
            tk.Label(card, text="✓", bg=bg, fg=fg, font=("Arial", 14, "bold")).place(
                relx=1, rely=0, anchor="ne", x=-6, y=4)

        for w in [card] + card.winfo_children():
            w.bind("<Button-1>", lambda e, dt=dtype: self._toggle_disc(dt))

    def _toggle_disc(self, dt):
        self.disc_type = None if self.disc_type == dt else dt
        self._refresh_cart()

    def _update_disc_label(self):
        if not hasattr(self, "disc_status_lbl"):
            return
        if self.disc_type == "senior":
            self.disc_status_lbl.config(
                text="✓ Senior Citizen Discount Applied — VAT Removed + 20% off", fg=C["blue"], bg="#E3F2FD")
        elif self.disc_type == "pwd":
            self.disc_status_lbl.config(
                text="✓ PWD Discount Applied — VAT Removed + 20% off", fg=C["purple"], bg="#F3E5F5")
        else:
            self.disc_status_lbl.config(text="", bg="white")

    def _calc_billing(self):
        subtotal = sum(v["price"] * v["qty"] for v in self.cart.values())
        disc_amt = subtotal * 0.20 if self.disc_type else 0.0
        after_disc = subtotal - disc_amt
        vat = 0.0 if self.disc_type else (after_disc * 0.12)
        return subtotal, disc_amt, after_disc, vat, after_disc + vat

    def _update_billing(self):
        subtotal, disc_amt, after_disc, vat, grand = self._calc_billing()
        self.grand_total = grand
        self.bill_labels["subtotal"].config(text=fmt(subtotal))
        self.bill_labels["vat"].config(text=fmt(vat))
        self.bill_labels["grand"].config(text=fmt(grand))

        if self.disc_type:
            lbl = "Senior Discount (20%)" if self.disc_type == "senior" else "PWD Discount (20%)"
            self.bill_labels["discount"].config(text=f"−{fmt(disc_amt)}")
            self.bill_labels["after_disc"].config(text=fmt(after_disc))
            for w in self.bill_labels["discount"].master.winfo_children():
                if isinstance(w, tk.Label) and w != self.bill_labels["discount"]:
                    w.config(text=lbl, fg=C["green"])
        else:
            self.bill_labels["discount"].config(text="—")
            self.bill_labels["after_disc"].config(text="—")

    def _clear_cart(self):
        self.cart.clear()
        self._refresh_cart()
        self._update_fab()

    def _cancel_and_reset(self):
        if self.cart:
            if not messagebox.askyesno("Cancel Order", "Are you sure you want to cancel your order? Your selection will be cleared."):
                return
        self.cart.clear()
        self.disc_type = None
        self.order_type = None
        self.cur_cat = "All"
        self._show_page("welcome")

    def _build_payment_page(self):
        pg = self.pages["payment"]
        pg.configure(bg=C["gray_bg"])

        self.pay_scroll = ScrollableFrame(pg, bg=C["gray_bg"])
        self.pay_scroll.pack(fill="both", expand=True)
        container = self.pay_scroll.inner

        # 1. ORDER SUMMARY CARD HEADER BLOCK
        self.sum_box = tk.LabelFrame(container, text=" Order Summary ", bg="white", fg=C["dark"], font=(
            "Arial", 10, "bold"), labelanchor="n", padx=16, pady=12)
        self.sum_box.pack(fill="x", padx=24, pady=(16, 8))

        self.sum_items_frame = tk.Frame(self.sum_box, bg="white")
        self.sum_items_frame.pack(fill="x")

        # Billing Metrics Segment Breakdown
        self.pay_bill_rows = {}
        for key, row_txt, is_bold, color in [
            ("subtotal", "Subtotal", False, C["dark"]),
            ("discount", "Discount Applied", False, C["green"]),
            ("vat", "VAT (12%)", False, C["dark"]),
            ("grand", "Total Amount Due", True, C["red_dark"])
        ]:
            r_frame = tk.Frame(self.sum_box, bg="white")
            r_frame.pack(fill="x", pady=2)

            f_style = ("Arial", 12, "bold") if is_bold else ("Arial", 11)
            tk.Label(r_frame, text=row_txt, bg="white",
                     fg=color, font=f_style).pack(side="left")

            lbl_v = tk.Label(r_frame, text="₱0.00",
                             bg="white", fg=color, font=f_style)
            lbl_v.pack(side="right")
            self.pay_bill_rows[key] = lbl_v

        # 2. CASH ENTER INPUT FIELD CONTROL BOX
        input_container = tk.Frame(
            container, bg="white", highlightthickness=1, highlightbackground="#999999", padx=16, pady=12)
        input_container.pack(fill="x", padx=24, pady=24)

        tk.Label(input_container, text="₱", bg="white", fg="#aaaaaa",
                 font=("Arial", 22)).pack(side="left", padx=(4, 10))

        self.cash_var = tk.StringVar()
        self.cash_var.trace_add(
            "write", lambda *args: self._on_cash_input_change())

        self.entry_cash = tk.Entry(input_container, textvariable=self.cash_var, font=(
            "Arial", 24, "bold"), fg=C["dark"], bd=0, bg="white")
        self.entry_cash.pack(side="left", fill="x", expand=True)

        # 3. ACTION SUBMIT BUTTON ARRAYS
        btn_center_wrap = tk.Frame(container, bg=C["gray_bg"])
        btn_center_wrap.pack(pady=10)

        self.btn_confirm_payment = RoundedButton(btn_center_wrap, text="CONFIRM PAYMENT", command=self._submit_checkout_validate,
                                                 bg=C["red"], fg="white", hover_bg=C["red_dark"], radius=8, width=320, height=46, font_size=14)
        self.btn_confirm_payment.pack(pady=4)

        RoundedButton(btn_center_wrap, text="← Back to Cart", command=lambda: self._show_page("cart"),
                      bg="#d0d0d0", fg=C["dark"], hover_bg="#c0c0c0", radius=8, width=320, height=36, font_size=11).pack(pady=4)

        # 4. REAL-TIME REGISTER CHANGE FOOTER PANEL
        self.change_footer = tk.Frame(pg, bg=C["green"], height=55)
        self.change_footer.pack(fill="x", side="bottom")
        self.change_footer.pack_propagate(False)

        tk.Label(self.change_footer, text="Your Change", bg=C["green"], fg="white", font=(
            "Arial", 13, "bold")).pack(side="left", padx=20)
        self.lbl_change_val = tk.Label(
            self.change_footer, text="₱0.00", bg=C["green"], fg="white", font=("Arial", 20, "bold"))
        self.lbl_change_val.pack(side="right", padx=20)

    def _setup_payment(self):
        """Populates dynamic item labels inside order overview template blocks."""
        for w in self.sum_items_frame.winfo_children():
            w.destroy()

        for pid, item in self.cart.items():
            r = tk.Frame(self.sum_items_frame, bg="white")
            r.pack(fill="x", pady=2)
            tk.Label(r, text=f"{item['name']} × {item['qty']}", bg="white",
                     fg=C["text_muted"], font=("Arial", 11)).pack(side="left")
            tk.Label(r, text=fmt(item['price'] * item['qty']), bg="white",
                     fg=C["text_muted"], font=("Arial", 11)).pack(side="right")

        subtotal, disc_amt, after_disc, vat, grand = self._calc_billing()
        self.grand_total = grand

        self.pay_bill_rows["subtotal"].config(text=fmt(subtotal))
        self.pay_bill_rows["vat"].config(text=fmt(vat))
        self.pay_bill_rows["grand"].config(text=fmt(grand))

        if self.disc_type:
            self.pay_bill_rows["discount"].config(text=f"−{fmt(disc_amt)}")
            self.pay_bill_rows["discount"].master.pack(fill="x")
        else:
            self.pay_bill_rows["discount"].master.pack_forget()

        self.cash_var.set("")
        self.lbl_change_val.config(text="₱0.00")
        self.entry_cash.focus_set()

    def _on_cash_input_change(self):
        try:
            val_str = self.cash_var.get().strip()
            if not val_str:
                self.lbl_change_val.config(text="₱0.00")
                return

            cash_val = float(val_str)
            if cash_val >= self.grand_total:
                diff = cash_val - self.grand_total
                self.lbl_change_val.config(text=fmt(diff))
            else:
                self.lbl_change_val.config(text="₱0.00")
        except ValueError:
            self.lbl_change_val.config(text="₱0.00")

    def _submit_checkout_validate(self):
        try:
            raw_val = self.cash_var.get().strip()
            if not raw_val:
                messagebox.showerror(
                    "Required Field", "Please input an amount to cover payment.")
                return

            cash_tendered = float(raw_val)
            if cash_tendered < self.grand_total:
                messagebox.showerror(
                    "Insufficient Funds", f"Entered cash amount ({fmt(cash_tendered)}) is less than total balance required ({fmt(self.grand_total)}).")
                return

            calculated_change = cash_tendered - self.grand_total
            self._process_checkout("Cash", cash_tendered, calculated_change)

        except ValueError:
            messagebox.showerror(
                "Invalid Amount", "Please input a valid numeric currency amount value.")

    def _process_checkout(self, method, amount_paid, calculated_change):
        for pid, item in self.cart.items():
            self.inventory[pid] = max(
                0, self.inventory.get(pid, 100) - item["qty"])
        save_inventory(self.inventory)

        subtotal, disc_amt, after_disc, vat, grand = self._calc_billing()
        order_no = random.randint(1000, 9999)

        sale_record = {
            "order_no": order_no,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "order_type": self.order_type,
            "payment_method": method,
            "items": [{"id": k, "name": v["name"], "qty": v["qty"], "price": v["price"]} for k, v in self.cart.items()],
            "subtotal": subtotal,
            "discount": disc_amt,
            "vat": vat,
            "total": grand,
            "amount_paid": amount_paid,
            "change_returned": calculated_change
        }

        history = load_sales_history()
        history.append(sale_record)
        save_sales_history(history)

        lines = [
            "               MCDONALD'S              ",
            f"          ORDER NO: #{order_no}          ",
            f"Date: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}",
            f"Mode: {self.order_type} · Pay: {method.upper()}",
            "─" * 39
        ]
        for v in self.cart.values():
            lines.append(
                f"{v['name'][:22]:<22} {v['qty']:>2}x {fmt(v['price']*v['qty']):>12}")

        lines.append("─" * 39)
        lines.append(f"Subtotal:                  {fmt(subtotal):>12}")
        if self.disc_type:
            lines.append(f"Discount:                 -{fmt(disc_amt):>12}")
            lines.append(f"VAT (12%):                 {fmt(vat):>12}")
        else:
            lines.append(
                f"VAT Inclusive:             {fmt(subtotal*0.12):>12}")

        lines.extend([
            "═" * 39,
            f"GRAND TOTAL:               {fmt(grand):>12}",
            f"CASH PAID:                 {fmt(amount_paid):>12}",
            f"CHANGE DUE:                {fmt(calculated_change):>12}",
            "─" * 39,
            "    Thank you for choosing McDonald's!   ",
            "      Please view your digital copy      "
        ])

        self.current_receipt_lines = lines
        self._refresh_receipt_view(order_no, lines)
        self._show_page("receipt")
        self.cart.clear()
        self.disc_type = None

    def _build_receipt_page(self):
        self.pages["receipt"].configure(bg=C["dark"])
        self.receipt_scroll = ScrollableFrame(
            self.pages["receipt"], bg=C["dark"])
        self.receipt_scroll.pack(fill="both", expand=True)
        container = self.receipt_scroll.inner

        tk.Label(container, text="🎉 Order Complete!", bg=C["dark"], fg=C["yellow"], font=(
            "Arial", 24, "bold")).pack(pady=(20, 4))
        tk.Label(container, text="Please collect your formal printed breakdown report below",
                 bg=C["dark"], fg="white", font=("Arial", 11)).pack(pady=(0, 10))

        self.paper = tk.Frame(container, bg="white", padx=24, pady=24,
                              highlightthickness=1, highlightbackground=C["border"])
        self.paper.pack(pady=16, padx=40, fill="none", expand=True)

    def _refresh_receipt_view(self, order_no, raw_lines):
        for w in self.paper.winfo_children():
            w.destroy()
        for line in raw_lines:
            tk.Label(self.paper, text=line, bg="white", fg=C["dark"], font=(
                "Courier", 11), anchor="center", justify="center").pack(fill="x", pady=1)

        actions = tk.Frame(self.paper, bg="white", pady=16)
        actions.pack(fill="x")
        RoundedButton(actions, text="💾 DOWNLOAD RECEIPT PDF", command=self._download_pdf_action,
                      bg=C["green"], fg="white", hover_bg="#114b24", radius=10, width=260, height=44, font_size=12).pack(pady=6)
        RoundedButton(actions, text="DONE & NEW ORDER", command=self._new_order,
                      bg=C["yellow"], fg=C["dark"], hover_bg="#e6b020", radius=10, width=260, height=44, font_size=13).pack(pady=6)

    def _download_pdf_action(self):
        try:
            export_txt_to_pdf(self.current_receipt_lines)
            messagebox.showinfo(
                "Success", "PDF Export successful! File stored as 'receipt.pdf'.")
        except Exception as ex:
            messagebox.showerror(
                "Error", f"Failed to output PDF template: {ex}")

    def _new_order(self):
        self._show_page("welcome")

    # ─────────────────────────────────────────────────────────────────
    #  ADMIN PORTAL CONTROLLERS & WORKSPACES
    # ─────────────────────────────────────────────────────────────────
    def _prompt_admin_login(self):
        dlg = tk.Toplevel(self)
        dlg.title("Admin Authenticator")
        dlg.geometry("300x160")
        dlg.resizable(False, False)
        dlg.configure(bg="white")
        dlg.grab_set()

        x = self.winfo_x() + (self.winfo_width() - 300) // 2
        y = self.winfo_y() + (self.winfo_height() - 160) // 2
        dlg.geometry(f"+{x}+{y}")

        tk.Label(dlg, text="Enter Security Passphrase:", bg="white",
                 fg=C["dark"], font=("Arial", 11, "bold")).pack(pady=12)
        pwd_entry = tk.Entry(dlg, show="*", font=("Arial", 12), justify="center",
                             width=20, highlightthickness=1, highlightbackground=C["border"])
        pwd_entry.pack(pady=4)
        pwd_entry.focus_set()

        def verify():
            if pwd_entry.get() == "admin123":
                dlg.destroy()
                self._show_page("admin_dashboard")
            else:
                messagebox.showerror(
                    "Access Denied", "Invalid administrative code credential entered.")

        tk.Button(dlg, text="Unlock Portal", bg=C["red"], fg="white", font=(
            "Arial", 10, "bold"), padx=12, command=verify, relief="flat", cursor="hand2").pack(pady=12)

    def _build_admin_dashboard_page(self):
        pg = self.pages["admin_dashboard"]
        pg.configure(bg=C["gray_bg"])

        db_hdr = tk.Frame(pg, bg=C["dark"], height=60)
        db_hdr.pack(fill="x")
        db_hdr.pack_propagate(False)

        tk.Label(db_hdr, text="📊 MANAGER CENTRAL OPERATIONS EXECUTIVE CONTROL",
                 bg=C["dark"], fg=C["yellow"], font=("Arial", 14, "bold")).pack(side="left", padx=16)
        RoundedButton(db_hdr, text="← EXIT SYSTEM", command=lambda: self._show_page(
            "welcome"), bg=C["red"], fg="white", hover_bg=C["red_dark"], radius=8, width=130, height=36, font_size=11).pack(side="right", padx=16)

        nb = ttk.Notebook(pg)
        nb.pack(fill="both", expand=True, padx=12, pady=12)

        self.sales_tab = tk.Frame(nb, bg="white")
        self.inv_tab = tk.Frame(nb, bg="white")
        nb.add(self.sales_tab, text=" Sales History Ledger ")
        nb.add(self.inv_tab, text=" Inventory Management Stock ")

        s_left = tk.Frame(self.sales_tab, bg="white", width=250,
                          highlightthickness=1, highlightbackground=C["border"])
        s_left.pack(side="left", fill="y", padx=10, pady=10)
        s_left.pack_propagate(False)

        tk.Label(s_left, text="Financial Summary", bg="white",
                 fg=C["dark"], font=("Arial", 12, "bold")).pack(pady=10)
        self.lbl_admin_total_sales = tk.Label(
            s_left, text="Total Revenue:\n₱0.00", bg="white", fg=C["green"], font=("Arial", 13, "bold"), justify="center")
        self.lbl_admin_total_sales.pack(pady=15)
        self.lbl_admin_order_count = tk.Label(
            s_left, text="Orders Placed: 0", bg="white", fg=C["dark"], font=("Arial", 10, "bold"))
        self.lbl_admin_order_count.pack(pady=5)

        tk.Button(s_left, text="🗑️ Clear Sales History", bg="#b22222", fg="white", font=("Arial", 10, "bold"), relief="flat",
                  command=self._clear_sales_history_action, cursor="hand2").pack(side="bottom", fill="x", padx=10, pady=15)

        s_right = tk.Frame(self.sales_tab, bg="white")
        s_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.sales_text_log = tk.Text(s_right, bg=C["gray_light"], fg=C["dark"], font=(
            "Courier", 10), state="disabled", wrap="none")
        s_scroll_y = ttk.Scrollbar(
            s_right, orient="vertical", command=self.sales_text_log.yview)
        s_scroll_x = ttk.Scrollbar(
            s_right, orient="horizontal", command=self.sales_text_log.xview)
        self.sales_text_log.configure(
            yscrollcommand=s_scroll_y.set, xscrollcommand=s_scroll_x.set)

        s_scroll_y.pack(side="right", fill="y")
        s_scroll_x.pack(side="bottom", fill="x")
        self.sales_text_log.pack(fill="both", expand=True)

        self.inv_scroll = ScrollableFrame(self.inv_tab, bg="white")
        self.inv_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.inv_inner_grid = self.inv_scroll.inner

    def _refresh_admin_data(self):
        history = load_sales_history()
        total_rev = sum(entry["total"] for entry in history)

        self.lbl_admin_total_sales.config(
            text=f"Total Revenue:\n{fmt(total_rev)}")
        self.lbl_admin_order_count.config(
            text=f"Orders Placed: {len(history)}")

        self.sales_text_log.config(state="normal")
        self.sales_text_log.delete("1.0", "end")

        if not history:
            self.sales_text_log.insert(
                "end", "--- NO SYSTEM REVENUE TRANSACTIONS RECORDED YET ---")
        else:
            for s in reversed(history):
                log_line = f"[{s['timestamp']}] ORDER #{s['order_no']} | Type: {s['order_type']} | Paid: {s['payment_method'].upper()}\n"
                log_line += "Items: " + \
                    ", ".join(
                        [f"{i['name']} (x{i['qty']})" for i in s['items']]) + "\n"
                log_line += f"Subtotal: {fmt(s['subtotal'])} | VAT: {fmt(s['vat'])} | Discount: {fmt(s['discount'])} | Tendered: {fmt(s.get('amount_paid', s['total']))} | Change: {fmt(s.get('change_returned', 0.0))} | Total: {fmt(s['total'])}\n"
                log_line += "─" * 80 + "\n"
                self.sales_text_log.insert("end", log_line)

        self.sales_text_log.config(state="disabled")

        for w in self.inv_inner_grid.winfo_children():
            w.destroy()

        th = tk.Frame(self.inv_inner_grid, bg=C["dark"])
        th.pack(fill="x", pady=2)
        tk.Label(th, text="PRODUCT ITEM MATCH", bg=C["dark"], fg=C["yellow"], font=(
            "Arial", 10, "bold"), width=30, anchor="w", padx=10).pack(side="left")
        tk.Label(th, text="CURRENT VOLUME LEVEL", bg=C["dark"], fg=C["yellow"], font=(
            "Arial", 10, "bold"), width=20, anchor="center").pack(side="left")
        tk.Label(th, text="RESTOCK CONTROL ACTION", bg=C["dark"], fg=C["yellow"], font=(
            "Arial", 10, "bold"), width=25, anchor="center").pack(side="left")

        for pid, name, cat, price, emoji in MENU:
            cur_stock = self.inventory.get(pid, 100)
            row = tk.Frame(self.inv_inner_grid, bg="white",
                           highlightthickness=1, highlightbackground="#e0e0e0")
            row.pack(fill="x", pady=2)

            tk.Label(row, text=f"{name} (# {pid})", bg="white", fg=C["dark"], font=(
                "Arial", 11, "bold"), width=30, anchor="w", padx=10).pack(side="left")

            lbl_stock = tk.Label(row, text=str(cur_stock), bg="white", fg=(
                C["red"] if cur_stock == 0 else C["dark"]), font=("Arial", 11, "bold"), width=20, anchor="center")
            lbl_stock.pack(side="left")

            act_frame = tk.Frame(row, bg="white", width=25)
            act_frame.pack(side="left", fill="x", expand=True)

            def restock_item(item_id=pid, label_ref=lbl_stock):
                self.inventory[item_id] = self.inventory.get(item_id, 0) + 50
                save_inventory(self.inventory)
                label_ref.config(
                    text=str(self.inventory[item_id]), fg=C["dark"])

            tk.Button(act_frame, text="+50 Units", bg=C["green"], fg="white", font=(
                "Arial", 9, "bold"), relief="flat", command=restock_item, cursor="hand2", padx=8).pack(pady=4)

    def _clear_sales_history_action(self):
        if messagebox.askyesno("Clear Ledger History", "Are you absolutely certain you wish to purge all persistent financial records? This action cannot be reversed."):
            save_sales_history([])
            self._refresh_admin_data()
            messagebox.showinfo(
                "Purged", "Sales transaction log history reset successfully.")


if __name__ == "__main__":
    app = McDonaldsKiosk()
    app.mainloop()
