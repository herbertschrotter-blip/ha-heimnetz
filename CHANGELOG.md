# CHANGELOG

## [0.28.5]

- Fix (GitHub #2): Hatte Heimnetz ein ZTE-Modem nur als „ZTE“ ohne Schnittstelle erkannt (die Suche gibt jedem Gerät
  wenig Zeit, das G5TC braucht mit https länger), blieb es dabei – der Reiter Internet zeigte weiter „Gerät erkannt,
  Werte noch nicht unterstützt“, obwohl 🔬 Diagnose die Werte las. Jetzt bestimmt der nächste Abruf die Schnittstelle
  mit den normalen Zeitlimits, liest die Werte und merkt sich das Ergebnis; „↻ Erneut suchen“ ist nicht nötig.

## [0.28.4]

- Fix (GitHub #2): Mit 0.28.3 liest Heimnetz das ZTE G5TC über ubus (Anmeldung und Funkwerte gehen). Drei Werte waren
  falsch umgerechnet: das **Band** (B1 statt B3 – `lte_band` ist beim G5TC die Liste der freigegebenen Bänder, das
  aktive steht in `wan_active_band`), die **Zellkennung** (ubus nennt sie dezimal, gelesen wurde sie hexadezimal –
  dadurch falsche Zelle und Sendeanlage) und die fehlende **TAC** (ubus: `lac_code`).

## [0.28.3]

- Fix (GitHub #2): Ein ZTE G5TC wurde zwar als „ZTE“ erkannt, aber keine seiner Schnittstellen („Gerät erkannt, Werte
  noch nicht unterstützt“). Die ubus-Aufrufe sehen jetzt aus wie die der Weboberfläche: ein einzelnes JSON-RPC-Objekt
  mit den Kopfzeilen `Z-Mode` und `Z-Tag` (nach dem Mitschnitt eines G5TS). Ob das beim G5TC reicht, ist am Gerät
  noch ungeprüft.
- 🔬 Diagnose: Erkennt Heimnetz ein ZTE, aber keine Schnittstelle, stehen die Antworten der Proben für goform und ubus
  (geschwärzt, gekürzt) in der Datei, dazu je eine Zeile in der Liste der Abfragen.

## [0.28.2]

- Fix (GitHub #2): Ein vorgeschaltetes Modem, dessen Startseite per http nur auf https weiterleitet (z. B. ZTE G5TC),
  wurde nicht erkannt – Heimnetz probierte https nur, wenn http gar nicht antwortete. Jetzt folgt es genau dieser einen
  Weiterleitung, wenn sie auf https an **dieselbe** private Adresse zeigt; Erkennen, Anmeldung und Werte laufen dann
  über https. Weiterleitungen auf andere Adressen bleiben gesperrt. Gilt für die Suche, den laufenden Abruf und
  🔬 Diagnose.

## [0.28.1]

- Fix (GitHub #1): Im Reiter **Verbrauch** ragte der Balken „davon Speedtests“ über das Diagramm hinaus, wenn an einem
  Tag Zählerwerte der FRITZ!Box fehlten (z. B. am Tag der Einrichtung). Der geschätzte Speedtest-Anteil ist jetzt höchstens
  die Tagesmenge.

## [0.28.0]

- WU-0010 (Mockups netzwerk.html · Warnungen und · Eigene Arten, abgenommen 28.10.2026): **Warnungen** unter ⚙ → 🔔
  Warnungen (nur Admins) – Nachricht über einen notify-Dienst von Home Assistant (eine Companion App, alle Companion
  Apps oder keine – nur Ereignis; ab Werk keine), „Offline melden nach“ 2/5/15/60 min (Vorgabe 5), Schalter je Art
  (ab Werk an: Netzwerk, Smart Home, Haushalt & Roboter, Kameras; Handy & Tablet aus), Ausnahmen je Gerät (immer/nie,
  im Fenster des Geräts „🔔 Bei offline warnen“), außerdem „wieder online“ mit Dauer, neues unbekanntes Gerät (einmal
  je Gerät) und „Internet oder FRITZ!Box weg“ (zugestellt, sobald es wieder geht). „🔔 Testnachricht senden“.
- WU-0010: Offline genau einmal nach der Verzögerung, kein Flattern; nach einem Neustart kein Schwall (Grundzustand
  aus dem ersten vollständigen Abruf); Box nicht erreichbar → keine Gerätemeldungen, stattdessen die Meldung zum
  Ausfall mit Dauer; eine leere oder stark geschrumpfte Gerätetabelle gilt wie „Box weg“, danach eine Schonfrist von
  einer Verzögerung. „Neues Gerät“ prüft gegen alle je gesehenen Geräte (Gedächtnis und Journal), mit Hinweis bei
  zufälliger WLAN-Adresse. Jede Meldung feuert das Ereignis **`heimnetz_warnung`** (art, geraet, ip, verbindung, dauer,
  nachricht) und steht im Journal; ein Fehler beim Versand kommt ins Protokoll und Journal. Texte in der Sprache der
  Seite (Deutsch/Englisch).
- WU-0010: **Eigene Arten** (⚙ → 🏷️ Arten und „＋ eigene Art …“ im Fenster eines Geräts): Symbol und Name anlegen,
  umbenennen, löschen (Geräte bekommen wieder die erkannte Art, ihre Warnungen fallen weg); sie gelten wie die festen
  unter Geräte › nach Art und bei den Warnungen. Gespeichert im Einstellungsspeicher ohne neue Version, Namen in der
  Diagnose geschwärzt.
- Zweite Ausnahme von „die Integration liest nur“: Nachrichten über notify-Dienste (README Datenschutz: Push über
  Google/Apple enthält den Gerätenamen).

## [0.27.0]

- AN-0007 (Mockup abgenommen 28.10.2026): **Einzelne Messung löschen** – im Fenster einer Messung „🗑 Messung löschen“
  mit Rückfrage, nur Admins (Befehl `heimnetz/messung/loeschen`, Kennung = Zeitpunkt). Gelöscht werden Messung und
  Momentaufnahme in der eigenen Datenbank, dazu der Durchlauf in der gemerkten Serie; der Sensor „Letzte Messung“ springt
  auf die davor, das Journal erhält „Messung <Zeit> gelöscht“. Eine Merkliste gelöschter Zeitpunkte verhindert, dass
  die Messung wieder eingetragen wird (Ookla zeigt sie weiter als letzten Test). Der Recorder-Verlauf bleibt.
- AN-0006 (Mockup abgenommen 28.10.2026, Variante B): Gruppenüberschriften der ganzen Seite deutlicher – fett in normaler
  Schreibweise, blauer Strich links, Trennlinie; im Fenster einer Messung dazu Symbole (📈 📶 📦 🏠 🌦️).
- Fix (FE-0006): „Öffentlich auf GitHub melden“ schwärzt Zellkennungen jetzt bis 16 Stellen (ECI/NCI dezimal, auch mit
  0x) – längere Kennungen blieben bisher im Issue stehen. Wörter wie „PCI face“ bleiben dafür stehen.
- WU-0009 Stufe 2 (Mockup netzwerk.html · Internet und Zugang, abgenommen 27.10.2026): Ein **vorgeschaltetes Gerät**
  vor der FRITZ!Box wird automatisch erkannt und liefert laufend Werte in den Reiter **Internet** – wie die Box selbst.
  Oben „Werte vom vorgeschalteten Modem (Beta)“, darunter die Mobilfunk-Ansicht mit Herkunft „vom vorgeschalteten
  Modem“ (Technik, Bänder, Zellen mit Kennung/PCI/TAC/Netz, RSRP/RSRQ und neu **SINR** und **Band** je Zelle, 5G,
  Betreiber, verbunden seit; die Karte zum Mast nutzt die Zellen wie bisher). Was ein Gerät nicht liefert, steht als
  „–“. Der Hinweis „Werte folgen“ aus 0.26.0 ist ersetzt.
- WU-0009: **Bausteine je Hersteller/Schnittstelle** mit demselben Muster (erkennen aus Startseite/Antwortkopf, nur
  lesende Abfragen, höchstens eine Anmeldung mit dem Kennwort des Besitzers, Umrechnen in das gemeinsame Format;
  Fachlogik mit Tests in `logik/vorgeschaltet/`, Netz in `vorgeschaltet/`): **ZTE goform** (aus 0.25 umgebaut), **ZTE
  ubus** (G5TS/G5TC; Protokoll nach dem öffentlichen Projekt chennest/zte-cpe-go nachgebaut, GPL-3.0, kein Code
  übernommen; nur `web_login_info`, `web_login`, `web_logout`, `nwinfo_get_netinfo`, `get_wwaniface`), **Huawei
  HiLink** über `huawei-lte-api` (ist die Integration Huawei LTE eingerichtet, gelten deren Entitäten und Heimnetz fragt
  das Gerät nicht selbst), **TP-Link** LTE/5G über `tplinkrouterc6u` (GPL-3.0, AlexandrErohin/TP-Link-Archer-C6U;
  Gerätefamilie nur über Schlüssel-Abfragen ohne Anmeldung, dann genau ein `authorize`, `get_lte_status`, `logout` –
  nicht `supports()` und nicht der Provider, die sich mehrfach anmelden), **NETGEAR LTE** und **Teltonika** über deren
  HA-Integration; MikroTik, Sagemcom, Nokia FastMile, Zyxel 5G und **Glasfaser-Modems (ONT)** von Nokia, Huawei, Zyxel
  nur erkennen (Hinweis „Rohdaten über 🔬 Diagnose schicken“). Alle Geräte: ungetestet am Gerät.
- WU-0009: **Automatisch erkennen** beim Einrichten des Zugangs und bei „↻ Erneut suchen“: nacheinander an der
  gespeicherten Adresse, dem Vorschlag der FRITZ!Box und 192.168.0.1, 192.168.1.1, 192.168.8.1, 192.168.18.1,
  192.168.100.1 (nie die Box selbst, kein Absuchen weiterer Adressen), bis ein Gerät erkannt ist. Beleg in ⚙ → 🌐 Zugang
  („✓ 192.168.0.1 antwortet: ZTE G5TC (ubus)“), Zeile „Erkannt“ mit Zeitpunkt und Befund. Das erkannte Gerät bleibt
  über einen Neustart gemerkt.
- WU-0009: **Laufender Abruf** im eigenen langsamen Takt (10 Minuten, getrennt von der Sperre der Box, im
  Hintergrund); Werte gehen in den Reiter Internet, in die Mobilfunk-Entitäten und in die **Momentaufnahme** jeder
  Speedtest-Messung (neu `mobil_quelle`, `modem_modell`, `sinr`, `band`, `nr_sinr`, `nr_band`). Neue Entitäten
  **Signal-Rausch-Abstand 4G-Anker / 5G** und **Mobilfunk-Band** (nur, wenn ein Modem davor Werte geliefert hat).
- WU-0009: **Befunde statt Stille**: nicht gefunden, nicht erreichbar, Kennwort fehlt, Anmeldung abgelehnt, gesperrt,
  keine Funkwerte, nicht unterstützt, Glasfaser-Modem (mit Hinweis, dass ein ONT am Internet-Anschluss der Box oft nicht
  erreichbar ist). Lehnt das Gerät das Kennwort ab, versucht Heimnetz es nicht wieder, bis ein anderes Kennwort
  hinterlegt ist; Reparatur-Hinweise „Vorgeschaltetes Modem lehnt das Kennwort ab“ (sofort) und „… antwortet nicht“
  (nach zwei Takten).
- WU-0009: Neue Zugangsart **„Glasfaser über ein eigenes Modem“** (ONT) in ⚙ → 🌐 Zugang.
- WU-0009: **🔬 Diagnose** nutzt dieselben Bausteine: erkannter Hersteller und Schnittstelle, Rohdaten aller passenden
  Schnittstellen (geschwärzt wie bisher), dazu die umgerechneten Werte; Befunde mit Text von der Integration. Sie läuft
  nie gleichzeitig mit dem Abruf am Gerät.
- Sicherheit: nur private Adressen, keine Weiterleitung auf einen anderen Host (die Bibliotheken bekommen eine eigene
  requests-Session, die jede andere Adresse ablehnt), Zeit- und Größengrenzen; das Kennwort steht in keiner Antwort und
  in keinem Protokoll – auch die Debug-Zeilen von huawei-lte-api mit Anmeldedaten werden verworfen.
- Anmeldung: angenommen, abgelehnt oder Fehler werden unterschieden – nur eine echte Ablehnung sperrt bis zum neuen
  Kennwort. Die Diagnose meldet sich nicht an, wenn die HA-Integration des Geräts eingerichtet ist, und verwendet ein
  schon abgelehntes hinterlegtes Kennwort nicht wieder.
- Neue Pflicht-Abhängigkeiten: `huawei-lte-api>=1.11.0` (wie Home Assistant für Huawei LTE), `tplinkrouterc6u>=5.37.0`
  (GPL-3.0).

## [0.26.0]

- WU-0009 Stufe 1 (Mockup abgenommen 27.10.2026): Der Reiter **Funk** heißt **Internet**. Oben steht, woher das
  Internet kommt („Internet über Mobilfunk / DSL / Glasfaser / Kabel / ein vorgeschaltetes Gerät“) mit Gerät, Weg und
  Abzeichen „automatisch erkannt“ oder „festgelegt“; „ändern ›“ öffnet ⚙ → 🌐 Zugang. Darunter die Werte der
  Zugangsart: Mobilfunk wie bisher; **DSL** mit Bewertung (Störabstandsmarge gut ab 6 dB, Fehler je Stunde,
  Neusynchronisierungen in 7 Tagen – z. B. „Reserve knapp“), Synchronrate mit möglicher Rate und Tarif, Dämpfung,
  Verfahren/Profil, CRC/FEC je Stunde, Verlauf 7 Tage; **Glasfaser** mit empfangener und gesendeter Lichtleistung im
  guten Bereich laut Box, Verbindung, Verlauf; **Kabel** mit der Geschwindigkeit der Verbindung. Was die Schnittstelle
  der Box (TR-064) nicht liefert – Gegenstelle und Vectoring bei DSL, Status O1–O7 und Temperatur bei Glasfaser, Kanäle,
  Pegel, MER und Fehler bei Kabel –, steht als „–“ mit dem Hinweis „liefert die Schnittstelle der Box nicht“; die
  Weboberfläche der Box wird nicht ausgelesen. **Ersatzzugang** (Mobilfunk-Stick an einer DSL-/Glasfaser-/Kabel-Box)
  als eigener Umschalter mit Umschaltungen und Dauer der letzten 30 Tage. Bei einem vorgeschalteten Modem der Hinweis
  „Werte vom vorgeschalteten Gerät folgen“ und der Sprung zu 🔬 Diagnose. Die Kopfzeile der Seite zeigt Box und Zugang.
- WU-0009: **WLAN** steht jetzt im Reiter **Geräte** (Umschalter „Geräte | WLAN“); die Kachel „Empfang“ der Übersicht
  springt in den Reiter Internet.
- WU-0009: Zugang erkennen in der Fachlogik `logik/zugang.py` (mit Tests) – aus TR-064 `GetCommonLinkProperties`
  (Zugangsart, Verbindung, Rate), `X_AVM-DE_GetAddonInfos` (Betriebsart, z. B. IP-Client; neuere FRITZ!OS), Mobilfunk
  `GetInfo`, DSL- und Glasfaser-Status und der Art der WAN-Adresse (privat / Netz des Anbieters / öffentlich – die
  Adresse selbst verlässt `box.py` nicht). Meldet eine DSL-Box plötzlich Mobilfunk, gilt das als Ersatz, nicht als
  Wechsel (nach 14 Tagen als neuer Zugang). Werte der Leitung und Bewertungen in `logik/leitung.py` (mit Tests).
  Gelesen wird nur im gemeinsamen Abruf im 10-Minuten-Takt, keine zweite Verbindung; ein Box-Abruf läuft nie doppelt.
  Journal: Zugang gewechselt, Ersatz springt ein / wieder aus, DSL neu synchronisiert.
- WU-0009: Neuer Reiter **⚙ → 🌐 Zugang** (vor „Einrichtung“, nur Admins): Vorschlag mit Belegen, Auswahl Automatisch /
  Mobilfunk über die Box / vorgeschaltetes Modem / DSL / Glasfaser / Kabel, Ersatzzugang automatisch/keiner; bei
  vorgeschaltetem Modem Adresse (Vorschläge: Adresse vor der Box und 192.168.0.1, 192.168.1.1, 192.168.8.1 – nur private
  Adressen, kein Absuchen) und Kennwort der Weboberfläche. Das Kennwort wird in den Optionen der Einrichtung gespeichert,
  nie an die Seite zurückgegeben („hinterlegt“), nie protokolliert und in der Diagnose geschwärzt; „Kennwort entfernen“.
  „↻ Erneut suchen“ liest den Zugang im nächsten gemeinsamen Abruf sofort (höchstens alle 30 s); „🔬 Rohdaten
  abfragen ›“ springt in die Diagnose und übernimmt die Adresse. Bleibt das Kennwortfeld der Diagnose leer, nimmt die
  Abfrage das hinterlegte Kennwort, wenn die Adresse die unter 🌐 Zugang gespeicherte ist. Neue WebSocket-Befehle `heimnetz/internet` (lesen) sowie `heimnetz/zugang`,
  `heimnetz/zugang/setzen` und `heimnetz/zugang/suchen` (nur Admins).
- WU-0009: Neue Entitäten **Internetzugang** (immer) und – nur wenn das Internet über diesen Anschluss kommt – DSL
  Synchronrate, Störabstandsmarge und Dämpfung je Richtung, DSL Fehler je Stunde, Glasfaser empfangene und gesendete
  Lichtleistung (Verlauf über den Recorder).
- Die Optionen von Heimnetz (OpenCellID-Schlüssel) behalten beim Speichern die übrigen Optionen.

## [0.25.1]

- Fix (WU-0008): Im Reiter **🔬 Diagnose** sprang eine eingetippte Adresse auf 192.168.0.1 zurück, sobald Home Assistant
  die Seite neu zeichnete, bevor man das Feld verlassen hatte. Die Adresse wird jetzt bei jeder Eingabe übernommen.

## [0.25.0]

- WU-0008 (Mockup abgenommen 27.10.2026): In den Einstellungen (⚙) fragt der neue Reiter **🔬 Diagnose** (Beta) auf
  Knopfdruck die Rohdaten eines vorgeschalteten Mobilfunk-Modems im eigenen Heimnetz ab (z. B. ein ZTE von Drei
  Österreich). Kommt das Internet über ein solches Modem vor der FRITZ!Box, kennt die Box das Funknetz nicht und
  „Funk › Mobilfunk“ bleibt leer; diese Version liefert nur das Abfrage- und Export-Werkzeug, damit der Entwickler die
  Unterstützung bauen kann – keine Auswertung. Felder Adresse (Vorgabe 192.168.0.1) und Kennwort (optional); das
  Kennwort wird nur für diese Abfrage verwendet, nie gespeichert, nie protokolliert und steht in keiner Antwort.
- WU-0008: Neuer WebSocket-Befehl `heimnetz/modem` (nur Admins, nur lesen) und die Fachlogik `logik/modem.py`. Abgefragt
  werden Startseite (Modell), ZTE-`goform` ohne und – mit dem eingegebenen Kennwort – mit Anmeldung sowie eine zweite
  lesende Schnittstelle (ubus), jede Stufe als eigener Eintrag. Nur private Adressen im eigenen Heimnetz (keine
  Hostnamen), keine Weiterleitungen, Zeit- und Größenlimit je Anfrage; `goform_set_cmd_process` nur mit `LOGIN`/`LOGOUT`,
  sonst nie ein set-Befehl. Die Rohdaten kommen geschwärzt zurück (IMEI, IMSI, ICCID, Rufnummer, Seriennummer, MAC- und
  öffentliche IP-Adressen, WLAN-Namen und -Kennwörter – die Zellkennung bleibt); „⬇ Als Datei speichern“
  (`heimnetz-modem-JJJJ-MM-TT.json`) und „⧉ Kopieren“ geben die geschwärzte Antwort mit Heimnetz-Version und Zeitpunkt.
  Heimnetz sendet selbst nichts nach außen.

## [0.24.0]

- WU-0007 (Mockup abgenommen 27.10.2026): In den Einstellungen (⚙) zeigt der neue Reiter **🧩 Einrichtung**, welche
  Voraussetzungen eingerichtet sind und was fehlt – in den Stufen Muss (Home Assistant mit Version, FRITZ!Box Tools
  mit Box-Modell, Recorder mit Aufbewahrung, HACS), Soll (Ookla Speedtest, Met.no, Holiday) und Kann
  (OpenCellID-Schlüssel, Langzeitarchiv Scribe oder InfluxDB), je Stufe „x von y“. Knöpfe öffnen Home Assistant oder
  HACS an der richtigen Stelle: „Einrichten ›“ (Einrichtungsdialog), „In HACS öffnen ↗“ (Repository), „Anleitung ↗“
  (hacs.xyz, ohne HACS), „Schlüssel holen ↗“ und „Eintragen ›“ (OpenCellID). Aus HACS heruntergeladen, aber noch
  nicht eingerichtet: „heruntergeladen – nach einem Neustart einrichten“; ohne HACS bei HACS-Teilen „erst HACS installieren“.
  Punkt am Reiter orange, wenn Empfohlenes fehlt, rot, wenn Nötiges fehlt. Erkannt wird in der Integration (neuer
  Befehl `heimnetz/einrichtung`, nur Admins; Fachlogik `logik/einrichtung.py`) beim Öffnen von ⚙ und des Reiters.
  Heimnetz installiert, lädt und startet dabei nichts.
- WU-0007: Neuer Reparatur-Hinweis „Recorder nicht geladen“ (Warnung) – ohne Recorder fehlen Verlauf und Verbrauch je
  Tag; Heimnetz läuft trotzdem.
- WU-0007: README mit „Schnelleinrichtung“ / „Quick start“ ganz oben (nummerierte Schritte, Muss/Soll/Kann, Links und
  My-Home-Assistant-Knöpfe); Scribe verlinkt (`jonathan-gtd/scribe`).

## [0.23.1]

- Fix (WU-0006): `fritzconnection` steht in `manifest.json` als Mindestversion (`>=1.15.1`) statt fest gepinnt –
  Home Assistant bringt das Paket über die FRITZ!-Integration selbst mit; hassfest lehnt den festen Pin ab.

## [0.23.0]

- WU-0006 (Veröffentlichung): Die Integration heißt jetzt **Heimnetz** (Domain `heimnetz`, vorher `netzwerk`).
  Entitäten `sensor.heimnetz_*` / `binary_sensor.heimnetz_*`, Seite `/heimnetz`, Befehle `heimnetz/*`, Aktion
  `heimnetz.ticket`, Daten unter `<config>/heimnetz/`. `manifest.json` mit Dokumentation, Issue-Tracker und Codeowner.
- WU-0006: Umstieg von „Netzwerk“ – beim ersten Laden übernimmt Heimnetz Datenbank (Messungen, Journal, Protokoll,
  Gedächtnis), Einstellungen, Messplan, Arten, gemerkte Masten, Tickets mit Nummern und Bildern sowie den
  OpenCellID-Schlüssel; die alten Daten bleiben unangetastet. Solange die alte Integration nicht deaktiviert ist,
  startet Heimnetz nicht (Reparatur-Hinweis), damit nie beide die FRITZ!Box abfragen. Ablauf: `docs/umstieg.md`.
- WU-0006: Die Seite spricht Deutsch und Englisch – nach der Sprache im Profil von Home Assistant (`de` und Varianten
  Deutsch, sonst Englisch), auch Zahlen (1.234,5 / 1,234.5) und Datum („Sa 10.10.“ / „Sat 10 Oct“); die Uhrzeit bleibt
  24-stündig.
- WU-0006: Auch die Texte der Integration gibt es auf Deutsch und Englisch – nach der Sprache von Home Assistant
  (Einstellungen → System → Allgemein): Befunde, Prüfungen, Mobilfunk-Befund, Zellen, Karte (Entfernung, Richtung),
  Gerätegruppen und Arten, WLAN-Hinweise, Speedtest-Hinweis, Tickets (Art, Status), Fehlermeldungen der Seite und neue
  Journal-Einträge. Was schon im Journal steht, bleibt in seiner Sprache. Übersetzungen der Einrichtung, Optionen,
  Aktion und Reparatur-Hinweise vollständig, dazu die Attribute des Sensors „Letzte Messung“. Gerätegruppen tragen
  eine feste Kennung und einen Text; Zellen nennen ihre Rolle zusätzlich als Kennung (`rolle_art`).
- WU-0006 (Mockup abgenommen 25.10.2026): Melden – neu „Senden + öffentlich auf GitHub ↗“. Eine Vorschau zeigt genau,
  was ins Issue geht: Titel `[Art] Text…`, Text der Meldung und ein grober Stand (Version von Heimnetz und Home
  Assistant, Reiter und Gerät, Box-Modell und FRITZ!OS, Netztechnik, Ookla ja/nein, lokale Ticketnummer). Schalter
  „Zell- und Signaldaten mitsenden“ (aus; mit Warnung, dass sich daraus der Wohnort eingrenzen lässt). Hardware- und
  IP-Adressen, Koordinaten, Kennwörter („Kennwort: …“) und Gerätenamen (der Box und der Geräte-Tracker in Home
  Assistant) schwärzt die Integration auch im Text der Meldung. „Speichern und weiter zu GitHub ↗“ öffnet das
  vorausgefüllte Issue genau wie gezeigt in einem neuen Fenster und speichert das Ticket lokal wie bisher; abgeschickt
  wird mit dem eigenen GitHub-Konto (kein Token in der Integration). Bilder gehen über den Link nicht mit – Hinweis,
  sie auf GitHub einzufügen. Zu lange Texte werden gekürzt, damit der Link unter 7000 Zeichen bleibt. Neuer Befehl
  `heimnetz/meldung/github` (Vorschau und Link, mit der Nummer, die das Ticket bekommt).
- WU-0006: Vorgaben für neue Nutzer – eine neue Installation startet mit eingeschaltetem Messplan, 4 Messungen am Tag
  (alle 6 Stunden), und speichert ihn gleich; übernommene Einstellungen und der Umstieg von „Netzwerk“ behalten ihren
  Plan. Die Einstellungen zeigen das geschätzte Datenvolumen je Messung, am Tag und im Monat (aus der letzten Messung,
  sonst aus dem Tarif; ohne beides der allgemeine Hinweis „einige hundert MB“). Ohne Ookla zeigt der Reiter Speedtest
  einen Hinweis mit Link zur Ookla-Integration; Einrichtung, Sensoren, Seite und Melden laufen ohne Ookla und ohne
  Mobilfunk-Box fehlerfrei (Tests).
- WU-0006: Die Diagnose darf öffentlich sein – sie nennt jetzt Versionen, Sprache, Box-Modell, FRITZ!OS, Netztechnik,
  Ookla ja/nein und den Messplan und schwärzt tief alles Vertrauliche (Zugang, Schlüssel, Zellkennungen, TAC/PCI,
  Koordinaten, Gerätenamen, Hardware- und IP-Adressen), auch in Fehlermeldungen (`logik/diagnose.py`).
- WU-0006: Paket für HACS und GitHub – Lizenz Apache-2.0, `hacs.json` mit README-Anzeige, eigenes Symbol
  (`brand/icon.png`), GitHub Actions für Tests, hassfest und HACS-Prüfung sowie Release per Tag `vX.Y.Z` mit dem
  Abschnitt aus diesem CHANGELOG, Issue-Vorlagen Fehler/Wunsch/Anregung (zweisprachig, mit Datenschutz-Hinweis).
  Testdaten enthalten nur noch erfundene Zellkennungen und Koordinaten.
- WU-0006: README neu, auf Deutsch mit vollständigem englischen Teil – was Heimnetz kann, für wen (FRITZ!Box mit
  Mobilfunk, ausgelegt für Österreich), Voraussetzungen getrennt nach **muss** (Home Assistant ab 2026.10.1, HACS,
  FRITZ!Box, FRITZ!Box Tools mit TR-064-Benutzer, Recorder), **soll** (Ookla Speedtest, Met.no, Holiday) und **kann**
  (OpenCellID-Schlüssel, Scribe/TimescaleDB) samt dem, was ohne sie fehlt; Installation über HACS, Einrichtung,
  Aktualisieren, Entfernen, Umstieg, Datenvolumen der Speedtests, Datenschutz (was wohin geht, was nie), Melden lokal
  und auf GitHub, Sprache, Liste der Entitäten, Langzeitarchiv, Ausblick (DSL/Glasfaser, UniFi, weitere Länder),
  Lizenz. Steckbrief auf den Stand 0.23.0 gebracht.
- WU-0006 (Nacharbeit nach Review): Umstieg – ein vorübergehender Fehler von SQLite beim Übernehmen der alten
  Datenbank (Platte voll, Ein-/Ausgabe, gesperrt) zählt nicht mehr als kaputte Datenbank; die Einrichtung versucht es
  später noch einmal, statt ohne Daten weiterzumachen. Bei einer wirklich kaputten Datenbank kommen die Bilder der
  Tickets trotzdem mit. Die alte lesbare Ablage (`meldungen.json`, `meldungen.md`) wird nicht mehr kopiert.
- WU-0006 (Nacharbeit): Öffentlich melden schwärzt auch Zellkennungen im Text (Muster `xxxxx-yy`, Werte hinter
  TAC/PCI/ECI/eNB und die Kennungen der Zellen, die die Box gerade sieht) und Koordinaten in Kartenlinks (`lat=`,
  `mlon=` …), in der Diagnose ebenso; das Gerät geht nur als bekannter Wert (Handy, Desktop) ins Issue.
- WU-0006 (Nacharbeit): Die Seite schickt ihre Sprache bei jedem Befehl mit – Befunde, Fehlermeldungen und die
  Vorschau des Issues folgen damit dem Profil des Nutzers, nicht mehr der Systemsprache. Journal und Abruf bleiben in
  der Sprache von Home Assistant.
- WU-0006 (Nacharbeit): Melden und Tickets ohne Hinweise auf Claude Code (die Seite ist auch für andere
  Installationen); `ookla_speedtest` nicht mehr unter `after_dependencies` (hassfest kennt keine HACS-Integrationen).
  README: Datenschutz-Tabelle um die Prüfungen „Pi → Internet“ (1.1.1.1, 8.8.8.8) und DNS ergänzt, Größe des
  Overpass-Ausschnitts richtig (etwa 44 × 30 km, grenzt auf 22 × 15 km ein). Checkliste zum Anlegen von `ha-heimnetz`
  in `docs/entscheidungen.md`.

## [0.22.0]

- WU-0002: Neue Sensoren Mobilfunkzelle (Ankerzelle), Entfernung zur Basisstation (laut Box), Nachbarzellen und
  5G-Zelle (PCI) – damit das Langzeitarchiv (Scribe → TimescaleDB) auch diese Werte dauerhaft mitschreibt.

## [0.21.1]

- WU-0005: Der Sensor „Letzte Messung“ zeigt die Momentaufnahme auch dann, wenn sie erst beim Nachtragen nach dem Start
  dazukommt (bisher blieb er bis zur nächsten Messung ohne Zusatzwerte).

## [0.21.0]

- WU-0005 (Mockup abgenommen 23.10.2026): Zu jeder Speedtest-Messung hält die Integration eine Momentaufnahme fest –
  Mobilfunk (Netz, Zelle, Sendeanlage, Signal, 5G, Entfernung, Nachbarzellen, verbunden seit, geschätzter Mast), Box
  (Modell, Firmware, Laufzeit, Bänder), Heimnetz, Auslöser, Ookla-Jitter/Bufferbloat/Anbieter/Ergebnis-Link, Wetter und
  Werktag/Wochenende/Feiertag. „Letzte Messungen“ zeigt Netz, Zelle, Signal und Box; Tippen auf eine Zeile zeigt alle
  Werte. Das Popup der Stundenkachel nennt Netz und Signal. Messungen der letzten 62 Tage werden aus Verlauf und
  Journal nachgetragen. Neuer Sensor „Letzte Messung“ mit den Werten als Attribute (für InfluxDB, WU-0002; ohne
  Mast-Entfernung und -Richtung). Neue Tabelle in der Datenbank, Schema bleibt – der Rückweg geht weiter.

## [0.20.0]

- AN-0005 (Mockup abgenommen 23.10.2026): Reiter Speedtest – Popup zur Stundenkachel. Bleibt die Maus über einer
  Kachel stehen, zeigt ein Popup Median, niedrigste und höchste Messung, Anzahl und belastete Messungen sowie die
  einzelnen Messungen dahinter (Zeit, Server, Wert, Grundlast, „zählt nicht/¼“; neueste zuerst, höchstens 20). Klick
  bzw. Tipp am Handy hält es fest, ✕ oder Tipp daneben schließt. Die Liste holt die Seite nur für diese Kachel
  (neuer Befehl `netzwerk/speedtest/kachel`, gleiche Auswahl wie das Raster).

## [0.19.0]

- WU-0004: Tagesverlauf mit geglättetem Mittelwert – eine Linie in Amber zeigt den gleitenden Mittelwert über die
  Stunde davor, die Stunde selbst und die danach (alle gezählten Messungen, belastete nach Einstellung gewichtet);
  beim Wochentag über Mitternacht hinweg. Tipp auf eine Stunde nennt auch den geglätteten Wert.

## [0.18.1]

- WU-0004: Tagesverlauf besser lesbar – Linie, Punkte und Band in der Textfarbe der Seite (weiß im dunklen, schwarz im
  hellen Design) statt im Akzentblau, das auf dem blauen Hintergrund kaum zu sehen war.

## [0.18.0]

- WU-0004 (Mockup abgenommen 23.10.2026): Reiter Speedtest – Tagesverlauf unter dem Wochenraster. Tipp auf einen
  Wochentag (Mo–So, auch links im Raster) zeigt den Verlauf aller dieser Tage im Zeitraum, „oder Datum …“ einen
  einzelnen Tag: Median je Stunde als Linie, niedrigste bis höchste Messung als Band, Tarif gestrichelt, beste und
  schwächste Stunde; Tipp auf eine Stunde zeigt Median, Spanne und Anzahl (so auch am Handy). Am breiten Bildschirm
  steht in jeder Kachel des Rasters der Median der Stunde.

## [0.17.0]

- WU-0003 (Teil 1, Mockup abgenommen 14.10.2026): Reiter Geräte, „nach Verbindung“ – Geräte, die sich von unterwegs per
  WireGuard (VPN) mit der Box verbinden, stehen in einer eigenen Gruppe „🔐 VPN (WireGuard)“ ganz oben.

## [0.16.3]

- AN-0004: Neue Geräte-Art „🖨️ Drucker“ – selbst wählbar und erkannt (Brother, Epson, Canon; Modelle wie LaserJet,
  OfficeJet, DeskJet, Pixma, EcoTank, WorkForce; „Drucker“/„Printer“ im Namen). Bisher liefen Drucker unter „Computer“.

## [0.16.2]

- FE-0003: Die Kacheln schweben nicht mehr dauernd leicht auf und ab (Animation aus dem Glas-Stil entfernt); beim Öffnen
  blenden sie weiter kurz ein.

## [0.16.1]

- WU-0002: Der geschätzte Mast bleibt auf der Karte, wenn die Box an einem Sektor hängt, den keine Datenbank kennt –
  einmal gefundene Zellen derselben Sendeanlage zählen einen Monat lang mit. „Passt“ richtet sich nach der Nähe zum
  geschätzten Mast statt nach der Entfernung laut Box, die je Zelle stark schwankt (z. B. 1 km und 4 km für Sektoren
  desselben Masts); das Infofeld sagt, warum ein Mast passt.

## [0.16.0]

- WU-0002 (Mockup abgenommen 14.10.2026): Karte mit ⛶ Vollbild über die ganze Seite. Antippen eines Funkmasts zeigt
  Entfernung, Richtung und – mit OpenCellID-Schlüssel – Anbieter und Technik (2G/3G/LTE/5G) der Zellen, die
  OpenCellID in höchstens 500 m Abstand kennt. Dafür lädt die Integration einmal im Monat im Hintergrund den
  OpenCellID-Datenabzug für Österreich und wertet ihn hier aus (kein Standort geht hinaus). Beschriftung am passenden
  Mast gekürzt, die Quelle OpenStreetMap steht nicht mehr doppelt.

## [0.15.0]

- WU-0002: Neue Ebene „📡 Masten (OSM)“ auf der Karte (Mockup abgenommen 14.10.2026): Funkmasten, die in
  OpenStreetMap eingetragen sind, als graue Dreiecke; der Mast, der am besten zur Entfernung laut Box und zur Richtung
  der gefundenen Zellen passt, ist orange umrandet und beschriftet. Die Integration holt die Masten einmal im Monat im
  Hintergrund (Ausschnitt auf festem Raster, der die Wohnung nur auf etwa 22 × 15 km eingrenzt – nie der eigene Standort). Ein- und ausschalten mit dem
  Knopf rechts oben; die Wahl merkt sich der Browser.

## [0.14.1]

- WU-0002: Läuft 5G mit, steht am Mast der Ankerzelle „4G + 5G (vermutlich)“ – die Box nennt für 5G nur die PCI,
  nachschlagen geht nicht; bei 5G-NSA hängt die 5G-Zelle aber meist am selben Mast. Karte: Beschriftungen weichen zur
  Seite aus, wenn am Rand kein Platz ist; Zellnamen erst beim Hineinzoomen; Knöpfe und Auswahl deckend, auch auf
  heller Grundlage gut lesbar.

## [0.14.0]

- WU-0002: Die Karte „Wo steht der Mast?“ war leer – CARTO verlangt inzwischen einen eigenen Schlüssel und liefert
  sonst nur „API KEY REQUIRED“. Neu ist sie eine echte Karte (Leaflet, Mockup abgenommen 14.10.2026): zoomen mit ＋/−,
  Mausrad oder zwei Fingern, ziehen zum Verschieben, ⌖ zeigt wieder alles. Oben rechts die Grundlage: Automatisch
  (hell basemap.at, dunkel basemap.at grau), basemap.at, basemap.at grau, OpenStreetMap – alle ohne Schlüssel; die
  Wahl merkt sich der Browser.

## [0.13.0]

- WU-0002 (Teil Zellen und Mast, Mockup abgenommen 14.10.2026): Die Integration schlägt jetzt jede Zelle mit voller
  Kennung nach, nicht nur die Ankerzelle – bei **BeaconDB** (neu, ohne Schlüssel) und mit eigenem Schlüssel zusätzlich
  bei OpenCellID; es zählt der genauere Fund. Funk → Mobilfunk: In der Zellenliste stehen TAC, PLMN und wo der Ort
  gefunden wurde („📍 BeaconDB · ±50 m“, „nur PCI – nicht nachschlagbar“). Die Karte zeigt jede gefundene Zelle mit
  Genauigkeitskreis und je Sendeanlage den geschätzten Mast mit Entfernung und Richtung; im Kopf „x von y Zellen
  gefunden“. Hinaus geht nur die Zellkennung, nie der Standort.

## [0.12.0]

- WU-0001: Speedtest-Serie (Mockup abgenommen 13.10.2026). Im Reiter Speedtest „▶ n× messen“: Netzwerk startet n
  Durchläufe bei Ookla nacheinander – den nächsten erst, wenn das Ergebnis des vorigen da ist – und zeigt in der Karte
  „Letzte Serie“ je Download, Upload und Ping den Median mit Spanne (Download auch in % vom Tarif) und die Durchläufe.
  Die Anzahl (2–5, Vorgabe 3) steht im Fenster ⚙ › Messplan. Gibt es in Ookla mehrere Tests (Server), wechselt die
  Serie reihum; ins Wochenraster kommen wie bisher die Messungen des ersten Ookla-Tests, in der Liste als „Serie“
  markiert. Während einer Serie misst der Messplan nicht dazwischen.

## [0.11.3]

- AN-0003: Befund „Keine Internetverbindung“ sagt, was gerade los ist – Mobilfunk steht ohne Neueinwahl („hakt
  vermutlich beim Anbieter“), Box wählt sich neu ein, Empfang schwach, Box selbst nicht erreichbar. Der alte Satz „Die
  Box wählt sich selbst neu ein“ stimmte oft nicht.
- Kurze Ausfälle kurz hintereinander werden zusammengefasst: Ist das Internet 10 Minuten ohne Unterbrechung da, kommt
  ein Eintrag ins Journal, z. B. „Internet-Störung vorbei: 3 Unterbrechungen in 8 min, zusammen 6 min weg – Mobilfunk
  stand (keine Neueinwahl), vermutlich beim Anbieter“. Eine offene Störung übersteht einen Neustart.

## [0.11.2]

- AN-0002: Fenster ⚙ Einstellungen mit Reitern 📈 Speedtest · ⏱️ Messplan · 📶 WLAN · 💬 Meldungen (Mockup abgenommen
  13.10.2026, Variante B); darunter nur die gewählte Gruppe in einer Karte. Ruhigeres Design: Eingaben als Felder mit
  Einheit, Schalter statt Checkbox, je Einstellung eine kurze Erklärung, „Ookla ›“ statt langem Link.

## [0.11.1]

- Geräteliste von Home Assistant über die vorgesehene Iteration lesen; die Warnung „uses `device_registry.devices` as a
  mapping“ (ab HA 2027.9 ein Fehler) entfällt.

## [0.11.0]

- AN-0001 (zweiter Teil, Mockup abgenommen 13.10.2026): In jeder Gerätezeile steht die volle IP-Adresse. Neuer
  Umschalter „nach Verbindung | nach Art“: Gruppen Netzwerk, Smart Home, Haushalt & Roboter, Computer, Handy & Tablet,
  Fernseher & Musik, Kameras, Unbekannt.
- Die Art erkennt die Integration selbst, in dieser Reihenfolge: aus der Geräteliste von Home Assistant (Hersteller und
  Modell von Geräten mit eigener Integration, z. B. Shelly; die Einträge „Tracked device“ von FRITZ!Box Tools zählen
  nicht), aus der Mesh-Liste der FRITZ!Box (Repeater, Powerline; alle 10 Minuten), aus dem Hersteller der
  Hardware-Adresse (Liste offline, `logik/hersteller.txt`, erzeugt mit `tools/hersteller.py`; Zufallsadressen haben
  keinen Hersteller) und aus dem Namen. Im Verlauf eines Geräts steht, woran die Art erkannt wurde; Admins können sie
  selbst festlegen oder auf „automatisch“ zurückstellen (`netzwerk/geraet/art`).

## [0.10.3]

- AN-0001: Geräte kompakter (Mockup abgenommen 13.10.2026, Variante „nach Verbindung“). Die Liste ist in aufklappbare
  Gruppen LAN, WLAN 6/5/2,4 GHz, „WLAN, nicht verbunden“ (anfangs zu), Powerline und Sonstige geteilt, je mit „x von y
  online“. Je Gerät eine Zeile: Symbol, Name, Endung der IP und Band, schmaler 24-h-Streifen, Punkt statt Abzeichen.
  Gruppen und Zahlen liefert die Integration (`netzwerk/geraete`: `gruppen`, je Gerät `verbindung` und `band`).

## [0.10.2]

- FE-0001 (wieder aufgetreten): „Bild wählen“ nimmt ein Bild je Auswahl. Mit Mehrfachauswahl gab die Android-App von
  Home Assistant das gewählte Bild nicht an die Seite weiter – es blieb bei „0 von 3“ ohne jede Meldung. Für ein
  zweites oder drittes Bild einfach noch einmal wählen.

## [0.10.1]

- FE-0001: Screenshot aus der Galerie kam am Handy nicht im Melde-Dialog an („0 von 3“). Die Seite verwarf Bilder ohne
  Typangabe, wie sie die Android-App liefert; jetzt entscheidet das Laden des Bildes. Jeder Schritt meldet sich
  („Bild wird geladen …“, „Bild gewählt“ oder warum nicht), und der Entwurf mit Text und Bildern übersteht ein
  Neuladen der Seite (Speicher des Browsers, bis Senden oder Abbrechen).

## [0.10.0]

- Tickets wie im Baustrommanager (Mockup abgenommen 13.10.2026): Melden-Knopf unten rechts auf jeder Ansicht –
  Fehler, Wunsch oder Anregung mit Text, Reiter, Version, Gerät, „Stand der Seite“ und bis zu 3 Screenshots (am Handy
  aus der Galerie, am PC auch Strg+V und „Fenster aufnehmen“, auf 1600 px verkleinert). Jede Meldung wird ein Ticket
  (FE-0001, WU-0001, AN-0001); die Rückmeldung nennt, wie viele Bilder angekommen sind.
- ⚙ › Meldungen: Tickets offen/erledigt/alle mit Bildern und letzter Notiz; Admins schließen, öffnen wieder, löschen;
  „Als Markdown kopieren“.
- Ablage lesbar unter `<config>/netzwerk/meldungen.json`, `meldungen.md` und `meldungen/`; neue Aktion
  `netzwerk.ticket` (nur Admin) und `tools/ticket.py` zum Abarbeiten in Claude Code, `tools/tickets-fenster.sh` für
  ein eigenes Tickets-Fenster.

## [0.9.0]

- Mobilfunk: Block „Wo steht der Mast?“ (Mockup abgenommen 13.10.2026). Karte um die Wohnung (Standort aus Home
  Assistant) mit Ring für die Entfernung laut Box; mit OpenCellID-Schlüssel zusätzlich der Mast der Ankerzelle mit
  Linie, Entfernung, Himmelsrichtung und Genauigkeit. Kartenkacheln von CARTO/OpenStreetMap wie die Karten von
  Home Assistant, hell oder dunkel nach dem Design.
- Neue Option „OpenCellID-Schlüssel“ (Geräte & Dienste → Netzwerk → Konfigurieren). Nachgeschlagen wird nur die
  Kennung der Ankerzelle (MCC, MNC, TAC, Zellkennung), nie der eigene Standort; Ergebnis einen Monat gemerkt, ohne
  Treffer einen Tag, nicht erreichbar eine Stunde; ein abgelehnter Schlüssel wird auf der Seite gemeldet. Ohne
  Schlüssel geht nichts an OpenCellID. Die Kartenkacheln lädt der Browser von CARTO (sieht den Kartenausschnitt). Die Diagnose schwärzt den Schlüssel.
- Zellliste liest zusätzlich PLMN und TAC je Zelle.

## [0.8.1]

- Mobilfunk aufgeräumt: Der Befund steht zugeklappt als eine Zeile (Punkt in der Farbe der Lage, Titel, ⓘ); Tippen
  klappt den Text auf. Die Erklärung unter der Zellenliste ebenso. Die Werte je Zelle brechen am Handy nicht mehr um.

## [0.8.0]

- Mobilfunk (Mockup abgenommen 13.10.2026): Block „Verbindung zur Basisstation“ statt der Karten „4G-Anker“ und
  „5G“. Eigene Zeichnung FRITZ!Box – Funkstrecke – Masten (5G/4G), die Linie in der Farbe der Signalstärke der
  Ankerzelle, dazu Entfernung zur Basisstation und Anbieter. Darunter alle Zellen der Zellliste (Art, Rolle Anker /
  bündelt dazu / in Reichweite, Zellkennung, vier Balken, RSRP, RSRQ). Die Zeile „Antenne 1 / 2“ entfällt.

## [0.7.0]

- Reiter „Funk“ (statt „Mobilfunk“) mit Umschalter WLAN/Mobilfunk (Mockup abgenommen 12.10.2026).
- WLAN neu: Befunde (Geräte mit schwachem Empfang unter der eingestellten Grenze; Gerät auf 2,4 GHz, das schon auf
  5 GHz verbunden war), Kacheln je Band (Kanal, automatisch/fest, Wi-Fi-Standard, Anzahl Geräte), Gast-WLAN an/aus,
  Geräte im WLAN schwächstes zuerst (Band, Empfang in %, Mbit/s; Tippen öffnet den Verlauf), Kanalwechsel der letzten
  7 Tage. Gelesen über TR-064 WLANConfiguration, nur lesend.
- Mobilfunk erweitert: Empfang je Antenne, „Verbunden seit“, Neueinwahlen der letzten 7 Tage (kommen ins Journal),
  eingeschaltete Bänder.
- Einstellungen an einem Ort: ⚙ im Kopf öffnet ein Fenster mit Speedtest-Auswertung, Messplan und WLAN-Grenze. Der
  Reiter Speedtest zeigt vom Messplan nur noch eine Zeile mit „Jetzt messen“.
- Neue Einstellung „schwacher WLAN-Empfang unter“ 30/40/50 % (Vorgabe 40 %); WebSocket `netzwerk/wlan`.

## [0.6.1]

- Seite am Handy: Das Wochenraster im Reiter Speedtest sprengte die Karte – leere Zellen erbten den Innenabstand des
  Hinweises „keine Messungen“ (gleiche Klasse), dadurch wurde die Spalte mit einer Messung breit und alle Zeilen hoch.
  Eigene Klasse für leere Zellen, Spalten dürfen schrumpfen. Die Tabelle „Letzte Messungen“ bleibt in der Karte und
  scrollt in sich, statt über den Rand zu laufen.

## [0.6.0]

- Messplan (Mockup abgenommen 12.10.2026): die Integration startet Ookla-Messungen selbst – automatisch ein/aus, wie
  oft (1/2/4/6/12/24 h), nur in einem Zeitfenster (auch über Mitternacht). Bei Verkehr im Heimnetz über der Schwelle
  (10 % vom Tarif, ohne Tarif 10 Mbit/s) wird verschoben: alle 5 Minuten neu, höchstens 30 Minuten, danach trotzdem
  (die Messung zählt dann als belastet). „Jetzt messen“ auf der Seite. Nur Admins ändern Plan und messen.
- Seite: Block „Messplan“ im Reiter Speedtest mit Verkehr gerade, nächster Messung, Server aus Ookla, Knopf zu den
  Ookla-Einstellungen und Warnung, wenn Ookla zusätzlich nach eigenem Takt misst. Ooklas Einstellungen ändert die
  Integration nicht.
- Ausgelöst wird gezielt der Ookla-Eintrag, dessen Sensoren gelesen werden; nur ein geladener Eintrag zählt. Eine
  gesetzte Startzeit in Ookla gilt als „misst selbst“ (Ookla plant dann auch auf „manuell“). Ein Fehler im Messplan
  macht keine Entität unverfügbar.

## [0.5.1]

- Kein Umzug: Übernahme der Altdaten (`netzdiagnose/data`), Lesen der alten Statistiken (Speedtest.net,
  `netz_mobil_*`) und Tarif aus den alten Helfern entfernt. Die Integration fängt leer an; den Tarif setzt man auf der
  Seite.

## [0.5.0]

- Etappe 4: eigene Seite „Netzwerk“ in der Seitenleiste nach dem abgenommenen Mockup (`mockups/netzwerk.html`), mit Lit
  gebaut und zu `frontend/netzwerk-panel.js` gebündelt (esbuild), Glas-Design wie die Baustelle: Hintergrund nach
  Tageszeit, hell/dunkel nach dem HA-Theme, Reiter Übersicht, Speedtest (Wochenraster, Grundlast, Server, letzte
  Messungen, Einstellungen), Geräte (24-h-Streifen, Filter, Einblendung mit 7 Tagen), Mobilfunk, Verbrauch, Protokoll.
  Daten nur über die WebSocket-Befehle; die Seite lädt jede Minute neu.
- Die Seite steht in der Seitenleiste („Netzwerk“, Symbol Router – anders als das alte Dashboard), solange die
  Integration geladen ist; eine belegte Adresse wird nicht überschrieben. Ausgeliefert wird nur die gebaute Datei.
- Nur noch eine Einrichtung (eine FRITZ!Box je Haushalt).
- Seite: nur die Antwort der neuesten Abfrage zählt (schnelles Umschalten), eine geschlossene Einblendung bleibt zu;
  „online 7 Tage“ zählt nur aufgezeichnete Zeit.
- Seitentests mit happy-dom gegen eine Vorlage, deren Form ein Integrationstest mit den echten Antworten vergleicht.

## [0.4.0]

- Etappe 3: Auswertung als Fachlogik (aus den Karten des Altbestands übernommen, Quantile gegen die JavaScript-Fassung
  geprüft): Speedtest-Wochenraster Wochentag × Stunde mit Median, Lage auf der Farbskala, Gewichtung belasteter
  Messungen (weglassen, ¼, voll), Server-Filter, Hinweis „auffällig“ (abends deutlich langsamer), geschätztes
  Datenvolumen der Messungen; Verbrauch je Tag mit Anteil der Speedtests; Befund zum Mobilfunk-Empfang; Verlauf je Gerät
  (24-h-Streifen, „wackelt“ ab 3 Abbrüchen, „neu“).
- Vor dem ersten eigenen Eintrag zählt die Langzeit-Statistik der alten Speedtest.net-Sensoren mit (ohne Server und
  Grundlast); der Mobilfunk-Verlauf nimmt davor die Statistik der alten `netz_mobil_*`-Sensoren.
- WebSocket-Befehle der Seite: `netzwerk/uebersicht`, `/speedtest`, `/geraete`, `/geraet`, `/mobilfunk`, `/verbrauch`,
  `/protokoll` (Suche in der Datenbank), `/einstellungen`, `/einstellungen/setzen` (nur Admin).
- Datenschutz: Geräte tragen an der Seite eine gesalzene Kennung statt der Hardware-Adresse; aus allen Texten an die
  Seite werden Hardware-Adressen entfernt. Neue Journalzeilen nennen Geräte nur noch beim Namen (ohne Adressendung),
  Geräte ohne Namen heißen „Gerät ohne Namen“.
- Einstellungen Tarif Download/Upload und „Auswerten ab“ im Integrations-Speicher; beim ersten Start (sobald HA ganz
  gestartet ist) aus den Helfern des Altbestands übernommen, jedes Feld für sich (0 = kein Tarif).

## [0.3.0]

- Etappe 2: eigene Datenbank `netzwerk/netzwerk.db` in der HA-Konfiguration (SQLite, Schema-Version 1) für Journal,
  Protokoll der Box, Speedtest-Messungen und das Gedächtnis zwischen zwei Abrufen. Nach einem Neustart von HA keine
  doppelten Protokollzeilen und keine „neuen“ Geräte. Journal und Protokoll bleiben 400 Tage, Messungen immer.
- Speedtest-Protokoll: jede neue Messung der Ookla-Integration wird mit Server und Grundlast eingetragen (Sensoren
  über das Entitätsregister gefunden; auch nachträglich installiert). Eine Messung, die nicht gespeichert werden
  konnte, wird beim nächsten Abruf nachgeholt.
- Einmalige Übernahme der Daten des Altbestands (`netzdiagnose/data`: Journal, Protokoll, Speedtest-Protokoll,
  Gedächtnis des Sammlers); der Altbestand bleibt unverändert.
- Während einer HA-Sicherung ruht das Schreiben in die Datenbank (Warteschlange). Ein Schreibfehler macht keine
  Entität unverfügbar; die Zeilen gehen beim nächsten Abruf mit. Das Gedächtnis wird nur bei echten Änderungen
  geschrieben (schont die SD-Karte).

## [0.2.0]

- Etappe 1: Abruf der FRITZ!Box jede Minute über fritzconnection (64-Bit-Byte-Zähler), Zugang aus FRITZ!Box Tools (Einrichtung wählt die
  Box). Fachlogik aus dem Altbestand übernommen: Ereignisprotokoll, Geräteabgleich, Befunde, Mobilfunk, Verkehr und
  Grundlast, Prüfungen vom Pi, DHCP-Test alle 10 Minuten.
- Sensoren Gesamtstand, Offene Befunde, Geräte online, Mobilfunk Technik und Empfang; Binärsensoren für die Prüfungen
  vom Pi. Box nicht erreichbar → Box-abhängige Werte nicht verfügbar; Reparatur-Hinweise bei fehlendem FRITZ!Box Tools
  oder abgelehnter Anmeldung; Diagnose ohne Namen und Adressen.
- Steckbrief `docs/steckbrief.md` und `module.yaml`.

## [0.1.0]

- Grundgerüst von projekt-anlegen erzeugt (siehe `.projekt-anlegen.json`): Start, Tests und Prüfungen laufen, noch
  ohne Fachlogik.
