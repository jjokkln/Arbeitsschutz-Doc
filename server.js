require('dotenv').config();
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const Anthropic = require('@anthropic-ai/sdk');

const app = express();
app.use(cors());
app.use(express.json({ limit: '5mb' }));

// Serve static files from the 'public' directory if it exists, otherwise root
app.use(express.static(__dirname));

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

app.post('/api/parse', async (req, res) => {
  try {
    const { text } = req.body;
    
    if (!text) {
      return res.status(400).json({ error: 'Kein Text übergeben.' });
    }

    // Lese das Schema ein
    const schemaPath = path.join(__dirname, 'ki-schema.json');
    const schemaRaw = fs.readFileSync(schemaPath, 'utf8');

    const systemPrompt = `Du bist ein Assistent, der Rohtext in ein striktes JSON-Format für eine Arbeitssicherheits-App umwandelt.
Extrahieren alle Informationen aus dem übergebenen Text und ordne sie den passenden Feldern zu.
Gebe AUSSCHLIESSLICH das fertige, gültige JSON-Objekt zurück. Erfinde keine Fakten. Fehlen Informationen, lasse die Felder leer.
Nutze exakt die Struktur des folgenden Schemas. Vermeide Markdown-Codeblöcke wie \`\`\`json, gebe nur den nackten JSON-String aus.

SCHEMA:
${schemaRaw}`;

    const msg = await anthropic.messages.create({
      model: "claude-haiku-4-5",
      max_tokens: 4096,
      temperature: 0,
      system: systemPrompt,
      messages: [
        {
          role: "user",
          content: `Hier ist der Text mit den gesammelten Informationen:\n\n${text}`
        }
      ]
    });

    let rawOutput = msg.content[0].text.trim();
    
    // Falls Claude doch Markdown benutzt hat, entferne es
    if (rawOutput.startsWith('```json')) {
      rawOutput = rawOutput.replace(/^```json/, '').replace(/```$/, '').trim();
    } else if (rawOutput.startsWith('```')) {
      rawOutput = rawOutput.replace(/^```/, '').replace(/```$/, '').trim();
    }

    const jsonOutput = JSON.parse(rawOutput);
    res.json(jsonOutput);

  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ error: error.message || 'Interner Server Fehler' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server läuft auf http://localhost:${PORT}`);
});
