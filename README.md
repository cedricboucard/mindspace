# MINDSPACE CLI — Le Conseil Intérieur de Vision

Un outil en ligne de commande qui soumet vos dilemmes à un conseil de trois agents IA, 100 % en français :

- 💎 **J.A.R.V.I.S.** — l'analyste logique, orienté efficacité et optimisation
- 🔴 **ULTRON** — le critique cynique, qui expose les failles et les coûts cachés
- 🟡 **VISION** — l'arbitre, qui pèse les deux avis et rend un verdict actionnable

JARVIS et ULTRON délibèrent en parallèle, puis VISION tranche. Chaque délibération est archivée dans une **mémoire persistante** (`mindspace_memory.json`), réinjectée comme « jurisprudence » dans les délibérations suivantes.

## Installation

```bash
git clone git@github.com:cedricboucard/mindspace.git
cd mindspace
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Fonctionne avec n'importe quelle API compatible OpenAI. Par défaut : [Ollama](https://ollama.com) en local avec `llama3`.

| Variable        | Défaut                        |
|-----------------|-------------------------------|
| `LLM_BASE_URL`  | `http://localhost:11434/v1`   |
| `LLM_API_KEY`   | `ollama`                      |
| `LLM_MODEL`     | `llama3`                      |

## Utilisation

```bash
# Mode interactif
./mindspace.py

# Dilemme passé directement en argument
./mindspace.py "Dois-je refactoriser toute l'application ce week-end ?"

# Afficher l'historique des décisions
./mindspace.py --history
```

En mode interactif, tapez `history` pour voir la jurisprudence et `q` pour quitter.

## Licence

Distribué sous licence MIT. Voir [LICENSE](LICENSE).
