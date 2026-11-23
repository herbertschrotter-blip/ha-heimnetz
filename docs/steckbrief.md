# Modul Heimnetz

Steckbrief nach HA-Grundsatz G-19; maschinenlesbar in `module.yaml`. Stand 0.38.0 (Veröffentlichung als „Heimnetz“
mit 0.23.0, WU-0006; seitdem Internet und Zugang mit vorgeschaltetem Gerät WU-0009, Warnungen WU-0010, Diagnose-Log,
Wächter, Ausfallbericht, Lagebild und Netzkarte – siehe `docs/entscheidungen.md`). Für Nutzer: `README.md`
(Voraussetzungen muss/soll/kann).

## 1 Zweck
Zeigt, wie es dem Heimnetz und dem Internetzugang geht (FRITZ!Box mit Mobilfunk, getestet 6860 5G; ausgelegt für
Österreich; DSL, Glasfaser, Kabel und ein vorgeschaltetes Modem nach dem, was Box bzw. Gerät melden): Gesamtstand und
Befunde als Lagebild, Journal, Protokoll der Box, Geräte mit WLAN und Netzkarte, Internet (Mobilfunk-Empfang, Leitung,
Zugang), Speedtest-Auswertung und Datenverbrauch auf eigener Seite. Dazu Warnungen aufs Handy, wenn Geräte, Internet
oder Box weg sind, und – nur wenn ein Admin einen einrichtet – Wächter, die ein hängendes Gerät neu starten.
Deutsch und Englisch nach der Sprache von Home Assistant bzw. dem Profil des Nutzers.

## 2 Nicht-Ziele
Keine Einstellungen der Box, des vorgeschalteten Geräts oder der Steckdosen ändern, keine Geräte steuern, keine eigene
Speedtest-Messung (das macht Ookla). Nichts doppelt, was FRITZ!Box Tools schon als Entität liefert (Verbindung,
Durchsatz, Datenmenge, Betriebszeit). Ausnahmen vom reinen Lesen (Begründung in `docs/entscheidungen.md`):
Ookla-Messungen auslösen (Messplan), Warnungen über den gewählten notify-Dienst (WU-0010, ab Werk keiner; immer das
Ereignis `heimnetz_warnung`), der Wächter (FRITZ!Box per TR-064 und vorgeschaltetes Gerät per Weboberfläche neu
starten, eigenes Skript „heimnetz-waechter“ samt KVS auf gewählten Shelly-Steckdosen anlegen/ändern/löschen und
blinken) und die Anmeldung an der Weboberfläche eines vorgeschalteten Geräts (nur lesend).

## 3 Ausbaustufe
Stufe 4: eigene Integration mit eigener Seite (Panel). Stufe 1 reicht nicht: Ereignisprotokoll, Gerätetabelle,
Mobilfunkzellen und der DHCP-Test gibt es in HA nicht; Abgleich und Befunde brauchen Gedächtnis zwischen Abrufen.

## 4 Abhängigkeiten
Muss: FRITZ!Box Tools (`fritz`) – liefert den Zugang zur Box; Recorder (Verlauf, Verbrauch, Momentaufnahme).
Bibliotheken `fritzconnection` ≥ 1.15.1 (dieselbe wie dort), `huawei-lte-api` ≥ 1.11.0 und `tplinkrouterc6u` ≥ 5.37.0
(Pflicht im Manifest, benutzt nur bei einem solchen vorgeschalteten Gerät). Soll: Ookla Speedtest (`ookla_speedtest`,
HACS) – ohne gibt es keinen Speedtest, alles andere läuft; Met.no (`met`) und Holiday (`holiday`) für Wetter und
Feiertag in der Momentaufnahme. Kann: OpenCellID-Schlüssel (Optionen); Companion App bzw. notify-Dienst für Warnungen;
Shelly-Steckdosen Gen 2+ (Integration `shelly`) für den Wächter; Integrationen Huawei LTE, NETGEAR LTE, Teltonika für
ein vorgeschaltetes Gerät; Scribe bzw. InfluxDB als Langzeitarchiv; HA OS (Supervisor) für den Ausfallbericht.
Mindestversion Home Assistant 2026.10.1 (`hacs.json`).

## 5 Quellen
| Quelle | Eigentümer | Ausfall |
|---|---|---|
| FRITZ!Box über TR-064 (Zugang aus dem Eintrag von FRITZ!Box Tools) | Box / `fritz` | Gesamtstand „FRITZ!Box nicht erreichbar“, Box-abhängige Entitäten nicht verfügbar; nächster Abruf bewertet neu. Abgelehnte Anmeldung → Reparatur-Hinweis. Eintrag fehlt → Einrichtung scheitert mit Reparatur-Hinweis |
| Zähler von FRITZ!Box Tools (Statistik des Recorders) | `fritz` | Reiter Verbrauch bleibt leer |
| Prüfungen vom Pi (TCP zur Box und zu 1.1.1.1/8.8.8.8, DNS `avm.de`, ARP, DHCP-Test) | Heimnetz | unabhängig von TR-064, laufen immer |
| Vorgeschaltetes Gerät im eigenen Heimnetz (Weboberfläche, nur private Adressen) oder dessen HA-Integration (WU-0009) | Gerät / `huawei_lte`, `netgear_lte`, `teltonika` | nur die Funkwerte, die allein von dort kommen, nicht verfügbar; Befund im Reiter Internet; Kennwort abgelehnt bzw. länger nicht erreichbar → Reparatur-Hinweis |
| Sensoren der Ookla-Integration (letzter Test, Download, Upload, Ping, Server), gefunden über das Entitätsregister | `ookla_speedtest` | fehlt sie, gibt es kein Speedtest-Protokoll; der Messplan versucht es beim nächsten Abruf wieder; wird sie später eingerichtet, verbindet sich die Integration beim nächsten Abruf |
| Wetter-Entität (bevorzugt `met`), Feiertags-Kalender (`holiday`) | `met` / `holiday` | diese Felder der Momentaufnahme fehlen |
| Shelly-Steckdosen (Wächter), gefunden über die Shelly-Integration und die Geräteliste der Box | Steckdose / `shelly` | Reiter Wächter zeigt sie als nicht erreichbar; Speichern geht nicht; die Regeln laufen auf der Steckdose weiter |
| Supervisor (Speicher je Programm, Systemprotokoll des vorigen Starts) | `hassio` | diese Werte des Ausfallberichts fehlen |
| BeaconDB, OpenCellID (mit Schlüssel; dazu der Monatsabzug Österreich), OpenStreetMap (Overpass, einmal im Monat) | Dienste im Internet | nur die Karte zum Mast; gemerkte Orte bleiben |
| Kartenkacheln basemap.at (`mapsneu.wien.gv.at`) oder OpenStreetMap | Dienste im Internet | lädt der Browser, nicht die Integration |

Abweichung vom Schema: Die Quelle FRITZ!Box ist ein Config Entry, keine Entität. Der Zugang wird nur gelesen, nie
gespeichert; so muss das Kennwort nicht ein zweites Mal eingegeben werden (Entscheidung 12.10.2026). Die
Kartenkacheln stehen mit `interface: browser` in `module.yaml`, weil sie eine Quelle der Seite sind.

## 6 Fachlogik
In `custom_components/heimnetz/logik/`, ohne HA: Ereignisprotokoll abgleichen, Gerätetabelle vergleichen (neu,
IP-Wechsel, online/offline, Anschluss), Befunde (doppelte IP, fremdes Netz, feste IP im DHCP-Bereich, Sperre, zweiter
DHCP-Server, Box-Adresse gewechselt, kein Internet), Gesamtstand, Mobilfunk (Technik, Zellen, Wechsel), Leitung (DSL,
Glasfaser), Zugang erkennen, vorgeschaltetes Gerät (Erkennen, Werte lesen), Verkehr und Grundlast, DHCP-Pakete.
`sammeln.auswerten` verbindet alles zu einem Abruf. Dazu die Auswertung für die Seite: Speedtest (`auswertung`,
Raster und Antwortleiste), Verbrauch je Tag (`verbrauch`), Befund Mobilfunk (`mobil.befund`), Verlauf je Gerät
(`verlauf`), WLAN, Netzkarte, Arten (`arten`), Warnungen (`warnungen`), Wächter (`waechter`), Diagnose-Log,
Einstellungen prüfen (`einstellungen`), Messplan (`messplan`), Schwärzen für Diagnose und Issue (`diagnose`).

## 7 Eigentumsregister
| Wert | Eigentümer | Speicher | Schreibweg |
|---|---|---|---|
| Wahl der FRITZ!Box | Heimnetz | Config Entry `data` | Einrichtungsdialog |
| Zugang zur Box | `fritz` | dessen Config Entry | nur dort |
| Gesamtstand, Befunde, Prüfungen, Empfang, Leitung | Heimnetz | Recorder (Verlauf der Entitäten) | Abruf |
| Journal, Protokoll der Box, Gedächtnis | Heimnetz | `heimnetz/heimnetz.db` | Abruf |
| Speedtest-Messungen, Momentaufnahme, Merkliste gelöschter Messungen | Ookla (Messwert), Heimnetz (Protokoll mit Grundlast) | `heimnetz/heimnetz.db` | Speedtest-Protokoll; Löschen über `heimnetz/messung/loeschen` (nur Admin) |
| Diagnose-Log, Speicherstand je Programm | Heimnetz | `heimnetz/heimnetz.db` | Abruf (Diagnose-Log nur mit Schalter), Ausfall-Baustein |
| Einstellungen der Seite, Messplan, Arten, Warnungen, Zugang, Wächter, letzte Serie | Heimnetz | Integrations-Speicher `heimnetz.<Eintrag>` | WebSocket (nur Admin) |
| Gemerkte Orte (Mast, OSM, OpenCellID-Abzug) | Heimnetz (Kopie fremder Daten) | `heimnetz.<Eintrag>.mast`, `.osm`, `.ocid` | Abruf |
| Kennwörter (vorgeschaltetes Gerät, Shelly), OpenCellID-Schlüssel | Heimnetz | Config Entry `options` | WebSocket (nur setzen/entfernen) bzw. Optionsdialog |
| Skript „heimnetz-waechter“ und seine KVS-Schlüssel auf den Steckdosen | Heimnetz (auf fremdem Gerät) | Shelly | `heimnetz/waechter/speichern`, `/aendern` |
| Tickets (Meldungen aus dem Melden-Knopf) | Heimnetz | Integrations-Speicher `heimnetz.meldungen`, lesbare Kopie und Bilder unter `heimnetz/meldungen.*`, `heimnetz/meldungen/` | Seite (`heimnetz/meldung/*`), Aktion `heimnetz.ticket` |

## 8 Entitäten
Gerät „Heimnetz“ (Dienst). Sensoren: Gesamtstand (ok, Hinweise, Störung, FRITZ!Box nicht erreichbar), Offene Befunde,
Geräte online, Letzte Messung (Zeitpunkt; Messwerte und Momentaufnahme als Attribute ohne Entfernung und Richtung zum
Mast, WU-0005), Internetzugang (Zugangsart, erkannt oder festgelegt). Mobilfunk (nur Boxen mit Mobilfunk oder wenn ein
vorgeschaltetes Gerät Funkwerte geliefert hat): Technik, Signalstärke/-qualität 4G-Anker und 5G, Mobilfunkzelle,
Entfernung zur Basisstation, Nachbarzellen, 5G-Zelle (PCI); nur vom vorgeschalteten Gerät und erst, wenn der Wert
einmal da war: Signal-Rausch-Abstand 4G-Anker und 5G, Mobilfunk-Band. DSL (nur mit DSL-Anschluss): Synchronrate,
Störabstandsmarge, Dämpfung je Richtung, Fehler je Stunde. Glasfaser: empfangene und gesendete Lichtleistung.
Binärsensoren (Verbindung): FRITZ!Box vom Pi aus, Internet vom Pi aus, Namensauflösung. Entitäts-IDs
`sensor.heimnetz_*` / `binary_sensor.heimnetz_*`, beim Einrichten aus dem Namen in der Systemsprache gebildet (Liste im
README).

## 9 Einstellungen
| Einstellung | Art | Speicher | Bedienung |
|---|---|---|---|
| Wahl der FRITZ!Box | Einrichtung | Config Entry `data` | Einrichtungsdialog |
| Tarif Download/Upload, Auswerten ab, Grenze „schwacher WLAN-Empfang“ (30/40/50 %) | Objekt der eigenen Oberfläche | Integrations-Speicher `heimnetz.<Eintrag>` | Seite über `heimnetz/einstellungen/setzen` (nur Admin) |
| Messplan (ein/aus, Takt, Zeitfenster, Verhalten bei Verkehr, Anzahl der Serie) | Objekt der eigenen Oberfläche | Integrations-Speicher `heimnetz.<Eintrag>` | Seite über `heimnetz/messplan/setzen` (nur Admin) |
| Art je Gerät (selbst gewählt, sonst automatisch), eigene Arten | Objekt der eigenen Oberfläche | Integrations-Speicher `heimnetz.<Eintrag>` (`arten`, `eigene_arten`) | Seite über `heimnetz/geraet/art`, `/art/*` (nur Admin) |
| Warnungen (Ziel, Arten, Zeiten, Ausnahmen je Gerät) | Objekt der eigenen Oberfläche | Integrations-Speicher `heimnetz.<Eintrag>` (`warnungen`) | Seite über `heimnetz/warnungen/*` (nur Admin) |
| Zugang (Wahl, Adresse eines vorgeschalteten Geräts, Ersatzzugang) | Objekt der eigenen Oberfläche | Integrations-Speicher `heimnetz.<Eintrag>` | Seite über `heimnetz/zugang/setzen` (nur Admin) |
| Diagnose-Log an/aus | Objekt der eigenen Oberfläche | Integrations-Speicher `heimnetz.<Eintrag>` | Seite über `heimnetz/diagnoselog/setzen` (nur Admin) |
| Wächter (Art, Gerät, Steckdose, Regeln) | Objekt der eigenen Oberfläche | Integrations-Speicher `heimnetz.<Eintrag>` (`waechter`) und Skript/KVS auf der Steckdose | Seite über `heimnetz/waechter/*` (nur Admin) |
| OpenCellID-Schlüssel (Karte zum Mast, optional) | Zugangsdaten | Config Entry `options` | Optionen des Eintrags („Konfigurieren“) |
| Kennwort des vorgeschalteten Geräts, Kennwort der Shelly-Steckdosen | Zugangsdaten | Config Entry `options` | Seite (nur setzen/entfernen, nie zurückgegeben; ⚙ › Zugang bzw. Reiter Wächter) |

Die Optionen werden bei jeder Verwendung frisch gelesen; es gibt keinen Update-Listener (bewusste Abweichung von G-16,
`docs/entscheidungen.md` › Technik).

## 10 Aktionen, Ereignisse, WebSocket
Eigene Aktion `heimnetz.ticket` (nur Admin, mit Antwort): Status, Notiz, Version, Commit eines Tickets ändern – für
`tools/ticket.py`. Die Integration ruft nach ihrem Messplan, auf „Jetzt messen“ oder für eine Serie die Aktion
`ookla_speedtest.run_speedtest` der Ookla-Integration auf. Warnungen gehen über den gewählten notify-Dienst; jede
feuert das Ereignis `heimnetz_warnung` (`art` `offline`, `online`, `neu`, `internet`, `test`, `waechter`; dazu
`geraet`, `ip`, `verbindung`, `dauer`, `oft`, `nachricht`).

WebSocket `heimnetz/*` (vollständige Liste in `module.yaml`; jeder Befehl nimmt zusätzlich `sprache` an): je Reiter
`uebersicht`, `speedtest` (tage 7/28/84, groesse down/up/ping, grundlast aus/halb/mit, server), `speedtest/kachel`
(Messungen hinter einer Stundenkachel), `geraete`, `geraet` (Kennung statt Hardware-Adresse, tage), `netzkarte`,
`wlan`, `internet`, `mobilfunk` (tage 1/7/30), `verbrauch` (tage 7/30), `protokoll` (journal/internet/wlan/system,
nur_warnungen, suche), `waechter`. Einstellungen: `einstellungen`, `einstellungen/setzen`, `messplan/setzen`, `messen`,
`serie`, `messung/loeschen`, `geraet/art`, `arten`, `art/neu`, `art/aendern`, `art/loeschen`, `warnungen`,
`warnungen/setzen`, `warnungen/geraet`, `warnungen/test`, `zugang`, `zugang/setzen`, `zugang/suchen`, `modem`
(Diagnose des vorgeschalteten Geräts), `einrichtung`, `diagnoselog`, `diagnoselog/setzen`, `diagnoselog/loeschen`,
`diagnoselog/datei`, `waechter/vorschlag`, `waechter/speichern`, `waechter/aendern`, `waechter/blinken` – Ändern und
Diagnose nur Admin. Tickets: `meldungen`, `meldung/neu` (jeder), `meldung/bild` (ein Bild je Aufruf, höchstens 3, nur
in den ersten 10 Minuten), `meldung/bild_zeigen`, `meldung/github` (Vorschau und Link für ein öffentliches Issue,
speichert nichts), `meldung/status` und `meldung/loeschen` (nur Admin). Antworten sind fertig gerechnet.

## 11 Speicherung und Verlauf
`heimnetz/heimnetz.db` in der HA-Konfiguration (SQLite, Schema-Version 1 in `PRAGMA user_version`; eine Datei einer
neueren Fassung wird nicht angefasst). Journal (auch Verlauf je Gerät), Protokoll der Box, Speedtest-Messungen mit
Momentaufnahme (`messung_kontext`) und Merkliste gelöschter Messungen (`messung_geloescht`), Gedächtnis (`meta`, auch
Herzschlag und Marke „sauber“ für den Ausfallbericht), Diagnose-Log (`diagnoselog`, 7 Tage), Speicher je Programm
(`speicherstand`, 8 Tage) – die Zusatztabellen ohne neue Schema-Version, damit der Rückweg weiter geht. Journal und
Protokoll 400 Tage, Messungen immer. Sicherung: vor einer HA-Sicherung WAL in die Datei und Schreiben in eine
Warteschlange, danach weiter.
Einstellungen im Integrations-Speicher `heimnetz.<Eintrag>`; gemerkte Orte der Zellen von OpenCellID und BeaconDB in
`heimnetz.<Eintrag>.mast`; Funkmasten aus OpenStreetMap (Ausschnitt, Zeit, Masten) in `heimnetz.<Eintrag>.osm`;
Zellen aus dem OpenCellID-Datenabzug im selben Ausschnitt (Technik, Netz, Ort) in `heimnetz.<Eintrag>.ocid`.
Tickets im Integrations-Speicher `heimnetz.meldungen` (eine Liste für die Integration, bleibt beim Löschen der
Einrichtung); lesbare Kopie `heimnetz/meldungen.json` und `meldungen.md`, Bilder `heimnetz/meldungen/<Ticket>-<n>.jpg`.
Zustände der Entitäten speichert der Recorder.

Langzeitarchiv (G-24): kein eigenes Archiv unter `<config>/archiv/heimnetz/` (`archive.anwendbar: false` in
`module.yaml`). Die Werte gehen als Entitäten an Scribe (TimescaleDB) bzw. InfluxDB (Entscheidung 24.10.2026); ein
Verlustfenster für unbestätigte Archivdaten entfällt damit.

## 12 Oberfläche
Seite „Heimnetz“ in der Seitenleiste (Panel, Lit, G-22) nach den Mockups unter `mockups/` (Seitenliste
`mockups/seiten.json`): Reiter Übersicht (Lagebild), Speedtest, Geräte (mit WLAN und Netzkarte: Fluss, Radar),
Internet (Mobilfunk, DSL, Glasfaser, Kabel, vorgeschaltetes Gerät), Verbrauch, Protokoll, Wächter; ⚙ mit
Einstellungen, Zugang, Warnungen, Arten, Diagnose, Meldungen. Deutsch/Englisch nach dem Profil des Nutzers;
Melden-Knopf unten rechts. Daten nur über WebSocket. Quellen `frontend/src`, gebaut mit
`node custom_components/heimnetz/frontend/bauen.mjs`; neue Darstellung zuerst im Mockup (Mockup-Policy).

## 13 Fehler, Diagnose, Reparatur-Hinweise
Teilausfälle stehen in der Diagnose als Fehlerliste. Diagnose enthält nur Zahlen und den groben Stand (Versionen,
Sprache, Box-Modell, FRITZ!OS, Netztechnik, Ookla, Messplan); Vertrauliches schwärzt `logik/diagnose.py`, auch in
Texten, Kennwörter in den Optionen ebenso. Reparatur-Hinweise: „FRITZ!Box Tools fehlt“ (`fritz_fehlt`), „Anmeldung
abgelehnt“ (`anmeldung`, verschwindet nach erfolgreichem Abruf), „alte Integration aktiv“ (`alt_aktiv`, Umstieg von
`netzwerk`), „Recorder fehlt“ (`recorder_fehlt`), Kennwort des vorgeschalteten Geräts abgelehnt (`modem_anmeldung`),
vorgeschaltetes Gerät länger nicht erreichbar (`modem_fehlt`). Nach einem unsauberen Ende des vorigen Laufs ein
Ausfallbericht im Journal und als Warnung.

## 14 Tests
`tests/seite` (Seite mit happy-dom gegen die Vorlage `daten.json`), `tests/logik` (Fachlogik ohne HA, Fälle aus den
Tests des Altbestands), `tests/integration` (Einrichtung, Entitäten, Vertrag der Seite, WebSocket, Box weg und zurück,
Wert fehlt → unbekannt, ohne Mobilfunk, Anmeldung abgelehnt, FRITZ!Box Tools fehlt, vorgeschaltetes Gerät, Zugang,
Warnungen, Wächter, Ausfall, Diagnose-Log, Tickets, Übernahme, Diagnose ohne private Daten, Entladen und neu Laden),
dazu `tools/seitenliste_check.py`.

## 15 Einspielen
Für Nutzer über HACS (benutzerdefiniertes Repository, Release per Tag `vX.Y.Z`). Bei der Entwicklung führt Claude
`python ausliefern.py` selbst aus und startet Home Assistant danach mit dem Skill neustart neu (Konfiguration prüfen,
still nachsehen, ob in einer anderen Claude-Sitzung etwas läuft) – Herbert, 29.10.2026. Rückweg:
`python ausliefern.py --zurueck`. Optionsänderungen wirken ohne Neuladen (Abschnitt 9). Die Ablösung der Netzdiagnose
ist erledigt (12.10.2026). Der Umstieg von der alten Integration `netzwerk` auf `heimnetz` (0.23.0) übernimmt die Daten
beim ersten Laden; Ablauf in `docs/umstieg.md`.

## 16 Entscheidungen
Siehe `docs/entscheidungen.md`.
