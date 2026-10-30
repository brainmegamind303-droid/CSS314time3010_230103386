import time
import math
from multiprocessing import Pool

def heavy_math(n):
    return sum(math.sin(i) * math.cos(i) for i in range(1, n))

def experiment(workers, total_chunks=16, chunk_size=2_000_000):
    start = time.perf_counter()
    time.sleep(0.40)  # Преднамеренный последовательный узкое место (~12% сериализации)[cite: 1]
    with Pool(processes=workers) as pool:
        pool.map(heavy_math, [chunk_size] * total_chunks)
    return time.perf_counter() - start

if __name__ == "__main__":
    cores = [1, 2, 4]
    runtimes = {}
    print("=== Experiment A: Serial Tail ===")
    for p in cores:
        t = experiment(p)
        runtimes[p] = t
        print(f"P={p} | Runtime = {t:.3f}s")
    
    t1 = runtimes[1]
    for p in [2, 4]:
        tp = runtimes[p]
        sp = t1 / tp if tp > 0 else 0
        e = ((p * (tp / t1)) - 1) / (p - 1)
        print(f"P={p} | Speedup = {sp:.2f}x | Karp-Flatt e = {e:.3f}")