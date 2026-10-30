import time
import json
import numpy as np
import os
from numba import jit
from salt import get_student_params

@jit(nopython=True)
def naive_kernel(A, B, C, N):
    for i in range(N):
        for j in range(N):
            s = 0.0
            for k in range(N):
                s += A[i, k] * B[k, j]
            C[i, j] = s

@jit(nopython=True)
def interchanged_kernel(A, B, C, N):
    for i in range(N):
        for k in range(N):
            aik = A[i, k]
            for j in range(N):
                C[i, j] += aik * B[k, j]

def run_loop_interchange():
    os.makedirs("results", exist_ok=True)
    params = get_student_params("230103386")
    N = params["N"] // 2  # M = N/2
    
    A = np.random.rand(N, N)
    B = np.random.rand(N, N)
    C_naive = np.zeros((N, N))
    C_interchanged = np.zeros((N, N))

    # Прогрев Numba
    naive_kernel(A, B, C_naive, N)
    interchanged_kernel(A, B, C_interchanged, N)

    # Naïve i-j-k
    runs_naive = []
    for _ in range(3):
        C_naive.fill(0.0)
        start = time.perf_counter()
        naive_kernel(A, B, C_naive, N)
        runs_naive.append(time.perf_counter() - start)
    t_naive = np.median(runs_naive)

    # Interchanged i-k-j
    runs_inter = []
    for _ in range(3):
        C_interchanged.fill(0.0)
        start = time.perf_counter()
        interchanged_kernel(A, B, C_interchanged, N)
        runs_inter.append(time.perf_counter() - start)
    t_interchanged = np.median(runs_inter)

    speedup = t_naive / t_interchanged if t_interchanged > 0 else 0.0

    output = {
        "matrix_size_M": N,
        "naive_time_s": float(t_naive),             # Требуемый ключ verifier.py
        "interchanged_time_s": float(t_interchanged), # Требуемый ключ verifier.py
        "speedup": float(speedup)
    }
    
    with open("results/loop_interchange.json", "w") as f:
        json.dump(output, f, indent=4)
        
    print(f"Loop interchange completed. Speedup: {speedup:.2f}x")

if __name__ == "__main__":
    run_loop_interchange()