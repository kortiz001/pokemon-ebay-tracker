import os
import importlib.util
from pathlib import Path
import pprint

# Path to folder containing the .py files
FOLDER_PATH = Path("psa_results")  # ⬅️ Change this to your folder path

combined_cards_info = {}

for file_path in FOLDER_PATH.glob("*.py"):
    if file_path.name == "combined_cards_info.py":
        continue  # Avoid loading the output file

    try:
        module_name = f"module_{file_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "cards_info") and isinstance(module.cards_info, dict):
            combined_cards_info.update(module.cards_info)
            print(f"✅ Loaded {len(module.cards_info)} entries from {file_path.name}")
        else:
            print(f"⚠️ Skipped {file_path.name} (no valid cards_info found)")

    except Exception as e:
        print(f"❌ Error loading {file_path.name}: {e}")

# Output file path
output_path = "django/pokemon_tracker_project/pokemon_ebay_tracker/scripts/tcgplayer_cards_info_psa_check.py"

# Pretty-print dictionary to the Python file
with open(output_path, "w", encoding="utf-8") as f:
    f.write("# Auto-generated file containing combined cards_info dictionary\n")
    f.write("cards_info = \\\n")
    pprint.pprint(combined_cards_info, stream=f, indent=2, width=100, sort_dicts=False)

print(f"\n✅ Combined total: {len(combined_cards_info)} cards")
print(f"📁 Saved nicely formatted to: {output_path}")
