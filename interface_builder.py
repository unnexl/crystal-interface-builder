from pathlib import Path

from pymatgen.core import Structure
from pymatgen.analysis.interfaces.zsl import ZSLGenerator
from pymatgen.analysis.interfaces.coherent_interfaces import (
    CoherentInterfaceBuilder,
)

# ============================================================
# SETTINGS
# ============================================================

# Input CIF files

CIF_A = "A.cif"
CIF_B = "B.cif"

# Miller indices

MILLER_A = (1, 0, 0)
MILLER_B = (1, 0, 0)

# 2D matching supercell tolerances

MAX_LENGTH_TOL = 0.01           # Maximum relative mismatch between surface-vector lengths
MAX_AREA_RATIO_TOL = 0.01       # Maximum relative mismatch between surface-cell areas
MAX_ANGLE_TOL = 0.01            # Maximum angle mismatch, radians
MAX_AREA = 1000                 # Maximum surface supercell area, Å²

# Interface parameters

INTERFACE_GAP = 2.5             # Distance between substrate and film surfaces, Å
VACUUM = 8.0                    # Vacuum thickness above the film, Å

LAYERS_A = 1                    # Number of substrate layers
LAYERS_B = 1                    # Number of film layers

# Output

OUTPUT_DIR = "interface_output"

# Additional settings

LABEL_INDEX = True              # Label interfaces by termination/symmetry indices
FILTER_OUT_SYM_SLABS = False    # Keep symmetry-equivalent slab terminations

# ============================================================
# LOAD CIF
# ============================================================


def load_structure(filename):
    path = Path(filename)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {filename}"
        )

    structure = Structure.from_file(filename)

    print(f"\nLoaded: {filename}")
    print(f"Formula: {structure.composition.reduced_formula}")
    print(f"Atoms: {len(structure)}")
    print(f"Volume: {structure.volume:.3f} Å³")

    return structure


# ============================================================
# VALIDATE MILLER INDICES
# ============================================================


def validate_miller(miller, name):
    if len(miller) != 3:
        raise ValueError(
            f"{name} must contain exactly 3 integers."
        )

    if not all(isinstance(x, int) for x in miller):
        raise ValueError(
            f"{name} must contain only integers."
        )

    if miller == (0, 0, 0):
        raise ValueError(
            f"{name} cannot be (0, 0, 0)."
        )


# ============================================================
# FIND 2D MATCHING SUPERCELLS
# ============================================================


def find_matching_interfaces(
    structure_A,
    structure_B,
    miller_A,
    miller_B,
):
    """
    Find matching 2D surface supercells
    and build interfaces between the two crystals.

    ZSL matching failures for individual terminations
    are skipped without stopping the program.
    """

    zsl = ZSLGenerator(
        max_area_ratio_tol=MAX_AREA_RATIO_TOL,
        max_area=MAX_AREA,
        max_length_tol=MAX_LENGTH_TOL,
        max_angle_tol=MAX_ANGLE_TOL,
        bidirectional=True,
    )

    print("\nSearching for 2D matching supercells...")
    print(f"Substrate Miller: {miller_A}")
    print(f"Film Miller: {miller_B}")

    print(
        f"Maximum length mismatch: "
        f"{MAX_LENGTH_TOL * 100:.2f}%"
    )

    print(
        f"Maximum area mismatch: "
        f"{MAX_AREA_RATIO_TOL * 100:.2f}%"
    )

    print(
        f"Maximum angle mismatch: "
        f"{MAX_ANGLE_TOL:.4f} rad"
    )

    print(
        f"Maximum supercell area: "
        f"{MAX_AREA:.2f} Å²"
    )

    builder = CoherentInterfaceBuilder(
        substrate_structure=structure_A,
        film_structure=structure_B,
        substrate_miller=miller_A,
        film_miller=miller_B,
        zslgen=zsl,
        label_index=LABEL_INDEX,
        filter_out_sym_slabs=FILTER_OUT_SYM_SLABS,
    )

    print(
        f"\nFound terminations: "
        f"{len(builder.terminations)}"
    )

    termination_results = {}
    successful_terminations = 0
    skipped_terminations = 0

    # Process each termination and keep its interfaces separate.
    for termination_index, termination in enumerate(
        builder.terminations,
        start=1,
    ):
        try:
            generated = builder.get_interfaces(
                termination=termination,
                gap=INTERFACE_GAP,
                vacuum_over_film=VACUUM,
                film_thickness=LAYERS_B,
                substrate_thickness=LAYERS_A,
                in_layers=True,
            )

            # Keep iteration inside the try block because errors
            # may occur while the generator is being consumed.
            termination_interfaces = list(generated)

            print(
                f"Termination {termination_index} ({termination}): "
                f"{len(termination_interfaces)} interface(s)"
            )

            if termination_interfaces:
                termination_results[termination_index] = (
                    termination,
                    termination_interfaces,
                )
                successful_terminations += 1
            else:
                skipped_terminations += 1

        except ValueError as error:
            skipped_terminations += 1
            print(
                f"Termination {termination_index} ({termination}) "
                f"was skipped: {type(error).__name__}: {error}"
            )
            continue

        except Exception as error:
            skipped_terminations += 1
            print(
                f"Termination {termination_index} ({termination}) "
                f"was skipped: {type(error).__name__}: {error}"
            )
            continue

    total_interfaces = sum(
        len(interfaces)
        for _, interfaces in termination_results.values()
    )

    # Print the final search summary.
    print("\n" + "=" * 60)
    print("SEARCH SUMMARY")
    print("=" * 60)

    print(
        f"Total terminations: "
        f"{len(builder.terminations)}"
    )

    print(
        f"Successful terminations: "
        f"{successful_terminations}"
    )

    print(
        f"Skipped terminations: "
        f"{skipped_terminations}"
    )

    print(
        f"Total interfaces generated: "
        f"{total_interfaces}"
    )

    return termination_results


# ============================================================
# SAVE RESULTS
# ============================================================


def save_interfaces(termination_results, output_dir):
    if not termination_results:
        print("\nNo matching interfaces found.")
        print(
            "Try increasing MAX_LENGTH_TOL, "
            "MAX_AREA_RATIO_TOL or MAX_AREA."
        )
        return

    print("\nSaving interfaces...")

    saved_count = 0
    failed_count = 0

    for termination_index, (termination, interfaces) in (
        termination_results.items()
    ):
        # Create a folder only when this termination has interfaces.
        termination_dir = output_dir / f"termination_{termination_index}"
        termination_dir.mkdir(parents=True, exist_ok=True)

        print(
            f"\nSaving {len(interfaces)} interface(s) "
            f"for termination {termination_index} ({termination})..."
        )

        for interface_index, interface in enumerate(interfaces, start=1):
            filename = termination_dir / f"interface_{interface_index}.cif"

            try:
                interface.to(filename)
                saved_count += 1
                print(f"Saved: {filename}")

            except Exception as error:
                failed_count += 1
                print(
                    f"Failed to save interface "
                    f"{termination_index}.{interface_index}: "
                    f"{type(error).__name__}: {error}"
                )
                continue

    # Print the final saving summary.
    print("\n" + "=" * 60)
    print("SAVING SUMMARY")
    print("=" * 60)

    print(f"Saved: {saved_count}")
    print(f"Failed: {failed_count}")
    print("\nDone.")


# ============================================================
# MAIN
# ============================================================


def main():
    # Validate Miller indices.
    validate_miller(MILLER_A, "MILLER_A")
    validate_miller(MILLER_B, "MILLER_B")

    # Load structures.
    structure_A = load_structure(CIF_A)
    structure_B = load_structure(CIF_B)

    # Find interfaces, grouped by termination.
    termination_results = find_matching_interfaces(
        structure_A,
        structure_B,
        MILLER_A,
        MILLER_B,
    )

    # Save each termination's interfaces in its own folder.
    save_interfaces(
        termination_results,
        Path(OUTPUT_DIR),
    )


if __name__ == "__main__":
    main()