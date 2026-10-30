import multiprocessing as mp
import ctypes
import time
import os
import numpy as np
from numba import jit

@jit(nopython=True)
def work_unpad(arr_view, pid, iters):
    for _ in range(iters):
        arr_view[pid] += 1

@jit(nopython=True)
def work_pad(arr_view, pid, iters):
    idx = pid * 8
    for _ in range(iters):
        arr_view[idx] += 1

@jit(nopython=True)
def work_priv(iters):
    val = 0
    for _ in range(iters):
        val += 1
    return val

def worker_unpadded_target(shared_arr, pid, iters):
    arr_view = np.frombuffer(shared_arr.get_obj(), dtype=np.int64)
    work_unpad(arr_view, pid, iters)

def worker_padded_target(shared_arr, pid, iters):
    arr_view = np.frombuffer(shared_arr.get_obj(), dtype=np.int64)
    work_pad(arr_view, pid, iters)

def worker_privatized_target(shared_arr, pid, iters):
    local_val = work_priv(iters)
    arr_view = np.frombuffer(shared_arr.get_obj(), dtype=np.int64)
    arr_view[pid] = local_val

def run_false_sharing():
    os.makedirs("results", exist_ok=True)
    iters = 5_000_000
    
    max_cpus = os.cpu_count() or 4
    processes = [p for p in [1, 2, 4, 8] if p <= max_cpus]
    if not processes:
        processes = [1]

    rows = ["P\tt_unpadded\tt_padded\tt_privatized\te_unpadded\te_padded"]
    t1_unpad = None

    for P in processes:
        # 1. Unpadded (False Sharing)
        shared_arr_unpad = mp.Array(ctypes.c_int64, 8)
        procs = [mp.Process(target=worker_unpadded_target, args=(shared_arr_unpad, i, iters)) for i in range(P)]
        start = time.perf_counter()
        for p in procs: p.start()
        for p in procs: p.join()
        t_unpad = time.perf_counter() - start
        if P == 1: t1_unpad = t_unpad

        # 2. Padded (64-byte separation)
        shared_arr_pad = mp.Array(ctypes.c_int64, 64)
        procs = [mp.Process(target=worker_padded_target, args=(shared_arr_pad, i, iters)) for i in range(P)]
        start = time.perf_counter()
        for p in procs: p.start()
        for p in procs: p.join()
        t_pad = time.perf_counter() - start

        # 3. Privatized (Local stack increment)
        shared_arr_priv = mp.Array(ctypes.c_int64, 8)
        procs = [mp.Process(target=worker_privatized_target, args=(shared_arr_priv, i, iters)) for i in range(P)]
        start = time.perf_counter()
        for p in procs: p.start()
        for p in procs: p.join()
        t_priv = time.perf_counter() - start

        if P > 1 and t1_unpad is not None and t_unpad > 0:
            sp_unpad = t1_unpad / t_unpad
            e_unpad = ((P / sp_unpad) - 1) / (P - 1)
            sp_pad = t1_unpad / t_pad if t_pad > 0 else sp_unpad
            e_pad = ((P / sp_pad) - 1) / (P - 1)
        else:
            e_unpad, e_pad = 0.0, 0.0

        rows.append(f"{P}\t{t_unpad:.6f}\t{t_pad:.6f}\t{t_priv:.6f}\t{e_unpad:.6f}\t{e_pad:.6f}")

    with open("results/false_sharing_karp_flatt.tsv", "w") as f:
        f.write("\n".join(rows) + "\n")
    print("False sharing benchmark completed instantly with Numba!")

if __name__ == "__main__":
    mp.freeze_support()
    run_false_sharing()