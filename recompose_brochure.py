#!/usr/bin/env python3
"""Recompose un scan de brochure A5 impose sur des feuilles A4.

Le scan fourni contient 2 feuilles de couverture, puis des feuilles tournees a
90 degres. La couverture de la deuxieme feuille est conservee, puis les autres
feuilles sont decoupees en pages A5 et remises dans l'ordre 1, 2, ..., 31,
suivi de la page blanche finale.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pymupdf


COVER_SHEETS = 2
BEST_COVER_SHEET = 1  # deuxieme page du PDF source (index Python 1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="PDF scanne")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="PDF recompose (par defaut: *_recompose.pdf)",
    )
    parser.add_argument(
        "--no-blank",
        action="store_true",
        help="ne pas conserver la page A5 blanche finale",
    )
    parser.add_argument(
        "--no-cover",
        action="store_true",
        help="ne pas ajouter la couverture issue de la deuxieme page source",
    )
    return parser.parse_args()


def add_half(
    output: pymupdf.Document,
    source: pymupdf.Document,
    source_index: int,
    side: str,
) -> None:
    """Ajoute une moitie de feuille comme page A5 portrait.

    Apres rotation horaire, la moitie inferieure du scan devient la page de
    gauche et la moitie superieure devient la page de droite.
    """
    source_page = source[source_index]
    width = source_page.rect.width
    height = source_page.rect.height
    half = height / 2

    if side == "left":
        clip = pymupdf.Rect(0, half, width, height)
    elif side == "right":
        clip = pymupdf.Rect(0, 0, width, half)
    else:
        raise ValueError(f"cote inconnu: {side}")

    # Les dimensions exactes de la moitie preserve la resolution du scan.
    page = output.new_page(width=half, height=width)
    page.show_pdf_page(page.rect, source, source_index, clip=clip, rotate=270)


def page_order(number_of_spreads: int) -> list[tuple[int, str]]:
    """Retourne l'ordre des pages numerotees pour l'imposition observee."""
    if number_of_spreads < 2:
        raise ValueError("Il faut au moins deux feuilles apres les couvertures")

    order: list[tuple[int, str]] = []

    # Feuille exterieure: page blanche a gauche, page 1 a droite.
    order.append((0, "right"))

    # Pages 2 a 16 (dans cet exemple).
    for spread in range(1, number_of_spreads):
        side = "left" if spread % 2 else "right"
        order.append((spread, side))

    # Au centre: pages 16/17 sur la derniere feuille.
    order.append((number_of_spreads - 1, "right"))

    # Retour depuis le centre: pages 18 a 31.
    for spread in range(number_of_spreads - 2, 0, -1):
        side = "left" if spread % 2 == 0 else "right"
        order.append((spread, side))

    # La boucle ci-dessus se termine deja par la page 31 (feuille 1,
    # cote droit).
    return order


def main() -> None:
    args = parse_args()
    input_path = args.input
    output_path = args.output or input_path.with_name(
        f"{input_path.stem}_recompose.pdf"
    )

    if output_path.resolve() == input_path.resolve():
        raise SystemExit("Le fichier de sortie doit etre different du fichier source")

    source = pymupdf.open(input_path)
    try:
        spread_count = source.page_count - COVER_SHEETS
        if spread_count != 16:
            raise SystemExit(
                f"Nombre inattendu de feuilles apres les couvertures: {spread_count} "
                "(16 attendu pour les pages 1 a 31)."
            )

        output = pymupdf.open()
        try:
            # La couverture est la moitie droite de la deuxieme page source,
            # qui est mieux scannee que la premiere.
            if not args.no_cover:
                add_half(output, source, BEST_COVER_SHEET, "right")

            for spread, side in page_order(spread_count):
                add_half(output, source, COVER_SHEETS + spread, side)

            if not args.no_blank:
                # La moitie blanche de la premiere feuille est la derniere
                # page physique de la brochure.
                add_half(output, source, COVER_SHEETS, "left")

            output.set_metadata(
                {
                    "title": "Brochure St-Maurice (recomposee)",
                    "creator": "recompose_brochure.py",
                }
            )
            output.save(output_path, garbage=4, deflate=True)
        finally:
            output.close()
    finally:
        source.close()

    page_count = (not args.no_cover) + 31 + (not args.no_blank)
    print(f"PDF cree: {output_path} ({page_count} pages)")


if __name__ == "__main__":
    main()
