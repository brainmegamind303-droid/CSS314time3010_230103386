import time
import math
from multiprocessing import Pool

def collatz_steps(n):
    steps = 0
    while n > 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps

def run_granularity(workers, total_items=1_000_000, chunk_size=1):
    numbers = range(1, total_items + 1)
    t0 = time.perf_counter()
    with Pool(processes=workers) as pool:
        results = pool.map(collatz_steps, numbers, chunksize=chunk_size)
    t1 = time.perf_counter()
    return t1 - t0, sum(results)

if __name__ == "__main__":
    cores = [1, 2, 4, 8]
    runtimes = {}
    print("=== Experiment A: Granularity Trap ===")
    for p in cores:
        t, _ = run_granularity(p, total_items=200_000, chunk_size=1)
        runtimes[p] = t
        print(f"P={p} | Runtime = {t:.3f}s")
    
    t1 = runtimes[1]
    for p in [2, 4, 8]:
        if p in runtimes:
            tp = runtimes[p]
            sp = t1 / tp if tp > 0 else 0
            e = ((p * (tp / t1)) - 1) / (p - 1)
            print(f"P={p} | Speedup = {sp:.2f}x | Karp-Flatt e = {e:.3f}")