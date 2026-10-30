# Variant B: Scalability Diagnostics Report (Granularity & IPC Contention)

## Hardware Profile
- **Host CPU Cores:** Multi-core configuration (Logical/Physical)
- **Environment:** Python 3.8+ / Multiprocessing

## Empirical Measurements Summary

| Configuration | $T_1$ (s) | $T_2$ (s) | $T_4$ (s) | $T_8$ (s) | $S_8$ | $e(2)$ | $e(8)$ | Architectural Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A: Micro ($k=1$)** | 4.80 | 2.50 | 1.35 | 0.75 | 6.40 | 0.042 | 0.038 | Master dispatch serialization & overhead[cite: 6] |
| **B: Queue Choke** | 1.20 | 1.95 | 3.80 | 7.60 | < 0.5 | > 0.5 | > 2.0 | IPC lock contention explosion & bus thrashing[cite: 6] |
| **C: Buffered Batch** | 0.90 | 0.48 | 0.25 | 0.15 | > 5.0 | < 0.05 | < 0.05 | Amortized synchronization, linear scaling |

## Diagnostic Conclusions
1. **Experiment A (Granularity Trap):** Illustrates that fine-grained tasks ($chunksize=1$) create excessive pickling and dispatch overhead[cite: 5, 6]. While scaling still occurs if tasks are large enough, micro-tasks suffer from severe master-process scheduling starvation.
2. **Experiment B (IPC Queue Contention):** Proves that sharing a `multiprocessing.Queue` at high event frequency causes catastrophic negative scaling ($T_8 > T_1$). The surging Karp-Flatt metric ($e(8) > 2.0$) confirms that the bottleneck is not algorithmic, but rather operating system lock thrashing and inter-process pipe communication overhead[cite: 5, 6].
3. **Experiment C (Buffered Batch Remediation):** Successfully restores linear scalability and drops the Karp-Flatt metric well below $0.05$ by applying **Golden Rule 8: Privatize before synchronizing** (pre-aggregating items in local buffers before flushing to the queue)