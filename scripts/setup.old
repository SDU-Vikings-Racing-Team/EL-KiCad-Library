import os
from pathlib import Path

# Path to KiCad 9.0 global sym-lib-table (Windows example)
sym_table = Path(os.environ["APPDATA"]) / "kicad" / "9.0" / "sym-lib-table"

# The new libraries you want to insert
new_libs = [
    '(lib (name "VIKING_passives")(type "KiCad")(uri "${VIKINGS}/symbols/VIKING_passives.kicad_sym")(options "")(descr ""))',
    '(lib (name "VIKING_connectors")(type "KiCad")(uri "${VIKINGS}/symbols/VIKING_connectors.kicad_sym")(options "")(descr ""))',
    '(lib (name "VIKING_semiconductors")(type "KiCad")(uri "${VIKINGS}/symbols/VIKING_semiconductors.kicad_sym")(options "")(descr ""))',
    '(lib (name "VIKING_ic")(type "KiCad")(uri "${VIKINGS}/symbols/VIKING_ic.kicad_sym")(options "")(descr ""))',
    '(lib (name "VIKING_misc")(type "KiCad")(uri "${VIKINGS}/symbols/VIKING_misc.kicad_sym")(options "")(descr ""))',
]

def main():
    if not sym_table.exists():
        print(f"❌ sym-lib-table not found at {sym_table}")
        return

    with sym_table.open("r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    # Avoid duplicates: check if any VIKING lib already exists
    if any("VIKING_" in line for line in lines):
        print("⚠️  VIKING libraries already present in sym-lib-table.")
        return

    # Insert before the final ")"
    if lines[-1].strip() == ")":
        head = lines[:-1]
        tail = [lines[-1]]
    else:
        head = lines
        tail = []

    updated = head + ["  " + lib for lib in new_libs] + tail

    # Backup original file
    backup = sym_table.with_suffix(".bak")
    sym_table.replace(backup)
    print(f"📂 Backup saved to {backup}")

    # Write updated file
    with sym_table.open("w", encoding="utf-8") as f:
        f.write("\n".join(updated) + "\n")

    print("✅ VIKING libraries added to sym-lib-table.")

if __name__ == "__main__":
    main()
