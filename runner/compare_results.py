import json
from collections import Counter
import statistics

MULTI_FILE = "results/multi_agent_results.json"
SINGLE_FILE = "results/single_model_results.json"

RISK_ORDER = ["none", "low", "medium", "high"]

def load_results():
    multi = json.load(open(MULTI_FILE, encoding="utf-8"))
    single = json.load(open(SINGLE_FILE, encoding="utf-8"))
    return multi, single

def risk_distribution(results, key):
    return Counter(item[key]["overall_risk_level"] for item in results)

def dominant_factor_counts(results, key):
    return Counter(len(item[key]["dominant_factors"]) for item in results)

def confidence_stats(results, key):
    confidences = [item[key]["confidence"] for item in results]
    return {
        "mean": round(statistics.mean(confidences), 3),
        "std": round(statistics.pstdev(confidences), 3),
        "min": round(min(confidences), 3),
        "max": round(max(confidences), 3),
    }

def main():
    multi, single = load_results()

    print("\n=== Risk Level Distribution ===")
    print("Multi-Agent :", dict(risk_distribution(multi, "final_output")))
    print("Single-Model:", dict(risk_distribution(single, "output")))

    print("\n=== Dominant Factors Count ===")
    print("Multi-Agent :", dict(dominant_factor_counts(multi, "final_output")))
    print("Single-Model:", dict(dominant_factor_counts(single, "output")))

    print("\n=== Confidence Statistics ===")
    print("Multi-Agent :", confidence_stats(multi, "final_output"))
    print("Single-Model:", confidence_stats(single, "output"))

if __name__ == "__main__":
    main()
