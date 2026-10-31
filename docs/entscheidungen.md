# Grundentscheidungen – Heimnetz (bis 0.22.0 „Netzwerk“)

Was beim Anlegen entschieden wurde. Die Skills lesen das vor der ersten fachlichen Erweiterung (Skill-Profil →
Doku → Entscheidungs-Ort). Es ist Projektkontext, keine unveränderliche Architektur: Ändert sich etwas, wird es hier
nachgetragen.

## Zweck und Grenzen

- Zweck: eigene Seite „Netzwerk“ in der Seitenleiste im Glas-Design wie die Baustelle (`ha-baustelle`). Sie zeigt, wie
  es dem Heimnetz und dem Internetzugang (FRITZ!Box 6860 5G, Mobilfunk bei Drei) geht: Gesamtstand und Befunde,
  Journal, Protokoll der FRITZ!Box, Geräte mit Verlauf, Datenverbrauch, Mobilfunk-Empfang, Speedtest.
- Erste Fassung: derselbe Umfang wie der Altbestand in `/config` (`packages/netzwerk.yaml`,
  `netzdiagnose/fritz_diag.py`, `dashboards/netzwerk.yaml`, `www/netzwerk-cards.js`), damit er danach vollständig
  abgelöst werden kann. Funktionen werden dabei überarbeitet, wo nötig.
- Ausdrücklich nicht: eigene Speedtest-Messung (das macht die Ookla-Integration, siehe unten); Geräte steuern oder
  Einstellungen der FRITZ!Box ändern – die Integration liest nur. Ausnahmen: Ookla-Messungen auslösen (Messplan) und – seit
  WU-0010 – Warnungen über notify-Dienste von Home Assistant schicken (siehe „Warnungen und eigene Arten“).

## Ablösung des Altbestands (Herbert, 12.10.2026)

- Erst die neue Integration in Betrieb nehmen, dann den Altbestand abschalten: Sammler-Sensoren, Automationen
  `netzdiag_*`, Dashboard und Karten, dazu die Kern-Integration Speedtest.net. Nie beide parallel die Box abfragen
  oder Messungen protokollieren lassen.
- Kein Umzug (Herbert, 12.10.2026): Die alten Daten werden nicht übernommen, die Integration fängt leer an. Beim
  Wechsel wird der Altbestand entfernt und die Integration ausgeliefert („alt weg, neu rein“).
- Umstieg erledigt (12.10.2026): Sammler, Automationen `netzdiag_*`, Dashboard, Karten und Speedtest.net sind aus
  `/config` entfernt; die Integration läuft seit 0.5.1, Messungen startet seit 0.6.0 ihr Messplan.

## Speedtest (Herbert, 12.10.2026)

- Befund 12.10.2026: Die Kern-Integration Speedtest.net ist seit 03.10.2026 „nicht verfügbar“. Sie hängt an der
  ungepflegten `speedtest-cli`, bietet nur Server in Polen und im Baltikum an, obwohl speedtest.net den Anschluss in
  Wien verortet, und lieferte zuletzt einen Ping von 1.800.000 ms.
- Ersatz: HACS-Integration Ookla Speedtest (`soulripper13/hass-speedtest-ookla`, offizielles Ookla-Programm) mit
  festem Server in Wien (Server-ID in deren Optionen, Ausweichen auf den nächsten Server erlaubt). Dort werden auch
  Takt und Zielserver eingestellt.
- Diese Integration liest deren Sensoren, protokolliert jede Messung mit Server und Grundlast (Verkehr über die Box
  vor der Messung) und wertet aus (Tarif, Tagesverlauf, Vergleichbarkeit je Server).
- Mobilfunk: Jede Messung kostet einige hundert MB; der Takt richtet sich nach dem Tarif.

## Technik

- Art: eigene Integration mit Abruf (`quelle: abruf`). Sie fragt die FRITZ!Box selbst über TR-064 ab (wie bisher
  `fritz_diag.py`: Ereignisprotokoll, Hosts, LAN/DHCP, Mobilfunk, WAN-Zähler) über einen gemeinsamen Abruf
  (Coordinator), dazu der DHCP-Test und die Erreichbarkeit vom Pi aus. Die Verbindung in
  `custom_components/netzwerk/api.py` ist noch ein Beispiel ohne Netz.
- Zugang zur Box: aus dem Eintrag der vorhandenen Integration FRITZ!Box Tools, nicht noch einmal eingeben; kein
  Kennwort im Repo, in Dateien oder Ausgaben.
- Ist die Box nicht erreichbar, werden die Entitäten „nicht verfügbar“; Home Assistant versucht es selbst wieder.
- Fachlogik ohne Home Assistant in `custom_components/netzwerk/logik/` (Befunde, Journal-Abgleich, Grundlast,
  Auswertung Speedtest), mit eigenen Tests.
- Daten: Messwerte mit Verlauf (Mobilfunk-Empfang, Speedtest, Zustände) als Sensoren über die Aufzeichnung von Home
  Assistant. Lange Listen (Journal, Protokoll der Box, Verlauf je Gerät, Speedtest-Protokoll mit Grundlast) gehören
  nicht in die HA-Datenbank, sondern in eine eigene kleine Datenbankdatei auf diesem Pi, mit Schema-Version ab Tag 1.
  Gerätenamen und MAC-Adressen nie unter `/local`.
- Oberfläche: eigene Seite (Panel) im Glas-Design wie `ha-baustelle`, gebaut aus Quellcode. Die Seite rechnet nichts
  Fachliches, sie bekommt fertige Daten von der Integration. Vor dem Bau ein Mockup zur Abnahme.
- Entwicklung bis 0.22.0 im privaten Repo `herbertschrotter-blip/ha-netzwerk` (jetzt Archiv); ab 0.23.0 öffentlich in
  `herbertschrotter-blip/ha-heimnetz` mit frischer Historie und automatischer Prüfung (siehe Veröffentlichung,
  WU-0006). Mockups und persönliche Arbeitsdateien bleiben lokal (`.gitignore`). Push nur durch den Entwickler.
- Auslieferung: `python ausliefern.py` kopiert nach `custom_components/` der HA-Konfiguration und sichert die vorige
  Fassung (Rückweg: `--zurueck`); ausführen nur Herbert oder Claude nach Bestätigung, Neustart durch Herbert.

## Seite (Mockup abgenommen von Herbert, 12.10.2026)

- Vorlage ist `mockups/netzwerk.html` (Abnahme in `mockups/README.md`): sechs Reiter Übersicht, Speedtest, Geräte,
  Mobilfunk, Verbrauch, Protokoll; Gesamtstand im Kopf jedes Reiters.
- Neu gegenüber dem Altbestand: Messungen unter Grundlast weglassen, ¼ oder voll zählen; Tabelle der letzten Messungen
  mit Grundlast; Anteil der Speedtests am Datenverbrauch. Die Hardware-Adresse der Box entfällt.

## Umsetzung (Herbert, 12.10.2026)

- TR-064 über `fritzconnection` 1.15.1, dieselbe Bibliothek und Fassung wie FRITZ!Box Tools – bewährt statt Eigenbau.
- Die Seite holt fertige Daten über eigene WebSocket-Befehle wie bei der Baustelle (G-11); aktuelle Zustände gibt es
  zusätzlich als Sensoren. Was FRITZ!Box Tools schon als Entität liefert, wird nicht doppelt angelegt.
- Fünf Etappen: 1 Abruf und Sensoren, 2 Datenbank und Speedtest-Protokoll, 3 Auswertung und WebSocket, 4 Seite,
  5 Umstieg. Ausgeliefert wird erst zum Umstieg, damit Altbestand und Integration nie gleichzeitig die Box abfragen.
- Antwortet die Box nicht, heißt der Gesamtstand „FRITZ!Box nicht erreichbar“; die Prüfungen vom Pi laufen weiter.

## Datenbank (12.10.2026)

- Datei `netzwerk/netzwerk.db` in der HA-Konfiguration (wie `baustelle/baustelle.db`), damit sie in der HA-Sicherung
  ist; nicht unter `/local`, weil sie Gerätenamen und Hardware-Adressen enthält. Schema-Version in
  `PRAGMA user_version`; während einer Sicherung ruht das Schreiben.
- Inhalt: Journal, Protokoll der Box, Speedtest-Messungen mit Grundlast, Momentaufnahme je Messung (eigene Tabelle,
  WU-0005), Gedächtnis des Abrufs. Verlauf je Gerät kommt
  aus dem Journal. Journal und Protokoll werden nach 400 Tagen gelöscht, Messungen bleiben.
- Einzelne Messung löschen (Herbert, 28.10.2026, AN-0007): nur Admins, im Fenster der Messung mit Rückfrage; Kennung
  ist der Zeitpunkt. Gelöscht wird nur in der eigenen Datenbank (Messung, Momentaufnahme, Durchlauf der gemerkten Serie);
  der Verlauf der Ookla-Entitäten im Recorder bleibt. Der Zeitpunkt kommt auf eine Merkliste (Tabelle
  `messung_geloescht`, ohne neue Schema-Version wie `messung_kontext`), damit die Messung nicht wieder eingetragen wird –
  Ookla zeigt sie weiter als letzten Test. Ins Journal kommt „Messung <Zeit> gelöscht“, ohne Person und Gerät. Bewusst
  nicht: „nicht werten“ und Rückgängig.
- Speedtest: Die Integration findet die Sensoren der Ookla-Integration über das Entitätsregister und trägt jede neue
  Messung ein. Takt und Server stellt Herbert in der Ookla-Integration ein (ab Werk alle 24 h).

## Auswertung und Schnittstelle (12.10.2026)

- Die Auswertung aus den Karten des Altbestands ist in die Fachlogik gewandert (gleiche Formeln, gegen die
  JavaScript-Fassung geprüft); die Seite bekommt fertige Zahlen, Lagen auf der Farbskala und Texte per WebSocket.
- Einstellungen (Tarif, Auswerten ab) liegen im Integrations-Speicher (G-09) und werden über die Seite geändert (nur
  Admin); ohne Eintrag gibt es keinen Tarif.
- Das Datenvolumen einer Messung ist geschätzt (Rate × 12 s je Richtung); Ookla meldet die Bytes nicht als Sensor.

## Seite (12.10.2026)

- Lit in JavaScript (wie die Baustelle), gebündelt mit esbuild zu einer Datei; Quellen unter `frontend/src`, die
  gebaute Datei ist eingecheckt und wird als einzige ausgeliefert. Stile aus dem abgenommenen Mockup.
- Die Seite rechnet nichts Fachliches: Lagen, Texte, Anteile kommen von der Integration; die Seite formatiert und
  bedient (Filter der Geräteliste nur in der Anzeige, Suche im Protokoll in der Datenbank).
- Vertrag Seite ↔ Integration: `tests/seite/daten.json` ist die Vorlage der Seitentests; ein Integrationstest prüft,
  dass die echten Antworten dieselbe Form haben.

## Messplan (Herbert, 12.10.2026)

- Die Integration führt einen eigenen Messplan (wie oft, Zeitfenster, Verhalten bei Verkehr) und startet die Messung
  über Ooklas Aktion `ookla_speedtest.run_speedtest`; Ookla steht dafür auf „manuell“. Gemessen wird weiter von Ookla.
  Ooklas eigene Einstellungen (Server, Takt, „manuell“) ändert die Integration nicht – die Seite zeigt sie und öffnet
  deren Dialog.
- Bei Verkehr über der Schwelle (10 % vom Download-Tarif, ohne Tarif 10 Mbit/s) wird verschoben: alle 5 min neu,
  höchstens 30 min, danach trotzdem gemessen und als belastet eingetragen. Keine Datenvolumen-Grenze (unbegrenzter
  Tarif).
- Ausnahme von „die Integration liest nur“: sie darf Ookla-Messungen auslösen. Die FRITZ!Box und Geräte steuert sie
  weiterhin nicht.

## Funk und Einstellungen (Herbert, 12.10.2026)

- Reiter „Mobilfunk“ wird „Funk“ mit Umschalter WLAN/Mobilfunk – es bleibt bei sechs Reitern (seit 0.26.0 „Internet“,
  WLAN unter Geräte – siehe „Internet und Zugang“). Alle Einstellungen
  (Tarif, Auswerten ab, belastete Messungen, Messplan, WLAN-Grenze) liegen in einem Fenster hinter ⚙ im Kopf; die
  Reiter zeigen nur noch Werte (Mockup netzwerk.html · Funk und Einstellungen).
- WLAN und Mobilfunk werden nur über die offiziellen TR-064-Dienste gelesen (WLANConfiguration,
  X_AVM-DE_WANMobileConnection). Was nur die Weboberfläche der Box zeigt (SINR, CQI, Band je Zelle), bleibt weg –
  das bräche mit jedem FRITZ!OS-Update. Den WLAN-Empfang meldet die Box in Prozent.
- Bänder und Kanäle der Box alle 10 Minuten, Geräteliste des WLAN jede Minute. Ein Kanalwechsel und eine Neueinwahl
  des Mobilfunks (Verbindungsdauer kleiner als zuvor) kommen ins Journal.
- Mobilfunk mit Basisstation (13.10.2026): Grafik und Zellliste nur aus der TR-064-Zellliste (Art, Rolle, Kennung,
  RSRP/RSRQ, Entfernung, Anbieter). Frequenz, Bandbreite, MIMO, Carrier Aggregation, Beamforming, vier Antennen,
  Mbit/s je Zelle und Latenz zeigt nur die Weboberfläche – bleiben aus demselben Grund weg; die IMEI nie.
- Karte zum Mast (Herbert, 13.10.2026): zweite Ausnahme vom „nur die Box lesen“ – mit einem eigenen
  OpenCellID-Schlüssel (Optionen des Eintrags, nicht im Repo) schlägt die Integration den Standort des Masts der
  Ankerzelle nach. Hinaus geht nur die Zellkennung, nie der Standort der Wohnung; gefragt wird nur beim Anzeigen,
  höchstens einmal am Tag je Zelle (gefunden: einen Monat gemerkt, nicht erreichbar: nach einer Stunde neu).
  Kartenkacheln lädt der Browser von CARTO wie bei den Karten von Home Assistant – CARTO sieht dabei den
  Kartenausschnitt um die Wohnung; das ist bei jeder Karte in HA so und bewusst hingenommen. Senderichtungen gibt es nicht (kennt OpenCellID nicht).
- BeaconDB als zweite Quelle (Herbert, 14.10.2026, WU-0002): OpenCellID kannte die Zellen nicht, BeaconDB schon.
  BeaconDB (ohne Schlüssel) wird immer gefragt, OpenCellID zusätzlich mit Schlüssel; je Zelle zählt der genauere
  Fund. Hinaus geht wieder nur die Zellkennung (`considerIp: false`, keine Ausweich-Ortung über die Adresse).
  Nachgeschlagen wird jede LTE-Zelle mit voller Kennung (Anker, gebündelte, in Reichweite); fehlen PLMN/TAC bei einer
  Zelle derselben Sendeanlage wie die Hauptzelle, gelten deren Werte. Beide Dienste liefern den Ort, an dem Nutzer
  die Zelle empfangen haben, nicht den Mast: Je Sendeanlage ist der Mast das Mittel ihrer Zellen, gewichtet mit
  1/Genauigkeit². Band und Frequenz je Zelle liefert TR-064 nicht – bleiben weg.
- Karte mit Leaflet, basemap.at und OpenStreetMap (Herbert, 14.10.2026, WU-0002): CARTO liefert seit 2026 ohne
  Schlüssel nur Platzhalter („API KEY REQUIRED“) und fällt weg. Grundlagen ohne Schlüssel: basemap.at (amtliche
  Grundkarte Österreichs, Server der Stadt Wien; normal und grau) und OpenStreetMap; „Automatisch“ nimmt im dunklen
  Design basemap.at grau, von der Seite abgedunkelt. Kein Satellitenbild (Herbert: nur Straßenkarten). Die Karte ist
  Leaflet 1.9.4 (zoomen, verschieben, ⌖); die Integration liefert Orte und den Startrahmen, die Seite zeichnet nur.
  Die Kacheln lädt der Browser; der Anbieter sieht den Kartenausschnitt um die Wohnung, wie bei jeder Online-Karte.
- Funkmasten aus OpenStreetMap (Herbert, 14.10.2026, WU-0002): Für 5G gibt die Box nur die PCI heraus, nachschlagen
  geht nicht; BeaconDB hat weder Gebietsabfrage noch Datenabzug, der Senderkataster (FMK) keine offene Lizenz. Echte
  Mast-Standorte liefert OpenStreetMap (ODbL): Die Integration fragt einmal im Monat im Hintergrund bei Overpass die
  Funkmasten in einem Ausschnitt auf festem Raster ab (Block von 0,2° plus 0,1° Rand, etwa 44 × 30 km) – daraus lässt
  sich die Wohnung nur auf den Block von etwa 22 × 15 km eingrenzen. An die Seite gehen die nächsten 100 Masten bis
  10 km. „Passt“ (geändert 14.10.2026): der OSM-Mast am nächsten am geschätzten Mast der Zellen (bis 1,5 km); ohne
  geschätzten Mast der, dessen Entfernung der laut Box am nächsten liegt – die schwankt je Zelle stark (z. B.
  1 km und 4 km für Sektoren derselben Sendeanlage). Einmal gefundene Zellen einer Sendeanlage zählen einen Monat
  lang für deren Mast mit, auch wenn die Box gerade an einem Sektor hängt, den keine Datenbank kennt. Auf der Karte als zuschaltbare Ebene; „passt“ markiert den Mast, dessen Entfernung am nächsten an der
  Entfernung laut Box liegt und der in Richtung der gefundenen Zellen steht – ein Hinweis, kein Beweis. 5G steht am
  Mast der Ankerzelle nur als „vermutlich“ (bei 5G-NSA meist am selben Mast).
- Anbieter und Technik je Mast aus dem OpenCellID-Datenabzug (Herbert, 14.10.2026, WU-0002): In OpenStreetMap haben
  die Masten nahe der Wohnung keine Angaben (in der Gegend 25 von 260 mit Betreiber, 3 mit LTE). Mit eigenem Schlüssel
  lädt die Integration einmal im Monat im Hintergrund die Datei für ganz Österreich (MCC 232), behält nur die Zellen
  im OSM-Ausschnitt (gestückelt geladen, Zeile für Zeile entpackt) und ordnet jede Zelle dem nächsten Mast in höchstens 500 m zu: Anbieter aus der Netzkennung
  (01/11/12 A1, 03/07/13 Magenta, 05/10 Drei, 91 ÖBB-Zugfunk), Technik 2G/3G/LTE/5G. Hinaus geht nur der Schlüssel, kein Standort. Die Orte sind
  Mittel aus Messungen von Nutzern – eine Schätzung, nicht amtlich; am Land oft lückenhaft. Fehlantworten (Limit,
  Schlüssel) werden einen Tag gemerkt. Karte: ⛶ Vollbild (Fullscreen-API, sonst fest über dem Fenster), Antippen eines
  Masts zeigt das Infofeld.

## Tickets (Herbert, 13.10.2026)

- Ticketsystem wie im Baustrommanager (Mockup netzwerk.html · Melden): Melden-Knopf unten rechts auf jedem Reiter,
  Fehler/Wunsch/Anregung mit Text, Reiter, Version, Gerät, „Stand der Seite“ und bis zu 3 Screenshots. Nummern je Art
  ab 0001 (FE, WU, AN). Abgearbeitet wird in Claude Code mit dem Skill `ticket` (Ticket-Profil in CLAUDE.md).
- Screenshots klassisch: am Handy mit den Tasten aufnehmen und aus der Galerie wählen, am PC zusätzlich Strg+V und
  „Fenster aufnehmen“. Die Seite fotografiert sich nicht selbst (Herbert). Bilder gehen nach der Meldung einzeln
  hinüber; die Rückmeldung nennt, wie viele angekommen sind – im Baustrommanager ist nie ein Bild angekommen
  (Baustelle FE-0027), das darf hier nicht still passieren.
- Speicher ist der Integrations-Speicher; die Integration legt eine lesbare Kopie unter `<config>/netzwerk/` ab, weil
  `.storage/` für Claude gesperrt ist. Geändert wird nur über die Seite und die Aktion `netzwerk.ticket`.
- Melden darf jeder angemeldete Benutzer; schließen, wieder öffnen, löschen und die Aktion nur Admins.

## Geräte nach Art (Herbert, 13.10.2026, AN-0001)

- Die Art eines Geräts wird nur aus Gelesenem bestimmt: Geräteliste von Home Assistant (über die Hardware-Adresse),
  Mesh-Liste der Box (offizielle TR-064-Aktion `X_AVM-DE_GetMeshListPath`), Hersteller der Adresse, Name. Selbst
  gewählt hat Vorrang. Nichts davon geht nach außen: Die Herstellerliste liegt offline in der Integration (aus den
  öffentlichen IEEE-Registern über Wireshark `manuf`, neu erzeugbar mit `tools/hersteller.py`).
- Hardware-Adressen bleiben in der Integration; die Seite bekommt nur Art, Quelle in Worten und die Geräte-Kennung.
- FRITZ!DECT-Stecker funken per DECT und erscheinen nicht in der Gerätetabelle des Heimnetzes – sie bleiben außen vor.

## Momentaufnahme je Messung und Langzeitarchiv (Herbert, 23.10.2026, WU-0005, WU-0002)

- Zu jeder Speedtest-Messung hält die Integration fest, was in diesem Moment los war: Mobilfunk (Netz, Ankerzelle,
  Sendeanlage, RSRP/RSRQ, 5G, Entfernung, Nachbarzellen, PLMN/TAC, verbunden seit, geschätzter Mast), Box (Modell,
  Firmware, Laufzeit, eingeschaltete Bänder; aus DeviceInfo im langsamen Takt), Heimnetz (Geräte online, davon WLAN),
  Auslöser (Messplan, „Jetzt messen“, Serie, Ookla), Zusatzwerte der Ookla-Sensoren (Jitter, Bufferbloat, Anbieter,
  Link zum Ergebnis), Umgebung (Wetter-Entität – bevorzugt Met.no –, Feiertags-Kalender der Integration „holiday“,
  Werktag/Wochenende). Gespeichert als JSON in der eigenen Tabelle `messung_kontext` – ohne neue Schema-Version, damit
  der Rückweg (`ausliefern.py --zurueck`) mit der älteren Fassung weiter geht. Nur Messungen, die während der Laufzeit
  der Integration entstehen, bekommen den Stand von jetzt; eine nach einem Neustart nachgeholte wird nachgetragen.
- Ältere Messungen der letzten 62 Tage (so lange hält der Recorder den Verlauf) werden beim Start einmal nachgetragen –
  aus dem Verlauf der eigenen Sensoren, der Ookla- und Wetter-Entitäten, der Feiertags-Kalender und den Zellwechseln im
  Journal; je Messung ein kleines Fenster (Pi schonen). Ookla-Werte zählen ab dem ersten Wert nach der Messung (davor
  steht noch der der vorigen). Box, Heimnetz und Teile des Mobilfunks fehlen dort; die Seite zeigt „nachgetragen“.
- Langzeitarchiv über Entitäten statt eigenem Archiv: die Integration gibt ihre Werte als Entitäten frei (dazu ab 0.22.0
  Mobilfunkzelle, Entfernung zur Basisstation, Nachbarzellen, 5G-PCI); dauerhaft mitgeschrieben werden sie von
  **Scribe** (HACS) in die vorhandene TimescaleDB, in der auch Baustelle schreibt (Herbert, 24.10.2026). LTSS kam nicht
  in Frage: eingefroren (Issue #277). InfluxDB wäre die offizielle, aber getrennte Alternative; Scribe-Daten sind
  normale PostgreSQL-Tabellen und bleiben lesbar, falls der Schreiber einmal getauscht werden muss. Der Sensor „Letzte
  Messung“ trägt Messwerte und Momentaufnahme als Attribute, damit das Archiv sie mitschreibt – ohne Entfernung und Richtung zum geschätzten
  Mast (daraus ließe sich die Wohnung bestimmen; die Seite zeigt sie). Weitere fehlende Werte als Entitäten folgen mit
  WU-0002; der Archiv-Baustein G-24 in claude-workbench wird entsprechend angepasst.

## Veröffentlichung und neuer Name (Herbert, 25.10.2026, WU-0006)

- Die Integration wird öffentlich: neue Domain `heimnetz`, Anzeigename „Heimnetz“ (vorher `netzwerk` – zu allgemein für
  HACS und für andere Nutzer). Entitäten heißen künftig `sensor.heimnetz_*` / `binary_sensor.heimnetz_*`; die Seite liegt
  unter `/heimnetz`, die WebSocket-Befehle unter `heimnetz/*`, die Aktion ist `heimnetz.ticket`, die Daten liegen unter
  `<config>/heimnetz/` (Datenbank `heimnetz.db`, Tickets) und in den Speichern `heimnetz.*`.
- Öffentliches Repo später `herbertschrotter-blip/ha-heimnetz` mit frischer Historie (legt Claude erst nach Rückfrage
  an), Lizenz Apache-2.0. `manifest.json` nennt es als Dokumentation und Issue-Tracker, Codeowner
  `@herbertschrotter-blip`.
- Umstieg bei Herbert ohne Datenverlust: Heimnetz übernimmt beim ersten Laden Messungen, Journal, Protokoll und
  Gedächtnis (Datenbank über die Sicherungs-Schnittstelle von SQLite), Einstellungen, Messplan, Arten, gemerkte Masten,
  OSM- und OpenCellID-Daten (Speicher der alten Einrichtung, über `Store` geladen), Tickets mit ihren Nummern und
  Bildern sowie die Optionen (OpenCellID-Schlüssel). Übernommen wird nur in eine leere Ablage, die alten Daten bleiben
  liegen. Neue Entitäts-IDs sind in Ordnung. Die lesbare Ablage der Tickets (`meldungen.json`, `meldungen.md`) wird
  nicht kopiert, Heimnetz schreibt sie aus dem übernommenen Speicher neu. Ist die alte Datenbank kaputt
  (SQLITE_CORRUPT, SQLITE_NOTADB), geht es ohne sie weiter, die Bilder kommen trotzdem mit; jeder andere Fehler
  (Platte voll, Ein-/Ausgabe, gesperrt) gilt als vorübergehend – die Einrichtung versucht es später noch einmal.
- Nie beide zugleich: Solange eine Einrichtung der alten Integration nicht deaktiviert ist, bricht die Einrichtung von
  Heimnetz ab, und eine vorhandene Heimnetz-Einrichtung startet nicht (Reparatur-Hinweis). Die alte Einrichtung wird
  deaktiviert, nicht gelöscht – beim Löschen entfernt die alte Integration ihre Einstellungen und gemerkten Masten
  (`async_remove_entry`). Reihenfolge in `docs/umstieg.md`.
- Sprache Deutsch und Englisch: Die Seite folgt der Sprache im Profil des Nutzers und schickt sie bei jedem
  WebSocket-Befehl im Feld `sprache` mit; alles, was die Integration für diese Antwort aufbereitet (Befunde der
  Ansichten, Fehlermeldungen, Tickets, Vorschau des Issues), kommt in dieser Sprache (`const.SEITEN_SPRACHE`, gilt nur
  in der Aufgabe des Befehls). Was der Abruf im Hintergrund erzeugt und speichert (Journal, Fehler beim Lesen der Box),
  Aktionen und Diagnose folgen der Sprache von Home Assistant (`hass.config.language`, `const.sprache_system`; `de`
  und Varianten Deutsch, sonst Englisch). Der deutsche Text im Code ist zugleich der Schlüssel, die englische Fassung steht in einer
  Tabelle daneben (`logik/sprache.py`, `logik/englisch.py`; Seite: `frontend/src/sprache.js`); die Fachlogik bekommt
  die Sprache als Parameter. Gespeichertes (Journal, Momentaufnahme) bleibt in der Sprache, in der es entstand.
  Kennungen, an denen Seite oder Logik etwas erkennen (Gerätegruppen, Rolle einer Zelle, Grund des Messplans),
  bleiben deutsch und fest; angezeigt wird der übersetzte Text.
- Öffentlich melden (Mockup `githubMelden`, abgenommen 25.10.2026): Lokal gespeichert wird immer; dazu öffnet der
  Browser ein vorausgefülltes Issue (`…/ha-heimnetz/issues/new?title=…&body=…`, Adresse in `const.GITHUB_ISSUE_NEU`),
  abgeschickt mit dem eigenen GitHub-Konto. Die Integration hat keinen Token und schickt selbst nichts an GitHub.
  Titel und Text baut die Integration (`logik/github.py`), die Seite zeigt sie nur. Mit geht nur Text und grober Stand
  (Versionen, Reiter, Gerät, Box-Modell und FRITZ!OS, Netztechnik, Ookla ja/nein, lokale Ticketnummer); Zell- und
  Signaldaten nur mit Schalter. Nie: Gerätenamen, Hardware- und IP-Adressen, Standort von Home Assistant, Kennwörter –
  auch im Text der Meldung werden sie geschwärzt (Muster für Adressen, Koordinaten – auch `lat=`/`mlon=` in
  Kartenlinks – und „Kennwort: …“, dazu die Gerätenamen der Box und der Geräte-Tracker in Home Assistant). Ebenso
  Zellkennungen, die der Nutzer selbst schreibt (Muster `xxxxx-yy`, Werte hinter TAC/PCI/ECI/eNB, dazu die Kennungen
  der Zellen, die die Box gerade sieht) – sie gehen nur über den Schalter hinaus. Das Gerät zur Meldung kommt nur als
  bekannter Wert (Handy/Phone, Desktop) ins Issue, sonst gar nicht. Das lokale Ticket behält den Text, wie er gemeldet
  wurde. Der Link bleibt unter 7000 Zeichen, sonst wird der Text gekürzt. Bilder gehen über den Link nicht. Geöffnet
  wird noch im Klick, vor dem Speichern – nach einer Antwort sperren Safari und die App von Home Assistant das Fenster;
  die Ticketnummer im Issue ist deshalb vorausgesagt (meldet zugleich jemand anderer, sagt die Rückmeldung es).
- Vorgaben für neue Nutzer: Ookla ist empfohlen, nicht Pflicht – ohne läuft alles, der Reiter Speedtest weist darauf
  hin. Eine neue Installation (nichts gespeichert, keine alte Einrichtung) misst 4-mal am Tag (`messplan.NEU`, alle
  6 Stunden) und speichert den Plan gleich, damit eine spätere Änderung der Vorgabe ihn nicht verschiebt. Übernommene
  Einstellungen bleiben, beim Umstieg ohne gespeicherten Plan bleibt er aus wie bisher. Das Datenvolumen je Messung
  schätzt die Integration wie im Speedtest-Protokoll ((Down + Up) × 12 s / 8, aus der letzten Messung, sonst dem Tarif).
- Diagnose: öffentlich anhängbar – nur Zahlen und grober Stand; `logik/diagnose.py` schwärzt tief nach Schlüsselnamen
  (Zugang, Schlüssel, Zelle, TAC/PCI, Koordinaten, Namen, Adressen) und in allen Texten wie beim Melden.
- Paket für HACS und GitHub: Lizenz Apache-2.0 (`LICENSE`), `hacs.json` (Mindestversion von Home Assistant, README
  in HACS). Eigenes Symbol unter `custom_components/heimnetz/brand/` (`icon.png`, `icon@2x.png`) – Home Assistant und
  die HACS-Prüfung nehmen es aus der Integration, ein Eintrag im Repo `home-assistant/brands` ist nicht nötig.
  GitHub Actions: `tests.yml` (dieselben Checks wie vor dem Commit), `validate.yml` (hassfest und HACS-Prüfung, auch
  täglich), `release.yml` (Tag `vX.Y.Z` → Release mit dem Abschnitt `## [X.Y.Z]` aus `CHANGELOG.md`; der Tag muss zur
  Version in `manifest.json` passen). Actions auf feste Commits gepinnt, die Version steht im Kommentar. Issue-Vorlagen
  Fehler/Wunsch/Anregung zweisprachig mit Datenschutz-Hinweis; leere Issues bleiben erlaubt, weil der Melden-Link ohne
  Vorlage öffnet. Testdaten nur erfunden (Zellen `aaaaa-xx`, TAC `1A2B`, Koordinaten in Wien).
  `manifest.json` nennt unter `after_dependencies` nur Integrationen von Home Assistant (`fritz`, `recorder`):
  hassfest kennt keine aus HACS. Ookla wird ohnehin bei jedem Abruf neu gesucht (`speedtest.verbinden`), eine später
  geladene Ookla-Einrichtung ist also beim nächsten Abruf da.
- Checkliste beim Anlegen von `ha-heimnetz` (die HACS-Prüfung in `validate.yml` liest Einstellungen des Repos, die
  in keiner Datei stehen – fehlen sie, ist der erste Lauf rot): Beschreibung setzen (z. B. „FRITZ!Box-Heimnetz und
  Mobilfunk in Home Assistant – ausgelegt für Österreich“), Topics `home-assistant`, `hacs`, `hacs-integration`,
  `fritzbox`, Issues eingeschaltet, Repo öffentlich. Nimmt die brands-Prüfung das Symbol unter `brand/` nicht an, in
  `validate.yml` `ignore: brands` mit Begründung eintragen. Nach dem ersten Lauf der Actions prüfen, ob hassfest und
  HACS grün sind.
- README für Fremde: Deutsch zuerst, darunter ein vollständiger englischer Teil (keine zweite Datei, damit HACS
  beides zeigt). Voraussetzungen als drei Tabellen **muss** / **soll** / **kann**, je Zeile mit dem, was ohne sie
  fehlt. Muss: Home Assistant ab der Mindestversion aus `hacs.json`, HACS, FRITZ!Box, FRITZ!Box Tools mit
  TR-064-Benutzer, Recorder. Soll: Ookla Speedtest, Met.no, Holiday. Kann: OpenCellID-Schlüssel, Scribe/TimescaleDB.
  „Ausgelegt für Österreich“ und „ohne Gewähr, Hobbyprojekt“ stehen oben; DSL/Glasfaser, weitere Hersteller und Länder
  nur als Ausblick. Entitäts-IDs in beiden Sprachen, weil sie beim Einrichten aus dem Namen in der Systemsprache
  entstehen. Das Einspielen per `ausliefern.py` steht nur noch unter „Entwickeln“.

## Einrichtung anzeigen (Herbert, 27.10.2026, WU-0007)

- Mockup `netzwerk.html` · Einrichtung abgenommen: fünfter Reiter „🧩 Einrichtung“ im Fenster ⚙ mit den
  Voraussetzungen aus dem README (Muss / Soll / Kann). Erkennen und Bewerten macht die Integration
  (`logik/einrichtung.py`, ohne HA; dünner Teil `einrichtung.py`, Befehl `heimnetz/einrichtung`, nur Admins), die Seite
  zeigt nur an. Gelesen werden geladene Integrationen (`hass.config.components`), Config-Einträge mit Zustand,
  heruntergeladene Custom Components (`loader.async_get_custom_components`), die Aufbewahrung des Recorders und aus den
  eigenen Optionen nur, ob ein OpenCellID-Schlüssel eingetragen ist. Von der Box nur das Modell, keine Gerätenamen
  oder Adressen. FRITZ!Box Tools zählt als eingerichtet, wenn der Eintrag da ist, aus dem Heimnetz den Zugang holt
  (geladen muss er dafür nicht sein).
- Heimnetz installiert, lädt und startet nichts: die Knöpfe navigieren in Home Assistant (`/_my_redirect/
  config_flow_start`, `/_my_redirect/hacs_repository`, Seite der Integration) oder öffnen hacs.xyz und opencellid.org
  im neuen Fenster. HACS-Repositories: Ookla `soulripper13/hass-speedtest-ookla`, Scribe `jonathan-gtd/scribe`
  (geprüft 27.10.2026). Langzeitarchiv gilt als eingerichtet mit geladenem Scribe-Eintrag oder geladener Integration
  `influxdb`. Die Mindestversion von Home Assistant steht in `const.HA_MINDEST` und muss zu `hacs.json` passen (Test).
- Fehlt der Recorder, gibt es zusätzlich einen Reparatur-Hinweis (Warnung, Heimnetz startet trotzdem); für FRITZ!Box
  Tools gab es ihn schon.

## Vorgeschaltetes Modem – Rohdaten-Werkzeug (Herbert, 27.10.2026, WU-0008)

- Anlass: Ein Nutzer hat das Mobilfunk-Modem nicht in der FRITZ!Box, sondern ein vorgeschaltetes ZTE-5G-Modem
  (vermutlich ZTE G5TC von Drei Österreich oder G5TS). Die FRITZ!Box kennt dann keine Funkdaten, „Funk › Mobilfunk“
  bleibt leer. Um das später zu unterstützen, braucht der Entwickler Rohdaten. Diese Version (Mockup `netzwerk.html` ·
  Diagnose, abgenommen 27.10.2026) liefert nur das Abfrage- und Export-Werkzeug, keine Auswertung.
- Reiter „🔬 Diagnose“ (Beta) im Fenster ⚙ Einstellungen: Adresse (Vorgabe 192.168.0.1) und Kennwort (optional). Abfragen
  und Schwärzen macht die Integration (`logik/modem.py` rein ohne HA, `modem.py` dünn über das Netz; WebSocket-Befehl
  `heimnetz/modem`, nur Admins), die Seite zeigt nur an und speichert/kopiert die geschwärzte Antwort.
- Dritte Ausnahme von „die Integration liest nur“ nach außen: auf Knopfdruck die Weboberfläche eines vorgeschalteten
  Modems im eigenen Heimnetz. Sicherheit (mit Tests): nur private IPv4/IPv6-Adressen, die nicht
  Loopback/Link-Local/unspezifiziert sind, keine Hostnamen; keine Weiterleitungen (außer der einen unten);
  Zeitlimit je Anfrage (~8 s), Gesamtzeit und Antwortgröße begrenzt (512 KB); http zuerst, https ohne
  Zertifikatsprüfung nur, wenn http nicht antwortet oder die Startseite per http auf https an genau diese Adresse
  weiterleitet (ZTE G5TC, GitHub #2, 30.10.2026: dieser einen Weiterleitung wird gefolgt), und nur zu genau dieser
  privaten Adresse. Nur lesende Abfragen plus Anmeldung/Abmeldung; der ZTE-Befehl `goform_set_cmd_process` wird ausschließlich mit `goformId=LOGIN`/`LOGOUT` aufgerufen, nie mit einem anderen
  set-Befehl. Eigene kurzlebige aiohttp-Session mit Cookie-Jar für die Anmeldung.
- Anmeldung nur mit dem Kennwort, das der Besitzer selbst eingibt, über das normale Web-Login des Geräts (LD-Wert holen,
  SHA-256-Hash bilden – öffentlich dokumentiert, z. B. `teixeluis/zte-lte-modem`); kein Raten, höchstens ein Versuch je
  Klick. Klappt es nicht → Befund `anmeldung_abgelehnt`, die Daten ohne Anmeldung bleiben im Ergebnis. Das Kennwort wird
  nie gespeichert, nie protokolliert, steht in keiner Antwort und wird nach der Abfrage im Frontend-Feld gelöscht.
- Abfrageablauf, jede Stufe als eigener Eintrag (auch wenn sie scheitert, Rohantwort gekürzt + geschwärzt): Startseite
  (Modell), goform ohne Anmeldung, Anmeldung, goform nach Anmeldung, zweite lesende Schnittstelle (ubus, höchstens eine
  Abfrage, sonst „nicht vorhanden“). Geschwärzt wird nach Schlüssel und nach Wert (IMEI, IMSI, ICCID, Rufnummer,
  Seriennummer, MAC- und öffentliche IP-Adressen, WLAN-Name/-Kennwort, Zugang, Sitzung, Koordinaten); Zellkennung,
  Signal, Band, Technik, Modell und Firmware bleiben, weil der Entwickler sie braucht. Export als Datei
  (`heimnetz-modem-JJJJ-MM-TT.json`) oder in die Zwischenablage, Inhalt = die geschwärzte Antwort plus Heimnetz-Version
  und Zeitpunkt. Heimnetz sendet selbst nichts an GitHub oder sonst nach außen; die Datei schickt der Nutzer selbst.
- Bewusst weggelassen: Versand an GitHub, Speichern des Kennworts, Auswerten der Werte (kommt mit der Unterstützung des
  Modems).

## Internet und Zugang (Herbert, 27.10.2026, WU-0009 Stufe 1)

- Mockup `netzwerk.html` · Internet und Zugang abgenommen („bau das alles“): Reiter „Funk“ heißt **„Internet“** und
  zeigt oben, woher das Internet kommt (Art, Gerät, Weg, „automatisch erkannt“/„festgelegt“, „ändern ›“), darunter die
  Werte der Zugangsart (Mobilfunk, DSL, Glasfaser, Kabel) und den Ersatzzugang als eigenen Umschalter. **WLAN wandert
  in den Reiter Geräte** (Umschalter „Geräte | WLAN“) – es bleibt bei sechs Reitern. Kopfzeile: Box und Zugang.
- Erkennen macht die Integration (`logik/zugang.py`, ohne HA), die Seite zeigt nur an. Grundlage ist nur, was die
  FRITZ!Box über die offiziellen TR-064-Dienste meldet (FRITZ!-Doku „TR-064 Support“, fritz.support/resources):
  `WANCommonInterfaceConfig1` `GetCommonLinkProperties` (NewWANAccessType, NewPhysicalLinkStatus, Layer1-Raten) und –
  ab neueren FRITZ!OS – `X_AVM-DE_GetAddonInfos` (NewX_AVM-DE_WANAccessType, z. B. „IP-Client“ = hinter einem anderen
  Router), Mobilfunk `GetInfo` (NewEnable), DSL `GetInfo` (NewStatus), Glasfaser `X_AVM-DE_WANFiber1` `GetInfo`
  (NewFiberMode), `Layer3Forwarding1` `GetDefaultConnectionService` + `GetExternalIPAddress` nur für die Art der
  WAN-Adresse (privat / Netz des Anbieters / öffentlich) und den Vorschlag „.1 im selben /24-Netz“ – die Adresse selbst
  bleibt in `box.py`. Ein Gateway der WAN-Verbindung meldet TR-064 nicht. Kein Absuchen des Heimnetzes, kein Abfragen
  fremder Adressen in dieser Stufe.
- Gelesen wird nur im gemeinsamen Abruf, im langsamen Takt (10 min); „↻ Erneut suchen“ liest den Zugang beim nächsten,
  sofort ausgelösten Abruf mit. Eine Sperre in `Box` sorgt dafür, dass nie zwei Abrufe gleichzeitig an der Box sind.
- Ersatz: Meldet eine Box, die vorher DSL/Glasfaser/Kabel hatte (Anschluss noch da), plötzlich Mobilfunk, ist das der
  Ersatz bei Ausfall, nicht ein Wechsel; nach 14 Tagen gilt der Mobilfunk als neuer Zugang. Ob ein Stick wirklich als
  Ersatz eingestellt ist, meldet TR-064 nicht – „Mobilfunk an der Box eingeschaltet“ zählt als bereit. Die Datenmenge
  über den Ersatz meldet die Box nicht getrennt („–“).
- Werte der Leitung (`logik/leitung.py`, mit Tests), nur wenn das Internet über diesen Anschluss kommt: DSL aus
  `WANDSLInterfaceConfig1` (`GetInfo`, `X_AVM-DE_GetDSLInfo`, `GetStatisticsTotal`; Raten kbit/s, Marge und Dämpfung
  0,1 dB nach der TR-064-Norm); Bewertung Marge gut ab 6 dB / unter 3 dB kritisch, CRC je Stunde über 10 erhöht / über
  100 hoch, Neusynchronisierungen in 7 Tagen ab 2 auffällig / ab 5 instabil (erkannt an „Up“ nach Ausfall oder
  zurückgesetzten Zählern). Glasfaser aus `X_AVM-DE_WANFiber1` (`GetInfo`, `GetStatistics`; dBm/1000), bewertet nach
  den Schwellen, die die Box selbst meldet (bis 2 dB über der unteren knapp). Kabel: TR-064 hat keinen DOCSIS-Dienst.
  Was TR-064 nicht liefert (DSLAM, Vectoring, Status O1–O7, Temperatur, Kanäle/Pegel/MER), steht als „–“ – **kein
  Auslesen der Weboberfläche der Box** (bräche mit FRITZ!OS-Updates, wie beim Mobilfunk). Seriennummern und Kennungen
  (SFP, GPON) werden nicht übernommen.
- Entitäten: „Internetzugang“ immer; DSL (Synchronrate, Störabstandsmarge, Dämpfung je Richtung, Fehler je Stunde) und
  Glasfaser (Lichtleistung empfangen/gesendet) erst, wenn die Box diese Werte gemeldet hat – eine Box mit ungenutztem
  Anschluss bekommt keine. Verläufe wie beim Mobilfunk aus dem Recorder.
- ⚙ → 🌐 Zugang (vor „Einrichtung“, nur Admins): Wahl Automatisch / Mobilfunk über die Box / vorgeschaltetes Modem /
  DSL / Glasfaser / Kabel und Ersatz automatisch/keiner im Einstellungsspeicher; Adresse eines vorgeschalteten Geräts
  nur privat (`modem.adresse_erlaubt`). Das **Kennwort der Weboberfläche wird gespeichert** (Herbert) – in den Optionen
  der Einrichtung (`modem_kennwort`, `async_update_entry`), nie an die Seite (nur „hinterlegt“), nie protokolliert, in
  der Diagnose geschwärzt; die Optionen von Heimnetz behalten es beim Speichern. Die 🔬 Diagnose (WU-0008) nimmt es,
  wenn ihr Kennwortfeld leer bleibt und die Adresse genau die gespeicherte ist; ein dort eingetipptes Kennwort wird
  weiterhin nicht gespeichert. Laufende Werte vom vorgeschalteten
  Gerät seit Stufe 2 (siehe unten; Bibliotheken huawei-lte-api und tplinkrouterc6u erlaubt).

## Vorgeschaltetes Gerät – laufende Werte (Herbert, 27.10.2026, WU-0009 Stufe 2)

- Mockup `netzwerk.html` · Internet und Zugang (abgenommen 27.10.2026, „bau das alles“): bei einem Modem vor der Box
  oben „Werte vom vorgeschalteten Modem (Beta)“, darunter die Mobilfunk-Ansicht wie bei der Box; in ⚙ › 🌐 Zugang der
  Beleg „Gateway antwortet: ZTE G5TC“ und die Zeile „Erkannt · über ubus · zuletzt gelesen“.
- Bausteine je Hersteller/Schnittstelle mit einem Muster: erkennen aus Startseite und Antwortkopf
  (`logik/vorgeschaltet/__init__.py`, Weiterleitungen werden nur gelesen, nicht verfolgt), nur lesende Abfragen,
  Anmeldung nur mit dem Kennwort des Besitzers über das normale Web-Login, höchstens ein Versuch je Abruf, umrechnen in
  `mobil.Mobilfunk` (neu je Zelle `sinr` und `band`). Fachlogik ohne HA mit Tests, Netz dünn in `vorgeschaltet/`.
  - ZTE goform und ZTE ubus (eigener Code). ubus nach dem öffentlichen Protokoll von chennest/zte-cpe-go nachgebaut –
    das Projekt ist GPL-3.0, Heimnetz Apache-2.0, deshalb kein Code übernommen. Erlaubt sind nur
    `zwrt_web.web_login_info/web_login/web_logout`, `zte_nwinfo_api.nwinfo_get_netinfo`, `zwrt_data.get_wwaniface`;
    `uci get` bewusst nicht (liest beliebige Einstellungen, auch WLAN-Kennwörter). Jeder Aufruf wie die Weboberfläche
    als einzelnes Objekt mit `Z-Mode: 0` und `Z-Tag: <methode>` (Mitschnitt eines G5TS im OpenWrt-Forum; GitHub #2,
    31.10.2026). Erkennt Heimnetz ein ZTE, aber keine Schnittstelle, legt 🔬 Diagnose die Antworten beider Proben
    geschwärzt ab (`probe_goform`, `probe_ubus`).
  - Huawei HiLink über `huawei-lte-api` (bewährt, in HA für Huawei LTE). Anforderung `>=1.11.0`, kein `==`: Home
    Assistant pinnt für Huawei LTE 1.11.0, ein eigener Pin würde sich mit dessen Anforderung beißen; die genutzten
    Aufrufe gibt es in 1.11 und 2.0. Ist Huawei LTE eingerichtet, liest Heimnetz deren Entitäten und fragt das Gerät
    nicht selbst – eine zweite Anmeldung würde deren Sitzung stören. Die Bibliothek schreibt im Debug-Protokoll
    Kennwort und Anmeldedaten mit; ein Filter an ihren Loggern verwirft diese Zeilen.
  - TP-Link über `tplinkrouterc6u` (`>=5.37.0`, GPL-3.0, AlexandrErohin/TP-Link-Archer-C6U – nur als Abhängigkeit
    installiert, nicht im Repo; Herbert, 28.10.2026: bleibt, Lizenz und Projekt im README). Nicht
    `TplinkRouterProvider.get_client` und nicht `supports()`: bei den EX- und MR-GCM-Clients meldet sich `supports()`
    in Wahrheit an, der Provider probiert so mehrere Kennwörter. Die Familie (MR600, EX, MR, MR200) bestimmen nur die
    Schlüssel-Abfragen ohne Anmeldung (`cgi/getParm`, `cgi/getGDPRParm`); ohne Kennwort keine Anmeldung; mit Kennwort
    genau ein `authorize()` mit der GCM-Variante der Familie (die Variante CBC/GCM/OAEP lässt sich ohne Anmeldung nicht
    unterscheiden – passt sie nicht, meldet das Gerät „abgelehnt“; am Gerät prüfen). `REQUEST_RETRIES = 1`. Fehler der
    Bibliothek, die nicht nach Ablehnung klingen, gelten als „Lesen fehlgeschlagen“, nicht als abgelehnt.
  - NETGEAR LTE und Teltonika: nur deren HA-Integration lesen, falls eingerichtet (Entitäten über die `unique_id`);
    MikroTik, Sagemcom, Nokia FastMile, Zyxel 5G und Glasfaser-Modems (Nokia, Huawei, Zyxel) nur erkennen, keine Werte,
    solange keine echte Antwort vorliegt. Neue Zugangsart „Glasfaser über ein eigenes Modem“ (`ont`, für die Box ein
    vorgeschaltetes Gerät).
- Suche: nacheinander an gespeicherter Adresse, Vorschlag der Box und 192.168.0.1, .1.1, .8.1, .18.1, .100.1 – nie die
  Adresse der Box, Ende beim ersten erkannten Gerät; kein Absuchen weiterer Adressen. Die Suche hat kurze Zeitlimits;
  erkennt sie nur „ZTE“ ohne Schnittstelle, bestimmt der nächste Abruf die Schnittstelle mit den normalen Zeitlimits
  und merkt sie (GitHub #2). Angestoßen beim Einrichten (Wahl oder Adresse geändert), bei „↻ Erneut suchen“ und – solange nichts gefunden ist – höchstens alle 10 Minuten. Das
  erkannte Gerät steht im Gedächtnis des Abrufs (Adresse, Baustein, Modell), ohne neue Schema-Version.
- Abruf: nur bei Internet über ein vorgeschaltetes Gerät (festgelegt oder erkannt), im eigenen 10-Minuten-Takt im
  Hintergrund, getrennt von der Sperre der Box (anderes Gerät), nie zweimal zugleich und nie neben der Diagnose (eine
  Sperre). Liefert das Gerät Funkwerte, gelten sie als `Stand.mobil` (Herkunft `modem`): Reiter Internet, die
  vorhandenen Mobilfunk-Entitäten, Journal (Zellwechsel, Neueinwahl) und Momentaufnahme. Werte gelten 22 Minuten, danach
  „nicht verfügbar“. Neu als Entitäten nur, was das Modem zusätzlich liefert: SINR (Anker, 5G) und Band.
- Befunde statt Stille (Texte von der Integration): nicht gefunden, nicht erreichbar, Kennwort fehlt, abgelehnt,
  gesperrt, keine Funkwerte, nicht unterstützt, Integration fehlt, Glasfaser-Modem. Abgelehnt: der Hash von Adresse und
  Kennwort bleibt nur im Speicher; mit diesem Kennwort keine weitere Anmeldung, bis ein anderes hinterlegt ist
  (Reparatur-Hinweis sofort). Nicht erreichbar: Reparatur-Hinweis erst nach zwei Takten (kein Flattern).
- Außenkontakt: nur das vorgeschaltete Gerät im eigenen Heimnetz (private Adresse). Sicherheit wie in WU-0008, dazu für
  die Bibliotheken eine eigene requests-Session, deren Adapter jede Anfrage an eine andere Adresse ablehnt und die
  Antwortgröße begrenzt; Weiterleitungen nur innerhalb derselben Adresse (HiLink leitet „/“ weiter). Das hinterlegte
  Kennwort nimmt die Diagnose für die gespeicherte oder – ohne gespeicherte – die gefundene Adresse.
- Pflicht-Abhängigkeiten (Herbert, 28.10.2026): `huawei-lte-api` und `tplinkrouterc6u` stehen in `manifest.json`
  und werden bei jeder Installation mitinstalliert, auch ohne vorgeschaltetes Gerät. Folge: Scheitert pip (Index,
  Plattform), lädt Heimnetz nicht. Importiert werden sie erst, wenn ein solches Gerät gelesen wird.
- Anmeldefehler unterscheiden: angenommen / abgelehnt / Fehler (Netz, keine lesbare Antwort, Fehlercode der
  Schnittstelle). Nur „abgelehnt“ setzt den Merker; bei Werten aus einer HA-Integration gibt es keinen. Die Diagnose
  meldet sich nicht selbst an, wenn die passende HA-Integration eingerichtet ist, und nimmt ein als abgelehnt
  gemerktes hinterlegtes Kennwort nicht noch einmal – nur ein frisch eingetipptes.
- Zusatz-Entitäten (SINR Anker/5G, Band) je Wert erst, wenn genau dieser Wert einmal geliefert wurde (Gedächtnis
  `modem_werte`). ZTE ubus: PCI und Zellkennung nur mit Ziffern dezimal, sonst hexadezimal; TAC aus `lac_code`
  (dezimal); aktives LTE-Band aus `wan_active_band` bzw. dem ersten Eintrag von `lteca` – `lte_band` ist dort die
  Liste der freigegebenen Bänder (am G5TC bestätigt, GitHub #2, 31.10.2026). Dauer aus Huawei LTE (CurrentConnectTime)
  nach der Einheit der Entität in Sekunden.
- Ungetestet am Gerät: alle Bausteine sind nach öffentlicher Doku und erfundenen Antworten gebaut; echte Rohdaten
  über 🔬 Diagnose bessern sie nach.

## Warnungen und eigene Arten (Herbert, 28.10.2026, WU-0010)

- Mockups `netzwerk.html` · Warnungen und · Eigene Arten abgenommen 28.10.2026: Fenster ⚙ mit zwei neuen Reitern
  „🏷️ Arten“ und „🔔 Warnungen“ nach WLAN (beide nur Admins); im Fenster eines Geräts die Auswahl „Art“ mit den eigenen
  Arten und „＋ eigene Art …“ sowie die Zeile „🔔 Bei offline warnen“ (wie Gruppe · immer · nie).
- **Zweite Ausnahme von „die Integration liest nur“** (Herbert, 28.10.2026): Nachrichten über notify-Dienste von Home
  Assistant. Ziel ist ein notify-Dienst (Companion App), „alle Companion Apps“ (alle `notify.mobile_app_*`) oder
  „keine“ (nur Ereignis); ab Werk „keine“ – nach außen geht erst etwas, wenn der Admin ein Ziel wählt. Die Companion
  App stellt über den Push-Dienst von Google bzw. Apple zu, der Text enthält Gerätename, IP und Verbindung – das
  steht im README und im Reiter. Zusätzlich feuert jede Meldung immer das Ereignis `heimnetz_warnung` (art
  offline/online/neu/internet/test, geraet, ip, verbindung, dauer in s, nachricht) und schreibt eine Journalzeile.
  Versand im Hintergrund (`notify.<dienst>` mit `title: Heimnetz`, höchstens 30 s je Nachricht); ein Fehler kommt ins
  Protokoll und ins Journal („Warnung nicht zugestellt …“), der Abruf läuft weiter.
- Wer überwacht wird, entscheidet die Integration (`logik/warnungen.py`, ohne HA): Ausnahme des Geräts (immer/nie) vor
  dem Schalter seiner Art. Vorgabe je Art: an für Netzwerk, Smart Home, Haushalt & Roboter, Kameras; aus für Computer,
  Drucker, Fernseher & Musik, Unbekannt, **Handy & Tablet** (Hinweis „ausgenommen – gehen unterwegs dauernd offline“)
  und neue eigene Arten. Gespeichert werden nur Abweichungen von der Vorgabe.
- Zustand je Gerät (nur im Speicher): online → weg seit t → nach der Verzögerung (2/5/15/60 min, Vorgabe 5) genau
  einmal „offline gemeldet“ → bei Rückkehr „wieder online“ mit Dauer, nur wenn vorher gemeldet. Zurück vor Ablauf =
  keine Meldung (kein Flattern). Ein nicht überwachtes Gerät geht beim Verschwinden still auf „aus“; wird es später
  überwacht, meldet es sich erst nach einmal online – Einschalten einer Art löst keine Welle aus.
- Neustart: kein Zustand wird gespeichert; den Grundzustand übernimmt der erste Abruf mit Gerätetabelle der Box,
  offline gilt dann als „aus“ – keine Massenmeldung. Box nicht erreichbar: keine Gerätemeldungen (alle wären weg), der
  Zustand bleibt stehen. Box oder Internet (Prüfung vom Pi) weg zählt als Ausfall; gemeldet wird er erst, wenn beides
  wieder geht (Push braucht Internet), mit Dauer und nur, wenn er mindestens so lang war wie die Verzögerung („FRITZ!Box
  war … nicht erreichbar“, sonst „Internet war … weg“). Gerätemeldungen während eines Internet-Ausfalls: Ereignis und
  Journal sofort, die Nachricht danach (höchstens 20 zurückgehalten; beim Kürzen fällt ein „offline“ mit seinem
  „wieder online“ weg). Zurückgehaltene Nachrichten liegen nur im Speicher – startet Home Assistant während des
  Ausfalls neu, gehen sie verloren (Ereignis und Journal sind schon da).
- Lücken der Gerätetabelle: Ist sie bei erreichbarer Box leer oder kleiner als die Hälfte des letzten vollen Abrufs,
  gilt sie für die Warnungen wie „Box nicht erreichbar“. Ein Gerät, das fehlt, wird erst nach drei vollen Abrufen
  vergessen. Nach einer Lücke oder einem Ausfall der Box zählt die Verzögerung für „weg“ frühestens ab der Rückkehr
  (Schonfrist – nach einem Neustart der Box melden sich Geräte nach und nach).
- Neues unbekanntes Gerät = nicht unter den je gesehenen Geräten. Diese Menge (Hardware-Adressen) liegt im Gedächtnis
  des Abrufs (Schlüssel `bekannt`, ohne neue Version, höchstens 5000, nie aufgeräumt) und wird beim Start mit den
  Geräten des Gedächtnisses (auch aus der Übernahme) und allen mit Verlauf im Journal ergänzt; eine neue Installation
  übernimmt die Geräte des ersten Abrufs ohne Meldung. Höchstens eine Meldung je Gerät. Bei zufälliger privater
  WLAN-Adresse steht in der Nachricht „zufällige Adresse – vermutlich ein bekanntes Handy/Tablet“.
- Der Wächter läuft nur im Event-Loop und nacheinander (Sperre; ein älterer Abruf zählt nicht); im Executor wird nur
  die Art der Geräte bestimmt. Ändernde Aufrufe des Einstellungsdienstes laufen nacheinander (Sperre).
- Texte der Nachrichten in der Sprache der Seite, mit der die Warnungen zuletzt gespeichert wurden (`sprache` in den
  Warn-Einstellungen); Journal in der Sprache von Home Assistant.
- **Eigene Arten**: Symbol (ein Zeichen/Emoji, ab Werk 🏷️) und Name (höchstens 30 Zeichen, eindeutig), höchstens 30;
  Kennung `eigen:<n>` zählt hoch und hängt nicht am Namen (umbenennen). Sie werden nie erkannt, nur selbst zugeordnet,
  und gelten wie die festen (Geräte › nach Art nach den festen, Warnungen). Löschen: Geräte bekommen wieder die
  erkannte Art, der Schalter dieser Art unter Warnungen fällt weg.
- Speicher: eigene Arten (`eigene_arten`) und Warnungen (`warnungen`: Ziel, Verzögerung, Schalter je Art, Ausnahmen je
  Geräte-Kennung, Schalter, Sprache) als weitere Schlüssel im Einstellungsdienst – ohne neue Version, damit der Rückweg
  (`ausliefern.py --zurueck`) weiter lädt; die ältere Fassung lässt Zuordnungen zu eigenen Arten beim Laden fallen und
  verliert beides, sobald sie speichert. Namen eigener Arten sind Daten des Nutzers: nie im Repo oder unter /local, in
  der Diagnose geschwärzt; die Diagnose nennt vom Ziel nur die Art (keine/alle/Companion App/Dienst), nie den
  Dienstnamen (er enthält den Gerätenamen).
- WebSocket-Befehle nur für Admins: `heimnetz/arten`, `art/neu` (auf Wunsch gleich einem Gerät zugeordnet),
  `art/aendern`, `art/loeschen`, `warnungen`, `warnungen/setzen`, `warnungen/geraet`, `warnungen/test`. Zählungen,
  Auswahl der Ziele und das Beispiel liefert die Integration; die Seite zeigt nur an.

## Offene Entscheidungen

- Keine.
