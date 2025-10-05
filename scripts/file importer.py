import os
import re
import zipfile

# Base library paths
FOOTPRINT_BASE = r"X:\DOCUMENTS\Uni\SDU_Vikings\EL-KiCad-Library\footprints"
MODEL_BASE     = r"X:\DOCUMENTS\Uni\SDU_Vikings\EL-KiCad-Library\3dmodels"
SYMBOL_BASE    = r"X:\DOCUMENTS\Uni\SDU_Vikings\EL-KiCad-Library\symbols\to_sort"

# Footprint libraries
FOOTPRINT_FOLDERS = [
    "VIKING_Connectors.pretty",
    "VIKING_Graphics.pretty",
    "VIKING_IC.pretty",
    "VIKING_Misc.pretty",
    "VIKING_Passives.pretty",
    "VIKING_Semiconductors.pretty",
]


def process_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Find candidate files
        kicad_mod = [f for f in zf.namelist() if f.endswith(".kicad_mod")]
        kicad_sym = [f for f in zf.namelist() if f.endswith(".kicad_sym")]
        step_files = [f for f in zf.namelist() if f.endswith(".stp")]

        if not kicad_mod and not kicad_sym and not step_files:
            print(f"⚠️  No relevant files found in {os.path.basename(zip_path)}")
            return

        chosen_folder = None

        # Ask user where the footprint should go (only if footprint exists)
        if kicad_mod:
            print(f"\n📦 Processing {os.path.basename(zip_path)}")
            print("Choose destination footprint library:")
            for i, folder in enumerate(FOOTPRINT_FOLDERS, 1):
                print(f"{i}. {folder}")
            choice = int(input("Enter number: "))
            chosen_folder = FOOTPRINT_FOLDERS[choice - 1]
            fp_dst_folder = os.path.join(FOOTPRINT_BASE, chosen_folder)
            os.makedirs(fp_dst_folder, exist_ok=True)

            # Determine the correct .stp filename if present
            if step_files:
                step_name = os.path.basename(step_files[0])  # use first found .stp file
            else:
                step_name = None

            # Extract and patch .kicad_mod
            for f in kicad_mod:
                fname = os.path.basename(f)
                dst_path = os.path.join(fp_dst_folder, fname)

                with zf.open(f) as src, open(dst_path, "wb") as out:
                    content = src.read().decode("utf-8")

                    # If a 3D model exists, update or add it
                    if step_name:
                        model_path = f"${{VIKINGS}}/3dmodels/{step_name}"

                        if "(model" in content:
                            # Replace any existing model path with the correct quoted path
                            content, n = re.subn(
                                r'\(model\s+("?)[^()\s"]+("?)(?=\s|\n|\r)',
                                f'(model "{model_path}"',
                                content
                            )
                            if n > 0:
                                print(f"✅ Updated model path in {fname} → {step_name}")
                            else:
                                print(f"⚠️  Could not match model line in {fname}, leaving as-is")
                        else:
                            # Append new model block before final closing parenthesis
                            model_block = f"""
  (model "{model_path}"
    (at (xyz 0 0 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0))
  )"""
                            idx = content.rstrip().rfind(')')
                            if idx != -1:
                                content = content[:idx] + model_block + "\n)"
                            else:
                                content += model_block
                            print(f"✅ Added new model block to {fname}")
                    else:
                        print(f"⚠️  No .stp file found for {fname}, skipping model path update")

                    out.write(content.encode("utf-8"))

        # Extract .kicad_sym
        if kicad_sym:
            sym_group = chosen_folder if chosen_folder else "unsorted"
            sym_dst_folder = os.path.join(SYMBOL_BASE, sym_group)
            os.makedirs(sym_dst_folder, exist_ok=True)

            for f in kicad_sym:
                fname = os.path.basename(f)
                dst_path = os.path.join(sym_dst_folder, fname)
                with zf.open(f) as src, open(dst_path, "wb") as out:
                    out.write(src.read())
                print(f"✅ Extracted symbol: {dst_path}")

        # Extract .stp files
        if step_files:
            os.makedirs(MODEL_BASE, exist_ok=True)
            for f in step_files:
                fname = os.path.basename(f)
                dst_path = os.path.join(MODEL_BASE, fname)
                with zf.open(f) as src, open(dst_path, "wb") as out:
                    out.write(src.read())
                print(f"✅ Extracted 3D model: {dst_path}")


def process_folder(folder_path):
    zips = [f for f in os.listdir(folder_path) if f.lower().endswith(".zip")]
    if not zips:
        print("❌ No .zip files found in folder.")
        return

    for zip_name in zips:
        zip_path = os.path.join(folder_path, zip_name)
        process_zip(zip_path)


if __name__ == "__main__":
    folder_path = input("Enter folder containing LIB_xxx.zip files: ").strip('"')
    if os.path.isdir(folder_path):
        process_folder(folder_path)
    else:
        print("❌ Invalid folder path")
