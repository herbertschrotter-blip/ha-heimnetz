"""Sprache der Texte, die die Integration erzeugt (WU-0006): Deutsch oder Englisch nach der Sprache von Home Assistant
(`hass.config.language`). „de“ und jede Variante davon (de-AT, de_CH …) ergibt Deutsch, alles andere Englisch.

Wie auf der Seite (`frontend/src/sprache.js`): Der deutsche Text steht im Code und ist zugleich der Schlüssel;
`t("Kanal {k}", sprache, k=6)` liefert auf Deutsch den Text selbst, auf Englisch die Zeile aus EN. Platzhalter
{name} füllt t() aus den Werten. `merke("…")` kennzeichnet Texte in Konstanten, die erst später über t() laufen; ein
gemerkter Text als Wert eines Platzhalters wird mitübersetzt. Der Test `tests/logik/test_sprache.py` prüft, dass zu
jedem Text eine englische Zeile mit denselben Platzhaltern da ist.

Was einmal gespeichert ist (Journal, Momentaufnahme), bleibt in der Sprache, in der es entstand.
"""

from __future__ import annotations

import re

from .englisch import EN

DE, ENG = "de", "en"
SPRACHEN = (DE, ENG)
_PLATZHALTER = re.compile(r"\{(\w+)\}")


def waehle(sprache: str | None) -> str:
    """„de“ für Deutsch und seine Varianten, sonst „en“."""
    s = (sprache or "").lower()
    return DE if s == DE or s.startswith(("de-", "de_")) else ENG


class Wort(str):
    """Gemerkter Text (merke): als Wert eines Platzhalters übersetzt t() ihn mit."""

    __slots__ = ()


def merke(text: str) -> Wort:
    """Kennzeichnet einen Text zum Übersetzen, ohne ihn zu übersetzen (Konstanten)."""
    return Wort(text)


def t(text: str, sprache: str = DE, /, **werte: object) -> str:
    """Text in der Sprache; fehlt eine englische Zeile, bleibt der deutsche Text (der Test meldet das)."""
    vorlage = str(text) if sprache == DE else EN.get(text, str(text))
    if not werte:
        return vorlage

    def ersetzen(m: re.Match[str]) -> str:
        if m.group(1) not in werte:
            return m.group(0)
        w = werte[m.group(1)]
        return t(w, sprache) if isinstance(w, Wort) else str(w)

    return _PLATZHALTER.sub(ersetzen, vorlage)


def zahl(wert: float, stellen: int = 0, sprache: str = DE) -> str:
    """Zahl mit Tausendertrennung: Deutsch 1.234,5, Englisch 1,234.5."""
    s = f"{wert:,.{stellen}f}"
    return s.replace(",", " ").replace(".", ",").replace(" ", ".") if sprache == DE else s


class Ungueltig(ValueError):
    """Wert verständlich abgelehnt: deutscher Text als Vorlage, `text(sprache)` für die Oberfläche. str() ist die
    deutsche Fassung (Protokoll, Tests)."""

    def __init__(self, vorlage: str, /, **werte: object) -> None:
        self.vorlage, self.werte = vorlage, werte
        super().__init__(t(vorlage, DE, **werte))

    def text(self, sprache: str) -> str:
        return t(self.vorlage, sprache, **self.werte)
