import numpy as np
import pandas as pd
import argparse
import sys
import traceback
from pathlib import Path

# Small constant to avoid division by zero or log(0)
EPS = 1e-12

# ────────────────────────────────────────────────
# Helper Functions
# ────────────────────────────────────────────────

def normalize(X):
    """Vector normalization: each column becomes unit vector."""
    norms = np.sqrt(np.sum(X**2, axis=0))
    norms[norms == 0] = 1.0
    R = X / norms
    return R


def entropy_weights(X):
    """Compute entropy-based weights from vector-normalized matrix."""
    m, n = X.shape
    col_sums = np.sum(X, axis=0)
    P = np.zeros_like(X)
    for j in range(n):
        if col_sums[j] > EPS:
            P[:, j] = X[:, j] / col_sums[j]
        else:
            P[:, j] = 0.0
    log_P = np.log(P + EPS)
    E = -(1.0 / np.log(m)) * np.sum(P * log_P, axis=0)
    D = 1 - E
    total_D = np.sum(D)
    if total_D < EPS:
        W = np.ones(n) / n
    else:
        W = D / total_D
    return W


def finalize_matrix(R, W):
    """Weighted normalized matrix V = R * W (broadcast)."""
    return R * W


def find_ideals(V, is_benefit):
    """Positive and Negative Ideal Solutions."""
    PIS = np.zeros(V.shape[1])
    NIS = np.zeros(V.shape[1])
    for j in range(V.shape[1]):
        if is_benefit[j]:
            PIS[j] = np.max(V[:, j])
            NIS[j] = np.min(V[:, j])
        else:
            PIS[j] = np.min(V[:, j])
            NIS[j] = np.max(V[:, j])
    return PIS, NIS


def calculate_separations(V, PIS, NIS):
    """Euclidean distances to PIS and NIS."""
    S_plus = np.sqrt(np.sum((V - PIS)**2, axis=1))
    S_minus = np.sqrt(np.sum((V - NIS)**2, axis=1))
    return S_plus, S_minus


def calculate_rating_scores(names, S_plus, S_minus):
    """Closeness coefficient C = S- / (S+ + S-)."""
    C = S_minus / (S_plus + S_minus + EPS)
    return {names[i]: float(C[i]) for i in range(len(names))}


# ────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TOPSIS with objective entropy weights")
    parser.add_argument("--file", required=True, help="Path to the input CSV file")
    parser.add_argument("--benefits", required=True, help="Comma-separated benefit flags (True/False)")
    args = parser.parse_args()

    # ── Logging setup ───────────────────────────────────────────────────────────
    input_path = Path(args.file)
    if not input_path.is_file():
        print(f"ERROR: Input file not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    base_name = input_path.stem
    log_filename = f"{base_name}_topsis.log"

    print(f"Starting TOPSIS analysis. Output duplicated to: {log_filename}\n")

    log_file = None
    original_print = print

    try:
        log_file = open(log_filename, mode="w", encoding="utf-8")

        def dual_print(*args, sep=" ", end="\n", flush=False, **kwargs):
            original_print(*args, sep=sep, end=end, flush=flush, **kwargs)
            original_print(*args, sep=sep, end=end, flush=flush, file=log_file, **kwargs)

        print = dual_print

        # ── Execution ───────────────────────────────────────────────────────────────
        print("=== TOPSIS with Entropy Weights ===\n")
        print(f"Input file:          {args.file}")
        print(f"Benefit flags:       {args.benefits}\n")

        # Load data
        df = pd.read_csv(args.file)
        criteria_keys = df.columns[1:].tolist()
        names = df.iloc[:, 0].tolist()
        X = df.iloc[:, 1:].to_numpy(dtype=float)

        print(f"Loaded {len(names)} alternatives with {len(criteria_keys)} criteria.\n")

        # Parse benefits
        benefits_str = [b.strip() for b in args.benefits.split(',')]
        if len(benefits_str) != len(criteria_keys):
            raise ValueError(
                f"Benefit flags count mismatch: got {len(benefits_str)} flags, "
                f"but {len(criteria_keys)} criteria found.\n"
                f"Flags:   {', '.join(benefits_str)}\n"
                f"Criteria: {', '.join(criteria_keys)}"
            )

        is_benefit = [b.lower() == 'true' for b in benefits_str]

        # Computations
        R = normalize(X)
        W = entropy_weights(R)
        V = finalize_matrix(R, W)
        PIS, NIS = find_ideals(V, is_benefit)
        S_plus, S_minus = calculate_separations(V, PIS, NIS)
        scores = calculate_rating_scores(names, S_plus, S_minus)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # ── Output ──────────────────────────────────────────────────────────────────
        print("1. Raw Decision Matrix (input data)\n")
        print(f"  Number of alternatives : {len(names)}")
        print(f"  Number of criteria     : {len(criteria_keys)}\n")

        print("  Alternatives:")
        for i, name in enumerate(names, 1):
            print(f"    {i:2d}. {name}")

        print("\n  Criteria & preference direction:")
        for i, (crit, benefit) in enumerate(zip(criteria_keys, is_benefit), 1):
            direction = "↑ benefit (maximize)" if benefit else "↓ cost (minimize)"
            print(f"    {i:2d}. {crit:26}  {direction}")

        print("\n  Raw values:")
        print(np.round(X, 4))
        print()

        print("2. Vector-Normalized Matrix R\n")
        print("Shape:", R.shape)
        print(np.round(R, 6))
        print()

        print("3. Entropy Weights\n")
        for crit, w in zip(criteria_keys, W):
            print(f"  {crit:26} : {w:.5f}")
        print(f"  {'─'*38}")
        print(f"  Sum                     : {W.sum():.5f}")
        print()

        print("4. Weighted Normalized Matrix V\n")
        print(np.round(V, 6))
        print()

        print("5. Final Ranking (most preferred → least preferred)\n")
        print(f"{'Rank':>4}  {'Closeness':>12}  Alternative")
        print("─" * 70)
        for rank, (name, score) in enumerate(ranked, 1):
            print(f"{rank:4d}  {score:12.5f}  {name}")
        print()

        print("Done.\n")
        print("Notes:")
        print(" • Weights are purely objective (entropy method)")
        print(" • Vector normalization used → scale-invariant")
        print(" • All input values should be non-negative")
        print(" • Higher closeness score = better alternative")

    except Exception as e:
        print("\n" + "="*80, file=sys.stderr)
        print("ERROR occurred during execution:", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        print("="*80, file=sys.stderr)
        sys.exit(1)

    finally:
        if log_file is not None and not log_file.closed:
            log_file.flush()
            log_file.close()
        print = original_print
        if log_filename:
            print(f"\nLog file created: {log_filename}")
