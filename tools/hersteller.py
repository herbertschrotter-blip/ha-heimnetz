#!/usr/bin/env python3
"""Herstellerliste für die Erkennung der Geräteart (AN-0001) neu erzeugen.

Quelle: die Liste `manuf` von Wireshark (aus den öffentlichen IEEE-Registern der Hardware-Adressen,
https://www.wireshark.org/download/automated/data/manuf). Übernommen werden nur ganze Adressblöcke (/24) der
Hersteller in HERSTELLER; das Ergebnis liegt offline in der Integration, zur Laufzeit wird nichts nachgeschlagen.

  python3 tools/hersteller.py <pfad-zu-manuf>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ZIEL = Path(__file__).parents[1] / "custom_components" / "heimnetz" / "logik" / "hersteller.txt"
# Teil des Herstellernamens in der Liste → kurzer Name (die Art je Hersteller steht in logik/arten.py)
HERSTELLER = {
    "AVM GmbH": "AVM",
    "Espressif": "Espressif",
    "Shelly": "Shelly",
    "Allterco": "Shelly",
    "Raspberry Pi": "Raspberry Pi",
    "Sonos": "Sonos",
    "Apple": "Apple",
    "Samsung": "Samsung",
    "Google": "Google",
    "Amazon": "Amazon",
    "Ubiquiti": "Ubiquiti",
    "TP-LINK": "TP-Link",
    "TP-Link": "TP-Link",
    "NETGEAR": "NETGEAR",
    "Xiaomi": "Xiaomi",
    "Tuya": "Tuya",
    "Signify": "Philips Hue",
    "Philips Lighting": "Philips Hue",
    "Brother": "Brother",
    "HP Inc": "HP",
    "Hewlett Packard": "HP",
    "Canon": "Canon",
    "Seiko Epson": "Epson",
    "Nintendo": "Nintendo",
    "Sony Interactive": "Sony PlayStation",
    "LG Electronics": "LG",
    "Dreame": "Dreame",
    "Roborock": "Roborock",
    "iRobot": "iRobot",
    "Ecovacs": "Ecovacs",
    "Mammotion": "Mammotion",
    "Hikvision": "Hikvision",
    "Reolink": "Reolink",
    "Intel Corporate": "Intel",
    "Dell": "Dell",
    "LCFC": "Lenovo",
    "Lenovo": "Lenovo",
    "ASUSTek": "ASUS",
    "Microsoft": "Microsoft",
    "Synology": "Synology",
    "QNAP": "QNAP",
    "Miele": "Miele",
    "BSH Hausger": "Bosch/Siemens",
    "Huawei": "Huawei",
    "OnePlus": "OnePlus",
    "Motorola Mobility": "Motorola",
    "Fairphone": "Fairphone",
    "Garmin": "Garmin",
    "Bose": "Bose",
    "Denon": "Denon",
    "Yamaha": "Yamaha",
}


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    zeilen = set()
    for zeile in Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines():
        if not zeile.strip() or zeile.startswith("#"):
            continue
        teile = [t.strip() for t in zeile.split("\t")]
        praefix, name = teile[0], teile[-1]
        if "/" in praefix or len(praefix) != 8:
            continue
        # ganzes Wort am Anfang eines Worts („Dell“ nicht in „Wendell“, „Canon“ nicht in „Canonical“)
        kurz = next(
            (v for k, v in HERSTELLER.items() if re.search(rf"\b{re.escape(k)}\b", name, re.I)),
            None,
        )
        if kurz:
            zeilen.add(f"{praefix.replace(':', '').upper()} {kurz}")
    kopf = "# Hersteller je Adressblock (AN-0001), erzeugt mit tools/hersteller.py aus Wireshark manuf (IEEE)\n"
    ZIEL.write_text(kopf + "\n".join(sorted(zeilen)) + "\n", encoding="utf-8")
    print(f"{len(zeilen)} Adressblöcke → {ZIEL}")


if __name__ == "__main__":
    main()
