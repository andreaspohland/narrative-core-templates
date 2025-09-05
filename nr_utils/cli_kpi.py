import json, argparse, sys
from nr_utils.kpi import build_kpi

def main():
    p = argparse.ArgumentParser(description="Build KPI payload for NarrativeReports")
    p.add_argument("--in",  dest="infile",  default="kpis.json", help="Input rows JSON")
    p.add_argument("--out1", dest="out1",   default="formatted_kpis.json", help='Output {"kpi": {...}}')
    p.add_argument("--out2", dest="out2",   default="kpi.json", help='Output only the kpi object')
    p.add_argument("--period-field", default="PeriodType", help="Input field for period (PeriodType/Scope)")
    args = p.parse_args()

    try:
        rows = json.load(open(args.infile, "r", encoding="utf-8"))
        if not isinstance(rows, list):
            raise ValueError("Input must be a list of rows")

        # Kompatibilität: PeriodType → Scope
        for r in rows:
            if isinstance(r, dict) and args.period_field in r and "Scope" not in r:
                r["Scope"] = r[args.period_field]

        kpi = build_kpi(rows)

        json.dump({"kpi": kpi}, open(args.out1, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        json.dump(kpi, open(args.out2, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[nr-kpi] Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
