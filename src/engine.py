from collections import deque
from typing import List, Tuple, Optional, Set
import copy

class Engine:
    """
    Moteur de jeu pour le parcours du cavalier sur échiquier avec obstacles.
    
    Pièces:
    - 'K' : Cavalier blanc (Knight)
    - 'P' : Pion blanc (obstacle)
    - 'p' : Pion noir (cible)
    - '.' : Case vide
    """
    
    def __init__(self, width: int = 8, height: int = 8):
        """
        Initialise l'échiquier.
        
        Args:
            width: Largeur de l'échiquier
            height: Hauteur de l'échiquier
        """
        self.width = width
        self.height = height
        self.board = [['.' for _ in range(width)] for _ in range(height)]
        self.knight_pos = None
        self.target_positions = [] #liste des pions noirs
        self.move_count = 0
        self.move_history = []
        
        # Mouvements possibles du cavalier (déplacements en L)
        self.knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
    
    def reset_board(self):
        """Remet l'échiquier à zéro."""
        self.board = [['.' for _ in range(self.width)] for _ in range(self.height)]
        self.knight_pos = None
        self.target_positions = []
        self.move_count = 0
        self.move_history = []
    
    def set_piece(self, row: int, col: int, piece: str) -> bool:
        """
        Place une pièce sur l'échiquier.
        
        Args:
            row: Ligne (0 à height-1)
            col: Colonne (0 à width-1)
            piece: Type de pièce ('K', 'P', 'p', '.')
            
        Returns:
            True si la pièce a été placée avec succès
        """
        if not self.is_valid_position(row, col):
            return False
        
        # Si on retire le cavalier
        if self.board[row][col] == 'K' and piece != 'K':
            self.knight_pos = None
        
        # Si on retire un pion noir
        if self.board[row][col] == 'p' and piece != 'p':
            self.target_positions = [(r, c) for r, c in self.target_positions if (r, c) != (row, col)]
        
        self.board[row][col] = piece
        
        # Mise à jour des positions spéciales
        if piece == 'K':
            self.knight_pos = (row, col)
        elif piece == 'p':
            if (row, col) not in self.target_positions:
                self.target_positions.append((row, col))
        
        return True
    
    def get_piece(self, row: int, col: int) -> Optional[str]:
        """Retourne la pièce à la position donnée."""
        if self.is_valid_position(row, col):
            return self.board[row][col]
        return None
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Vérifie si la position est dans l'échiquier."""
        return 0 <= row < self.height and 0 <= col < self.width
    
    def can_move_to(self, row: int, col: int) -> bool:
        """Vérifie si le cavalier peut se déplacer vers cette position."""
        if not self.is_valid_position(row, col):
            return False
        
        piece = self.board[row][col]
        # Le cavalier peut aller sur une case vide ou manger un pion noir
        return piece == '.' or piece == 'p'
    
    def get_possible_moves(self, from_pos: Tuple[int, int] = None) -> List[Tuple[int, int]]:
        """
        Retourne la liste des mouvements possibles depuis une position.
        
        Args:
            from_pos: Position de départ (par défaut: position actuelle du cavalier)
            
        Returns:
            Liste des positions accessibles
        """
        if from_pos is None:
            from_pos = self.knight_pos
        
        if from_pos is None:
            return []
        
        possible_moves = []
        row, col = from_pos
        
        for dr, dc in self.knight_moves:
            new_row, new_col = row + dr, col + dc
            if self.can_move_to(new_row, new_col):
                possible_moves.append((new_row, new_col))
        
        return possible_moves
    
    def move_knight(self, to_row: int, to_col: int) -> bool:
        """
        Déplace le cavalier vers une nouvelle position.
        
        Args:
            to_row: Ligne de destination
            to_col: Colonne de destination
            
        Returns:
            True si le mouvement a été effectué
        """
        if self.knight_pos is None:
            return False
        
        possible_moves = self.get_possible_moves()
        if (to_row, to_col) not in possible_moves:
            return False
        
        from_row, from_col = self.knight_pos
        captured_piece = self.board[to_row][to_col]
        
        # Effectuer le mouvement
        self.board[from_row][from_col] = '.'
        self.board[to_row][to_col] = 'K'
        self.knight_pos = (to_row, to_col)
        
        # Mise à jour de l'historique
        self.move_history.append({
            'from': (from_row, from_col),
            'to': (to_row, to_col),
            'captured': captured_piece,
            'move_number': self.move_count + 1
        })
        
        self.move_count += 1
        
        # Si on a mangé un pion noir, le retirer des cibles
        if captured_piece == 'p':
            self.target_positions = [(r, c) for r, c in self.target_positions if (r, c) != (to_row, to_col)]
        
        return True
    
    def undo_last_move(self) -> bool:
        """
        Annule le dernier mouvement.
        
        Returns:
            True si l'annulation a été effectuée
        """
        if not self.move_history:
            return False
        
        last_move = self.move_history.pop()
        from_pos = last_move['from']
        to_pos = last_move['to']
        captured_piece = last_move['captured']
        
        # Restaurer les positions
        self.board[from_pos[0]][from_pos[1]] = 'K'
        self.board[to_pos[0]][to_pos[1]] = captured_piece
        self.knight_pos = from_pos
        self.move_count -= 1
        
        # Si on avait capturé un pion noir, le remettre dans les cibles
        if captured_piece == 'p':
            self.target_positions.append(to_pos)
        
        return True
    
    def find_shortest_path_to_target(self) -> Optional[List[Tuple[int, int]]]:
        """
        Trouve le chemin le plus court vers le pion noir le plus proche.
        Utilise l'algorithme BFS.
        
        Returns:
            Liste des positions du chemin (sans la position de départ) ou None
        """
        if self.knight_pos is None or not self.target_positions:
            return None
        
        start = self.knight_pos
        targets = set(self.target_positions)
        
        # BFS
        queue = deque([(start, [])])
        visited = {start}
        
        while queue:
            current_pos, path = queue.popleft()
            
            # Si on atteint une cible
            if current_pos in targets:
                return path + [current_pos]
            
            # Explorer les mouvements possibles
            for next_pos in self.get_possible_moves(current_pos):
                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, path + [current_pos]))
        
        return None
    
    def solve_optimal(self) -> Optional[List[Tuple[int, int]]]:
        """
        Trouve la solution optimale (chemin le plus court vers n'importe quel pion noir).
        
        Returns:
            Liste des positions du chemin complet ou None si pas de solution
        """
        path = self.find_shortest_path_to_target()
        if path:
            # Retirer la position de départ du chemin
            return path[1:] if len(path) > 1 else path
        return None
    
    def is_game_won(self) -> bool:
        """Vérifie si le jeu est gagné (tous les pions noirs mangés)."""
        return len(self.target_positions) == 0
    
    def get_board_state(self) -> List[List[str]]:
        """Retourne une copie de l'état actuel de l'échiquier."""
        return copy.deepcopy(self.board)
    
    def display_board(self) -> str:
        """
        Affiche l'échiquier sous forme de chaîne.
        
        Returns:
            Représentation textuelle de l'échiquier
        """
        result = []
        result.append("  " + " ".join(str(i) for i in range(self.width)))
        result.append("  " + "-" * (self.width * 2 - 1))
        
        for i, row in enumerate(self.board):
            result.append(f"{i}| " + " ".join(row))
        
        result.append(f"\nCavalier en: {self.knight_pos}")
        result.append(f"Pions noirs restants: {len(self.target_positions)}")
        result.append(f"Nombre de mouvements: {self.move_count}")
        
        return "\n".join(result)
    
    def get_game_stats(self) -> dict:
        """Retourne les statistiques de la partie."""
        return {
            'board_size': (self.height, self.width),
            'knight_position': self.knight_pos,
            'targets_remaining': len(self.target_positions),
            'targets_positions': self.target_positions.copy(),
            'move_count': self.move_count,
            'game_won': self.is_game_won(),
            'possible_moves': self.get_possible_moves() if self.knight_pos else []
        }


# Exemple d'utilisation
if __name__ == "__main__":
    # Créer un échiquier 6x6
    engine = Engine(6, 6)
    
    # Placer les pièces
    engine.set_piece(0, 0, 'K')  # Cavalier blanc
    engine.set_piece(2, 2, 'P')  # Pion blanc (obstacle)
    engine.set_piece(3, 3, 'P')  # Pion blanc (obstacle)
    engine.set_piece(5, 5, 'p')  # Pion noir (cible)
    
    print("État initial:")
    print(engine.display_board())
    
    # Trouver le chemin optimal
    optimal_path = engine.solve_optimal()
    if optimal_path:
        print(f"\nChemin optimal trouvé: {optimal_path}")
        print(f"Nombre de mouvements nécessaires: {len(optimal_path)}")
        
        # Simuler les mouvements
        for i, (row, col) in enumerate(optimal_path):
            print(f"\nMouvement {i+1}: vers ({row}, {col})")
            engine.move_knight(row, col)
            print(engine.display_board())
    else:
        print("\nAucun chemin trouvé!")
    
    print(f"\nStatistiques finales:")
    stats = engine.get_game_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
