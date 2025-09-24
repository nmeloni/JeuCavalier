import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path

from src.gui import Board, Menu
from src.engine import Engine



class MainApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.root.title("Jeu du cavalier")
        
        # Initialiser l'engine (il sera configuré lors du chargement du niveau)
        self.engine = Engine(8, 8)  # Taille par défaut
        
        # Charger les images depuis le répertoire assets/img
        self.assets_path = Path(__file__).parent / "assets" / "img"
        #print(self.assets_path.parent.parent / "assets" / "img")
        self.img_name = ["cavalier.png", "pion.png", "pion_noir.png", "left.png", "right.png"]
        self.init_images()
        
        # Créer l'interface
        self.board = Board(self)
        self.board.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        
        self.menu = Menu(self)
        self.menu.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        # Charger le premier niveau
        self.menu.load_level()
    
    def init_images(self):
        """Charge les images du jeu."""
        self.images = {}
        for i in range(len(self.img_name)):
            name = self.assets_path / self.img_name[i]
            try:
                image = Image.open(name)
                image = image.resize((SIDE, SIDE), Image.LANCZOS)
                img = ImageTk.PhotoImage(image)
                self.images[i + 1] = img
            except FileNotFoundError:
                print(f"Image {name} non trouvée, utilisation du mode texte")
                continue
    
    def mainloop(self):
        self.root.mainloop()


if __name__ == '__main__':
    App = MainApp(tk.Tk())
    App.pack(side="top", fill="both", expand=True)
    App.mainloop()
