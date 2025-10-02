# KiCad Library Integration Guide

This guide explains how to set up and maintain the shared EL-KiCad-Library across multiple repositories and projects. It is written for both maintainers and team members.

---

## Maintainer Guide

### Library repository structure

The EL-KiCad-Library repository is structured as follows:

```
EL-KiCad-Library/
├─ symbols/
│   ├─ VIKING_Connectors.kicad_sym
│   ├─ VIKING_Passives.kicad_sym
│   └─ ...
├─ footprints/
│   ├─ VIKING_Connectors.pretty/
│   ├─ VIKING_Passives.pretty/
│   └─ ...
├─ 3dmodels/
│   └─ ...
├─ scripts/
│   └─ setup_project.py
└─ docs/
    └─ README.md
```

- **symbols**: schematic symbol libraries
    
- **footprints**: PCB footprint libraries
    
- **3dmodels**: 3D models
    
- **library-tables**: template tables
    
- **scripts**: library setup and helpers
    
- **docs**: documentation
    

### Responsibilities of maintainers

- Add new components to the library repository
    
- Tag releases of the library repository so other repositories can use known working versions
    
- Review contributions from team members
    

### Releasing new versions

1. Test changes locally with at least one KiCad project.
    
2. Commit and push updates to **EL-KiCad-Library**.
    
3. Tag a release, for example `v0.2.0`.
    
4. Notify teams to update their submodule reference.
    

---

## Team Member Guide

### Adding the library submodule

If your repository does not yet contain the library, add it once as a submodule:

```bash
git submodule add https://github.com/SDU-Vikings-Racing-Team/EL-KiCad-Library libs/EL-KiCad-Library
git commit -m "Add EL-KiCad-Library submodule"
```

After this, teammates only need to clone with `--recurse-submodules` to get it.

> **Important:** The submodule must always live at `libs/EL-KiCad-Library` relative to the repository root. The setup script depends on this path.

### Cloning a repository with the library

When you clone a repository, make sure to include submodules:

```bash
git clone --recurse-submodules https://github.com/SDU-Vikings-Racing-Team/EL-Dashboard.git
```

If already cloned without submodules:

```bash
git submodule update --init --recursive
```

This ensures `libs/EL-KiCad-Library` is present.

### Generating project library tables

From the repository root, run:

```bash
# Preview changes
python libs/EL-KiCad-Library/scripts/setup_project.py --dry-run

# Write tables for all projects
python libs/EL-KiCad-Library/scripts/setup_project.py
```

This creates or updates `sym-lib-table` and `fp-lib-table` in each KiCad project folder.

Commit these files:

```bash
git add **/sym-lib-table **/fp-lib-table
git commit -m "Generate KiCad library tables"
```

### KiCad global setup

If you have never opened KiCad before, the first time you open KiCad it will prompt you to configure the global symbol library table.

- Select **Copy default global symbol library table (recommended)**
    
- Press **OK**
    

This ensures you have both the default KiCad libraries and the Vikings library.

### Verifying in KiCad

1. Open the project `.kicad_pro`.
    
2. In **Schematic Editor**, press **A** and search for `VIKING_`. Your libraries should appear.
    
3. In **PCB Editor**, open the **Footprint Libraries Browser** and confirm `VIKING_*` entries.
    
4. Place a symbol, update PCB, and verify that the footprint and 3D model are correct.
    

### Updating submodule

When there is a new release:

```bash
git -C libs/EL-KiCad-Library fetch --tags
git -C libs/EL-KiCad-Library checkout v0.2.0
git add libs/EL-KiCad-Library
git commit -m "Update EL-KiCad-Library to v0.2.0"
```

### Bumping the library pointer after changes

If a teammate adds or edits content in **EL-KiCad-Library** and you need it in your repository:

```bash
git submodule update --init --recursive
git -C libs/EL-KiCad-Library fetch origin
git submodule update --remote libs/EL-KiCad-Library
git add libs/EL-KiCad-Library
git commit -m "Bumped EL-KiCad-Library submodule to latest"
git push
```

- If a new symbol was added inside an existing `.kicad_sym` file, no table regeneration is needed.
    
- If a brand new `.kicad_sym` file or a new `.pretty` library was added, regenerate project tables:
    

```bash
python libs/EL-KiCad-Library/scripts/setup_project.py
git add **/sym-lib-table **/fp-lib-table
git commit -m "Refresh KiCad library tables"
git push
```

### Handling Git safe.directory

On shared or VM paths, Git may block submodule operations. If you see a message about dubious ownership, mark the path as safe:

```bash
git config --global --add safe.directory /absolute/path/to/your/repo/libs/EL-KiCad-Library
git submodule update --init --recursive
```

### Ignoring projects

To skip irrelevant folders during setup, create `.kicadprojignore` in the repository root:

```
**/libs/**
**/third_party/**
**/archive/**
```

You can also create a `kicad-projects.yml` with explicit project paths to include:

```yaml
projects:
  - projects/EL-Dashboard/4D-Systems-Dashboard (TIVA)/DashboardPCB
  - projects/EL-Dashboard/4D-Systems-Dashboard (TIVA)/Steering Wheel/SteeringWheelPCB
```

---