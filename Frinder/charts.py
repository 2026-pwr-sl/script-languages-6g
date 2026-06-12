from collections import Counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from models import Recipe


def recipe_difficulty(recipe):
    if isinstance(recipe, Recipe):
        return recipe.difficulty
    if isinstance(recipe, dict):
        return recipe.get("difficulty", "Unknown")
    return "Unknown"


def generate_summary_graphs(missing_counter, suggestions, path_missing, path_difficulty):
    fig1 = plt.figure(figsize=(6, 5))
    fig1.patch.set_facecolor('#f4f7fb')
    ax1 = fig1.add_subplot(111)

    if missing_counter:
        top_missing = missing_counter.most_common(5)
        names = [item[0].capitalize() for item in top_missing]
        counts = [item[1] for item in top_missing]

        ax1.bar(names, counts, color='#0C9961', edgecolor='#0a8253', alpha=0.8)
        ax1.set_title("Most Needed Ingredients", fontsize=12, fontweight='bold', color='#1f4f46')
        ax1.set_ylabel("Recipe Appearances")
        ax1.grid(axis='y', linestyle='--', alpha=0.5)
    else:
        ax1.text(0.5, 0.5, "No missing data", ha='center', va='center')

    plt.tight_layout()
    fig1.savefig(path_missing, dpi=200, facecolor=fig1.get_facecolor(), edgecolor='none')
    plt.close(fig1)

    fig2 = plt.figure(figsize=(6, 5))
    fig2.patch.set_facecolor('#f4f7fb')
    ax2 = fig2.add_subplot(111)

    if suggestions:
        difficulties = [recipe_difficulty(s) for s in suggestions]
        diff_counts = Counter(difficulties)

        colors = ['#0C9961', '#f59e0b', '#ef4444', '#94a3b8']
        ax2.pie(diff_counts.values(), labels=diff_counts.keys(), autopct='%1.1f%%', colors=colors)
        ax2.set_title("Recipe Difficulty Levels", fontsize=12, fontweight='bold', color='#1f4f46')
    else:
        ax2.text(0.5, 0.5, "No difficulty data", ha='center', va='center')

    plt.tight_layout()
    fig2.savefig(path_difficulty, dpi=200, facecolor=fig2.get_facecolor(), edgecolor='none')
    plt.close(fig2)
