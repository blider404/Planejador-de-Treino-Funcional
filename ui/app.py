# ui/app.py
import customtkinter as ctk
from ui.tabs import DashboardTab, ExerciciosTab, CircuitosTab, AnaliseTab, BibliotecaTab, ConfiguracoesTab

class MainWindow(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        
        self.title("Soldier Academia - Planejador Funcional")
        self.geometry("1300x800")
        self.minsize(1100, 700)
        
        # Cores globais configuradas no inicializador main.py
        
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=(15, 0))
        ctk.CTkLabel(header, text="⚡ SOLDIER ACADEMIA | PLANEJADOR", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=15)
        
        nomes_abas = [
            "📊  Dashboard", 
            "🏋  Exercicios", 
            "🧩  Circuitos", 
            "📈  Análise", 
            "📚  Biblioteca", 
            "⚙  Configurações"
        ]
        
        self.tabs = {}
        for nome in nomes_abas:
            aba = self.tabview.add(nome)
            key = nome.split("  ")[1].lower().replace("í", "i").replace("ç", "c").replace("õ", "o").replace("á", "a")
            
            if key == "dashboard": self.tabs[key] = DashboardTab(aba, self)
            elif key == "exercicios": self.tabs[key] = ExerciciosTab(aba, self)
            elif key == "circuitos": self.tabs[key] = CircuitosTab(aba, self)
            elif key == "analise": self.tabs[key] = AnaliseTab(aba, self)
            elif key == "biblioteca": self.tabs[key] = BibliotecaTab(aba, self)
            elif key == "configuracoes": self.tabs[key] = ConfiguracoesTab(aba, self)
            
            # Ajustando grid dos masters das abas
            aba.grid_columnconfigure(0, weight=1)
            aba.grid_rowconfigure(0, weight=1)
            self.tabs[key].grid(row=0, column=0, sticky="nsew")

        # Inicializa dados
        self.tabs['dashboard'].atualizar_dados()
        self.tabs['biblioteca'].atualizar_lista()
        
        # Evento de mudança de aba para forçar refresh de análise
        self.tabview.configure(command=self._on_tab_change)

    def _on_tab_change(self):
        aba_atual = self.tabview.get()
        if "Análise" in aba_atual:
            # Reflete o circuito atual que está no montador
            itens = self.tabs['circuitos'].itens_circuito
            r, _, dr = self.tabs['circuitos']._ler_ints()
            self.tabs['analise'].atualizar_analise(itens, r, dr)
        elif "Biblioteca" in aba_atual:
            self.tabs['biblioteca'].atualizar_lista()