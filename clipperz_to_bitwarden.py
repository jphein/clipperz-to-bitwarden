#!/usr/bin/env python3
"""Convert Clipperz HTML+JSON export to Bitwarden JSON import format."""

import html
import json
import re
import sys

def extract_json_from_html(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"<textarea[^>]*>(.*?)</textarea>", content, re.DOTALL)
    if not match:
        sys.exit("No <textarea> with JSON data found in export file.")
    return json.loads(html.unescape(match.group(1)))

def convert_to_bitwarden(clipperz_items):
    bw_items = []
    for item in clipperz_items:
        label = item.get("label", "Untitled")
        data = item.get("data", {})
        version = item.get("currentVersion", {})
        fields_dict = version.get("fields", {})
        notes = data.get("notes", "")

        username = None
        password = None
        uris = []
        custom_fields = []

        for _fid, field in fields_dict.items():
            fl = field.get("label", "").lower()
            fv = field.get("value", "")
            action = field.get("actionType", "NONE")

            if action == "PASSWORD" or "password" in fl or "passwd" in fl:
                if password is None:
                    password = fv
                else:
                    custom_fields.append({"name": field["label"], "value": fv, "type": 1})  # hidden
            elif action == "EMAIL" or "email" in fl or "user" in fl or "login" in fl or "account" in fl:
                if username is None:
                    username = fv
                else:
                    custom_fields.append({"name": field["label"], "value": fv, "type": 0})  # text
            elif "url" in fl or "site" in fl or "web" in fl:
                if fv:
                    uris.append({"match": None, "uri": fv})
            else:
                hidden = field.get("hidden", False)
                custom_fields.append({
                    "name": field.get("label", "unknown"),
                    "value": fv,
                    "type": 1 if hidden else 0
                })

        # Try to extract URL from directLogins
        direct_logins = data.get("directLogins", {})
        if isinstance(direct_logins, dict):
            for _dl_id, dl in direct_logins.items():
                if isinstance(dl, dict):
                    form_attrs = dl.get("formData", {}).get("attributes", {})
                    action_url = form_attrs.get("action", "")
                    if action_url:
                        uris.append({"match": None, "uri": action_url})

        # If no URI found, try to derive from label
        if not uris:
            name_lower = label.lower()
            if "." in name_lower and " " not in name_lower:
                uris.append({"match": None, "uri": f"https://{label}"})

        bw_item = {
            "type": 1,  # login
            "name": label,
            "notes": notes if notes else None,
            "favorite": False,
            "login": {
                "uris": uris if uris else None,
                "username": username,
                "password": password,
                "totp": None,
            },
            "fields": custom_fields if custom_fields else None,
        }
        bw_items.append(bw_item)

    return {"encrypted": False, "folders": [], "items": bw_items}

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "20260326-Clipperz_Export.html"
    dst = sys.argv[2] if len(sys.argv) > 2 else "bitwarden_import.json"

    clipperz_data = extract_json_from_html(src)
    bw_data = convert_to_bitwarden(clipperz_data)

    with open(dst, "w", encoding="utf-8") as f:
        json.dump(bw_data, f, indent=2)

    print(f"Converted {len(bw_data['items'])} items -> {dst}")

if __name__ == "__main__":
    main()
