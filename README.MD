# ⚡ SOLDIER ACADEMIA — Planejador de Treino Funcional

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![CustomTkinter](https://img.shields.io/badge/Interface-CustomTkinter-00c2a8?style=for-the-badge)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey?style=for-the-badge&logo=sqlite)

Um sistema desktop moderno, desenvolvido em Python, focado exclusivamente no **planejamento, organização e análise** de circuitos de treinamento funcional para professores e instrutores da Soldier Academia. 

> **Nota:** Este software é uma ferramenta de back-office estrutural. Ele NÃO possui cronômetros, alarmes ou modos de execução de treino em tempo real. O foco é a montagem profissional e estruturada das fichas de treino.

---

## 🚀 Funcionalidades

- **📊 Dashboard Analítico:** Visão geral da quantidade de exercícios, circuitos montados, grupos musculares e atalhos rápidos.
- **🏋️ Biblioteca de Exercícios:** Cadastro detalhado contendo nome, grupo muscular, tipo (Força, Cardio, etc.), equipamento, nível e padrão de movimento.
- **🧩 Montador de Circuitos Dinâmico:** 
  - Interface em *Grid* responsivo (escolha de 1 a 5 colunas).
  - Reordenação fácil de exercícios (setas de posicionamento).
  - Definição de **descanso individual** após cada exercício.
- **📈 Motor de Análise:** Cálculo automático do tempo de trabalho *vs.* descanso e análise didática do equilíbrio do circuito (Foco Principal).
- **📄 Exportação Profissional:** Geração de fichas de treino estruturadas em **PDF** (via FPDF2), **TXT** ou **JSON**.
- **⚙️ Backup e Restauração:** Sistema integrado de salvamento de segurança do banco de dados SQLite.

---

## 🏗️ Arquitetura do Sistema

O projeto foi refatorado utilizando princípios de código limpo e separação de responsabilidades (MVC adaptado para Desktop):

```text
soldier_academia/
├── main.py                 # Ponto de entrada do sistema
├── requirements.txt        # Dependências do projeto
├── database/               # Modelos e gerenciador do SQLite (Migrações automáticas)
├── services/               # Regras de negócio isoladas (ex: Exportação PDF/JSON)
├── ui/                     # Telas, abas e componentes visuais (CustomTkinter)
├── utils/                  # Funções auxiliares (cálculos de tempo e formatação)
└── data/                   # Armazenamento do arquivo treino_funcional.db