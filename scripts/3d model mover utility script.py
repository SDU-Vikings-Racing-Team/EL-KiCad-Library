# This script is chat gpt vibe coded, by the undertakers of the project to bulk move 3d model files and references from one location to another
# all the paths are hardcoded, so if you want to use it yourself, you have to modify the paths a bit

import os
import re
import shutil

# Configure these paths
OLD_3D_ROOT = r"X:\DOCUMENTS\Uni\SDU_Vikings\0 - KICAD Material\3D"
NEW_3D_ROOT = r"X:\DOCUMENTS\Uni\SDU_Vikings\EL-KiCad-Library\3dmodels"
FOOTPRINTS_DIR = r"X:\DOCUMENTS\Uni\SDU_Vikings\EL-KiCad-Library\footprints\VIKING_connectors.pretty"

# Regex to match model lines
MODEL_REGEX = re.compile(r'^\s*\(model\s+("?)(\$\{VIKINGSX\}/3D/[^"\s\)]+)\1')

def process_footprint_file(filepath):
    updated_lines = []
    models_found = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            match = MODEL_REGEX.match(line)
            if match:
                old_model_ref = match.group(2)  # path only, no quotes
                filename = os.path.basename(old_model_ref)

                # Construct new model ref
                new_model_ref = f'${{VIKINGS}}/3dmodels/{filename}'

                # Replace the reference in the line
                newline = line.replace(old_model_ref, new_model_ref)
                updated_lines.append(newline)

                # Build old/new absolute paths
                rel_path = old_model_ref.replace("${VIKINGSX}/3D/", "")
                old_path = os.path.join(OLD_3D_ROOT, rel_path)
                new_path = os.path.join(NEW_3D_ROOT, filename)
                models_found.append((old_path, new_path))
            else:
                updated_lines.append(line)

    # Write updated footprint file
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    # Move/copy model files
    for old_path, new_path in models_found:
        if os.path.exists(old_path):
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            if not os.path.exists(new_path):
                print(f"Moving {old_path} → {new_path}")
                shutil.move(old_path, new_path)
            else:
                print(f"Skipped (already exists): {new_path}")
        else:
            print(f"Missing file: {old_path}")

def main():
    for root, _, files in os.walk(FOOTPRINTS_DIR):
        for file in files:
            if file.endswith(".kicad_mod"):
                filepath = os.path.join(root, file)
                print(f"Processing {filepath}")
                process_footprint_file(filepath)

if __name__ == "__main__":
    main()
