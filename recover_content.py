import os
import subprocess

PAGES = [
    ("", "index.html"),
    ("about/", "about/index.html"),
    ("services/", "services/index.html"),
    ("services/lead-generation/", "services/lead-generation/index.html"),
    ("services/virtual-assistance/", "services/virtual-assistance/index.html"),
    ("services/crm-management/", "services/crm-management/index.html"),
    ("services/accounting-bookkeeping/", "services/accounting-bookkeeping/index.html"),
    ("services/ecommerce-management/", "services/ecommerce-management/index.html"),
    ("services/automation/", "services/automation/index.html"),
    ("portfolio/", "portfolio/index.html"),
    ("testimonials/", "testimonials/index.html"),
    ("contact/", "contact/index.html"),
    ("404/", "404.html"),
    ("automation/", "automation/index.html")
]

BASE_URL = "https://growthleder.com/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

for path, local_file in PAGES:
    print(f"Recovering {local_file} from {BASE_URL}{path}...")
    
    # Ensure local directory exists
    dir_name = os.path.dirname(local_file)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    url = f"{BASE_URL}{path}"
    cmd = ["curl", "-s", "-k", "-A", UA, "-L", url]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout:
            with open(local_file, "w") as f:
                f.write(result.stdout)
            print(f"  [OK] Saved to {local_file} ({len(result.stdout)} bytes)")
        else:
            print(f"  [FAILED] Empty response for {url}")
    except Exception as e:
        print(f"  [ERROR] {e}")

print("Recovery finished.")
