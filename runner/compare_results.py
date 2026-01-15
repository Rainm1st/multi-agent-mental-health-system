import json
from collections import Counter
from statistics import mean, stdev


# ---------- IO ----------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- Shared schema extractors ----------

def extract_risk_levels(results):
    """
    Extract overall risk levels from standardized final_output.
    """
    return [
        item["final_output"]["overall_risk_level"]
        for item in results
    ]


def extract_confidences(results):
    """
    Extract confidence scores from standardized final_output.
    """
    return [
        item["final_output"]["confidence"]
        for item in results
    ]


def extract_dominant_factor_counts(results):
    """
    Count number of dominant factors in final_output.
    """
    return [
        len(item["final_output"]["dominant_factors"])
        for item in results
    ]


# ---------- Statistics helpers ----------

def summarize_confidence(values):
    return {
        "mean": round(mean(values), 3),
        "std": round(stdev(values), 3) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "count": len(values),
    }


# ---------- Main comparison ----------

def main():
    multi = load_json("results/multi_agent_results.json")
    single = load_json("results/single_model_results.json")

    # Risk level distribution
    multi_risk = Counter(extract_risk_levels(multi))
    single_risk = Counter(extract_risk_levels(single))

    print("\n=== Risk Level Distribution ===")
    print("Multi-Agent :", dict(multi_risk))
    print("Single-Model:", dict(single_risk))

    # Dominant factor counts
    multi_factors = Counter(extract_dominant_factor_counts(multi))
    single_factors = Counter(extract_dominant_factor_counts(single))

    print("\n=== Dominant Factors Count ===")
    print("Multi-Agent :", dict(multi_factors))
    print("Single-Model:", dict(single_factors))

    # Confidence statistics
    multi_conf = summarize_confidence(extract_confidences(multi))
    single_conf = summarize_confidence(extract_confidences(single))

    print("\n=== Confidence Statistics ===")
    print("Multi-Agent :", multi_conf)
    print("Single-Model:", single_conf)


if __name__ == "__main__":
    main()
