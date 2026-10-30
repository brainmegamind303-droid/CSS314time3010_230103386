import hashlib
import json
import os

def get_student_params(student_id: str):
    h = int(hashlib.sha256(student_id.encode('utf-8')).hexdigest()[:8], 16)
    N = 1024 + ((h % 9) * 64)  # Исправлено с 1924 на 1024 под verify_outputs.py
    buffer_elements = 16_777_216
    seed = h % 100_007
    return {"student_id": student_id, "N": N, "buffer_elements": buffer_elements, "seed": seed}

if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    import sys
    sid = sys.argv[1] if len(sys.argv) > 1 else "230103386"
    params = get_student_params(sid)
    with open("results/salted_params.json", "w") as f:
        json.dump(params, f, indent=4)
    print(f"Salted params generated for ID {sid}")