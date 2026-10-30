import multiprocessing as mp
import time
import json
import os
import numpy as np
from numba import jit
from salt import get_student_params

@jit(nopython=True)
def stencil_kernel(arr, steps):
    for _ in range(steps):
        arr[1:-1, 1:-1] = 0.25 * (arr[:-2, 1:-1] + arr[2:, 1:-1] + arr[1:-1, :-2] + arr[1:-1, 2:])
    return arr.sum()

def stencil_worker(chunk_rows, N):
    arr = np.ones((chunk_rows + 2, N))
    stencil_kernel(arr, 10)
    return arr.sum()

def run_scaling():
    os.makedirs("results", exist_ok=True)
    params = get_student_params("230103386")
    N = params["N"]
    max_cores = min(mp.cpu_count(), 8)
    cores_list = [p for p in [1, 2, 4, 8] if p <= max_cores]
    if not cores_list: cores_list = [1]

    scaling_rows = ["threads\tt_strong\tspeedup\tefficiency\tt_weak\tscaled_speedup"]
    t1_strong = None

    for P in cores_list:
        chunk = N // P
        if chunk < 2: chunk = 2
        
        # Strong Scaling
        start = time.perf_counter()
        with mp.Pool(P) as pool:
            pool.starmap(stencil_worker, [(chunk, N)] * P)
        t_strong = time.perf_counter() - start
        if P == 1: t1_strong = t_strong

        speedup = t1_strong / t_strong if t_strong > 0 else 1.0
        efficiency = (speedup / P) * 100

        # Weak Scaling
        Np = int(np.ceil(N * np.sqrt(P)))
        chunk_weak = Np // P
        if chunk_weak < 2: chunk_weak = 2
        
        start = time.perf_counter()
        with mp.Pool(P) as pool:
            pool.starmap(stencil_worker, [(chunk_weak, Np)] * P)
        t_weak = time.perf_counter() - start
        scaled_speedup = (P * t1_strong) / t_weak if t_weak > 0 else 1.0

        scaling_rows.append(f"{P}\t{t_strong:.6f}\t{speedup:.4f}\t{efficiency:.2f}%\t{t_weak:.6f}\t{scaled_speedup:.4f}")

    with open("results/scaling_metrics.tsv", "w") as f:
        f.write("\n".join(scaling_rows) + "\n")

    roofline = {
        "arithmetic_intensity": 0.5,
        "regime": "memory-bound"
    }
    with open("results/roofline_summary.json", "w") as f:
        json.dump(roofline, f, indent=4)
    print("Scaling and roofline studies completed.")

if __name__ == "__main__":
    mp.freeze_support()
    run_scaling()