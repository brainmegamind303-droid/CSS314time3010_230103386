import time
from multiprocessing import Process, Queue

def buffered_worker(out_queue, items_per_worker, batch_size=10_000):
    buffer = []
    for i in range(items_per_worker):
        buffer.append(i % 7)
        if len(buffer) >= batch_size:
            out_queue.put(sum(buffer))
            buffer.clear()
    if buffer:
        out_queue.put(sum(buffer))
    out_queue.put(None)  # Sentinel 

def run_buffered(p, total_items=10_000_000):
    q = Queue()
    items_per_worker = total_items // p
    workers = [Process(target=buffered_worker, args=(q, items_per_worker)) for _ in range(p)]
    
    t0 = time.perf_counter()
    for w in workers:
        w.start()
        
    total_sum, active = 0, p
    while active > 0:
        val = q.get()
        if val is None:
            active -= 1
        else:
            total_sum += val
            
    for w in workers:
        w.join()
    t1 = time.perf_counter()
    return t1 - t0, total_sum

if __name__ == "__main__":
    cores = [1, 2, 4, 8]
    runtimes = {}
    print("\n--- Buffered Batch Karp-Flatt Analysis ---")
    for p in cores:
        tp, _ = run_buffered(p)
        runtimes[p] = tp
        if p == 1:
            print(f"P={p:2d} | Time={tp:6.3f}s | Speedup= 1.00x")
        else:
            t1 = runtimes[1]
            sp = t1 / tp
            e = ((p * (tp / t1)) - 1.0) / (p - 1.0)
            print(f"P={p:2d} | Time={tp:6.3f}s | Speedup={sp:5.2f}x | Karp-Flatt e={e:6.3f}")