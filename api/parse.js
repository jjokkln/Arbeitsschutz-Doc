const fs = require('fs');
const path = require('path');
const Anthropic = require('@anthropic-ai/sdk');

// In a Vercel Serverless Function, standard process.env is populated.
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

module.exports = async function handler(req, res) {
  // CORS Headers allowing any origin for testing, or restricted to your domain
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { text } = req.body;
    
    if (!text) {
      return res.status(400).json({ error: 'Kein Text übergeben.' });
    }

    // Lese das Schema direkt über require ein, damit Vercel es automatisch bündelt
    const schemaObj = require('../ki-schema.json');
    const schemaRaw = JSON.stringify(schemaObj, null, 2);

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
    
    if (rawOutput.startsWith('```json')) {
      rawOutput = rawOutput.replace(/^```json/, '').replace(/```$/, '').trim();
    } else if (rawOutput.startsWith('```')) {
      rawOutput = rawOutput.replace(/^```/, '').replace(/```$/, '').trim();
    }

    const jsonOutput = JSON.parse(rawOutput);
    res.status(200).json(jsonOutput);

  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ error: error.message || 'Interner Server Fehler' });
  }
}
