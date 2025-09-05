import json, argparse, sys, traceback
from nr_utils.kpi import build_kpi

def main():
    p = argparse.ArgumentParser(description="Build KPI payload for NarrativeReports")
    p.add_argument("--in",  dest="infile",  default="kpis.json", help="Input rows JSON")
    p.add_argument("--out1", dest="out1",   default="formatted_kpis.json", help='Output {"kpi": {...}}')
    p.add_argument("--out2", dest="out2",   default="kpi.json", help='Output only the kpi object')
    p.add_argument("--period-field", default="PeriodType", help="Input field for period (PeriodType/Scope)")
    args = p.parse_args()

    try:
        with open(args.infile, "r", encoding="utf-8") as f:
            rows = json.load(f)

        # Debug-Ausgabe zum Input
        print(f"[nr-kpi] Loaded type={type(rows)}", file=sys.stderr)
        if isinstance(rows, list):
            print(f"[nr-kpi] List length={len(rows)}", file=sys.stderr)
            if rows:
                print(f"[nr-kpi] First row keys={list(rows[0].keys())}", file=sys.stderr)
        elif isinstance(rows, dict):
            print(f"[nr-kpi] Dict keys={list(rows.keys())}", file=sys.stderr)
        else:
            print(f"[nr-kpi] Unexpected JSON structure", file=sys.stderr)

        if not isinstance(rows, list):
            raise ValueError("Input must be a list of rows")

        # Kompatibilität: PeriodType -> Scope
        for r in rows:
            if isinstance(r, dict) and args.period_field in r and "Scope" not in r:
                r["Scope"] = r[args.period_field]

        kpi = build_kpi(rows)

        json.dump({"kpi": kpi}, open(args.out1, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        json.dump(kpi, open(args.out2, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)

        print("[nr-kpi] Success, files written.", file=sys.stderr)

    except Exception as e:
        msg = f"[nr-kpi] Error: {e}"
        print(msg, file=sys.stderr)
        print(msg)  # zusätzlich stdout
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
