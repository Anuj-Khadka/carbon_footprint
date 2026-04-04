"""
power_analysis.py
-----------------
Reads pilot_summary CSV and computes the required N per cell for the full
experiment, using a two-sample Welch's t-test power analysis.

This is the bridge between pilot_study.py and benchmark_runner.py.

Method:
  For each (algorithm, size) pair, we identify the two languages with the
  most similar mean energy — the hardest comparison to distinguish. We then
  compute the required n to detect that smallest difference at:
    alpha = 0.05 / 15   (Bonferroni corrected for 15 language pairs)
    power = 0.80

  The recommended N is the maximum across all (algorithm, size) pairs,
  rounded up to the nearest 10.

Usage:
  python power_analysis.py --pilot pilot_output/pilot_summary_<timestamp>.csv

Output:
  Prints recommended N to stdout.
  Writes power_analysis_report.txt to the same directory as the input CSV.

Dependencies:
  pip install scipy --break-system-packages
"""

import argparse
import csv
import sys
import math
from pathlib import Path
from itertools import combinations


def welch_t_required_n(mean1, std1, mean2, std2, alpha=0.05/15, power=0.80):
    """
    Approximate required n per group for a two-sample Welch's t-test using
    the formula from Cohen (1988) adapted for unequal variances.

    Uses a normal approximation which is accurate for n > 30.
    """
    from scipy import stats as sp_stats

    # Effect size (raw mean difference / pooled SD approximation)
    pooled_sd = math.sqrt((std1**2 + std2**2) / 2)
    if pooled_sd == 0:
        return None   # identical distributions
    effect = abs(mean1 - mean2) / pooled_sd

    if effect == 0:
        return None

    z_alpha = sp_stats.norm.ppf(1 - alpha / 2)   # two-tailed
    z_beta  = sp_stats.norm.ppf(power)

    # n per group (equal n assumption)
    n = ((z_alpha + z_beta) / effect) ** 2 * 2
    return math.ceil(n)


def main():
    p = argparse.ArgumentParser(description="Power analysis from pilot CSV")
    p.add_argument("--pilot", required=True, help="Path to pilot_summary CSV")
    p.add_argument("--alpha", type=float, default=0.05, help="Uncorrected alpha (default 0.05)")
    p.add_argument("--power", type=float, default=0.80, help="Desired power (default 0.80)")
    p.add_argument("--pairs", type=int,   default=15,   help="Number of language pairs (default 15 = C(6,2))")
    args = p.parse_args()

    pilot_path = Path(args.pilot)
    if not pilot_path.exists():
        sys.exit(f"File not found: {pilot_path}")

    alpha_corrected = args.alpha / args.pairs
    print(f"Alpha (uncorrected) : {args.alpha}")
    print(f"Language pairs      : {args.pairs}")
    print(f"Bonferroni alpha    : {alpha_corrected:.6f}")
    print(f"Target power        : {args.power}")
    print()

    # Read pilot CSV
    rows = []
    with open(pilot_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Group by (algo, size) → {language: (mean, std)}
    from collections import defaultdict
    groups: dict[tuple, dict] = defaultdict(dict)
    for row in rows:
        key  = (row["algorithm"], row["size"])
        lang = row["language"]
        mean = float(row["mean_energy_j"]) if row["mean_energy_j"] else None
        std  = float(row["std_energy_j"])  if row["std_energy_j"]  else None
        if mean is not None and std is not None and std > 0:
            groups[key][lang] = (mean, std)

    # For each (algo, size), find the hardest pair (smallest relative difference)
    required_ns = []
    report_lines = []

    report_lines.append("POWER ANALYSIS REPORT")
    report_lines.append("=" * 60)
    report_lines.append(f"Alpha (Bonferroni corrected): {alpha_corrected:.6f}")
    report_lines.append(f"Target power: {args.power}")
    report_lines.append("")
    report_lines.append(f"{'Algorithm':20s} {'Size':8s} {'Hardest pair':28s} {'Effect':8s} {'Req N':8s}")
    report_lines.append("-" * 80)

    for (algo, size), lang_stats in sorted(groups.items()):
        langs = list(lang_stats.keys())
        if len(langs) < 2:
            continue

        worst_n    = 0
        worst_pair = ("?", "?")
        worst_eff  = 0.0

        for l1, l2 in combinations(langs, 2):
            m1, s1 = lang_stats[l1]
            m2, s2 = lang_stats[l2]
            pooled_sd = math.sqrt((s1**2 + s2**2) / 2)
            effect    = abs(m1 - m2) / pooled_sd if pooled_sd > 0 else 0.0
            n = welch_t_required_n(m1, s1, m2, s2, alpha=alpha_corrected, power=args.power)
            if n is not None and n > worst_n:
                worst_n    = n
                worst_pair = (l1, l2)
                worst_eff  = effect

        if worst_n > 0:
            required_ns.append(worst_n)
            pair_str = f"{worst_pair[0]} vs {worst_pair[1]}"
            report_lines.append(
                f"{algo:20s} {size:8s} {pair_str:28s} {worst_eff:.4f}   {worst_n:6d}"
            )

    report_lines.append("")

    if not required_ns:
        print("Could not compute required N — check that pilot CSV has std > 0.")
        return

    max_n    = max(required_ns)
    # Round up to nearest 10 for cleanliness
    rec_n    = math.ceil(max_n / 10) * 10

    report_lines.append(f"Maximum required N across all cells: {max_n}")
    report_lines.append(f"Recommended N (rounded to nearest 10): {rec_n}")
    report_lines.append("")
    report_lines.append("Run the full experiment with:")
    report_lines.append(f"  python benchmark_runner.py --n {rec_n}")

    report_text = "\n".join(report_lines)
    print(report_text)

    out_path = pilot_path.parent / "power_analysis_report.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report_text + "\n")
    print(f"\nReport saved to: {out_path}")


if __name__ == "__main__":
    main()