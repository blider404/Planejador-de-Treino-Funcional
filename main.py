# main.py
import os
import customtkinter as ctk
from database.db_manager import DatabaseManager
from ui.app import MainWindow

# --------------------------------------------------------------------------- #
# CONFIGURAÇÃO VISUAL GLOBAL
# --------------------------------------------------------------------------- #
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Aplicando as cores CustomTkinter por meio dos argumentos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

if __name__ == "__main__":
    # Garante que a pasta data exista
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    # Inicializa o Banco de Dados (irá migrar a base antiga caso seja colocada na pasta data)
    db = DatabaseManager(DATA_DIR)
    
    # Inicializa a Interface
    app = MainWindow(db)
    
    # Ajuste de cores para abas do CTK no nível da aplicação
    app.tabview.configure(
        fg_color="#101418",
        segmented_button_fg_color="#181d24",
        segmented_button_selected_color="#00c2a8",
        segmented_button_selected_hover_color="#00a390",
        segmented_button_unselected_color="#181d24",
        text_color="#ffffff"
    )
    
    app.mainloop()