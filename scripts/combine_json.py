import os
import importlib.util
from pathlib import Path

# Path to folder containing the .py files
FOLDER_PATH = Path("psa_results")  # ⬅️ Update this to your folder path

combined_cards_info = {}

for file_path in FOLDER_PATH.glob("*.py"):
    if file_path.name == "combined_cards_info.py":
        continue

    try:
        # Create a unique module name
        module_name = f"module_{file_path.stem}"

        # Load the module from file
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check if it has cards_info dict
        if hasattr(module, "cards_info") and isinstance(module.cards_info, dict):
            combined_cards_info.update(module.cards_info)
            print(f"✅ Loaded {len(module.cards_info)} entries from {file_path.name}")
        else:
            print(f"⚠️ Skipped {file_path.name} (no valid cards_info found)")

    except Exception as e:
        print(f"❌ Error loading {file_path.name}: {e}")

# Output file path
output_path = FOLDER_PATH / "combined_cards_info.py"

# Write the combined dictionary as a Python file
with open(output_path, "w", encoding="utf-8") as f:
    f.write("# Auto-generated file containing combined cards_info dictionary\n")
    f.write("cards_info = ")
    f.write(repr(combined_cards_info))  # Write as a Python literal

print(f"\n✅ Combined total: {len(combined_cards_info)} cards")
print(f"📁 Saved to: {output_path}")
