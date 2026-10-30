import platform
import json
import os

def profile_environment():
    os.makedirs("results", exist_ok=True)
    
    profile = {
        "cpu_model": platform.processor() or "Unknown",
        "system": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "physical_cores": os.cpu_count() or 1,
        "logical_threads": os.cpu_count() or 1,
        "cache_line_bytes": 64,  # Исправлено на cache_line_bytes
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation()
    }
    
    with open("results/host_profile.json", "w") as f:
        json.dump(profile, f, indent=4)
    print("Host profile successfully saved to results/host_profile.json")

if __name__ == "__main__":
    profile_environment()