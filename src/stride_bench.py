import time
import numpy as np
import os
from numba import jit

@jit(nopython=True)
def traverse_stride(data, s):
    total = 0.0
    for i in range(0, len(data), s):
        total += data[i]
    return total

def run_stride_benchmark():
    os.makedirs("results", exist_ok=True)
    buffer_size = 16_777_216
    data = np.ones(buffer_size, dtype=np.float64)
    strides = [1, 2, 4, 8, 16, 32, 64, 128]
    results = ["stride\tlatency_ns"]

    # Прогрев Numba
    traverse_stride(data, 1)

    for s in strides:
        latencies = []
        for _ in range(5):
            start = time.perf_counter_ns()
            traverse_stride(data, s)
            elapsed = time.perf_counter_ns() - start
            touched = buffer_size // s
            latencies.append(elapsed / touched)
        
        median_lat = float(np.median(latencies))
        results.append(f"{s}\t{median_lat:.4f}")

    with open("results/stride_results.tsv", "w") as f:
        f.write("\n".join(results) + "\n")
    print("Stride benchmark completed.")

if __name__ == "__main__":
    run_stride_benchmark()