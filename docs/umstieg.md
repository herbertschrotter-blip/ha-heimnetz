# Umstieg von „Netzwerk“ auf „Heimnetz“ (0.23.0, WU-0006)

Ab 0.23.0 heißt die Integration **Heimnetz** (Domain `heimnetz`). Das ist für Home Assistant eine neue Integration:
Die alte Integration `netzwerk` läuft weiter, bis sie abgeschaltet wird. Heimnetz übernimmt beim ersten Laden ihre
Daten, ohne sie anzufassen. Es dürfen nie beide zugleich laufen, sonst fragen zwei Integrationen die FRITZ!Box ab und
schreiben zwei Speedtest-Protokolle. Deshalb startet Heimnetz nicht, solange die alte Einrichtung aktiv ist.

## Was übernommen wird

| Was | Alt | Neu |
|-----|-----|-----|
| Messungen, Journal, Protokoll der Box, Gedächtnis, Momentaufnahmen | `<config>/netzwerk/netzwerk.db` | `<config>/heimnetz/heimnetz.db` (Kopie über die Sicherungs-Schnittstelle von SQLite, mit dem Inhalt der WAL-Datei) |
| Bilder der Tickets und sonstige Dateien | `<config>/netzwerk/…` | `<config>/heimnetz/…` (nur, was dort noch fehlt) |
| Tarif, Auswerten ab, WLAN-Grenze, Messplan, Arten der Geräte, letzte Serie | Speicher `netzwerk.<alte Einrichtung>` | Speicher `heimnetz.<neue Einrichtung>` |
| Gemerkte Masten, OSM-Masten, OpenCellID-Abzug | `netzwerk.<alte Einrichtung>.mast` / `.osm` / `.ocid` | `heimnetz.<neue Einrichtung>.mast` / `.osm` / `.ocid` |
| Tickets mit ihren Nummern | Speicher `netzwerk.meldungen` | Speicher `heimnetz.meldungen`, lesbar unter `<config>/heimnetz/meldungen.*` |
| OpenCellID-Schlüssel (Optionen) | Optionen der alten Einrichtung | Optionen der neuen Einrichtung (beim Anlegen) |

Übernommen wird nur in eine leere Ablage: Was Heimnetz schon hat, wird nie überschrieben. Datenbank, Dateien und
Speicher je Einrichtung werden einmal beim ersten Laden übernommen (danach steht `uebernommen` in den Daten der
Einrichtung); die Tickets so lange, bis Heimnetz eigene hat. Die Speicher liest Heimnetz über die Speicher-Schnittstelle
von Home Assistant, nicht als Datei. Nicht übernommen wird der Verlauf der alten Entitäten im Recorder: Die
Entitäten heißen neu `sensor.heimnetz_*` / `binary_sensor.heimnetz_*`, die alten `sensor.netzwerk_*` bekommen keine
neuen Werte mehr.

## Was die alte Integration beim Löschen entfernt

Wird die Einrichtung der alten Integration **gelöscht**, entfernt sie (`async_remove_entry`) ihre Speicher
`netzwerk.<Einrichtung>` (Einstellungen, Messplan, Arten), `.mast`, `.osm` und `.ocid`. Die Datenbank
`<config>/netzwerk/netzwerk.db`, die Tickets (`netzwerk.meldungen`) und die Bilder bleiben. Deshalb wird die alte
Einrichtung erst **deaktiviert** und erst gelöscht, wenn Heimnetz alles übernommen hat. Ist der Ordner
`custom_components/netzwerk` schon weg, löscht Home Assistant nur die Einrichtung; ihre Speicher bleiben dann zwar
liegen, Heimnetz findet sie ohne die Einrichtung aber nicht mehr und übernimmt nur Datenbank, Dateien und Tickets.
Wird die alte Einrichtung wieder aktiviert, während Heimnetz läuft, hält Heimnetz sofort an (Reparatur-Hinweis).

## Reihenfolge

1. **Sicherung:** Einstellungen → System → Sicherungen → Sicherung jetzt erstellen.
2. **Heimnetz einspielen:** `python ausliefern.py` im Projekt – kopiert nach `custom_components/heimnetz` neben die
   alte `custom_components/netzwerk` (die bleibt vorerst).
3. **Alte Einrichtung deaktivieren, nicht löschen:** Einstellungen → Geräte & Dienste → Netzwerk → ⋮ → Deaktivieren.
   Damit fragt sie die Box sofort nicht mehr ab.
4. **Konfiguration prüfen und Home Assistant neu starten.**
5. **Heimnetz einrichten:** Geräte & Dienste → Integration hinzufügen → „Heimnetz“ → FRITZ!Box wählen. Ist die alte
   Einrichtung noch aktiv, bricht der Dialog mit einem Hinweis ab (zurück zu Schritt 3). Beim ersten Laden übernimmt
   Heimnetz die Daten; im Protokoll steht „Heimnetz: Daten der alten Integration übernommen (…)“.
6. **Übernahme prüfen:** Seite „Heimnetz“ in der Seitenleiste – Speedtest (Messungen der letzten Wochen, Messplan,
   Tarif), Protokoll und Journal, Geräte (selbst gewählte Arten), Funk → Mobilfunk (Karte zum Mast; unter Geräte &
   Dienste → Heimnetz → Konfigurieren steht der OpenCellID-Schlüssel), ⚙ → Meldungen (alle Tickets; ein neues Ticket
   bekommt die nächste Nummer). `python3 tools/ticket.py liste` liest jetzt `<config>/heimnetz/meldungen.json`.
7. **Entitäten nachziehen:** Automationen, Dashboards und das Langzeitarchiv (Scribe) von `sensor.netzwerk_*` auf
   `sensor.heimnetz_*` umstellen. Wer die alten Namen behalten will: erst nach Schritt 8 die neuen Entitäten unter
   Einstellungen → Entitäten auf die alten IDs umbenennen.
8. **Alte Einrichtung löschen:** Geräte & Dienste → Netzwerk → ⋮ → Löschen (entfernt ihre Speicher, siehe oben; die
   Daten hat Heimnetz schon).
9. **Alte Integration entfernen:** Ordner `custom_components/netzwerk` aus der HA-Konfiguration löschen, Konfiguration
   prüfen, neu starten. Die alte Seite `/netzwerk` verschwindet.
10. Später, nach der nächsten Sicherung: `<config>/netzwerk/` kann weg – Heimnetz nutzt den Ordner nicht mehr.

## Zurück

Bis Schritt 8 ist alles umkehrbar, denn die alten Daten bleiben unangetastet: Heimnetz-Einrichtung deaktivieren oder
löschen, alte Einrichtung wieder aktivieren, neu starten. `python ausliefern.py --zurueck` entfernt
`custom_components/heimnetz` wieder (vor der ersten Auslieferung gab es keine Fassung). Was in Heimnetz seit dem
Umstieg dazukam (neue Messungen, neue Tickets), hat die alte Integration dann nicht.
