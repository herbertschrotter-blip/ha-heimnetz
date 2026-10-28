"""Warnungen (WU-0010): wer überwacht wird, wann ein Gerät als offline gemeldet wird und was zurück kommt – ohne Home
Assistant. Versand (notify-Dienst, Ereignis `heimnetz_warnung`, Journal) macht der dünne Teil `warnungen.py`.

Überwacht wird nach Art (AN-0001 und eigene Arten), mit Ausnahmen je Gerät (immer/nie). Zustand je Gerät:

    online ──(weg)──▶ weg seit t ──(Verzögerung um)──▶ gemeldet ──(wieder da)──▶ online („wieder online“, mit Dauer)
                       └──(vor Ablauf wieder da)──▶ online (keine Meldung – kein Flattern)

Ein Gerät, das nicht überwacht wird, geht beim Verschwinden still auf „aus“; wird es später überwacht, meldet es sich
erst, nachdem es einmal wieder online war – Einschalten einer Art löst keine Welle von Meldungen aus.

- Neustart von Home Assistant: der Zustand liegt nur im Speicher. Den Grundzustand übernimmt der erste Abruf, der die
  Gerätetabelle der Box hat; offline ist dann „aus“, ohne Meldung.
- Box nicht erreichbar: keine Gerätemeldungen (alle wären weg), der Zustand bleibt stehen. Ist Box oder Internet weg,
  zählt das als Ausfall; gemeldet wird er erst, wenn beides wieder geht (Push braucht Internet) – mit Dauer, und nur,
  wenn er mindestens so lange war wie die Verzögerung. Meldungen von Geräten während eines Ausfalls des Internets
  gehen erst danach hinaus (Ereignis und Journal sofort).
- Neues Gerät: nicht unter den je gesehenen (`Waechter.bekannt`, vom Aufrufer gespeichert und beim Start aus
  Gedächtnis und Journal gefüllt) – höchstens eine Meldung je Gerät, auch nach dem Aufräumen des Journals.
- Leere oder stark geschrumpfte Gerätetabelle bei erreichbarer Box: wie „Box nicht erreichbar“. Danach eine Frist von
  einer Verzögerung, bevor ein Gerät als offline gilt (nach einem Neustart der Box melden sich Geräte nach und nach).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, tzinfo
from typing import Any

from .geraete import anzeigename
from .sprache import DE, Ungueltig, merke, t, waehle
from .werte import ohne_mac

KEINE, ALLE = "keine", "alle"  # Ziel: nur Ereignis / alle Companion Apps (notify.mobile_app_*)
MOBILE_APP = "mobile_app_"
VERZOEGERUNGEN = (2, 5, 15, 60)  # Minuten
VORGABE_VERZOEGERUNG = 5
# Vorgabe je Art: Infrastruktur und Geräte, die immer da sein sollen; Handys gehen unterwegs dauernd offline
VORGABE_AN = frozenset({"netz", "smart", "haushalt", "kamera"})
AUSGENOMMEN = {"mobil": merke("ausgenommen – gehen unterwegs dauernd offline")}
IMMER, NIE, GRUPPE = "immer", "nie", "gruppe"
AUSNAHMEN = (IMMER, NIE)
ARTEN = ("offline", "online", "neu", "internet", "test")
ZURUECK_HOECHSTENS = 20  # so viele Meldungen warten höchstens auf das Internet
_DIENST = re.compile(r"^[a-z0-9_]{1,100}$")

ONLINE, WEG, GEMELDET, AUS = "online", "weg", "gemeldet", "aus"


@dataclass(frozen=True)
class Warneinstellungen:
    """Gespeichert im Einstellungsdienst. `arten` und `geraete` enthalten nur, was vom Vorgabewert abweicht bzw.
    eine Ausnahme ist; `sprache` ist die der Seite beim letzten Speichern (Texte der Nachrichten)."""

    ziel: str = KEINE
    verzoegerung: int = VORGABE_VERZOEGERUNG
    arten: dict[str, bool] = field(default_factory=dict)
    geraete: dict[str, str] = field(default_factory=dict)  # Geräte-Kennung → immer/nie
    wieder: bool = True
    neu: bool = True
    internet: bool = True
    sprache: str = DE

    def art_an(self, kat: str) -> bool:
        return self.arten.get(kat, kat in VORGABE_AN)

    def ausnahme(self, kennung: str) -> str:
        return self.geraete.get(kennung, GRUPPE)

    def ueberwacht(self, kat: str, kennung: str) -> bool:
        """Ausnahme des Geräts vor der Art."""
        a = self.geraete.get(kennung)
        return True if a == IMMER else False if a == NIE else self.art_an(kat)

    def als_dict(self) -> dict[str, Any]:
        return {
            "ziel": self.ziel,
            "verzoegerung": self.verzoegerung,
            "arten": dict(self.arten),
            "geraete": dict(self.geraete),
            "wieder": self.wieder,
            "neu": self.neu,
            "internet": self.internet,
            "sprache": self.sprache,
        }


def _schalter(wert: Any, name: str, vorgabe: bool) -> bool:
    if wert is None:
        return vorgabe
    if not isinstance(wert, bool):
        raise Ungueltig("{name}: an oder aus", name=name)
    return wert


def pruefen(
    daten: Mapping[str, Any], arten: Iterable[str], dienste: Iterable[str] | None = None
) -> Warneinstellungen:
    """Aus Eingaben oder gespeichertem dict. `arten` = bekannte Arten (feste und eigene): Schalter anderer Arten fallen
    still weg (gelöschte eigene Art). `dienste` = vorhandene notify-Dienste; None = nicht prüfen (beim Laden sind
    noch nicht alle Dienste da)."""
    ziel = str(daten.get("ziel") or KEINE)
    if ziel not in (KEINE, ALLE) and not _DIENST.match(ziel):
        raise Ungueltig("Nachricht an: kein notify-Dienst")
    if dienste is not None and ziel not in (KEINE, ALLE) and ziel not in set(dienste):
        raise Ungueltig("Nachricht an: den Dienst notify.{dienst} gibt es nicht", dienst=ziel)
    roh = daten.get("verzoegerung")
    try:
        verz = VORGABE_VERZOEGERUNG if roh in (None, "") else int(roh)
    except (TypeError, ValueError) as err:
        raise Ungueltig("Offline melden nach: keine Zahl") from err
    if verz not in VERZOEGERUNGEN:
        raise Ungueltig(
            "Offline melden nach: {werte} Minuten", werte=", ".join(map(str, VERZOEGERUNGEN))
        )
    bekannt = set(arten)
    art_roh = daten.get("arten") or {}
    geraete_roh = daten.get("geraete") or {}
    return Warneinstellungen(
        ziel=ziel,
        verzoegerung=verz,
        arten={
            str(k): v
            for k, v in (art_roh.items() if isinstance(art_roh, dict) else ())
            if k in bekannt and isinstance(v, bool)
        },
        geraete={
            str(k): str(v)
            for k, v in (geraete_roh.items() if isinstance(geraete_roh, dict) else ())
            if v in AUSNAHMEN
        },
        wieder=_schalter(daten.get("wieder"), merke("Wieder online"), True),
        neu=_schalter(daten.get("neu"), merke("Neues unbekanntes Gerät"), True),
        internet=_schalter(daten.get("internet"), merke("Internet oder FRITZ!Box weg"), True),
        sprache=waehle(str(daten.get("sprache") or DE)),
    )


def ziel_dienste(ziel: str, vorhanden: Iterable[str]) -> list[str]:
    """Welche notify-Dienste eine Nachricht bekommen: keiner, alle Companion Apps oder der gewählte (falls da)."""
    liste = sorted(vorhanden)
    if ziel == KEINE:
        return []
    if ziel == ALLE:
        return [d for d in liste if d.startswith(MOBILE_APP)]
    return [ziel] if ziel in liste else []


# ── Texte ──
def dauer_text(sekunden: float, sprache: str = DE) -> str:
    """„5 min“, „2 h 5 min“, „3 Tage 4 h“ (Englisch „3 days 4 h“); unter einer Minute „1 min“."""
    m = max(1, int(sekunden // 60))
    if m < 60:
        return f"{m} min"
    h, m = divmod(m, 60)
    if h < 24:
        return f"{h} h {m} min" if m else f"{h} h"
    d, h = divmod(h, 24)
    tage = t("{n} Tag", sprache, n=d) if d == 1 else t("{n} Tage", sprache, n=d)
    return f"{tage} {h} h" if h else tage


def _uhr(ts: float | None, tz: tzinfo) -> str:
    return datetime.fromtimestamp(ts, tz).strftime("%H:%M") if ts else "–"


@dataclass(frozen=True)
class Meldung:
    """Eine Warnung. `schluessel` (Hardware-Adresse) bleibt in der Integration (Journal je Gerät), geht nie ins
    Ereignis oder an die Seite."""

    art: str  # offline, online, neu, internet, test
    t: float
    schluessel: str = ""
    name: str = ""
    ip: str = ""
    verbindung: str = ""
    dauer_s: float | None = None
    zuletzt: float | None = None  # offline: zuletzt online gesehen
    von: float | None = None  # internet: Ausfall von … bis t
    box: bool = False  # internet: die FRITZ!Box war (auch) nicht erreichbar
    zufall: bool = False  # neu: zufällige private WLAN-Adresse

    def text(self, sprache: str, tz: tzinfo) -> str:
        n = ohne_mac(anzeigename(self.name, sprache))
        dauer = dauer_text(self.dauer_s or 0, sprache)
        v = self.verbindung or "–"
        if self.art == "offline":
            return t(
                "{name} ist seit {dauer} offline (zuletzt {uhr}, {verbindung})",
                sprache,
                name=n,
                dauer=dauer,
                uhr=_uhr(self.zuletzt, tz),
                verbindung=v,
            )
        if self.art == "online":
            return t(
                "{name} ist wieder online – war {dauer} weg ({verbindung})",
                sprache,
                name=n,
                dauer=dauer,
                verbindung=v,
            )
        if self.art == "neu":
            text = t(
                "Neues Gerät im Heimnetz: {name}, IP {ip}, {verbindung}",
                sprache,
                name=n,
                ip=self.ip or "–",
                verbindung=v,
            )
            if self.zufall:
                text += " – " + t(
                    "zufällige Adresse – vermutlich ein bekanntes Handy/Tablet", sprache
                )
            return text
        if self.art == "internet":
            return t(
                "FRITZ!Box war {dauer} nicht erreichbar ({von}–{bis})"
                if self.box
                else "Internet war {dauer} weg ({von}–{bis})",
                sprache,
                dauer=dauer,
                von=_uhr(self.von, tz),
                bis=_uhr(self.t, tz),
            )
        return t("Testnachricht von Heimnetz – so kommen Warnungen an.", sprache)

    def ereignis(self, sprache: str, tz: tzinfo) -> dict[str, Any]:
        """Daten des Ereignisses `heimnetz_warnung` für eigene Automationen (ohne Hardware-Adresse)."""
        return {
            "art": self.art,
            "geraet": ohne_mac(anzeigename(self.name, sprache)) if self.name else None,
            "ip": self.ip or None,
            "verbindung": self.verbindung or None,
            "dauer": None if self.dauer_s is None else int(self.dauer_s),
            "nachricht": self.text(sprache, tz),
        }


def test(jetzt: float) -> Meldung:
    return Meldung("test", jetzt)


def beispiel(jetzt: float, name: str, verbindung: str, verzoegerung: int) -> Meldung:
    """Beispiel für ⚙ › Warnungen: so sähe die Meldung „offline“ aus."""
    return Meldung(
        "offline",
        jetzt,
        name=name,
        verbindung=verbindung,
        dauer_s=verzoegerung * 60,
        zuletzt=jetzt - verzoegerung * 60,
    )


# ── Zustand ──
FEHLT_ABRUFE = (
    3  # so viele volle Abrufe muss ein Gerät in der Tabelle fehlen, bis sein Zustand vergessen wird
)
GESCHRUMPFT = 0.5  # Tabelle kleiner als die Hälfte des letzten vollen Abrufs: gilt als Lücke, nicht als Wahrheit
BEKANNT_HOECHSTENS = 5000  # gemerkte Geräte (älteste fallen zuerst weg)


@dataclass(frozen=True)
class Beobachtung:
    """Ein Gerät in einem Abruf. `schluessel` ist eine feste Kennung des Geräts (in der Integration die
    Hardware-Adresse), `zufall` = zufällige private WLAN-Adresse (Handy/Tablet)."""

    schluessel: str
    name: str
    ip: str
    aktiv: bool
    verbindung: str = ""
    zufall: bool = False


@dataclass
class Zustand:
    stand: str  # online, weg, gemeldet, aus
    seit: float  # weg/gemeldet: seit wann weg
    zuletzt: float | None  # zuletzt online gesehen
    name: str
    ip: str
    verbindung: str
    fehlt: int = 0  # volle Abrufe in Folge ohne dieses Gerät


@dataclass(frozen=True)
class Ergebnis:
    """`neu`: gerade entstanden – Ereignis und Journal sofort. `senden`: jetzt per notify hinausschicken (enthält
    zurückgehaltene Meldungen aus einem Ausfall des Internets)."""

    neu: tuple[Meldung, ...] = ()
    senden: tuple[Meldung, ...] = ()


def kuerzen(liste: list[Meldung], hoechstens: int) -> list[Meldung]:
    """Älteste zuerst verwerfen; mit einer „offline“-Meldung auch das spätere „wieder online“ desselben Geräts (sonst
    käme „wieder online“ ohne das „offline“ davor)."""
    rest = list(liste)
    while len(rest) > hoechstens:
        m = rest.pop(0)
        if m.art == "offline":
            paar = next(
                (x for x in rest if x.art == "online" and x.schluessel == m.schluessel), None
            )
            if paar is not None:
                rest.remove(paar)
    return rest


@dataclass
class Waechter:
    """Zustand der Warnungen – im Speicher; nach einem Neustart neu aus dem ersten vollständigen Abruf. Nur `bekannt`
    (je gesehene Geräte) speichert der Aufrufer, damit „neues Gerät“ auch nach Jahren nur wirklich Neue meldet."""

    geraete: dict[str, Zustand] = field(default_factory=dict)
    grundzustand: bool = False
    ausfall_seit: float | None = None
    ausfall_box: bool = False
    zurueck: list[Meldung] = field(default_factory=list)
    bekannt: dict[str, None] = field(default_factory=dict)  # geordnet: älteste zuerst
    bekannt_geaendert: bool = False
    voll: int = 0  # Geräte im letzten vollen Abruf
    luecke: bool = False  # Gerätetabelle fehlte oder war unbrauchbar
    ruhe_ab: float | None = (
        None  # Tabelle nach einer Lücke wieder da: Frist für „weg“ zählt ab hier
    )

    def schritt(
        self,
        jetzt: float,
        box_erreichbar: bool,
        internet: bool,
        geraete: Iterable[Beobachtung],
        einst: Warneinstellungen,
        ueberwacht: Callable[[str], bool],
    ) -> Ergebnis:
        """Ein Abruf. Eine leere oder stark geschrumpfte Gerätetabelle bei erreichbarer Box gilt für die Geräte wie
        „Box nicht erreichbar“ (kein Schritt) – sonst gingen Zustände verloren und es käme eine Welle „neu“."""
        meldungen: list[Meldung] = []
        frei = box_erreichbar and internet
        if not frei:
            if self.ausfall_seit is None:
                self.ausfall_seit = jetzt
            self.ausfall_box = self.ausfall_box or not box_erreichbar
        elif self.ausfall_seit is not None:
            dauer = jetzt - self.ausfall_seit
            if einst.internet and dauer >= einst.verzoegerung * 60:
                meldungen.append(
                    Meldung(
                        "internet",
                        jetzt,
                        dauer_s=dauer,
                        von=self.ausfall_seit,
                        box=self.ausfall_box,
                    )
                )
            self.ausfall_seit, self.ausfall_box = None, False

        liste = list(geraete)
        brauchbar = (
            box_erreichbar
            and bool(liste)
            and not (self.voll and len(liste) < self.voll * GESCHRUMPFT)
        )
        if brauchbar:
            if self.luecke and self.grundzustand:
                self.ruhe_ab = jetzt  # nach einem Neustart der Box melden sich Geräte erst nach und nach zurück
            self.luecke = False
            meldungen += self._geraete(jetzt, liste, einst, ueberwacht)
            self.voll = len(liste)
        else:
            self.luecke = True

        if not frei:
            self.zurueck = kuerzen(self.zurueck + meldungen, ZURUECK_HOECHSTENS)
            return Ergebnis(tuple(meldungen), ())
        # zuerst die Meldung zum Ausfall, dann was während des Ausfalls zurückgehalten wurde, dann der Rest
        erst = meldungen[:1] if meldungen and meldungen[0].art == "internet" else []
        senden = tuple(erst + self.zurueck + meldungen[len(erst) :])
        self.zurueck = []
        return Ergebnis(tuple(meldungen), senden)

    def _merken(self, schluessel: str) -> None:
        self.bekannt[schluessel] = None
        self.bekannt_geaendert = True
        while len(self.bekannt) > BEKANNT_HOECHSTENS:
            del self.bekannt[next(iter(self.bekannt))]

    def _geraete(
        self,
        jetzt: float,
        liste: list[Beobachtung],
        einst: Warneinstellungen,
        ueberwacht: Callable[[str], bool],
    ) -> list[Meldung]:
        out: list[Meldung] = []
        verz = einst.verzoegerung * 60
        # noch nie etwas gemerkt (neue Installation): die Geräte von jetzt sind die bekannten, keine Meldung „neu“
        frisch = not self.bekannt
        for b in liste:
            if b.schluessel not in self.bekannt:
                if einst.neu and not frisch:
                    out.append(
                        Meldung(
                            "neu", jetzt, b.schluessel, b.name, b.ip, b.verbindung, zufall=b.zufall
                        )
                    )
                self._merken(b.schluessel)
        if not self.grundzustand:
            # erster Abruf mit Gerätetabelle: Grundzustand übernehmen, nichts melden (kein Schwall nach dem Neustart)
            for b in liste:
                self.geraete[b.schluessel] = self._neu(b, jetzt)
            self.grundzustand = True
            return out
        ruhe = self.ruhe_ab or 0.0
        for b in liste:
            z = self.geraete.get(b.schluessel)
            if z is None:
                self.geraete[b.schluessel] = self._neu(b, jetzt)
                continue
            z.fehlt = 0
            z.name, z.ip = b.name, b.ip or z.ip
            if b.aktiv:
                if z.stand == GEMELDET and einst.wieder:
                    out.append(
                        Meldung(
                            "online",
                            jetzt,
                            b.schluessel,
                            z.name,
                            z.ip,
                            b.verbindung or z.verbindung,
                            jetzt - z.seit,
                        )
                    )
                z.stand, z.zuletzt, z.verbindung = ONLINE, jetzt, b.verbindung or z.verbindung
                continue
            if z.stand == ONLINE:
                z.stand, z.seit = (WEG if ueberwacht(b.schluessel) else AUS), jetzt
            elif z.stand == WEG:
                if not ueberwacht(b.schluessel):
                    z.stand = AUS
                elif jetzt - max(z.seit, ruhe) >= verz:
                    out.append(
                        Meldung(
                            "offline",
                            jetzt,
                            b.schluessel,
                            z.name,
                            z.ip,
                            z.verbindung,
                            jetzt - z.seit,
                            z.zuletzt,
                        )
                    )
                    z.stand = GEMELDET
        da = {b.schluessel for b in liste}
        for k in [
            k for k in self.geraete if k not in da
        ]:  # aus der Gerätetabelle der Box entfernt?
            self.geraete[k].fehlt += 1
            if self.geraete[k].fehlt >= FEHLT_ABRUFE:
                del self.geraete[k]
        return out

    @staticmethod
    def _neu(b: Beobachtung, jetzt: float) -> Zustand:
        return Zustand(
            ONLINE if b.aktiv else AUS,
            jetzt,
            jetzt if b.aktiv else None,
            b.name,
            b.ip,
            b.verbindung if b.aktiv else "",
        )

    def zaehlen(self) -> dict[str, int]:
        """Für die Diagnose: wie viele Geräte in welchem Zustand (keine Namen)."""
        out = {ONLINE: 0, WEG: 0, GEMELDET: 0, AUS: 0}
        for z in self.geraete.values():
            out[z.stand] = out.get(z.stand, 0) + 1
        return out
