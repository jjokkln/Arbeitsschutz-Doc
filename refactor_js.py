import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find generateDocx function
start_marker = "    async function generateDocx() {"
# Find the end of it (it ends before `$('demoBtn').addEventListener`)
end_marker = "    $('demoBtn').addEventListener('click', fillDemo);"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Could not find generateDocx")
    exit(1)

js_new = """
    async function createBaseDoc(docTitleSuffix) {
      if (!docxReady()) throw new Error('DOCX-Bibliothek konnte nicht geladen werden.');
      const { Document, Paragraph, TextRun, AlignmentType, Header, Footer, ImageRun, WidthType, Table, TableRow, TableCell, BorderStyle } = docx;
      
      const accent = cleanHex($('accentColor').value);
      const selectedLogoUrl = $('predefinedLogo') ? $('predefinedLogo').value : null;
      const ownLogo = await imageFromUrl(selectedLogoUrl, 210, 90);
      const clientLogo = await imageFromInput('clientLogo', 170, 80);
      const footerLogo = await imageFromUrl(selectedLogoUrl, 80, 38);

      const headerChildren = [];
      if (ownLogo) {
        headerChildren.push(new Paragraph({ alignment: AlignmentType.RIGHT, children: [new ImageRun({ data: ownLogo.data, transformation: { width: Math.min(120, ownLogo.width), height: Math.min(52, ownLogo.height) } })] }));
      }
      headerChildren.push(new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: `${safe($('docTitle').value)} - ${docTitleSuffix} · Stand ${safe($('version').value)}`, size: 15, color: '6B7280' })] }));

      const footerChildren = [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: `Stand: ${safe($('version').value)}  |  ${safe($('workplace').value)}`, size: 15, color: '6B7280' })] })];
      if (footerLogo) footerChildren.unshift(new Paragraph({ alignment: AlignmentType.RIGHT, children: [new ImageRun({ data: footerLogo.data, transformation: { width: footerLogo.width, height: footerLogo.height } })] }));

      const children = [];
      if (ownLogo || clientLogo) {
        const logoCells = [];
        logoCells.push(new TableCell({ borders: { top:{style:BorderStyle.NONE}, bottom:{style:BorderStyle.NONE}, left:{style:BorderStyle.NONE}, right:{style:BorderStyle.NONE} }, children: ownLogo ? [new Paragraph({ children: [new ImageRun({ data: ownLogo.data, transformation: { width: ownLogo.width, height: ownLogo.height } })] })] : [p('')] }));
        logoCells.push(new TableCell({ borders: { top:{style:BorderStyle.NONE}, bottom:{style:BorderStyle.NONE}, left:{style:BorderStyle.NONE}, right:{style:BorderStyle.NONE} }, children: clientLogo ? [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new ImageRun({ data: clientLogo.data, transformation: { width: clientLogo.width, height: clientLogo.height } })] })] : [p('')] }));
        children.push(new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, borders: { top:{style:BorderStyle.NONE}, bottom:{style:BorderStyle.NONE}, left:{style:BorderStyle.NONE}, right:{style:BorderStyle.NONE}, insideHorizontal:{style:BorderStyle.NONE}, insideVertical:{style:BorderStyle.NONE} }, rows: [new TableRow({ children: logoCells })] }));
      }

      children.push(new Paragraph({ spacing: { before: 600, after: 80 }, children: [new TextRun({ text: safe($('docTitle').value), bold: true, color: accent, size: 38 })] }));
      children.push(new Paragraph({ children: [new TextRun({ text: docTitleSuffix, size: 28, color: '6B7280', bold: true })] }));
      children.push(new Paragraph({ children: [new TextRun({ text: `Arbeitsplatz: ${safe($('workplace').value)}`, size: 24 })] }));
      children.push(new Paragraph({ children: [new TextRun({ text: `Stand: ${safe($('version').value)}`, size: 24 })] }));
      children.push(new Paragraph({ spacing: { before: 260, after: 160 }, children: [new TextRun({ text: `Kundenunternehmen / Einsatzbetrieb: ${safe($('clientCompany').value)}`, size: 22 })] }));
      children.push(new Paragraph({ children: [new TextRun({ text: `Datum: ${safe($('docDate').value)}`, size: 20, color: '6B7280' })] }));
      children.push(new Paragraph({ children: [docx.PageBreak ? new docx.PageBreak() : new docx.TextRun("")] })); // In browser umd docx PageBreak is not a constructor directly sometimes, but it's part of docx

      return { children, headerChildren, footerChildren, accent };
    }

    async function finishAndDownloadDoc(baseData, docTitleSuffix, fileSuffix) {
      const { Document, Packer, Header, Footer } = docx;
      const doc = new Document({
        creator: 'Arbeitssicherheit Tool',
        title: safe($('docTitle').value) + ' - ' + docTitleSuffix,
        styles: {
          default: {
            document: { run: { font: 'Aptos', size: 21, color: '111827' }, paragraph: { spacing: { after: 90 } } }
          }
        },
        sections: [{
          properties: { page: { margin: { top: 900, right: 720, bottom: 780, left: 720 } } },
          headers: { default: new Header({ children: baseData.headerChildren }) },
          footers: { default: new Footer({ children: baseData.footerChildren }) },
          children: baseData.children
        }]
      });
      const blob = await Packer.toBlob(doc);
      downloadBlob(blob, `${fileBaseName()}_${fileSuffix}.docx`);
    }

    function appendGeneralInfo(children, accent) {
      children.push(heading('1. Allgemeine Angaben & Arbeitsplatz', 1, accent));
      children.push(labelTable([
        ['Kundenunternehmen / Einsatzbetrieb', $('clientCompany').value], ['Kunden-Nr.', $('clientNumber').value], ['Datum der Begehung', $('docDate').value], ['Durchgeführt durch', $('conductedBy').value], ['Ansprechpartner/-in beim Kunden', $('clientContact').value], ['Oberbegriff / Position', $('position').value], ['Arbeitsplatz / Arbeitsbereich', $('area').value], ['Mitarbeiter/-in', $('employee').value], ['Mitarbeiter/-in am vereinbarten Arbeitsplatz?', $('employeeOnSite').value]
      ]));
    }

    async function generateArbeitssicherheitDoc() {
      try {
        setStatus('Dokument 1 (Arbeitssicherheit) wird erstellt ...');
        const base = await createBaseDoc('Arbeitssicherheitsdokument');
        const { children, accent } = base;
        const { TableCell, Paragraph, BorderStyle, Table, WidthType, TableRow, TextRun } = docx;

        appendGeneralInfo(children, accent);

        children.push(heading('2. Gefährdungsbeurteilung & Maßnahmen', 1, accent));
        const riskRows = collectRows('.risk-row');
        children.push(table([headerRow(['Gefährdung / Bereich', 'Risiko / Ursache', 'Maßnahmen', 'Bewertung', 'Zusatz / Status'])].concat(riskRows.map(r => [r.area, r.risk, r.measures, r.rating, `${safe(r.owner)}\\n${safe(r.status)}`])), [18, 24, 28, 14, 16]));

        children.push(heading('3. Persönliche Schutzausrüstung (PSA)', 1, accent));
        const psaRows = collectRows('.psa-row');
        children.push(table([headerRow(['PSA-Art', 'Pflicht', 'Gestellt durch', 'Tragebereich / Hinweis'])].concat(psaRows.map(r => [r.item, r.required, r.provided, r.note])), [28, 16, 25, 31]));

        children.push(heading('4. Arbeitsmedizinische Vorsorge', 1, accent));
        children.push(labelTable([['Pflichtvorsorge', $('mandatoryCare').value], ['Angebotsvorsorge', $('optionalCare').value], ['Wunschvorsorge', $('requestCare').value], ['Durchführung durch', $('careBy').value]]));

        children.push(heading('5. Organisation & Ansprechpartner', 1, accent));
        const orgRows = collectRows('.org-row');
        children.push(table([headerRow(['Bereich', 'Zuständig / Prüfung', 'Kontakt / Stelle', 'Hinweis / Frist'])].concat(orgRows.map(r => [r.area, r.owner, r.contact, r.note])), [25, 25, 25, 25]));

        children.push(heading('6. Gesamteinschätzung & Freigabe', 1, accent));
        children.push(labelTable([['Gesamteinschätzung', $('overallRating').value], ['Auflagen / Maßnahmen', $('conditions').value], ['Nächste Arbeitsplatzbesichtigung', $('nextReview').value]]));

        children.push(heading('7. Dokumentation & Unterschriften', 1, accent));
        children.push(p('Mit der Unterzeichnung wird bestätigt, dass die Unterweisung durchgeführt wurde und die Inhalte verstanden wurden.'));
        const sigLines = lines($('signatures').value);
        const sigRow = sigLines.map(label => new TableCell({
          margins: { top: 420, bottom: 80, left: 80, right: 80 },
          children: [new Paragraph({ border: { top: { color: '9CA3AF', space: 1, style: BorderStyle.SINGLE, size: 6 } }, children: [new TextRun({ text: label, size: 18 })] })]
        }));
        children.push(new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, borders: { top:{style:BorderStyle.NONE}, bottom:{style:BorderStyle.NONE}, left:{style:BorderStyle.NONE}, right:{style:BorderStyle.NONE}, insideHorizontal:{style:BorderStyle.NONE}, insideVertical:{style:BorderStyle.NONE} }, rows: [new TableRow({ children: sigRow.length ? sigRow : [cell('Unterschrift')] })] }));

        await finishAndDownloadDoc(base, 'Arbeitssicherheitsdokument', 'Arbeitssicherheit');
        setStatus('Dokument 1 wurde erstellt.');
      } catch(e) { setStatus('Fehler: ' + e.message, true); console.error(e); }
    }

    async function generateStellenbeschreibungDoc() {
      try {
        setStatus('Dokument 2 (Stellenbeschreibung) wird erstellt ...');
        const base = await createBaseDoc('Stellenbeschreibung / Tätigkeitsprofil');
        const { children, accent } = base;

        appendGeneralInfo(children, accent);

        children.push(heading('2. Stellenbeschreibung / Tätigkeitsprofil', 1, accent));
        children.push(labelTable([['Position', $('position').value], ['Arbeitsbereich', $('area').value], ['Arbeitszeit / Schicht', $('worktime').value], ['Besondere Hinweise', $('specialNotes').value]]));
        children.push(heading('Tätigkeiten', 2, accent)); children.push(...bullets($('duties').value));
        children.push(heading('Arbeitsmittel / Maschinen', 2, accent)); children.push(...bullets($('equipment').value));

        children.push(heading('3. Voraussetzungen & Qualifikation', 1, accent));
        children.push(heading('Grundvoraussetzungen an Personal', 2, accent)); children.push(...bullets($('requirements').value));
        children.push(heading('Qualifikation / Ziel', 2, accent)); children.push(...bullets($('qualification').value));

        children.push(heading('4. Verkehrswege, Be-/Entladung & Lagerung', 1, accent));
        children.push(heading('Verkehrswege', 2, accent)); children.push(...bullets($('traffic').value));
        children.push(heading('Be- & Entladung', 2, accent)); children.push(...bullets($('loading').value));
        children.push(heading('Lagerung', 2, accent)); children.push(...bullets($('storage').value));
        children.push(heading('Zusatzregeln', 2, accent)); children.push(...bullets($('extraRules').value));

        await finishAndDownloadDoc(base, 'Stellenbeschreibung', 'Stellenbeschreibung');
        setStatus('Dokument 2 wurde erstellt.');
      } catch(e) { setStatus('Fehler: ' + e.message, true); console.error(e); }
    }

    async function generateUnterweisungDoc() {
      try {
        setStatus('Dokument 3 (Unterweisungen) wird erstellt ...');
        const base = await createBaseDoc('Sicherheitsunterweisung');
        const { children, accent } = base;

        appendGeneralInfo(children, accent);

        children.push(heading('2. Allgemeine Sicherheitsunterweisung', 1, accent));
        children.push(heading('Sicherheitskennzeichen', 2, accent)); children.push(...bullets($('signage').value));
        children.push(heading('Allgemeines Verhalten', 2, accent)); children.push(...bullets($('generalSafety').value));
        children.push(heading('Notfall / Erste Hilfe', 2, accent)); children.push(...bullets($('emergency').value));
        children.push(heading('Psychische Gesundheit / Belastung', 2, accent)); children.push(...bullets($('mentalHealth').value));

        children.push(heading('3. Tätigkeitsspezifische Unterweisung', 1, accent));
        collectRows('.instruction-row').forEach((r, index) => {
          children.push(heading(`${index + 1}. ${safe(r.title)}`, 2, accent));
          children.push(labelTable([['Stand / Version', r.stand], ['Besonderheiten / Defekte / Notfall', r.special]]));
          children.push(...bullets(r.points));
        });

        await finishAndDownloadDoc(base, 'Sicherheitsunterweisung', 'Unterweisung');
        setStatus('Dokument 3 wurde erstellt.');
      } catch(e) { setStatus('Fehler: ' + e.message, true); console.error(e); }
    }

    async function generateAllDocs() {
      await generateArbeitssicherheitDoc();
      await generateStellenbeschreibungDoc();
      await generateUnterweisungDoc();
      setStatus('Alle 3 Dokumente wurden generiert.');
    }

"""

new_content = content[:start_idx] + js_new + content[end_idx:]

# Update the event listener for the generateAllBtn
new_content = new_content.replace("$('generateBtn').addEventListener('click', generateDocx);", "$('generateAllBtn').addEventListener('click', generateAllDocs);")
# Also need to fix PageBreak issue with children.push(new Paragraph({ children: [new PageBreak()] }));
# Because PageBreak is accessed destructured. But in the base doc I did `docx.PageBreak`.
# That should work.

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("JS logic replacement completed.")
