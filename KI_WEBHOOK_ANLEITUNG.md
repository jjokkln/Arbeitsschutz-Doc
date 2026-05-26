# KI-Webhook-Anleitung für n8n

## Ziel
Eine bestehende Stellenbeschreibung, ein PDF oder ein Foto wird analysiert und als strukturiertes JSON an das Tool zurückgegeben.

## Einfacher n8n-Aufbau
1. **Webhook**
   - Methode: `POST`
   - Response: über eigenen `Respond to Webhook` Node
   - Binary Data aktivieren, damit Uploads angenommen werden

2. **KI-/OCR-Schritt**
   - Für PDF/DOCX: Dateiinhalt extrahieren oder direkt an ein Modell mit File-Input geben
   - Für Fotos: Vision/OCR-Modell nutzen
   - Prompt aus `n8n-systemprompt.txt` verwenden
   - `schema` aus dem Webhook-Body als Zielstruktur mitgeben

3. **JSON normalisieren**
   - Ergebnis muss ein Objekt mit `fields`, `riskRows`, `psaRows`, `instructionRows`, `orgRows` sein
   - Keine Markdown-Codeblöcke zurückgeben
   - Keine erfundenen Angaben ergänzen

4. **Respond to Webhook**
   - Status: `200`
   - Body: reines JSON
   - Header: `Content-Type: application/json`

## Wichtig
Der Browser wartet direkt auf die Antwort. Der Workflow sollte daher synchron antworten und nicht nur später eine Mail oder Sheet-Zeile erstellen.
