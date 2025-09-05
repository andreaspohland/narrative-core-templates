import json, argparse, sys
from nr_utils.weather import build_weather_payload

def main():
    p = argparse.ArgumentParser(description="Build weather payload for NarrativeReports")
    p.add_argument("--in",  dest="infile",  default="weather_rows.json", help="Input rows JSON")
    p.add_argument("--out", dest="outfile", default="weather_numeric.json", help="Output normalized payload")
    args = p.parse_args()

    try:
        rows = json.load(open(args.infile, "r", encoding="utf-8"))
        if not isinstance(rows, list):
            rows = []
        payload = build_weather_payload(rows)

        json.dump(payload, open(args.outfile, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[nr-weather] Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
