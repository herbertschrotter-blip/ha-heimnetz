# Heimnetz

**Deutsch** · [English](#english)

Home-Assistant-Integration, die zeigt, wie es dem Heimnetz und dem Internetzugang geht: Gesamtstand und Befunde,
Speedtest-Auswertung, Geräte, WLAN und Mobilfunk, Datenverbrauch und das Protokoll der FRITZ!Box – auf einer eigenen
Seite in der Seitenleiste und als Entitäten für Automationen und Dashboards.

> **Für wen:** FRITZ!Box mit Mobilfunk (LTE/5G), getestet mit der **FRITZ!Box 6860 5G**. Ausgelegt für
> **Österreich** (Betreibernamen, OpenCellID-Datenabzug für Österreich, Kartenkacheln von basemap.at). Andere Boxen
> und Länder funktionieren teilweise, sind aber nicht getestet – siehe [Ausblick](#ausblick). DSL, Glasfaser und Kabel
> zeigt der Reiter Internet mit dem, was die Box über TR-064 meldet (ab 0.26.0, ohne eigene Box getestet). Ein
> vorgeschaltetes Modem (ZTE, Huawei, TP-Link) liest Heimnetz ab 0.27.0 selbst – Beta, ungetestet am Gerät.
>
> Hobbyprojekt, **ohne Gewähr**. Die Integration liest nur: Sie ändert keine Einstellungen der FRITZ!Box und steuert
> keine Geräte. Ausnahmen: Sie startet Speedtest-Messungen über die Ookla-Integration und meldet sich mit dem
> hinterlegten Kennwort an der Weboberfläche eines vorgeschalteten Modems an (nur zum Lesen).

## Schnelleinrichtung

**Muss** = ohne das läuft Heimnetz nicht · **Soll** = empfohlen · **Kann** = optional. Einzelheiten stehen unter
[Voraussetzungen](#voraussetzungen), [Installation](#installation) und [Einrichtung](#einrichtung).

1. **Muss:** Home Assistant ab 2026.10.1 und [HACS](https://hacs.xyz) ([Anleitung](https://hacs.xyz/docs/use/)).
2. **Muss:** FRITZ!Box Tools einrichten – mit einem Box-Benutzer, der über TR-064 zugreifen darf (in der Box
   „Zugriff für Anwendungen zulassen“ an).
   [![FRITZ!Box Tools einrichten](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=fritz)
3. **Muss:** Heimnetz über HACS herunterladen (benutzerdefiniertes Repository, Kategorie Integration), danach Home
   Assistant neu starten.
   [![In HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=herbertschrotter-blip&repository=ha-heimnetz&category=integration)
4. **Muss:** Integration hinzufügen → Heimnetz → FRITZ!Box wählen.
   [![Heimnetz einrichten](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=heimnetz)
5. **Soll:** [Ookla Speedtest](https://my.home-assistant.io/redirect/hacs_repository/?owner=soulripper13&repository=hass-speedtest-ookla&category=integration)
   aus HACS (herunterladen, neu starten, [einrichten](https://my.home-assistant.io/redirect/config_flow_start/?domain=ookla_speedtest)),
   [Met.no](https://my.home-assistant.io/redirect/config_flow_start/?domain=met) und
   [Holiday](https://my.home-assistant.io/redirect/config_flow_start/?domain=holiday) einrichten.
6. **Kann:** OpenCellID-Schlüssel ([opencellid.org](https://opencellid.org)) in den Optionen von Heimnetz eintragen;
   Langzeitarchiv mit [Scribe](https://my.home-assistant.io/redirect/hacs_repository/?owner=jonathan-gtd&repository=scribe&category=integration)
   (HACS) oder InfluxDB.

Danach zeigt **⚙ → 🧩 Einrichtung** auf der Seite Heimnetz, was eingerichtet ist und was noch fehlt – mit Knöpfen, die
Home Assistant oder HACS an der richtigen Stelle öffnen.

## Was Heimnetz kann

| Reiter | Inhalt |
|--------|--------|
| **Übersicht** | Gesamtstand (In Ordnung / Hinweise / Störung / FRITZ!Box nicht erreichbar), offene Befunde (z. B. doppelte IP-Adresse, zweiter DHCP-Server, kein Internet), Prüfungen vom Home-Assistant-Rechner aus (Box, Internet, Namensauflösung, DHCP-Test) |
| **Speedtest** | Messungen der Ookla-Integration mit Grundlast im Netz, Raster nach Wochentag und Stunde, Tagesverlauf, Vergleich mit dem Tarif, Messplan und Serien-Messungen |
| **Geräte** | Geräte im Heimnetz nach Verbindung oder Art, neu / online / offline, IP-Wechsel, Verlauf je Gerät; Umschalter **WLAN** (Bänder, Empfang je Gerät, Kanalwechsel, Hinweise) |
| **Internet** | Woher das Internet kommt (erkannt oder unter ⚙ → 🌐 Zugang festgelegt) und die Werte dazu: **Mobilfunk** (Technik, Zellen, Signal, Neueinwahlen, Karte zum Mast), **DSL** (Synchronrate, Störabstandsmarge, Dämpfung, Fehler, Neusynchronisierungen), **Glasfaser** (Lichtleistung mit dem guten Bereich laut Box), **Kabel** (nur die Geschwindigkeit – Kanäle und Pegel gibt die Box über TR-064 nicht heraus), **Ersatzzugang** über einen Mobilfunk-Stick; bei einem **vorgeschalteten Modem** (ZTE, Huawei, TP-Link, Beta) dessen Funkwerte mit Herkunft „vom vorgeschalteten Modem“ |
| **Verbrauch** | Datenmenge je Tag aus den Zählern von FRITZ!Box Tools |
| **Protokoll** | Journal der Integration und Ereignisprotokoll der Box, mit Suche und Filter |

Dazu: Melden-Knopf für Fehler und Wünsche (lokal, auf Wunsch auch öffentlich auf GitHub), Diagnose-Download ohne
private Daten, Deutsch und Englisch.

## Voraussetzungen

### Muss – ohne das läuft Heimnetz nicht

| Was | Wofür | Ohne |
|-----|-------|------|
| **Home Assistant ab 2026.10.1**, als Home Assistant OS oder Container (Linux) | Grundlage | Installation nicht möglich (HACS lehnt ältere Fassungen ab) |
| **[HACS](https://hacs.xyz)** | Installieren und Aktualisieren | nur manuell installierbar (Ordner `custom_components/heimnetz` kopieren) |
| **FRITZ!Box** im Heimnetz, mit Mobilfunk für die Mobilfunk-Teile | Quelle aller Netzdaten | – |
| **Integration „FRITZ!Box Tools“** (in Home Assistant enthalten) eingerichtet – mit einem Box-Benutzer, der über TR-064 zugreifen darf (Recht „FRITZ!Box Einstellungen“; in der Box „Heimnetz → Netzwerk → Netzwerkeinstellungen → Zugriff für Anwendungen zulassen“ eingeschaltet) | Heimnetz benutzt deren Zugang mit und fragt nicht noch einmal nach dem Kennwort | Einrichtung bricht ab („Zuerst die Integration FRITZ!Box Tools einrichten“); Reparatur-Hinweis, wenn sie später fehlt oder die Anmeldung abgelehnt wird |
| **Recorder** aktiv (Standard in Home Assistant) | Verlauf, Verbrauch je Tag, Mobilfunk-Verlauf, Momentaufnahme zur Messung | Reiter Verbrauch und die Verläufe zeigen „keine Daten“; Reparatur-Hinweis |

### Soll – empfohlen

| Was | Wofür | Ohne |
|-----|-------|------|
| **[Ookla Speedtest](https://github.com/soulripper13/hass-speedtest-ookla)** aus HACS (als benutzerdefiniertes Repository) | misst die Geschwindigkeit; Heimnetz liest die Ergebnisse und startet Messungen nach seinem Messplan | kein Speedtest: der Reiter zeigt einen Hinweis, alles andere läuft normal |
| **Met.no** (Wetter, in Home Assistant enthalten; meist schon als „Home“ eingerichtet) | Wetter in der Momentaufnahme jeder Messung | Momentaufnahme ohne Wetter |
| **Holiday** (Feiertags-Kalender, in Home Assistant enthalten) für das eigene Land | Werktag / Wochenende / Feiertag in der Momentaufnahme | nur Werktag / Wochenende |

### Kann – optional

| Was | Wofür | Ohne |
|-----|-------|------|
| **OpenCellID-Schlüssel** (kostenlos auf [opencellid.org](https://opencellid.org)), unter Geräte & Dienste → Heimnetz → Konfigurieren | genauere Karte zum Mast; einmal im Monat der Zell-Abzug für Österreich | Standort der Zellen nur aus BeaconDB und OpenStreetMap |
| **[Scribe](https://github.com/jonathan-gtd/scribe)** (HACS) mit **TimescaleDB** oder ein anderes Langzeitarchiv (z. B. InfluxDB) | Werte der Entitäten über Jahre aufheben | der Recorder hält den Verlauf nur so lange, wie er eingestellt ist (Standard 10 Tage); Messungen und Journal in Heimnetz bleiben trotzdem |
| **Kennwort der Weboberfläche** eines vorgeschalteten Modems, unter ⚙ → 🌐 Zugang (nur bei Internet über ein eigenes Modem vor der Box) | Funkwerte vom Modem im Reiter Internet und in den Mobilfunk-Entitäten | die meisten Modems geben ohne Anmeldung keine Signalwerte heraus; Befund „Kennwort fehlt“ |
| Integration **Huawei LTE**, **NETGEAR LTE** oder **Teltonika** (in Home Assistant enthalten) für das Modem davor | Heimnetz liest deren Entitäten, statt das Gerät selbst zu fragen | Huawei fragt Heimnetz selbst (mit Kennwort); NETGEAR und Teltonika nur erkennen |

## Installation

1. HACS → ⋮ → **Benutzerdefinierte Repositories** → `https://github.com/herbertschrotter-blip/ha-heimnetz`,
   Kategorie **Integration** → Hinzufügen.
2. „Heimnetz“ in HACS öffnen → **Herunterladen**.
3. Home Assistant neu starten.
4. Empfohlen: genauso Ookla Speedtest installieren und einrichten (siehe oben).

## Einrichtung

Einstellungen → Geräte & Dienste → **Integration hinzufügen** → „Heimnetz“ → FRITZ!Box wählen (die Einrichtung von
FRITZ!Box Tools). Danach erscheint „Heimnetz“ in der Seitenleiste. Eine Einrichtung je Haushalt.

- **Einstellungen der Seite** (⚙, nur Administratoren): Tarif Download/Upload, Auswerten ab, Grenze für schwachen
  WLAN-Empfang, Messplan. Der Reiter **🧩 Einrichtung** zeigt, welche Voraussetzungen eingerichtet sind und was fehlt
  (Punkt am Reiter: orange = Empfohlenes fehlt, rot = Nötiges fehlt); Heimnetz installiert dabei nichts selbst.
- **Optionen der Einrichtung** (Geräte & Dienste → Heimnetz → Konfigurieren): OpenCellID-Schlüssel.

## Aktualisieren

Neue Fassungen erscheinen als [Release](https://github.com/herbertschrotter-blip/ha-heimnetz/releases) mit den
Änderungen aus dem [CHANGELOG](CHANGELOG.md). HACS zeigt sie als Update an: Update installieren, Home Assistant neu
starten. Danach im Browser die Seite neu laden, falls noch die alte Seite angezeigt wird.

## Entfernen

1. Einstellungen → Geräte & Dienste → Heimnetz → ⋮ → **Löschen**.
2. HACS → Heimnetz → ⋮ → **Entfernen**, Home Assistant neu starten.
3. Wer auch die Daten loswerden will: Ordner `<config>/heimnetz/` löschen (Messungen, Journal, Tickets). Die Tickets
   im Speicher von Home Assistant bleiben beim Löschen der Einrichtung absichtlich erhalten.

## Umstieg von „Netzwerk“

Bis 0.22.0 hieß die Integration „Netzwerk“ (Domain `netzwerk`). Heimnetz übernimmt beim ersten Start Messungen,
Journal, Einstellungen und Tickets – die Reihenfolge ist wichtig: [docs/umstieg.md](docs/umstieg.md).

## Speedtest und Datenvolumen

Gemessen wird von Ookla; Heimnetz liest die Ergebnisse und löst Messungen nach seinem Messplan aus. Eine neue
Installation misst zurückhaltend **4-mal am Tag** (alle 6 Stunden); ändern unter ⚙ → Messplan (Takt, Zeitfenster,
Verhalten bei Verkehr im Netz).

Jede Messung kostet Datenvolumen – etwa (Download + Upload in Mbit/s) × 12 s / 8. Bei schnellen Anschlüssen sind das
einige hundert MB, z. B. 150/30 Mbit/s ≈ 270 MB je Messung, 4-mal am Tag rund 32 GB im Monat. **Bei Mobilfunk mit
Datenlimit lieber selten messen.** Die Einstellungen zeigen die Schätzung für den eigenen Plan.

Eine einzelne Messung (z. B. eine Fehlmessung) löschen Admins im Fenster der Messung (Tipp auf eine Zeile in „Letzte
Messungen“ → „🗑 Messung löschen“). Sie verschwindet aus Raster, Tagesverlauf, Auswertung und dem Sensor „Letzte
Messung“; gelöscht wird nur in Heimnetz, der Verlauf der Ookla-Entitäten in Home Assistant bleibt.

## Datenschutz

Heimnetz arbeitet lokal. Nach außen geht nur:

| Wohin | Was | Wann |
|-------|-----|------|
| [BeaconDB](https://beacondb.net) | Kennung der Mobilfunkzelle (Netz, Gebiet, Zelle) | neue Zelle, für die Karte zum Mast |
| [OpenCellID](https://opencellid.org) | Kennung der Zelle; Abruf des Zell-Abzugs für Österreich | nur mit eingetragenem Schlüssel; Abzug einmal im Monat |
| OpenStreetMap (Overpass) | Ausschnitt auf festem Raster (etwa 44 × 30 km) für die Funkmasten; grenzt die Wohnung nur auf einen Block von etwa 22 × 15 km ein | einmal im Monat |
| Cloudflare (1.1.1.1) und Google (8.8.8.8), Port 443 | nur Verbindungsaufbau, keine Daten (Prüfung „Pi → Internet“) | jede Minute |
| DNS-Server des eigenen Netzes | Auflösung von `avm.de` (Prüfung „Namensauflösung“) | jede Minute |
| basemap.at oder OpenStreetMap | Kartenkacheln – lädt der **Browser**, nicht die Integration | beim Ansehen der Karte |
| GitHub | vorausgefülltes Issue – öffnet der **Browser**, abgeschickt mit dem eigenen Konto | nur, wenn man selbst „öffentlich auf GitHub“ meldet |
| Vorgeschaltetes Gerät im eigenen Heimnetz (nur private Adressen) | Suche: Startseite an wenigen Adressen nacheinander (gespeicherte, Vorschlag der Box, 192.168.0.1, 192.168.1.1, 192.168.8.1, 192.168.18.1, 192.168.100.1) bis ein Gerät erkannt ist; danach nur lesende Abfragen und die Anmeldung mit dem hinterlegten Kennwort (höchstens ein Versuch, abgelehnt: kein weiterer) | nur bei Internet über ein vorgeschaltetes Gerät: alle 10 Minuten, beim Einrichten, bei „↻ Erneut suchen“ und unter ⚙ → Diagnose „Abfragen“ |

**Vorgeschaltetes Gerät** (Beta): Kommt das Internet über ein eigenes Modem vor der FRITZ!Box, kennt die Box das
Funknetz nicht. Heimnetz sucht das Gerät dann an den oben genannten Adressen (kein Absuchen des Heimnetzes), erkennt
Hersteller und Schnittstelle an der Startseite und liest im 10-Minuten-Takt die Funkwerte (Technik, Band, Zellen mit
Kennung/PCI/TAC/Netz, RSRP/RSRQ/SINR, 5G, Betreiber, verbunden seit) – in den Reiter Internet, die Mobilfunk-Entitäten
und die Momentaufnahme jeder Messung. Nur lesende Abfragen; keine Einstellung des Modems wird geändert. Antwortet es
nicht oder lehnt es das Kennwort ab, steht ein Befund im Reiter und unter Einstellungen → Reparaturen. Die Werte
bleiben in Home Assistant; die Zellkennung geht – wie bei der Box – nur für die Karte zum Mast an BeaconDB/OpenCellID.

| Gerät | Schnittstelle | Werte | Stand |
|-------|---------------|-------|-------|
| ZTE (MC801A, MF289F und ähnliche) | goform (Weboberfläche) | ja | ungetestet am Gerät |
| ZTE (G5TS, G5TC und ähnliche) | ubus (JSON-RPC der Weboberfläche) | ja | ungetestet am Gerät |
| Huawei HiLink (B535, B818, E5xxx, 5G CPE …) | Bibliothek huawei-lte-api oder Integration Huawei LTE | ja | ungetestet am Gerät |
| TP-Link LTE/5G (Archer MR-, NX-Serie, M-Serie) | Bibliothek tplinkrouterc6u | Signal, Netz, Betreiber (keine Zellkennung) | ungetestet am Gerät |
| NETGEAR LTE, Teltonika | Integration von Home Assistant, wenn eingerichtet | Signal, Band, Betreiber | ungetestet am Gerät |
| MikroTik, Sagemcom, Nokia FastMile, Zyxel 5G | – | nur erkennen | Rohdaten über 🔬 Diagnose schicken |
| Glasfaser-Modem (ONT) von Nokia, Huawei, Zyxel | – | nur erkennen | ein ONT am Internet-Anschluss der Box ist vom Heimnetz aus oft nicht erreichbar |

Neue Abhängigkeiten dafür (installiert Home Assistant aus `manifest.json`): `huawei-lte-api` ≥ 1.11.0 (LGPL-3.0, dieselbe
wie die Integration Huawei LTE) und `tplinkrouterc6u` ≥ 5.37.0 (GPL-3.0, Projekt
[AlexandrErohin/TP-Link-Archer-C6U](https://github.com/AlexandrErohin/TP-Link-Archer-C6U); wird nur installiert, nicht
im Repo mitgeliefert). Beide sind Pflicht-Abhängigkeiten: Kann Home Assistant sie nicht installieren, lädt Heimnetz
nicht. Benutzt werden sie nur bei einem solchen Gerät.

Die **Diagnose** (⚙ → 🔬 Diagnose, Beta) zeigt erkannten Hersteller und Schnittstelle und die Rohdaten aller passenden
Schnittstellen geschwärzt an (die Zellkennung bleibt, IMEI, Kennwort, Rufnummer und Adressen nicht), damit man sie dem
Entwickler schicken kann – für Geräte, die Heimnetz noch nicht ausliest. Heimnetz sendet selbst nichts; ein dort
eingetipptes Kennwort wird nur für die Abfrage verwendet und nicht gespeichert (leer gelassen, nimmt Heimnetz das unter
🌐 Zugang für die gespeicherte bzw. gefundene Adresse hinterlegte).

**Zugang** (⚙ → 🌐 Zugang): Woher das Internet kommt, liest Heimnetz bei der FRITZ!Box (TR-064, alle 10 Minuten) und –
nur bei einem vorgeschalteten Gerät – an dessen wenigen Adressen; der Beleg lautet z. B. „192.168.0.1 antwortet: ZTE G5TC
(ubus)“. Zur Wahl steht auch „Glasfaser über ein eigenes Modem“ (ONT). Wer ein vorgeschaltetes Modem festlegt, kann dessen Adresse (nur private Adressen) und
das Kennwort der Weboberfläche eintragen. **Das Kennwort wird in Home Assistant gespeichert** (in den Optionen der
Heimnetz-Einrichtung, wie bei anderen Integrationen), nie an die Seite zurückgegeben (sie zeigt nur „hinterlegt“), nie
protokolliert und in der Diagnose geschwärzt; „Kennwort entfernen“ löscht es.

**Nie** gehen hinaus: der Standort von Home Assistant, Kennwörter, Gerätenamen, Hardware- (MAC) und IP-Adressen. Der
Zugang zur Box bleibt in FRITZ!Box Tools und wird von Heimnetz nicht gespeichert. Die **Diagnose** (Geräte & Dienste →
Heimnetz → ⋮ → Diagnose herunterladen) enthält nur Zahlen und den groben Stand (Versionen, Box-Modell, FRITZ!OS,
Netztechnik, Ookla, Messplan); Zugangsdaten, Schlüssel, Zellkennungen, TAC/PCI, Koordinaten, Gerätenamen und Adressen
werden geschwärzt – auch in Fehlermeldungen.

## Fehler melden

Knopf unten rechts auf der Seite: Art (Fehler, Wunsch, Anregung), Text, bis zu 3 Screenshots (am Handy aus der
Galerie, am PC auch mit Strg+V).

- **Senden** speichert die Meldung lokal (`<config>/heimnetz/meldungen.json`, `meldungen.md`, Bilder unter
  `<config>/heimnetz/meldungen/`); sie steht unter ⚙ → Meldungen.
- **Senden + öffentlich auf GitHub ↗** speichert lokal und öffnet zusätzlich ein vorausgefülltes Issue. Eine Vorschau
  zeigt genau, was hinausgeht: der Text und ein grober Stand (Versionen, Reiter, Gerät, Box-Modell und FRITZ!OS,
  Netztechnik, Ookla ja/nein, lokale Ticketnummer). Zell- und Signaldaten nur mit dem Schalter „Zell- und Signaldaten
  mitsenden“ – daraus lässt sich der Wohnort eingrenzen. Adressen, Koordinaten, Kennwörter und bekannte Gerätenamen
  sowie Zellkennungen (auch TAC/PCI) werden auch im Text geschwärzt; das ist musterbasiert, also die Vorschau lesen. Bilder gehen über den Link nicht
  mit – auf GitHub selbst einfügen. Abgeschickt wird mit dem eigenen GitHub-Konto; Heimnetz hat keinen Token.

Alternativ direkt: [Issues](https://github.com/herbertschrotter-blip/ha-heimnetz/issues).

## Sprache

Deutsch und Englisch. Die Seite folgt der Sprache im eigenen Profil von Home Assistant und schickt sie bei jeder
Abfrage mit; was die Integration für die Seite aufbereitet (Befunde, Fehlermeldungen, Vorschau des Issues), kommt in
dieser Sprache. Was der Abruf im Hintergrund erzeugt und speichert (Journal, Fehler beim Lesen der Box) und die Texte
von Entitäten und Einrichtung folgen der Sprache des Systems (Einstellungen → System → Allgemein). `de` und seine
Varianten ergeben Deutsch, alles andere Englisch. Was schon im Journal steht, bleibt in seiner Sprache.

## Entitäten

Alle unter dem Gerät „Heimnetz“. Die Entitäts-ID entsteht beim Einrichten aus dem Namen in der Sprache des Systems
(Deutsch z. B. `sensor.heimnetz_gesamtstand`, Englisch `sensor.heimnetz_overall_state`).

| Entität (Deutsch) | Inhalt |
|-------------------|--------|
| `sensor.heimnetz_gesamtstand` | In Ordnung, Hinweise, Störung, FRITZ!Box nicht erreichbar |
| `sensor.heimnetz_offene_befunde` | Anzahl offener Befunde |
| `sensor.heimnetz_gerate_online` | Geräte im Heimnetz, die gerade online sind |
| `sensor.heimnetz_letzte_messung` | Zeitpunkt der letzten Speedtest-Messung; Messwerte und Momentaufnahme als Attribute |
| `sensor.heimnetz_mobilfunk_technik` | Zugangstechnik laut Box (z. B. LTE, 5G NSA) |
| `sensor.heimnetz_signalstarke_4g_anker` / `_signalqualitat_4g_anker` | RSRP (dBm) / RSRQ (dB) der 4G-Ankerzelle |
| `sensor.heimnetz_signalstarke_5g` / `_signalqualitat_5g` | RSRP / RSRQ der 5G-Zelle |
| `sensor.heimnetz_mobilfunkzelle` | Ankerzelle |
| `sensor.heimnetz_entfernung_zur_basisstation` | Entfernung laut Box |
| `sensor.heimnetz_nachbarzellen` | Anzahl sichtbarer Nachbarzellen |
| `sensor.heimnetz_5g_zelle_pci` | PCI der 5G-Zelle |
| `sensor.heimnetz_signal_rausch_abstand_4g_anker` / `_signal_rausch_abstand_5g` | SINR (dB) – nur von einem vorgeschalteten Modem |
| `sensor.heimnetz_mobilfunk_band` | genutzte Bänder, z. B. „B3 · n78“ – nur von einem vorgeschalteten Modem |
| `sensor.heimnetz_internetzugang` | Zugangsart: Mobilfunk, DSL, Glasfaser, Kabel oder vorgeschaltetes Gerät (erkannt oder festgelegt) |
| `sensor.heimnetz_dsl_synchronrate_download` / `_upload` | DSL-Synchronrate (Mbit/s) |
| `sensor.heimnetz_dsl_storabstandsmarge_download` / `_upload` | Störabstandsmarge (dB) |
| `sensor.heimnetz_dsl_dampfung_download` / `_upload` | Dämpfung (dB) |
| `sensor.heimnetz_dsl_fehler_je_stunde` | nicht korrigierbare Fehler (CRC) je Stunde |
| `sensor.heimnetz_glasfaser_empfangene_lichtleistung` / `_gesendete_lichtleistung` | Lichtleistung (dBm) |
| `binary_sensor.heimnetz_fritz_box_vom_pi_aus` | Box vom Home-Assistant-Rechner aus erreichbar |
| `binary_sensor.heimnetz_internet_vom_pi_aus` | Internet vom Home-Assistant-Rechner aus erreichbar |
| `binary_sensor.heimnetz_namensauflosung` | Namensauflösung (DNS) funktioniert |

Die Mobilfunk-Sensoren gibt es nur bei Boxen mit Mobilfunk oder wenn ein vorgeschaltetes Modem Funkwerte geliefert hat
(dann kommen die Werte von dort), die DSL- und Glasfaser-Sensoren nur, wenn das Internet
über diesen Anschluss kommt (sie erscheinen mit dem ersten Lesen). **Langzeitarchiv:** Messungen und Journal hebt Heimnetz
selbst auf (Datenbank `<config>/heimnetz/heimnetz.db`); den Verlauf der Entitäten hält der Recorder nur begrenzt. Wer
Jahre braucht, schreibt die Entitäten mit Scribe (TimescaleDB) oder InfluxDB mit.

## Ausblick

Geplant, aber noch nicht umgesetzt:

- Werte eines **Glasfaser-Modems (ONT)** und weiterer vorgeschalteter Geräte, sobald echte Rohdaten vorliegen.
- Mehr Werte bei **Kabel** und **Glasfaser**, als die Box über TR-064 herausgibt.
- **Weitere Hersteller**, z. B. UniFi.
- **Weitere Länder** (Betreibernamen, Zell-Abzug, Kartenkacheln).
- Aufnahme in die HACS-Standardliste.

## Entwickeln

Die Tests gegen Home Assistant brauchen Python 3.14 und laufen unter Linux (unter Windows in WSL).

```sh
uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python -r requirements-logik.txt
uv pip install --python .venv/bin/python -r requirements-ha.txt
.venv/bin/python -m ruff format --check .
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy
.venv/bin/python -m pytest -q tests/logik
.venv/bin/python -m pytest -q -n auto tests/integration
npm ci --prefix custom_components/heimnetz/frontend
npm test --prefix custom_components/heimnetz/frontend
node custom_components/heimnetz/frontend/bauen.mjs   # Seite bauen, gebaute Datei mitcommitten
```

Auf Home Assistant OS gehört zu beiden `uv pip install` noch `--index-strategy unsafe-best-match`. Die Fachlogik liegt
ohne Home Assistant in `custom_components/heimnetz/logik/` (Tests in `tests/logik`). GitHub Actions führen dieselben
Checks sowie hassfest und die HACS-Prüfung aus; ein Tag `vX.Y.Z` erzeugt ein Release mit dem Abschnitt aus dem
CHANGELOG. Grundentscheidungen: [docs/entscheidungen.md](docs/entscheidungen.md).

Ohne HACS einspielen (Entwicklung): `python ausliefern.py` kopiert `custom_components/heimnetz` in die
Home-Assistant-Konfiguration (ohne `--ziel` in den Ordner zwei Ebenen über dem Projekt, wenn dort eine
`configuration.yaml` liegt) und sichert die vorige Fassung unter `.auslieferung/vorher/`; `python ausliefern.py
--zurueck` stellt sie wieder her. Danach Konfiguration prüfen und neu starten. Tickets lassen sich mit
`python3 tools/ticket.py --help` auf der Kommandozeile bearbeiten.

## Lizenz

[Apache-2.0](LICENSE). Hobbyprojekt, ohne Gewähr – Nutzung auf eigene Verantwortung. Nicht verbunden mit AVM, Ookla
oder Home Assistant. FRITZ!Box ist eine Marke der AVM GmbH.

---

## English

Home Assistant integration that shows how your home network and internet access are doing: overall state and
findings, speed test analysis, devices, Wi-Fi and mobile, data usage and the FRITZ!Box event log – on its own page in
the sidebar and as entities for automations and dashboards.

> **For whom:** FRITZ!Box with mobile broadband (LTE/5G), tested with the **FRITZ!Box 6860 5G**. Designed for
> **Austria** (operator names, OpenCellID export for Austria, map tiles from basemap.at). Other boxes and countries
> partly work but are untested – see [Outlook](#outlook). DSL, fibre and cable are shown in the Internet tab with
> what the box reports via TR-064 (from 0.26.0, not tested with a real box of that kind). From 0.27.0 Heimnetz reads an
> upstream modem (ZTE, Huawei, TP-Link) itself – beta, untested on a real device.
>
> Hobby project, **no warranty**. The integration only reads: it never changes FRITZ!Box settings and controls no
> devices. Exceptions: it starts speed tests through the Ookla integration and logs in to the web interface of an
> upstream modem with the stored password (read-only).

### Quick start

**Must** = Heimnetz does not run without · **Should** = recommended · **Can** = optional. Details are under
[Requirements](#requirements), [Installation](#installation-1) and [Setup](#setup).

1. **Must:** Home Assistant 2026.10.1 or newer and [HACS](https://hacs.xyz) ([guide](https://hacs.xyz/docs/use/)).
2. **Must:** set up FRITZ!Box Tools – with a box user allowed to use TR-064 ("Allow access for applications" switched
   on in the box).
   [![Set up FRITZ!Box Tools](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=fritz)
3. **Must:** download Heimnetz through HACS (custom repository, category Integration), then restart Home Assistant.
   [![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=herbertschrotter-blip&repository=ha-heimnetz&category=integration)
4. **Must:** Add integration → Heimnetz → pick the FRITZ!Box.
   [![Set up Heimnetz](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=heimnetz)
5. **Should:** [Ookla Speedtest](https://my.home-assistant.io/redirect/hacs_repository/?owner=soulripper13&repository=hass-speedtest-ookla&category=integration)
   from HACS (download, restart, [set up](https://my.home-assistant.io/redirect/config_flow_start/?domain=ookla_speedtest)), set up
   [Met.no](https://my.home-assistant.io/redirect/config_flow_start/?domain=met) and
   [Holiday](https://my.home-assistant.io/redirect/config_flow_start/?domain=holiday).
6. **Can:** enter an OpenCellID key ([opencellid.org](https://opencellid.org)) in the Heimnetz options; long-term
   archive with [Scribe](https://my.home-assistant.io/redirect/hacs_repository/?owner=jonathan-gtd&repository=scribe&category=integration)
   (HACS) or InfluxDB.

Then **⚙ → 🧩 Setup** on the Heimnetz page shows what is set up and what is still missing – with buttons that open
Home Assistant or HACS at the right place.

### Features

| Tab | Content |
|-----|---------|
| **Overview** | Overall state (OK / warnings / problem / FRITZ!Box unreachable), open findings (e.g. duplicate IP address, second DHCP server, no internet), checks from the Home Assistant host (box, internet, name resolution, DHCP test) |
| **Speed test** | Ookla measurements with background load, grid by weekday and hour, daily curve, comparison with your plan, test schedule and series |
| **Devices** | Devices by connection or type, new / online / offline, IP changes, history per device; switch **Wi-Fi** (bands, signal per device, channel changes, hints) |
| **Internet** | Where the internet comes from (detected or set under ⚙ → 🌐 Access) and its values: **mobile** (technology, cells, signal, reconnects, map to the mast), **DSL** (sync rate, noise margin, attenuation, errors, resyncs), **fibre** (optical power with the good range reported by the box), **cable** (speed only – the box does not provide channels and levels via TR-064), **backup access** via a mobile stick; with an **upstream modem** (ZTE, Huawei, TP-Link, beta) its radio values, marked “from the upstream modem” |
| **Usage** | Data per day from the FRITZ!Box Tools counters |
| **Log** | Journal of the integration and the box event log, with search and filter |

Plus: a report button for bugs and wishes (stored locally, optionally also public on GitHub), a diagnostics download
without private data, German and English.

### Requirements

#### Must – Heimnetz does not run without

| What | Why | Without |
|------|-----|---------|
| **Home Assistant 2026.10.1 or newer**, as Home Assistant OS or Container (Linux) | base | cannot be installed (HACS refuses older versions) |
| **[HACS](https://hacs.xyz)** | install and update | manual install only (copy `custom_components/heimnetz`) |
| **FRITZ!Box** in your network, with mobile broadband for the mobile parts | source of all network data | – |
| **"FRITZ!Box Tools" integration** (built into Home Assistant) set up – with a box user allowed to use TR-064 (right "FRITZ!Box settings"; in the box "Home Network → Network → Network Settings → Allow access for applications" switched on) | Heimnetz reuses its credentials and never asks for the password again | setup aborts ("Set up the FRITZ!Box Tools integration first"); repair issue if it disappears later or the login is refused |
| **Recorder** active (Home Assistant default) | history, usage per day, mobile history, snapshot per measurement | Usage tab and histories show "no data"; repair issue |

#### Should – recommended

| What | Why | Without |
|------|-----|---------|
| **[Ookla Speedtest](https://github.com/soulripper13/hass-speedtest-ookla)** from HACS (as custom repository) | measures the speed; Heimnetz reads the results and starts tests by its schedule | no speed test: the tab shows a hint, everything else works |
| **Met.no** (weather, built in; usually already set up as "Home") | weather in the snapshot of each measurement | snapshot without weather |
| **Holiday** (holiday calendar, built in) for your country | working day / weekend / holiday in the snapshot | working day / weekend only |

#### Can – optional

| What | Why | Without |
|------|-----|---------|
| **OpenCellID key** (free at [opencellid.org](https://opencellid.org)), under Devices & services → Heimnetz → Configure | more accurate map to the mast; monthly cell export for Austria | cell locations from BeaconDB and OpenStreetMap only |
| **[Scribe](https://github.com/jonathan-gtd/scribe)** (HACS) with **TimescaleDB**, or another long-term store (e.g. InfluxDB) | keep entity values for years | the recorder keeps history only as long as configured (default 10 days); measurements and journal in Heimnetz are kept anyway |
| **Web interface password** of an upstream modem, under ⚙ → 🌐 Access (only when the internet comes through an own modem in front of the box) | radio values from the modem in the Internet tab and in the mobile entities | most modems give no signal values without login; finding “Password missing” |
| Integration **Huawei LTE**, **NETGEAR LTE** or **Teltonika** (built into Home Assistant) for that modem | Heimnetz reads its entities instead of querying the device itself | Heimnetz queries Huawei itself (with password); NETGEAR and Teltonika detection only |

### Installation

1. HACS → ⋮ → **Custom repositories** → `https://github.com/herbertschrotter-blip/ha-heimnetz`, category
   **Integration** → Add.
2. Open "Heimnetz" in HACS → **Download**.
3. Restart Home Assistant.
4. Recommended: install and set up Ookla Speedtest the same way (see above).

### Setup

Settings → Devices & services → **Add integration** → "Heimnetz" → pick the FRITZ!Box (the FRITZ!Box Tools entry).
"Heimnetz" then appears in the sidebar. One setup per household.

- **Page settings** (⚙, administrators only): plan download/upload, evaluate from, weak Wi-Fi threshold, test
  schedule. The **🧩 Setup** tab shows which requirements are set up and what is missing (dot on the tab: orange =
  something recommended is missing, red = something required is missing); Heimnetz installs nothing itself.
- **Integration options** (Devices & services → Heimnetz → Configure): OpenCellID key.

### Updating

New versions are published as [releases](https://github.com/herbertschrotter-blip/ha-heimnetz/releases) with the
changes from the [CHANGELOG](CHANGELOG.md) (written in German). HACS offers them as an update: install, restart Home
Assistant, reload the page in the browser if it still shows the old one.

### Removal

1. Settings → Devices & services → Heimnetz → ⋮ → **Delete**.
2. HACS → Heimnetz → ⋮ → **Remove**, restart Home Assistant.
3. To remove the data as well: delete `<config>/heimnetz/` (measurements, journal, tickets). Tickets in Home
   Assistant's storage are deliberately kept when the setup is deleted.

### Migrating from "Netzwerk"

Up to 0.22.0 the integration was called "Netzwerk" (domain `netzwerk`). Heimnetz takes over measurements, journal,
settings and tickets on first start – the order matters: [docs/umstieg.md](docs/umstieg.md) (German).

### Speed tests and data volume

Ookla measures; Heimnetz reads the results and triggers tests by its schedule. A new installation measures modestly
**4 times a day** (every 6 hours); change it under ⚙ → Schedule (interval, time window, behaviour under network
load).

Each test uses data – roughly (download + upload in Mbit/s) × 12 s / 8. On fast lines that is a few hundred MB, e.g.
150/30 Mbit/s ≈ 270 MB per test, 4 times a day about 32 GB a month. **On mobile plans with a data cap, test rarely.**
The settings show the estimate for your schedule.

Admins delete a single test (e.g. a failed one) in the test's window (tap a row in "Recent measurements" → "🗑 Delete
measurement"). It disappears from the grid, daily profile, analysis and the "Last measurement" sensor; it is deleted in
Heimnetz only, the history of the Ookla entities in Home Assistant stays.

### Privacy

Heimnetz works locally. Only this leaves your network:

| Where | What | When |
|-------|------|------|
| [BeaconDB](https://beacondb.net) | mobile cell identifier (network, area, cell) | new cell, for the map to the mast |
| [OpenCellID](https://opencellid.org) | cell identifier; download of the cell export for Austria | only with a key; export once a month |
| OpenStreetMap (Overpass) | area on a fixed grid (about 44 × 30 km) for radio masts; narrows your home down only to a block of about 22 × 15 km | once a month |
| Cloudflare (1.1.1.1) and Google (8.8.8.8), port 443 | connection setup only, no data (check “Pi → Internet”) | every minute |
| DNS server of your network | lookup of `avm.de` (check “Name resolution”) | every minute |
| basemap.at or OpenStreetMap | map tiles – loaded by the **browser**, not the integration | when viewing the map |
| GitHub | prefilled issue – opened by the **browser**, submitted with your own account | only when you report "publicly on GitHub" yourself |
| Upstream device in your own home network (private addresses only) | search: home page at a few addresses (stored one, box suggestion, 192.168.0.1, 192.168.1.1, 192.168.8.1, 192.168.18.1, 192.168.100.1) until a device is recognised; then read-only queries and the login with the stored password (at most one attempt; rejected: no further attempt) | only with internet via an upstream device: every 10 minutes, at setup, on “↻ Search again” and under ⚙ → Diagnostics “Query” |

**Upstream device** (beta): if the internet comes through an own modem in front of the FRITZ!Box, the box does not
know the mobile network. Heimnetz then looks for the device at the addresses above (no scanning of the home network),
recognises maker and interface from its home page and reads the radio values every 10 minutes (technology, band, cells
with ID/PCI/TAC/network, RSRP/RSRQ/SINR, 5G, operator, connected since) – into the Internet tab, the mobile entities and
the snapshot of each measurement. Read-only queries; no modem setting is changed. If it does not answer or rejects the
password, a finding shows in the tab and under Settings → Repairs. The values stay in Home Assistant; as with the box,
only the cell ID goes to BeaconDB/OpenCellID for the map to the mast.

| Device | Interface | Values | Status |
|--------|-----------|--------|--------|
| ZTE (MC801A, MF289F and similar) | goform (web interface) | yes | untested on a real device |
| ZTE (G5TS, G5TC and similar) | ubus (JSON-RPC of the web interface) | yes | untested on a real device |
| Huawei HiLink (B535, B818, E5xxx, 5G CPE …) | library huawei-lte-api or the Huawei LTE integration | yes | untested on a real device |
| TP-Link LTE/5G (Archer MR, NX series, M series) | library tplinkrouterc6u | signal, network, operator (no cell ID) | untested on a real device |
| NETGEAR LTE, Teltonika | Home Assistant integration, if set up | signal, band, operator | untested on a real device |
| MikroTik, Sagemcom, Nokia FastMile, Zyxel 5G | – | detection only | send raw data via 🔬 Diagnostics |
| Fibre modem (ONT) from Nokia, Huawei, Zyxel | – | detection only | an ONT on the internet port of the box is often not reachable from the home network |

New dependencies for this (installed by Home Assistant from `manifest.json`): `huawei-lte-api` ≥ 1.11.0 (LGPL-3.0, the
same as the Huawei LTE integration) and `tplinkrouterc6u` ≥ 5.37.0 (GPL-3.0, project
[AlexandrErohin/TP-Link-Archer-C6U](https://github.com/AlexandrErohin/TP-Link-Archer-C6U); only installed, not shipped in
this repository). Both are required dependencies: if Home Assistant cannot install them, Heimnetz does not load. They
are used only with such a device.

The **Diagnostics** tab (⚙ → 🔬 Diagnostics, beta) shows the detected maker and interface and the raw data of all
matching interfaces, redacted (the cell ID stays; IMEI, password, phone number and addresses do not), so you can send
it to the developer – for devices Heimnetz does not read yet. Heimnetz sends nothing itself; a password typed there is
used only for the query and not stored (left empty, Heimnetz uses the one stored under 🌐 Access for the stored or found
address).

**Access** (⚙ → 🌐 Access): Heimnetz finds out where the internet comes from by asking the FRITZ!Box (TR-064, every
10 minutes) and – only with an upstream device – its few addresses; the evidence reads e.g. “192.168.0.1 answers: ZTE
G5TC (ubus)”. You can also choose “Fibre via an own modem” (ONT). If you set an upstream modem, you can enter its address (private
addresses only) and the password of its web interface. **The password is stored in Home Assistant** (in the options of
the Heimnetz entry, like other integrations), never returned to the page (it only shows "stored"), never logged and
redacted in the diagnostics; "Remove password" deletes it.

**Never** sent: the Home Assistant location, passwords, device names, hardware (MAC) and IP addresses. Box credentials
stay in FRITZ!Box Tools and are not stored by Heimnetz. The **diagnostics** (Devices & services → Heimnetz → ⋮ →
Download diagnostics) contain only numbers and a rough state (versions, box model, FRITZ!OS, network technology,
Ookla, schedule); credentials, keys, cell identifiers, TAC/PCI, coordinates, device names and addresses are redacted –
in error messages too.

### Reporting issues

Button at the bottom right of the page: type (bug, wish, suggestion), text, up to 3 screenshots (gallery on the phone,
Ctrl+V on the PC).

- **Send** stores the report locally (`<config>/heimnetz/meldungen.json`, `meldungen.md`, images under
  `<config>/heimnetz/meldungen/`); it appears under ⚙ → Reports.
- **Send + report publicly on GitHub ↗** stores locally and also opens a prefilled issue. A preview shows exactly what goes
  out: the text and a rough state (versions, tab, device, box model and FRITZ!OS, network technology, Ookla yes/no,
  local ticket number). Cell and signal data only with the switch "Include cell and signal data" – it can narrow down
  where you live. Addresses, coordinates, passwords, known device names and cell identifiers (TAC/PCI too) are redacted in the text too; this is
  pattern based, so read the preview. Images cannot travel through the link – add them on GitHub. You submit with your
  own GitHub account; Heimnetz holds no token.

Or directly: [issues](https://github.com/herbertschrotter-blip/ha-heimnetz/issues).

### Language

German and English. The page follows the language in your Home Assistant profile and sends it with every request;
what the integration prepares for the page (findings, error messages, issue preview) comes in that language. What the
background polling creates and stores (journal, errors reading the box) and the texts of entities and setup follow
the system language (Settings → System → General). `de` and its variants give German, everything else English.
Existing journal entries keep their language.

### Entities

All under the device "Heimnetz". The entity ID is created at setup from the name in the system language (English e.g.
`sensor.heimnetz_overall_state`, German `sensor.heimnetz_gesamtstand`).

| Entity (English) | Content |
|------------------|---------|
| `sensor.heimnetz_overall_state` | OK, warnings, problem, FRITZ!Box unreachable |
| `sensor.heimnetz_open_findings` | number of open findings |
| `sensor.heimnetz_devices_online` | devices currently online |
| `sensor.heimnetz_last_measurement` | time of the last speed test; values and snapshot as attributes |
| `sensor.heimnetz_mobile_technology` | access technology reported by the box (e.g. LTE, 5G NSA) |
| `sensor.heimnetz_signal_strength_4g_anchor` / `_signal_quality_4g_anchor` | RSRP (dBm) / RSRQ (dB) of the 4G anchor cell |
| `sensor.heimnetz_signal_strength_5g` / `_signal_quality_5g` | RSRP / RSRQ of the 5G cell |
| `sensor.heimnetz_cell` | anchor cell |
| `sensor.heimnetz_distance_to_base_station` | distance reported by the box |
| `sensor.heimnetz_neighbour_cells` | number of visible neighbour cells |
| `sensor.heimnetz_5g_cell_pci` | PCI of the 5G cell |
| `sensor.heimnetz_signal_to_noise_ratio_4g_anchor` / `_signal_to_noise_ratio_5g` | SINR (dB) – only from an upstream modem |
| `sensor.heimnetz_mobile_band` | bands in use, e.g. “B3 · n78” – only from an upstream modem |
| `sensor.heimnetz_internet_access` | access type: mobile, DSL, fibre, cable or upstream device (detected or set) |
| `sensor.heimnetz_dsl_sync_rate_download` / `_upload` | DSL sync rate (Mbit/s) |
| `sensor.heimnetz_dsl_noise_margin_download` / `_upload` | noise margin (dB) |
| `sensor.heimnetz_dsl_attenuation_download` / `_upload` | attenuation (dB) |
| `sensor.heimnetz_dsl_errors_per_hour` | uncorrectable errors (CRC) per hour |
| `sensor.heimnetz_fibre_received_optical_power` / `_transmitted_optical_power` | optical power (dBm) |
| `binary_sensor.heimnetz_fritz_box_from_the_pi` | box reachable from the Home Assistant host |
| `binary_sensor.heimnetz_internet_from_the_pi` | internet reachable from the Home Assistant host |
| `binary_sensor.heimnetz_name_resolution` | name resolution (DNS) works |

Mobile sensors exist only for boxes with mobile broadband or once an upstream modem has delivered radio values (the
values then come from there), DSL and fibre sensors only when the internet comes through
that connection (they appear with the first reading). **Long-term archive:** Heimnetz keeps measurements and
journal itself (database `<config>/heimnetz/heimnetz.db`); the recorder keeps entity history only for a limited time.
For years of history, record the entities with Scribe (TimescaleDB) or InfluxDB.

### Outlook

Planned, not yet done:

- Values of a **fibre modem (ONT)** and further upstream devices, once real raw data is available.
- More values for **cable** and **fibre** than the box provides via TR-064.
- **Other vendors**, e.g. UniFi.
- **Other countries** (operator names, cell export, map tiles).
- Inclusion in the HACS default list.

### Development

See [Entwickeln](#entwickeln) above (commands are the same). Business logic without Home Assistant lives in
`custom_components/heimnetz/logik/`; code and documentation are written in German.

### License

[Apache-2.0](LICENSE). Hobby project, no warranty – use at your own risk. Not affiliated with AVM, Ookla or Home
Assistant. FRITZ!Box is a trademark of AVM GmbH.
