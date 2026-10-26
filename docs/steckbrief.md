# Modul Heimnetz

Steckbrief nach HA-Grundsatz G-19; maschinenlesbar in `module.yaml`. Stand 0.23.0 (Veröffentlichung als „Heimnetz“,
WU-0006, siehe `docs/entscheidungen.md`). Für Nutzer: `README.md` (Voraussetzungen muss/soll/kann).

## 1 Zweck
Zeigt, wie es dem Heimnetz und dem Internetzugang geht (FRITZ!Box mit Mobilfunk, getestet 6860 5G; ausgelegt für
Österreich): Gesamtstand und Befunde, Journal, Protokoll der Box, Geräte, WLAN, Mobilfunk-Empfang, Speedtest-Auswertung
und Datenverbrauch auf eigener Seite. Deutsch und Englisch nach der Sprache von Home Assistant.

## 2 Nicht-Ziele
Keine Einstellungen der Box ändern, keine Geräte steuern, keine eigene Speedtest-Messung (das macht Ookla). Nichts
doppelt, was FRITZ!Box Tools schon als Entität liefert (Verbindung, Durchsatz, Datenmenge, Betriebszeit).

## 3 Ausbaustufe
Stufe 4: eigene Integration mit eigener Seite (Panel). Stufe 1 reicht nicht: Ereignisprotokoll, Gerätetabelle,
Mobilfunkzellen und der DHCP-Test gibt es in HA nicht; Abgleich und Befunde brauchen Gedächtnis zwischen Abrufen.

## 4 Abhängigkeiten
Muss: FRITZ!Box Tools (`fritz`) – liefert den Zugang zur Box; Recorder (Verlauf, Verbrauch, Momentaufnahme).
Bibliothek `fritzconnection` 1.15.1 (dieselbe wie dort). Soll: Ookla Speedtest (`ookla_speedtest`, HACS) – ohne gibt es
keinen Speedtest, alles andere läuft; Met.no (`met`) und Holiday (`holiday`) für Wetter und Feiertag in der
Momentaufnahme. Kann: OpenCellID-Schlüssel (Optionen). Mindestversion Home Assistant 2026.10.1 (`hacs.json`).

## 5 Quellen
| Quelle | Eigentümer | Ausfall |
|---|---|---|
| FRITZ!Box über TR-064 (Zugang aus dem Eintrag von FRITZ!Box Tools) | Box / `fritz` | Gesamtstand „FRITZ!Box nicht erreichbar“, Box-abhängige Entitäten nicht verfügbar; nächster Abruf bewertet neu. Abgelehnte Anmeldung → Reparatur-Hinweis. Eintrag fehlt → Einrichtung scheitert mit Reparatur-Hinweis |
| Prüfungen vom Pi (TCP zur Box und ins Internet, DNS, ARP, DHCP-Test) | Heimnetz | unabhängig von TR-064, laufen immer |
| Sensoren der Ookla-Integration (letzter Test, Download, Upload, Ping, Server), gefunden über das Entitätsregister | `ookla_speedtest` | fehlt sie, gibt es kein Speedtest-Protokoll; wird sie später eingerichtet, verbindet sich die Integration beim nächsten Abruf |

Abweichung vom Schema: Die Quelle ist ein Config Entry, keine Entität. Der Zugang wird nur gelesen, nie gespeichert;
so muss das Kennwort nicht ein zweites Mal eingegeben werden (Entscheidung 12.10.2026).

## 6 Fachlogik
In `custom_components/heimnetz/logik/`, ohne HA: Ereignisprotokoll abgleichen, Gerätetabelle vergleichen (neu,
IP-Wechsel, online/offline, Anschluss), Befunde (doppelte IP, fremdes Netz, feste IP im DHCP-Bereich, Sperre, zweiter
DHCP-Server, Box-Adresse gewechselt, kein Internet), Gesamtstand, Mobilfunk (Technik, Zellen, Wechsel), Verkehr und
Grundlast, DHCP-Pakete. `sammeln.auswerten` verbindet alles zu einem Abruf. Dazu die Auswertung für die Seite:
Speedtest (`auswertung`), Verbrauch je Tag (`verbrauch`), Befund Mobilfunk (`mobil.befund`), Verlauf je Gerät
(`verlauf`), Einstellungen prüfen (`einstellungen`).

## 7 Eigentumsregister
| Wert | Eigentümer | Speicher | Schreibweg |
|---|---|---|---|
| Wahl der FRITZ!Box | Heimnetz | Config Entry `data` | Einrichtungsdialog |
| Zugang zur Box | `fritz` | dessen Config Entry | nur dort |
| Gesamtstand, Befunde, Prüfungen, Empfang | Heimnetz | Recorder (Verlauf der Entitäten) | Abruf |
| Journal, Protokoll der Box, Gedächtnis | Heimnetz | `heimnetz/heimnetz.db` | Abruf |
| Speedtest-Messungen | Ookla (Messwert), Heimnetz (Protokoll mit Grundlast) | `heimnetz/heimnetz.db` | Speedtest-Protokoll |
| Tickets (Meldungen aus dem Melden-Knopf) | Heimnetz | Integrations-Speicher `heimnetz.meldungen`, lesbare Kopie und Bilder unter `heimnetz/meldungen.*`, `heimnetz/meldungen/` | Seite (`heimnetz/meldung/*`), Aktion `heimnetz.ticket` |

## 8 Entitäten
Gerät „Heimnetz“ (Dienst). Sensoren: Gesamtstand (ok, Hinweise, Störung, FRITZ!Box nicht erreichbar), Offene Befunde,
Geräte online, Mobilfunk Technik, Signalstärke/-qualität 4G-Anker und 5G, Mobilfunkzelle, Entfernung zur Basisstation,
Nachbarzellen, 5G-Zelle (PCI) (nur Boxen mit Mobilfunk), Letzte Messung
(Zeitpunkt; Messwerte und Momentaufnahme als Attribute, WU-0005). Binärsensoren
(Verbindung): FRITZ!Box vom Pi aus, Internet vom Pi aus, Namensauflösung. Entitäts-IDs `sensor.heimnetz_*` /
`binary_sensor.heimnetz_*`, beim Einrichten aus dem Namen in der Systemsprache gebildet (Liste im README).

## 9 Einstellungen
| Einstellung | Art | Speicher | Bedienung |
|---|---|---|---|
| Wahl der FRITZ!Box | Einrichtung | Config Entry `data` | Einrichtungsdialog |
| Tarif Download/Upload, Auswerten ab, Grenze „schwacher WLAN-Empfang“ (30/40/50 %) | Objekt der eigenen Oberfläche | Integrations-Speicher `heimnetz.<Eintrag>` | Seite über `heimnetz/einstellungen/setzen` (nur Admin) |
| Messplan (ein/aus, Takt, Zeitfenster, Verhalten bei Verkehr) | Objekt der eigenen Oberfläche | Integrations-Speicher `heimnetz.<Eintrag>` | Seite über `heimnetz/messplan/setzen` (nur Admin) |
| Art je Gerät (selbst gewählt, sonst automatisch) | Objekt der eigenen Oberfläche | Integrations-Speicher `heimnetz.<Eintrag>` (`arten`, je Geräte-Kennung) | Seite über `heimnetz/geraet/art` (nur Admin) |
| OpenCellID-Schlüssel (Karte zum Mast, optional) | Zugangsdaten | Config Entry `options` | Optionen des Eintrags („Konfigurieren“) |

## 10 Aktionen, Ereignisse, WebSocket
Eigene Aktion `heimnetz.ticket` (nur Admin, mit Antwort): Status, Notiz, Version, Commit eines Tickets ändern – für
`tools/ticket.py`. Die Integration ruft nach ihrem Messplan oder auf „Jetzt messen“ die Aktion
`ookla_speedtest.run_speedtest` der Ookla-Integration auf (einzige Ausnahme vom reinen Lesen). WebSocket je Reiter der Seite: `heimnetz/uebersicht`, `/speedtest`
(tage 7/28/84, groesse down/up/ping, grundlast aus/halb/mit, server), `/geraete`, `/geraet` (Kennung statt
Hardware-Adresse, tage), `/mobilfunk` (tage 1/7/30; mit Verbindung zur Basisstation, allen Zellen, Karte zum Mast, Verbindungsdauer, Neueinwahlen, Bändern), `/wlan` (Bänder, Geräte im WLAN mit Empfang in %, Befunde, Kanalwechsel), `/verbrauch` (tage 7/30), `/protokoll` (journal/internet/wlan/
system, nur_warnungen, suche), `/einstellungen` (mit Messplan und Ookla-Zustand), `/einstellungen/setzen`,
`/messplan/setzen` (auch Anzahl der Serie), `/messen`, `/serie` (Speedtest-Serie, nur Admin), `/geraet/art` (Art eines Geräts, nur Admin). `/geraete` liefert je Gerät Verbindung, Band, Art und Quelle der Art sowie die Gruppen nach Verbindung und nach Art. Antworten sind fertig gerechnet. Tickets: `heimnetz/meldungen`, `/meldung/neu` (jeder),
`/meldung/bild` (ein Bild je Aufruf, höchstens 3, nur in den ersten 10 Minuten), `/meldung/bild_zeigen`,
`/meldung/github` (Vorschau und Link für ein öffentliches Issue, speichert nichts), `/meldung/status` und
`/meldung/loeschen` (nur Admin). Dazu `/speedtest/kachel` (Messungen hinter einer Stundenkachel).

## 11 Speicherung und Verlauf
Gemerkte Orte der Zellen von OpenCellID und BeaconDB im Integrations-Speicher `heimnetz.<Eintrag>.mast`; Funkmasten aus
OpenStreetMap (Ausschnitt, Zeit, Masten) in `heimnetz.<Eintrag>.osm`; Zellen aus dem OpenCellID-Datenabzug im selben
Ausschnitt (Technik, Netz, Ort) in `heimnetz.<Eintrag>.ocid`.
Tickets im Integrations-Speicher `heimnetz.meldungen` (eine Liste für die Integration, bleibt beim Löschen der
Einrichtung); lesbare Kopie `heimnetz/meldungen.json` und `meldungen.md`, Bilder `heimnetz/meldungen/<Ticket>-<n>.jpg`.
`heimnetz/heimnetz.db` in der HA-Konfiguration (SQLite, Schema-Version 1 in `PRAGMA user_version`; eine Datei einer
neueren Fassung wird nicht angefasst). Journal (auch Verlauf je Gerät), Protokoll der Box, Speedtest-Messungen,
Gedächtnis. Journal und Protokoll 400 Tage, Messungen immer. Sicherung: vor einer HA-Sicherung WAL in die Datei und
Schreiben in eine Warteschlange, danach weiter.
Zustände der Entitäten speichert der Recorder.

## 12 Oberfläche
Seite „Heimnetz“ in der Seitenleiste (Panel, Lit, G-22) nach `mockups/netzwerk.html`: Übersicht, Speedtest, Geräte,
Funk (WLAN, Mobilfunk), Verbrauch, Protokoll; Deutsch/Englisch nach dem Profil des Nutzers; Melden-Knopf unten rechts, Tickets unter ⚙ › Meldungen. Daten nur über WebSocket. Quellen `frontend/src`, gebaut mit
`node custom_components/heimnetz/frontend/bauen.mjs`; neue Darstellung zuerst im Mockup (Mockup-Policy).

## 13 Fehler, Diagnose, Reparatur-Hinweise
Teilausfälle stehen in der Diagnose als Fehlerliste. Diagnose enthält nur Zahlen und den groben Stand (Versionen,
Sprache, Box-Modell, FRITZ!OS, Netztechnik, Ookla, Messplan); Vertrauliches schwärzt `logik/diagnose.py`, auch in
Texten. Reparatur-Hinweise: „FRITZ!Box Tools fehlt“, „Anmeldung abgelehnt“ (verschwindet nach erfolgreichem Abruf),
„alte Integration aktiv“ (`alt_aktiv`, Umstieg von `netzwerk`).

## 14 Tests
`tests/seite` (Seite mit happy-dom gegen die Vorlage `daten.json`), `tests/logik` (Fachlogik ohne HA, Fälle aus den
Tests des Altbestands), `tests/integration` (Einrichtung, Entitäten, Vertrag der Seite,
Box weg und zurück, Wert fehlt → unbekannt, ohne Mobilfunk, Anmeldung abgelehnt, FRITZ!Box Tools fehlt, Diagnose ohne
private Daten, Entladen und neu Laden).

## 15 Einspielen
Für Nutzer über HACS (benutzerdefiniertes Repository, Release per Tag `vX.Y.Z`). Bei der Entwicklung:
`python ausliefern.py`, Konfiguration prüfen, Neustart durch den Nutzer. Rückweg: `python ausliefern.py --zurueck`.
Die Ablösung der Netzdiagnose ist erledigt (12.10.2026). Der Umstieg von der alten Integration `netzwerk` auf
`heimnetz` (0.23.0) übernimmt die Daten beim ersten Laden; Ablauf in `docs/umstieg.md`.

## 16 Entscheidungen
Siehe `docs/entscheidungen.md`.
