<div align="center">
  <h1>Crystal Interface Builder</h1>
  <p><strong>A Python script for finding and constructing possible interfaces between two crystal structures from CIF files.</strong></p>
  <p>Surface-lattice matching with <a href="https://pymatgen.org/">pymatgen</a> and <code>ZSLGenerator</code></p>
</div>

## Overview

This Python script searches for and constructs possible interfaces between two crystal structures from CIF files. It uses `ZSLGenerator` from the [`pymatgen`](https://pymatgen.org/) library to match surface lattices.

To build an interface model, the surface orientations of both crystals must be specified, suitable surface cells must be found, and the structures must be assembled into a single model. The script automates this process: it searches for geometrically compatible surface supercells, creates interface candidates, and saves them as CIF files.

The script creates initial geometric models for inspection and further calculations. It does not optimize atomic coordinates or determine the energy or stability of an interface. The resulting structures therefore need to be checked separately.

## Workflow

1. Loads two structures from CIF files.
2. Validates the Miller indices specified for each structure.
3. Uses `ZSLGenerator` to search for pairs of two-dimensional surface supercells that meet the specified tolerances for vector lengths, cell areas, and angles.
4. Uses `CoherentInterfaceBuilder` to construct interfaces for the available atomic configurations of the surfaces.
5. Saves the resulting structures in CIF format, organized into separate directories.
6. Prints a summary of how many configurations were found, processed, and saved.

If an error occurs while an interface is being created for one configuration, the script reports it and continues processing the remaining configurations.

## Requirements

Versions in the environment used:

- Python **3.12.12**
- `pymatgen` **2026.5.4**

Install the dependency from the project directory:

```bash
python3 -m pip install -r requirements.txt
```

## Input files

By default, the script expects two CIF files:

- `A.cif` — the first structure, used as the substrate;
- `B.cif` — the second structure, used as the film.

Place both files in the directory from which you run the script, or specify different filenames and paths in the `CIF_A` and `CIF_B` settings near the top of `interface_builder.py`.

CIF files are not included in this repository.

## Settings

Settings are defined near the top of `interface_builder.py`.

| Parameter | Default value | Description |
| :--- | ---: | :--- |
| `CIF_A`, `CIF_B` | `A.cif`, `B.cif` | Paths to the two input structures |
| `MILLER_A`, `MILLER_B` | `(1, 0, 0)` | Miller indices of the surfaces |
| `MAX_LENGTH_TOL` | `0.01` | Tolerance for relative mismatch between surface-vector lengths |
| `MAX_AREA_RATIO_TOL` | `0.01` | Tolerance for relative mismatch between surface-cell areas |
| `MAX_ANGLE_TOL` | `0.01` rad | Tolerance for angle mismatch |
| `MAX_AREA` | `1000` Å² | Maximum surface-supercell area |
| `INTERFACE_GAP` | `2.5` Å | Gap between the two surfaces in the interface |
| `VACUUM` | `8.0` Å | Vacuum thickness above the film |
| `LAYERS_A`, `LAYERS_B` | `1`, `1` | Number of layers in the first and second structures |
| `OUTPUT_DIR` | `interface_output` | Output directory |
| `LABEL_INDEX` | `True` | Add indices to surface-configuration labels |
| `FILTER_OUT_SYM_SLABS` | `False` | Keep symmetry-equivalent surface slabs |

Length and area tolerances are specified as fractions; for example, `0.01` corresponds to 1%. The angle tolerance is specified in radians. Changing the tolerances and maximum area affects the number, size, and geometric match quality of the generated models.

## Run

Go to the project directory containing the script and input CIF files, activate a Python environment with `pymatgen` installed, and run:

```bash
python3 interface_builder.py
```

## Output

The script saves structures in the directory specified by `OUTPUT_DIR`. A separate `termination_N` subdirectory is created for each surface atomic configuration, where `N` is its index.

Example output structure:

```text
interface_output/
├── termination_1/
│   ├── interface_1.cif
│   └── interface_2.cif
└── termination_2/
    └── interface_1.cif
```

The `interface_N.cif` files contain the generated interface structures. If no suitable matches are found, the script reports this and suggests changing the tolerances or maximum surface-supercell area.

## Examples

The script was used to generate three interfaces for different pairs of materials. Their structures were visualized in VESTA, and the images are included in the `examples/` folder to illustrate the script’s output.

## Method and references

`ZSLGenerator` in `pymatgen` implements a surface-lattice matching method based on the following paper:

A. Zur and T. C. McGill, “Lattice match: An application to heteroepitaxy,” *Journal of Applied Physics*, vol. 55, pp. 378–386 (1984). [https://doi.org/10.1063/1.333084](https://doi.org/10.1063/1.333084)

In this script, `ZSLGenerator` searches for compatible surface supercells, while `CoherentInterfaceBuilder` constructs interface models based on those matches. See the [`pymatgen` documentation](https://pymatgen.org/pymatgen.analysis.interfaces.html) for details about these classes.
