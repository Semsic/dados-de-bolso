"""Inspeção rápida de CSV, com café imaginário incluído."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def _guess_delimiter(sample: str) -> str:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        # CSV sem pistas suficientes: a vírgula leva o desempate no VAR.
        return ","


def _kind(value: str) -> str:
    value = value.strip()
    if not value:
        return "vazio"
    try:
        int(value)
        return "inteiro"
    except ValueError:
        pass
    try:
        float(value.replace(",", "."))
        return "decimal"
    except ValueError:
        return "texto"


def inspect_csv(path: Path, delimiter: str | None, encoding: str) -> dict[str, Any]:
    with path.open("r", encoding=encoding, newline="") as source:
        sample = source.read(8192)
        source.seek(0)
        chosen = delimiter or _guess_delimiter(sample)
        reader = csv.DictReader(source, delimiter=chosen)
        if not reader.fieldnames:
            raise ValueError("não encontrei cabeçalho; sem ele, até planilha fica tímida")

        names = [name.strip() for name in reader.fieldnames]
        empty = Counter({name: 0 for name in names})
        kinds: dict[str, set[str]] = {name: set() for name in names}
        seen: set[tuple[str, ...]] = set()
        duplicates = 0
        row_count = 0
        for row in reader:
            row_count += 1
            values = tuple((row.get(original) or "").strip() for original in reader.fieldnames)
            if values in seen:
                duplicates += 1
            seen.add(values)
            for original, name, value in zip(reader.fieldnames, names, values):
                if not value:
                    empty[name] += 1
                else:
                    kinds[name].add(_kind(value))

    columns = []
    for name in names:
        observed = kinds[name]
        inferred = next(iter(observed)) if len(observed) == 1 else ("vazio" if not observed else "texto")
        columns.append({"nome": name, "tipo_estimado": inferred, "vazios": empty[name]})
    return {
        "arquivo": path.name,
        "linhas": row_count,
        "colunas": len(names),
        "separador": chosen,
        "linhas_duplicadas": duplicates,
        "campos": columns,
    }


def _format_report(report: dict[str, Any]) -> str:
    lines = [
        f"{report['arquivo']} — {report['linhas']} linhas, {report['colunas']} colunas",
        f"Separador: {report['separador']!r} | Linhas duplicadas: {report['linhas_duplicadas']}",
        "",
        "Coluna                    Tipo estimado   Vazios",
        "-" * 52,
    ]
    lines.extend(
        f"{column['nome'][:24]:24}  {column['tipo_estimado']:13}  {column['vazios']}"
        for column in report["campos"]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dá uma olhada no CSV antes da planilha pedir socorro.")
    parser.add_argument("arquivo", type=Path, help="caminho do arquivo CSV")
    parser.add_argument("--delimiter", help="separador explícito (ex.: ';')")
    parser.add_argument("--encoding", default="utf-8-sig", help="codificação do arquivo (padrão: utf-8-sig)")
    parser.add_argument("--json", action="store_true", help="imprime o relatório em JSON")
    args = parser.parse_args()
    try:
        report = inspect_csv(args.arquivo, args.delimiter, args.encoding)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"Não consegui ler o CSV: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else _format_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
