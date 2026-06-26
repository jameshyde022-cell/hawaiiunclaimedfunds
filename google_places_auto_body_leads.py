#!/usr/bin/env python3
"""
Generate a Hawaii auto body/collision repair lead list from Google Places.

This script does not search or scrape State of Hawaii unclaimed-property sites.
Those fields are intentionally left for manual review after you search the
official site yourself.
"""

import argparse
import csv
import json
import os
import time
import urllib.error
import urllib.request


API_URL = "https://places.googleapis.com/v1/places:searchText"
DEFAULT_OUTPUT = "leads_auto_body_hawaii.csv"

FIELDNAMES = [
    "Business Name",
    "Category",
    "Address",
    "City",
    "Phone",
    "Website",
    "Google Maps URL",
    "Source",
    "State Unclaimed Property Search Completed",
    "Total Found",
    "Number of Records",
    "Priority",
    "Notes",
]

SEARCH_QUERIES = [
    "auto body shop Honolulu",
    "collision repair Honolulu",
    "auto paint Honolulu",
    "towing Honolulu",
    "auto body Kapolei",
    "auto body Waipahu",
    "auto body Pearl City",
    "auto body Aiea",
    "auto body Kaneohe",
    "auto body Kailua",
    "auto body Mililani",
    "auto body Ewa Beach",
    "auto body Wahiawa",
    "auto body Waianae",
]


def infer_city(query):
    known_cities = [
        "Ewa Beach",
        "Pearl City",
        "Honolulu",
        "Kapolei",
        "Waipahu",
        "Aiea",
        "Kaneohe",
        "Kailua",
        "Mililani",
        "Wahiawa",
        "Waianae",
    ]
    for city in known_cities:
        if city.lower() in query.lower():
            return city
    return ""


def infer_category(query, place):
    q = query.lower()
    primary = place.get("primaryTypeDisplayName", {}).get("text", "")
    if "towing" in q:
        return "Towing"
    if "collision" in q:
        return "Collision Repair"
    if "paint" in q:
        return "Auto Paint/Body"
    if primary:
        return primary
    return "Auto Body"


def places_text_search(api_key, query, page_size=20):
    payload = {
        "textQuery": query,
        "pageSize": page_size,
        "locationBias": {
            "rectangle": {
                "low": {"latitude": 18.85, "longitude": -161.0},
                "high": {"latitude": 22.35, "longitude": -154.5},
            }
        },
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": ",".join(
            [
                "places.id",
                "places.displayName",
                "places.formattedAddress",
                "places.nationalPhoneNumber",
                "places.websiteUri",
                "places.googleMapsUri",
                "places.primaryTypeDisplayName",
                "places.types",
            ]
        ),
    }
    request = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8")).get("places", [])


def place_to_row(place, query):
    return {
        "Business Name": place.get("displayName", {}).get("text", ""),
        "Category": infer_category(query, place),
        "Address": place.get("formattedAddress", ""),
        "City": infer_city(query),
        "Phone": place.get("nationalPhoneNumber", ""),
        "Website": place.get("websiteUri", ""),
        "Google Maps URL": place.get("googleMapsUri", ""),
        "Source": "Google Places API",
        "State Unclaimed Property Search Completed": "No",
        "Total Found": "",
        "Number of Records": "",
        "Priority": "Medium",
        "Notes": "State unclaimed-property search must be completed manually.",
    }


def write_template(path):
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()


def write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Create a Hawaii auto body/collision/towing lead CSV using Google Places."
    )
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="CSV output path.")
    parser.add_argument("--page-size", type=int, default=20, help="Google Places results per query, max 20.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Delay between API calls.")
    args = parser.parse_args()

    api_key = os.environ.get("GOOGLE_PLACES_API_KEY") or os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        write_template(args.output)
        print(f"No Google Places API key found. Wrote blank template: {args.output}")
        print("Set GOOGLE_PLACES_API_KEY and rerun to populate business leads.")
        return

    seen = set()
    rows = []
    for query in SEARCH_QUERIES:
        print(f"Searching: {query}")
        try:
            places = places_text_search(api_key, query, min(args.page_size, 20))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise SystemExit(f"Google Places API error for '{query}': {exc.code} {detail}") from exc

        for place in places:
            key = place.get("id") or (
                place.get("displayName", {}).get("text", "").lower(),
                place.get("formattedAddress", "").lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            rows.append(place_to_row(place, query))
        time.sleep(args.sleep)

    rows.sort(key=lambda row: (row["City"], row["Business Name"]))
    write_rows(args.output, rows)
    print(f"Wrote {len(rows)} leads to {args.output}")
    print("Manual next step: search State of Hawaii unclaimed property yourself and fill in the review columns.")


if __name__ == "__main__":
    main()
