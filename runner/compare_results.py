import json
from collections import Counter
from statistics import mean, stdev
from pathlib import Path
import matplotlib.pyplot as plt


# ---------- IO ----------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- Shared schema extractors ----------

def extract_risk_levels(results):
    return [item["final_output"]["overall_risk_level"] for item in results]


def extract_confidences(results):
    return [item["final_output"]["confidence"] for item in results]


def extract_dominant_factor_counts(results):
    return [len(item["final_output"]["dominant_factors"]) for item in results]


# ---------- Statistics helpers ----------

def summarize_confidence(values):
    return {
        "mean": round(mean(values), 3),
        "std": round(stdev(values), 3) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "count": len(values),
    }


# ---------- Plot helpers ----------

def plot_bar_comparison(counter_a, counter_b, labels, title, ylabel, save_path):
    """
    Generate a side-by-side bar chart for comparison.
    """
    categories = sorted(set(counter_a.keys()) | set(counter_b.keys()))
    values_a = [counter_a.get(c, 0) for c in categories]
    values_b = [counter_b.get(c, 0) for c in categories]

    x = range(len(categories))

    plt.figure()
    plt.bar(x, values_a, width=0.4, label=labels[0])
    plt.bar([i + 0.4 for i in x], values_b, width=0.4, label=labels[1])
    plt.xticks([i + 0.2 for i in x], categories)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_confidence_boxplot(values_a, values_b, labels, title, save_path):
    """
    Generate a boxplot for confidence comparison.
    """
    plt.figure()
    plt.boxplot([values_a, values_b], labels=labels)
    plt.ylabel("Confidence")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


# ---------- Main comparison ----------

def main():
    multi = load_json("results/multi_agent_results.json")
    single = load_json("results/single_model_results.json")

    figures_dir = Path("results/figures")
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Risk level distribution
    multi_risk = Counter(extract_risk_levels(multi))
    single_risk = Counter(extract_risk_levels(single))

    print("\n=== Risk Level Distribution ===")
    print("Multi-Agent :", dict(multi_risk))
    print("Single-Model:", dict(single_risk))

    plot_bar_comparison(
        multi_risk,
        single_risk,
        labels=["Multi-Agent", "Single-Model"],
        title="Risk Level Distribution Comparison",
        ylabel="Number of Samples",
        save_path=figures_dir / "risk_level_distribution.png"
    )

    # Dominant factor counts
    multi_factors = Counter(extract_dominant_factor_counts(multi))
    single_factors = Counter(extract_dominant_factor_counts(single))

    print("\n=== Dominant Factors Count ===")
    print("Multi-Agent :", dict(multi_factors))
    print("Single-Model:", dict(single_factors))

    plot_bar_comparison(
        multi_factors,
        single_factors,
        labels=["Multi-Agent", "Single-Model"],
        title="Dominant Factors Count Comparison",
        ylabel="Number of Samples",
        save_path=figures_dir / "dominant_factors_count.png"
    )

    # Confidence statistics
    multi_conf = extract_confidences(multi)
    single_conf = extract_confidences(single)

    print("\n=== Confidence Statistics ===")
    print("Multi-Agent :", summarize_confidence(multi_conf))
    print("Single-Model:", summarize_confidence(single_conf))

    plot_confidence_boxplot(
        multi_conf,
        single_conf,
        labels=["Multi-Agent", "Single-Model"],
        title="Confidence Score Comparison",
        save_path=figures_dir / "confidence_boxplot.png"
    )


if __name__ == "__main__":
    main()
