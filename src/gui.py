from .engine import Engine
import tkinter as tk

# couleur des cases
COLORS = ['Cornsilk','Sienna']

# États du jeu
STATE_NONE = 0
STATE_PLAYING = 1
STATE_WON = 2

# Taille des cases
SIDE = 64

# Format: (largeur, hauteur, [(row, col, piece), ...])
PUZZLES = [
    # Niveau 1: 6x6 simple
    (6, 6, [
        (0, 0, 'K'),  # Cavalier
        (2, 2, 'P'),  # Obstacle
        (5, 5, 'p')   # Cible
    ]),
    # Niveau 2: 8x8 avec plus d'obstacles
    (8, 8, [
        (0, 0, 'K'),   # Cavalier
        (2, 2, 'P'),   # Obstacles
        (3, 3, 'P'),
        (4, 4, 'P'),
        (7, 7, 'p'),   # Cible
        (6, 5, 'p')    # Deuxième cible
    ]),
    # Ajoutez d'autres niveaux ici...
]
class Board(tk.Canvas):
    """Classe pour afficher l'échiquier graphiquement."""
    
    def __init__(self, parent, *args, **kwargs):
        # Calculer la taille initiale du canvas
        initial_size = 8 * SIDE  # Taille par défaut 8x8
        tk.Canvas.__init__(self, parent, width=initial_size, height=initial_size, 
                          bg='white', *args, **kwargs)
        self.app = parent
        self.engine = parent.engine
        self.state = STATE_NONE
        self.selected_pos = None
        
        # Bind des événements de clic
        self.bind("<Button-1>", self.on_click)
        
    def draw_game(self):
        """Dessine l'échiquier et les pièces."""
        self.delete("all")
        
        if not self.engine or not self.engine.knight_pos:
            return
        
        # Redimensionner le canvas selon la taille du plateau
        canvas_width = self.engine.width * SIDE
        canvas_height = self.engine.height * SIDE
        self.config(width=canvas_width, height=canvas_height)
        
        # Dessiner les cases
        for row in range(self.engine.height):
            for col in range(self.engine.width):
                x1, y1 = col * SIDE, row * SIDE
                x2, y2 = x1 + SIDE, y1 + SIDE
                
                # Couleur des cases (échiquier)
                color = COLORS[0] if (row + col) % 2 == 0 else COLORS[1]
                
                # Surligner les mouvements possibles
                if self.selected_pos == self.engine.knight_pos:
                    possible_moves = self.engine.get_possible_moves()
                    if (row, col) in possible_moves:
                        color = "lightgreen"
                
                # Surligner la case sélectionnée
                if self.selected_pos == (row, col):
                    color = "yellow"
                
                self.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                
                # Dessiner les pièces
                piece = self.engine.get_piece(row, col)
                if piece and piece != '.':
                    self.draw_piece(row, col, piece)
    
    def draw_piece(self, row, col, piece):
        """Dessine une pièce sur la case donnée."""
        x = col * SIDE + SIDE // 2
        y = row * SIDE + SIDE // 2
        
        # Utiliser les images si disponibles
        image_map = {'K': 1, 'P': 2, 'p': 3}  # Mapping avec les indices d'images
        
        if hasattr(self.app, 'images') and piece in image_map:
            image_idx = image_map[piece]
            if image_idx in self.app.images:
                self.create_image(x, y, image=self.app.images[image_idx])
                return
        
        # Fallback: dessiner du texte si pas d'image
        colors = {'K': 'blue', 'P': 'gray', 'p': 'red'}
        symbols = {'K': '♘', 'P': '♙', 'p': '♟'}
        
        color = colors.get(piece, 'black')
        symbol = symbols.get(piece, piece)
        
        self.create_text(x, y, text=symbol, font=("Arial", 20), fill=color)
    
    def on_click(self, event):
        """Gère les clics sur l'échiquier."""
        if self.state != STATE_PLAYING:
            return
        
        # Convertir les coordonnées pixel en coordonnées de case
        col = event.x // SIDE
        row = event.y // SIDE
        
        if not self.engine.is_valid_position(row, col):
            return
        
        # Si le cavalier est sélectionné et on clique sur une case valide
        if self.selected_pos == self.engine.knight_pos:
            possible_moves = self.engine.get_possible_moves()
            if (row, col) in possible_moves:
                # Effectuer le mouvement
                if self.engine.move_knight(row, col):
                    self.selected_pos = None
                    self.app.menu.update_display()
                    self.draw_game()
                    
                    # Vérifier si le jeu est gagné
                    if self.engine.is_game_won():
                        self.state = STATE_WON
                        self.show_victory_message()
                return
        
        # Sélectionner le cavalier
        if (row, col) == self.engine.knight_pos:
            self.selected_pos = (row, col)
            self.draw_game()
        else:
            self.selected_pos = None
            self.draw_game()
    
    def show_victory_message(self):
        """Affiche un message de victoire."""
        # Centrer le message sur le canvas
        x = self.engine.width * SIDE // 2
        y = self.engine.height * SIDE // 2
        
        self.create_rectangle(x-100, y-30, x+100, y+30, 
                            fill="gold", outline="black", width=3)
        self.create_text(x, y, text="VICTOIRE!", 
                        font=("Arial", 16, "bold"), fill="red")


class Menu(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.app = parent
        self.level_nb = 0
        self.engine = parent.engine
        self.board = parent.board
        
        # Variables pour l'affichage
        self.var_level = tk.StringVar()
        self.var_tries = tk.StringVar()
        self.var_max_tries = tk.StringVar()
        self.var_moves = tk.StringVar()
        
        # Interface
        self.setup_ui()
        
    def setup_ui(self):
        """Initialise l'interface utilisateur du menu."""
        # Titre du niveau
        self.level = tk.Label(self, textvariable=self.var_level, 
                             font=("Helvetica", 16, "bold"))
        self.level.pack(side='top', pady=10)
        
        # Frame pour les boutons de navigation
        self.boutons = tk.Frame(self)
        self.boutons.pack(side='top', pady=10)
        
        # Boutons de navigation (avec images si disponibles)
        if hasattr(self.app, 'images') and 4 in self.app.images and 5 in self.app.images:
            self.bouton_prev = tk.Button(self.boutons, image=self.app.images[4],
                                       command=self.prev_level)
            self.bouton_next = tk.Button(self.boutons, image=self.app.images[5],
                                       command=self.next_level)
        else:
            self.bouton_prev = tk.Button(self.boutons, text="← Précédent",
                                       command=self.prev_level)
            self.bouton_next = tk.Button(self.boutons, text="Suivant →",
                                       command=self.next_level)
        
        self.bouton_prev.pack(side="left", padx=5)
        self.bouton_next.pack(side="right", padx=5)
        
        # Frame pour les informations
        self.info = tk.Frame(self)
        self.info.pack(side='top', pady=10)
        
        # Affichage des mouvements
        tk.Label(self.info, text="Mouvements:", font=("Helvetica", 12)).pack()
        self.moves = tk.Label(self.info, textvariable=self.var_moves, 
                             font=("Helvetica", 14, "bold"))
        self.moves.pack()
        
        # Boutons d'action
        self.actions = tk.Frame(self)
        self.actions.pack(side='top', pady=20)
        
        self.btn_restart = tk.Button(self.actions, text="Recommencer",
                                   command=self.restart_level)
        self.btn_restart.pack(pady=5)
        
        self.btn_hint = tk.Button(self.actions, text="Indice",
                                command=self.show_hint)
        self.btn_hint.pack(pady=5)
        
        self.btn_solve = tk.Button(self.actions, text="Résoudre",
                                 command=self.auto_solve)
        self.btn_solve.pack(pady=5)
        
    def load_level(self):
        """Charge le niveau actuel."""
        if 0 <= self.level_nb < len(PUZZLES):
            width, height, pieces = PUZZLES[self.level_nb]
            
            # Réinitialiser l'engine avec la nouvelle taille
            self.engine.width = width
            self.engine.height = height
            self.engine.reset_board()
            
            # Placer les pièces
            for row, col, piece in pieces:
                self.engine.set_piece(row, col, piece)
            
            # Mettre à jour l'affichage
            self.board.state = STATE_PLAYING
            self.var_level.set(f"Niveau {self.level_nb + 1}")
            self.update_display()
            self.board.draw_game()
    
    def update_display(self):
        """Met à jour l'affichage des informations."""
        self.var_moves.set(str(self.engine.move_count))
        
        # Mettre à jour l'état des boutons
        self.bouton_prev.config(state="normal" if self.level_nb > 0 else "disabled")
        self.bouton_next.config(state="normal" if self.level_nb < len(PUZZLES)-1 else "disabled")
    
    def next_level(self):
        """Passe au niveau suivant."""
        if self.level_nb < len(PUZZLES) - 1:
            self.level_nb += 1
            self.load_level()
    
    def prev_level(self):
        """Passe au niveau précédent."""
        if self.level_nb > 0:
            self.level_nb -= 1
            self.load_level()
    
    def restart_level(self):
        """Recommence le niveau actuel."""
        self.load_level()
    
    def show_hint(self):
        """Affiche un indice (premier mouvement optimal)."""
        if self.board.state == STATE_PLAYING:
            optimal_path = self.engine.solve_optimal()
            if optimal_path and len(optimal_path) > 0:
                next_move = optimal_path[0]
                # Surligner temporairement le mouvement suggéré
                self.board.selected_pos = next_move
                self.board.draw_game()
                # Retirer le surlignage après 2 secondes
                self.after(2000, lambda: self.clear_hint())
    
    def clear_hint(self):
        """Retire l'affichage de l'indice."""
        self.board.selected_pos = None
        self.board.draw_game()
    
    def auto_solve(self):
        """Résout automatiquement le niveau."""
        if self.board.state == STATE_PLAYING:
            optimal_path = self.engine.solve_optimal()
            if optimal_path:
                self.animate_solution(optimal_path, 0)
    
    def animate_solution(self, path, step):
        """Anime la solution étape par étape."""
        if step < len(path):
            row, col = path[step]
            if self.engine.move_knight(row, col):
                self.update_display()
                self.board.draw_game()
                
                if self.engine.is_game_won():
                    self.board.state = STATE_WON
                    self.board.show_victory_message()
                else:
                    # Continuer l'animation après 500ms
                    self.after(500, lambda: self.animate_solution(path, step + 1))


if __name__ == "__main__":
    pass
