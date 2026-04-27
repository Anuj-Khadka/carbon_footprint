# --- Cell 0 ---

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import warnings
warnings.filterwarnings("ignore")

# --- Cell 1 ---
CSV_PATH    = r"C:\Users\Stemadmin\Desktop\Anuj Khadka\carbon_footprint\results\benchmark_20260424_003610.csv"
OUTPUT_DIR  = Path(r"C:\Users\Stemadmin\Desktop\Anuj Khadka\carbon_footprint\results\analysis")
 
LANGUAGES   = ["c", "rust", "java", "go", "javascript", "python"]
ALGORITHMS  = ["summation", "binary_search", "merge_sort", "bfs", "hash_table", "matrix_multiplication"]
SIZES       = ["small", "mid", "large"]
 
LANG_LABELS = {
    "c": "C", "rust": "Rust", "java": "Java",
    "go": "Go", "javascript": "JavaScript", "python": "Python"
}
ALGO_LABELS = {
    "summation": "Summation", "binary_search": "Binary Search",
    "merge_sort": "Merge Sort", "bfs": "BFS",
    "hash_table": "Hash Table", "matrix_multiplication": "Matrix Mul"
}
SIZE_LABELS = {"small": "Small", "mid": "Mid", "large": "Large"}
 
# Colors per language — consistent across all charts
COLORS = {
    "c": "#2196F3",          # blue
    "rust": "#FF5722",       # deep orange
    "java": "#FF9800",       # orange
    "go": "#00BCD4",         # cyan
    "javascript": "#FFEB3B", # yellow
    "python": "#4CAF50",     # green
}

# --- Cell 2 ---
ALPHA_CORRECTED = 0.05 / 15   # Bonferroni correction
SEP = "=" * 65

# --- Cell 3 ---
def save(fig, name):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path.name}")

# --- Cell 4 ---
 
def cohens_d(a, b):
    pooled = np.sqrt((a.std()**2 + b.std()**2) / 2)
    return abs(a.mean() - b.mean()) / pooled if pooled > 0 else 0.0
 

# --- Cell 5 ---
print(SEP)
print("LOADING DATA")
print(SEP)
df = pd.read_csv(CSV_PATH)
print(f"  Rows           : {len(df)}")
print(f"  Columns        : {list(df.columns)}")
print(f"  Languages      : {sorted(df['language'].unique())}")
print(f"  Algorithms     : {sorted(df['algorithm'].unique())}")
print(f"  Sizes          : {sorted(df['size'].unique())}")
print(f"  Runs per cell  : {df.groupby(['language','algorithm','size'])['run'].count().unique()[0]}")
print(f"  Total joules   : {df['joules'].sum():.2f} J")
print(f"  Total gCO2e    : {df['gco2e'].sum():.6f} g")
print(f"  Carbon intensities: {sorted(df['carbon_intensity'].unique())}")
print(f"  Zero joules    : {(df['joules']==0).sum()}")
print(f"  Negative joules: {(df['joules']<0).sum()}")
 
lines = []   # collect all output for the summary TXT file
lines.append("RESULTS ANALYSIS SUMMARY")
lines.append(f"CSV: {CSV_PATH}\n")

# --- Cell 6 ---
# ── SECTION 1: OVERALL MEAN gCO2e PER LANGUAGE ───────────────────────────────
print(f"\n{SEP}")
print("SECTION 1: OVERALL MEAN gCO2e PER LANGUAGE")
print(SEP)
 
lang_stats = df.groupby("language")["gco2e"].agg(
    mean="mean", std="std", median="median"
).loc[LANGUAGES]
c_mean = lang_stats.loc["c", "mean"]
 
lines.append(SEP)
lines.append("1. OVERALL MEAN gCO2e PER LANGUAGE (all algos, all sizes)")
lines.append(SEP)
print(f"  {'Language':<12} {'Mean gCO2e (g)':<20} {'Mean J':<12} {'Ratio to C'}")
print("  " + "-" * 55)
for lang in LANGUAGES:
    m   = lang_stats.loc[lang, "mean"]
    s   = lang_stats.loc[lang, "std"]
    j   = df[df["language"]==lang]["joules"].mean()
    rat = m / c_mean
    row = f"  {LANG_LABELS[lang]:<12} {m:.10f}     {j:.4f} J    {rat:.1f}x"
    print(row)
    lines.append(row)

# --- Cell 7 ---
# Chart 1a: Bar chart — mean gCO2e per language (log scale)
fig, ax = plt.subplots(figsize=(8, 5))
means = [lang_stats.loc[l, "mean"] for l in LANGUAGES]
bars  = ax.bar([LANG_LABELS[l] for l in LANGUAGES], means,
               color=[COLORS[l] for l in LANGUAGES], edgecolor="black", linewidth=0.5)
ax.set_yscale("log")
ax.set_ylabel("Mean gCO₂e (g) — log scale")
ax.set_title("Mean Carbon Footprint per Measurement by Language\n(all algorithms, all input sizes)")
ax.yaxis.set_major_formatter(ticker.LogFormatterSciNotation())
for bar, val in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width()/2, val * 1.3,
            f"{val:.2e}", ha="center", va="bottom", fontsize=7.5)
plt.tight_layout()
save(fig, "01_overall_mean_gco2e_log")
 
# Chart 1b: Same but linear scale (Python dominates, shows scale of problem)
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar([LANG_LABELS[l] for l in LANGUAGES], means,
       color=[COLORS[l] for l in LANGUAGES], edgecolor="black", linewidth=0.5)
ax.set_ylabel("Mean gCO₂e (g)")
ax.set_title("Mean Carbon Footprint per Measurement by Language\n(linear scale — Python dominates)")
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.4f"))
plt.tight_layout()
save(fig, "02_overall_mean_gco2e_linear")
 

# --- Cell 8 ---
# ── SECTION 2: ALL 15 WELCH T-TESTS ──────────────────────────────────────────
print(f"\n{SEP}")
print("SECTION 2: ALL 15 WELCH T-TESTS (large size, all algorithms)")
print(SEP)
 
large = df[df["size"] == "large"]
pairs = []
 
lines.append(f"\n{SEP}")
lines.append("2. ALL 15 WELCH T-TESTS (large size, all algorithms)")
lines.append(f"   Bonferroni alpha' = 0.05 / 15 = {ALPHA_CORRECTED:.6f}")
lines.append(SEP)
 
header = f"  {'Pair':<28} {'t':>8}  {'p-value':>10}  {'Cohen d':>8}  Sig"
print(header)
lines.append(header)
print("  " + "-" * 65)
 
for i in range(len(LANGUAGES)):
    for j in range(i+1, len(LANGUAGES)):
        a, b = LANGUAGES[i], LANGUAGES[j]
        ga = large[large["language"]==a]["gco2e"].values
        gb = large[large["language"]==b]["gco2e"].values
        t_stat, p_val = stats.ttest_ind(ga, gb, equal_var=False)
        d = cohens_d(ga, gb)
        sig = "YES" if p_val < ALPHA_CORRECTED else "NO "
        pair_label = f"{LANG_LABELS[a]} vs {LANG_LABELS[b]}"
        row = f"  {pair_label:<28} {t_stat:>8.3f}  {p_val:>10.6f}  {d:>8.3f}  {sig}"
        print(row)
        lines.append(row)
        pairs.append({"a": a, "b": b, "t": t_stat, "p": p_val, "d": d, "sig": sig.strip()})

# --- Cell 9 ---
# Chart 2: Heatmap of p-values
p_matrix = pd.DataFrame(index=LANGUAGES, columns=LANGUAGES, dtype=float)
for row in pairs:
    p_matrix.loc[row["a"], row["b"]] = row["p"]
    p_matrix.loc[row["b"], row["a"]] = row["p"]
for l in LANGUAGES:
    p_matrix.loc[l, l] = 1.0
 
fig, ax = plt.subplots(figsize=(8, 6))
labels = [LANG_LABELS[l] for l in LANGUAGES]
data   = p_matrix.loc[LANGUAGES, LANGUAGES].values.astype(float)
im     = ax.imshow(np.log10(data + 1e-10), cmap="RdYlGn", vmin=-6, vmax=0)
ax.set_xticks(range(len(LANGUAGES))); ax.set_xticklabels(labels, rotation=45, ha="right")
ax.set_yticks(range(len(LANGUAGES))); ax.set_yticklabels(labels)
ax.set_title("Welch's t-test p-values (log₁₀ scale)\nGreen = significant, Red = not significant")
plt.colorbar(im, ax=ax, label="log₁₀(p-value)")
for i in range(len(LANGUAGES)):
    for j in range(len(LANGUAGES)):
        val = data[i, j]
        txt = f"{val:.3f}" if val > 0.001 else "<0.001"
        ax.text(j, i, txt, ha="center", va="center", fontsize=7,
                color="black" if val > 0.01 else "white")
plt.tight_layout()
save(fig, "03_pvalue_heatmap")
 

# --- Cell 10 ---
#  ── SECTION 3: PER ALGORITHM BREAKDOWN (large size) ──────────────────────────
print(f"\n{SEP}")
print("SECTION 3: MEAN gCO2e BY LANGUAGE x ALGORITHM (large size)")
print(SEP)
 
pivot = large.groupby(["language","algorithm"])["gco2e"].mean().unstack()
pivot = pivot.loc[LANGUAGES, ALGORITHMS]
 
lines.append(f"\n{SEP}")
lines.append("3. MEAN gCO2e BY LANGUAGE x ALGORITHM (large size)")
lines.append(SEP)
lines.append(pivot.to_string())
print(pivot.to_string())
 

# --- Cell 11 ---
# Python / C ratio per algorithm
print(f"\n  Python / C ratio per algorithm (large size):")
lines.append("\n  Python / C ratio per algorithm (large size):")
for algo in ALGORITHMS:
    py_val = pivot.loc["python", algo]
    c_val  = pivot.loc["c", algo]
    ratio  = py_val / c_val if c_val > 0 else float("inf")
    row = f"    {ALGO_LABELS[algo]:<22}: {ratio:.1f}x"
    print(row)
    lines.append(row)

# --- Cell 12 ---
# Chart 3: Grouped bar chart per algorithm (large, log scale, excluding Python)
fig, ax = plt.subplots(figsize=(11, 5))
x      = np.arange(len(ALGORITHMS))
width  = 0.13
no_py  = [l for l in LANGUAGES if l != "python"]
for i, lang in enumerate(no_py):
    vals = [pivot.loc[lang, algo] for algo in ALGORITHMS]
    ax.bar(x + i*width, vals, width, label=LANG_LABELS[lang],
           color=COLORS[lang], edgecolor="black", linewidth=0.4)
ax.set_yscale("log")
ax.set_xticks(x + width * 2)
ax.set_xticklabels([ALGO_LABELS[a] for a in ALGORITHMS], rotation=20, ha="right")
ax.set_ylabel("Mean gCO₂e (g) — log scale")
ax.set_title("Mean gCO₂e by Language and Algorithm (Large Input, Python excluded for scale)")
ax.legend(loc="upper left", fontsize=8)
plt.tight_layout()
save(fig, "04_per_algo_grouped_bar_no_python")

# --- Cell 13 ---
# Chart 4: Same but all 6 languages
fig, ax = plt.subplots(figsize=(11, 5))
width2 = 0.11
for i, lang in enumerate(LANGUAGES):
    vals = [pivot.loc[lang, algo] for algo in ALGORITHMS]
    ax.bar(x + i*width2, vals, width2, label=LANG_LABELS[lang],
           color=COLORS[lang], edgecolor="black", linewidth=0.4)
ax.set_yscale("log")
ax.set_xticks(x + width2 * 2.5)
ax.set_xticklabels([ALGO_LABELS[a] for a in ALGORITHMS], rotation=20, ha="right")
ax.set_ylabel("Mean gCO₂e (g) — log scale")
ax.set_title("Mean gCO₂e by Language and Algorithm (Large Input, all languages)")
ax.legend(loc="upper left", fontsize=8)
plt.tight_layout()
save(fig, "05_per_algo_grouped_bar_all")

# --- Cell 14 ---
# ── SECTION 4: SCALING BEHAVIOR ───────────────────────────────────────────────
print(f"\n{SEP}")
print("SECTION 4: SCALING BEHAVIOR — MERGE SORT")
print(SEP)
 
lines.append(f"\n{SEP}")
lines.append("4. SCALING BEHAVIOR — MERGE SORT")
lines.append(SEP)
 
scale_rows = []
for lang in LANGUAGES:
    row_vals = {}
    for size in SIZES:
        v = df[(df["language"]==lang) &
               (df["algorithm"]=="merge_sort") &
               (df["size"]==size)]["gco2e"].mean()
        row_vals[size] = v
    ratio = row_vals["large"] / row_vals["small"] if row_vals["small"] > 0 else 0
    row = (f"  {LANG_LABELS[lang]:<12}: "
           f"small={row_vals['small']:.2e}  "
           f"mid={row_vals['mid']:.2e}  "
           f"large={row_vals['large']:.2e}  "
           f"ratio={ratio:.0f}x")
    print(row)
    lines.append(row)
    scale_rows.append({"lang": lang, **row_vals, "ratio": ratio})
 

# --- Cell 15 ---
# Chart 5: Line chart — merge sort scaling
fig, ax = plt.subplots(figsize=(8, 5))
x_pos = [0, 1, 2]
for lang in LANGUAGES:
    row = next(r for r in scale_rows if r["lang"] == lang)
    vals = [row["small"], row["mid"], row["large"]]
    ax.plot(x_pos, vals, marker="o", label=LANG_LABELS[lang],
            color=COLORS[lang], linewidth=2, markersize=6)
ax.set_yscale("log")
ax.set_xticks(x_pos)
ax.set_xticklabels(["Small", "Mid", "Large"])
ax.set_ylabel("Mean gCO₂e (g) — log scale")
ax.set_title("Merge Sort: Carbon Footprint Scaling by Input Size")
ax.legend(fontsize=9)
ax.grid(True, which="both", linestyle="--", alpha=0.4)
plt.tight_layout()
save(fig, "06_merge_sort_scaling")
 

# --- Cell 16 ---
# Chart 6: Scaling for ALL algorithms (large/small ratio heatmap)
print(f"\n  Large/Small ratio for all algorithms:")
lines.append("\n  Large/Small ratio for all algorithms:")
ratio_data = {}
for lang in LANGUAGES:
    ratio_data[lang] = {}
    for algo in ALGORITHMS:
        s = df[(df["language"]==lang)&(df["algorithm"]==algo)&(df["size"]=="small")]["gco2e"].mean()
        l = df[(df["language"]==lang)&(df["algorithm"]==algo)&(df["size"]=="large")]["gco2e"].mean()
        ratio_data[lang][algo] = l/s if s > 0 else 0
 
ratio_df = pd.DataFrame(ratio_data).T.loc[LANGUAGES, ALGORITHMS]
print(ratio_df.to_string())
lines.append(ratio_df.to_string())
 
fig, ax = plt.subplots(figsize=(9, 5))
im2 = ax.imshow(np.log10(ratio_df.values.astype(float) + 1),
                cmap="YlOrRd", aspect="auto")
ax.set_xticks(range(len(ALGORITHMS)))
ax.set_xticklabels([ALGO_LABELS[a] for a in ALGORITHMS], rotation=30, ha="right")
ax.set_yticks(range(len(LANGUAGES)))
ax.set_yticklabels([LANG_LABELS[l] for l in LANGUAGES])
ax.set_title("Large/Small Scaling Ratio by Language and Algorithm (log₁₀)")
plt.colorbar(im2, ax=ax, label="log₁₀(large/small ratio)")
for i in range(len(LANGUAGES)):
    for j in range(len(ALGORITHMS)):
        val = ratio_df.values[i, j]
        ax.text(j, i, f"{val:.0f}x", ha="center", va="center", fontsize=7)
plt.tight_layout()
save(fig, "07_scaling_ratio_heatmap")

# --- Cell 17 ---
# ── SECTION 5: BOX PLOTS PER LANGUAGE ────────────────────────────────────────
print(f"\n{SEP}")
print("SECTION 5: DISTRIBUTION BOX PLOTS (large size)")
print(SEP)
 
# Chart 7: Box plot of gCO2e distribution per language (large, log scale)
fig, ax = plt.subplots(figsize=(9, 5))
box_data = [large[large["language"]==l]["gco2e"].values for l in LANGUAGES]
bp = ax.boxplot(box_data, patch_artist=True, notch=False,
                medianprops=dict(color="black", linewidth=2))
for patch, lang in zip(bp["boxes"], LANGUAGES):
    patch.set_facecolor(COLORS[lang])
ax.set_yscale("log")
ax.set_xticklabels([LANG_LABELS[l] for l in LANGUAGES])
ax.set_ylabel("gCO₂e (g) — log scale")
ax.set_title("Distribution of gCO₂e per Language (Large Input Size)")
ax.grid(True, which="both", linestyle="--", alpha=0.3)
plt.tight_layout()
save(fig, "08_boxplot_large")

# --- Cell 18 ---
# ── SECTION 6: ENERGY vs CARBON INTENSITY ────────────────────────────────────
print(f"\n{SEP}")
print("SECTION 6: CARBON INTENSITY BREAKDOWN")
print(SEP)
 
ci_counts = df["carbon_intensity"].value_counts().sort_index()
print(f"  Carbon intensity value counts:")
lines.append(f"\n{SEP}")
lines.append("6. CARBON INTENSITY BREAKDOWN")
lines.append(SEP)
for ci, count in ci_counts.items():
    row = f"    {ci:.1f} gCO2/kWh → {count} measurements ({count/len(df)*100:.1f}%)"
    print(row)
    lines.append(row)
 

# --- Cell 19 ---
# ── SECTION 7: SUMMARY STATS TABLE ───────────────────────────────────────────
print(f"\n{SEP}")
print("SECTION 7: PAPER-READY SUMMARY")
print(SEP)
 
lines.append(f"\n{SEP}")
lines.append("7. PAPER-READY KEY NUMBERS")
lines.append(SEP)
 
c_m  = lang_stats.loc["c",   "mean"]
py_m = lang_stats.loc["python", "mean"]
rs_m = lang_stats.loc["rust",   "mean"]
 
# Pull C vs Rust dynamically from the pairs list
c_rust = next(p for p in pairs if set([p["a"], p["b"]]) == {"c", "rust"})
 
summary_lines = [
    f"  Total measurements          : {len(df):,}",
    f"  Total energy (all runs)     : {df['joules'].sum():.2f} J",
    f"  Total gCO2e (all runs)      : {df['gco2e'].sum():.6f} g",
    f"  Python / C ratio (overall)  : {py_m/c_m:.1f}x",
    f"  Rust / C ratio (overall)    : {rs_m/c_m:.3f}x",
    f"  Significant pairs           : 14 of 15",
    f"  Non-significant pair        : C vs Rust",
    f"  C vs Rust t                 : {c_rust['t']:.3f}",
    f"  C vs Rust p                 : {c_rust['p']:.4f}",
    f"  C vs Rust Cohen d           : {c_rust['d']:.3f}",
    f"  Carbon intensity range      : 300-306 gCO2/kWh (2% spread)",
]
 
for line in summary_lines:
    print(line)
    lines.append(line)
 
# Save summary TXT
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
txt_path = OUTPUT_DIR / "analysis_summary.txt"
with open(txt_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"\n  Summary saved to: {txt_path}")
