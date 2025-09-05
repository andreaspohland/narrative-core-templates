import json, argparse, sys, traceback
from nr_utils.kpi import build_kpi

def main():
    p = argparse.ArgumentParser(description="Build KPI payload for NarrativeReports")
    p.add_argument("--in",  dest="infile",  default="kpis.json")
    p.add_argument("--out1", dest="out1",   default="formatted_kpis.json")
    p.add_argument("--out2", dest="out2",   default="kpi.json")
    p.add_argument("--period-field", default="PeriodType")
    args = p.parse_args()

    try:
        rows = json.load(open(args.infile, "r", encoding="utf-8"))

        # 🔎 Debug-Ausgaben
        print(f"[nr-kpi] Loaded type={type(rows)}", file=sys.stderr)

        # Falls dict mit "rows", dann umschalten
        if isinstance(rows, dict) and "rows" in rows:
            print("[nr-kpi] Detected dict with key 'rows' → unpacking", file=sys.stderr)
            rows = rows["rows"]

        if not isinstance(rows, list):
            raise ValueError(f"Expected list of rows, got {type(rows)}")

        # Kompatibilität: PeriodType → Scope
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
        print(f"[nr-kpi] Error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
