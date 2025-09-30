
import tkinter as tk
from interfaz.ventana import SistemaVentas

def main():
    root = tk.Tk()
    app = SistemaVentas(root)
    app.crear_interfaz()
    root.mainloop()

if __name__ == "__main__":
    main()
