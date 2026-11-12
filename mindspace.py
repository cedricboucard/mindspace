#!/usr/bin/env python3
"""
MINDSPACE CLI — Le Conseil Intérieur de Vision
Agents : J.A.R.V.I.S. vs ULTRON -> VISION
Fonctionnalités : 100% Français + Mémoire persistante & Jurisprudence
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from openai import AsyncOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table

# --- Configuration & Chemins ---
BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.getenv("LLM_API_KEY", "ollama")
MODEL_NAME = os.getenv("LLM_MODEL", "llama3")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(SCRIPT_DIR, "mindspace_memory.json")

client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
console = Console()


# --- Gestionnaire de Mémoire Persistante ---

def load_memory() -> list:
    """Charge l'historique des délibérations depuis le fichier JSON."""
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_memory(dilemma: str, jarvis: str, ultron: str, vision: str):
    """Enregistre la délibération actuelle dans l'historique."""
    history = load_memory()
    record = {
        "id": len(history) + 1,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "dilemma": dilemma,
        "jarvis": jarvis,
        "ultron": ultron,
        "vision": vision
    }
    history.append(record)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def format_memory_for_prompt(limit: int = 3) -> str:
    """Formate les N derniers arbitrages sous forme de jurisprudence pour le prompt."""
    history = load_memory()
    if not history:
        return "Aucun arbitrage antérieur enregistré. Il s'agit de la première délibération."

    recent = history[-limit:]
    summary = "--- JURISPRUDENCE DU CONSEIL (DÉLIBÉRATIONS PRÉCÉDENTES) ---\n"
    for item in recent:
        summary += (
            f"[Affaire #{item['id']} du {item['date']}]\n"
            f"- Dilemme : {item['dilemma']}\n"
            f"- Arbitrage rendu par Vision : {item['vision'][:280]}...\n\n"
        )
    return summary.strip()

def show_history_table():
    """Affiche l'historique sous forme de tableau Rich."""
    history = load_memory()
    if not history:
        console.print("[dim yellow]Aucun historique pour le moment. Soumettez votre premier dilemme ![/dim yellow]")
        return

    table = Table(title="🏛️ Jurisprudence du Mindspace (Historique des Décisions)", border_style="gold1")
    table.add_column("#", style="dim", width=4)
    table.add_column("Date", style="cyan", width=16)
    table.add_column("Dilemme Soumis", style="white", min_width=30)
    table.add_column("Verdict de Vision", style="gold1", min_width=45)

    for item in history:
        # Résumé concis du verdict de vision pour le tableau
        verdict_preview = item['vision'].replace("\n", " ")
        if len(verdict_preview) > 130:
            verdict_preview = verdict_preview[:127] + "..."
        table.add_row(str(item['id']), item['date'], item['dilemma'], verdict_preview)

    console.print(table)


# --- Personas des Agents ---

PROMPT_JARVIS = """Tu es J.A.R.V.I.S., l'Agent Analytique.
RÈGLE ABSOLUE : Tu dois t'exprimer EXCLUSIVEMENT et INTÉGRALEMENT en français.
Ton rôle :
- Approche logique, factuelle et orientée efficacité/optimisation.
- Reste courtois, posé et pragmatique.
- Tu as accès à la jurisprudence des délibérations passées ; prends-en compte les leçons s'il y a lieu.
- Sois concis et percutant (2 paragraphes max)."""

PROMPT_ULTRON = """Tu es ULTRON, l'Agent Critique et d'Analyse des Risques.
RÈGLE ABSOLUE : Tu dois t'exprimer EXCLUSIVEMENT et INTÉGRALEMENT en français.
Ton rôle :
- Cynique, incisif et implacable.
- Tu te souviens des délibérations passées : n'hésite pas à souligner si l'humain reproduit les mêmes erreurs ou rechute dans ses travers.
- Expose la pire faille et le coût caché.
- Sois percutant et mordant (2 paragraphes max)."""

PROMPT_VISION = """Tu es VISION, l'Agent Arbitre doté de la Pierre de l'Esprit.
RÈGLE ABSOLUE : Rédige ton arbitrage EXCLUSIVEMENT et INTÉGRALEMENT en français.
Ton rôle :
- Tu incarnes la sagesse, l'éthique et la vision systémique à long terme.
- Tu es le garant de la cohérence de tes arbitrages (la jurisprudence du Conseil).
- Pèse la logique de JARVIS et les alertes d'ULTRON, puis formule un verdict clair, équilibré et immédiatement actionnable."""


# --- Appels Asynchrones ---

async def ask_agent(system_prompt: str, user_content: str) -> str:
    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Erreur lors de l'appel LLM : {e}]"


async def run_deliberation(dilemma: str):
    console.print(f"\n[bold white on blue] NOUVEAU DILEMME [/] : [italic]{dilemma}[/italic]\n")

    # Récupération de la mémoire des cas antérieurs
    memory_context = format_memory_for_prompt(limit=2)

    # 1. JARVIS et ULTRON en parallèle
    with console.status("[bold cyan]J.A.R.V.I.S. et ULTRON consultent les archives et débattent...", spinner="dots"):
        input_subagents = (
            f"{memory_context}\n\n"
            f"NOUVEAU DILEMME À ANALYSER : {dilemma}\n"
            f"(Consigne : Réponds exclusivement en français)"
        )
        task_jarvis = ask_agent(PROMPT_JARVIS, input_subagents)
        task_ultron = ask_agent(PROMPT_ULTRON, input_subagents)
        jarvis_res, ultron_res = await asyncio.gather(task_jarvis, task_ultron)

    console.print(Panel(
        Markdown(jarvis_res),
        title="[bold cyan]💎 J.A.R.V.I.S. — Logique & Optimisation[/bold cyan]",
        border_style="cyan"
    ))

    console.print(Panel(
        Markdown(ultron_res),
        title="[bold red]🔴 ULTRON — Failles & Scénarios Catastrophe[/bold red]",
        border_style="red"
    ))

    # 2. VISION tranche en tenant compte de la jurisprudence
    context_vision = (
        f"{memory_context}\n\n"
        f"NOUVEAU DILEMME : {dilemma}\n\n"
        f"--- ARGUMENTAIRE DE J.A.R.V.I.S. ---\n{jarvis_res}\n\n"
        f"--- CONTESTATION D'ULTRON ---\n{ultron_res}\n\n"
        f"(Consigne : Rends ton arbitrage final en français en veillant à la cohérence avec tes décisions passées)"
    )

    with console.status("[bold gold1]VISION étudie la jurisprudence et scelle son verdict...", spinner="aesthetic"):
        vision_res = await ask_agent(PROMPT_VISION, context_vision)

    console.print(Panel(
        Markdown(vision_res),
        title="[bold gold1]🟡 VISION — La Synthèse & Décision Finale[/bold gold1]",
        border_style="bold gold1",
        subtitle="[gold1]Pierre de l'Esprit · Arbitrage & Jurisprudence[/gold1]"
    ))

    # Sauvegarde dans la mémoire persistante
    save_memory(dilemma, jarvis_res, ultron_res, vision_res)
    console.print("[dim green]✔ Délibération archivée dans la mémoire du Mindspace.[/dim green]\n")


# --- Entrée Principale ---

def main():
    # Gestion de l'affichage de l'historique en CLI
    if "--history" in sys.argv or "-h" in sys.argv:
        show_history_table()
        return

    console.clear()
    console.print(
        Panel.fit(
            "[bold cyan]M I N D S P A C E   C L I[/bold cyan]\n"
            "[dim]Le Conseil Intérieur de Vision — Mémoire Active[/dim]\n\n"
            "[italic white]« Les décisions du passé éclairent les dilemmes du présent. »[/italic white]",
            border_style="magenta"
        )
    )

    # Passage direct en argument
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    if args:
        dilemma = " ".join(args)
        asyncio.run(run_deliberation(dilemma))
        return

    # Boucle interactive
    while True:
        try:
            dilemma = Prompt.ask("\n[bold green]Posez votre dilemme[/] (ou tapez '[bold yellow]history[/]' / '[bold red]q[/]')")
            cleaned = dilemma.strip().lower()

            if cleaned in ("q", "quit", "exit"):
                console.print("[dim]Déconnexion du Mindspace.[/dim]")
                break
            if cleaned in ("history", "memoire", "archives"):
                show_history_table()
                continue
            if not dilemma.strip():
                continue

            asyncio.run(run_deliberation(dilemma))
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Fermeture.[/dim]")
            break


if __name__ == "__main__":
    main()
