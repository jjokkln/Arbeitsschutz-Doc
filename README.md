# Arbeitssicherheit Word-Generator mit KI-Import

## Start
1. ZIP entpacken
2. `index.html` im Browser öffnen
3. Logos hochladen, Daten prüfen, Word-Dokument erstellen

## Neu in dieser Version
- PDF-/Foto-/DOCX-/TXT-Upload für bestehende Stellenbeschreibungen
- KI-Webhook-Feld für n8n oder eigenen API-Endpunkt
- Automatisches Befüllen der Formularfelder aus KI-JSON
- Modus „ersetzen“ oder „nur leere Felder ergänzen“
- JSON-Schema direkt im Tool herunterladbar
- Lokale Rohtext-Vorbefüllung ohne KI als Notlösung

## Wichtiger Hinweis zur KI
Das Tool ist bewusst browserbasiert. OpenAI-/Gemini-/Claude-API-Keys sollten nicht direkt in `index.html` stehen, weil sie sonst sichtbar wären.

Empfohlener Aufbau:
Browser-Tool → n8n Webhook → KI-Modell/OCR → JSON zurück ans Tool

## Webhook Request
Das Tool sendet per `multipart/form-data`:
- `file`: hochgeladene Datei, falls vorhanden
- `raw_text`: eingefügter Text
- `schema`: gewünschtes Antwortschema
- `current_data`: aktueller Formularstand
- `merge_mode`: `overwrite` oder `fill-empty`
- `format`: `arbeitssicherheit_docx_schema_v1`

## Webhook Response
Der Webhook muss valides JSON zurückgeben. Beispiel:

```json
{
  "fields": {
    "clientCompany": "Muster Logistik GmbH",
    "position": "Staplerfahrer",
    "area": "Zentrallager",
    "duties": "Wareneingang\nBe- und Entladung\nSichtprüfung",
    "equipment": "Gabelstapler\nScanner",
    "requirements": "Staplerschein\nDeutschkenntnisse"
  },
  "riskRows": [
    {
      "area": "Transport & mobile Arbeitsmittel",
      "risk": "Fahrverkehr und Rangieren",
      "measures": "Unterweisung, Fahrwege nutzen, Geschwindigkeit anpassen",
      "rating": "Ausreichend",
      "owner": "Einsatzbetrieb",
      "status": "laufend"
    }
  ],
  "psaRows": [
    {
      "item": "Sicherheitsschuhe S3",
      "required": "Ja",
      "provided": "Zeitarbeitunternehmen",
      "note": "Im Lagerbereich"
    }
  ]
}
```

## Dateien
- `index.html`: fertiges Mini-Tool
- `ki-schema.json`: erwartetes KI-Antwortformat
- `n8n-systemprompt.txt`: Prompt für den KI-Schritt
- `KI_WEBHOOK_ANLEITUNG.md`: kurze n8n-Anleitung
