import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add CSS
css_to_add = """
    .tabs { display: flex; gap: 10px; margin-bottom: 22px; border-bottom: 1px solid var(--line); padding-bottom: 14px; overflow-x: auto; }
    .tab-btn { background: #fff; color: var(--muted); border: 1px solid var(--line); padding: 11px 18px; border-radius: 12px; cursor: pointer; font-weight: 700; font-size: 14px; transition: all .15s ease; white-space: nowrap; }
    .tab-btn:hover { background: #f9fafb; border-color: #d1d5db; }
    .tab-btn.active { background: var(--accent); color: white; border-color: var(--accent); }
    .tab-content { display: none; animation: fadeIn 0.3s ease; }
    .tab-content.active { display: block; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
"""
content = content.replace('</style>', css_to_add + '\n  </style>')

# Replace the sticky actions generate button with export all, and add Tabs HTML
hero_end = content.find('    <section class="section ai-section">')
if hero_end == -1:
    print("Could not find ai-section")
    exit(1)

# Modify sticky actions button
content = content.replace('<button id="generateBtn" class="primary">Word-Dokument erstellen</button>',
                          '<button id="generateAllBtn" class="primary">Alle 3 Dokumente exportieren</button>')

tabs_html = """
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('tab-basis', this)">1. Basis & KI-Import</button>
      <button class="tab-btn" onclick="switchTab('tab-doc1', this)">2. Arbeitssicherheit</button>
      <button class="tab-btn" onclick="switchTab('tab-doc2', this)">3. Stellenbeschreibung</button>
      <button class="tab-btn" onclick="switchTab('tab-doc3', this)">4. Unterweisung</button>
    </div>
"""
content = content[:hero_end] + tabs_html + content[hero_end:]

# Now we need to wrap sections.
# Let's extract all sections.
sections_raw = re.split(r'(    <section class="section.*?)</section>', content, flags=re.DOTALL)
# sections_raw will have: [before_first_section, section1_start, section1_inner..., before_second_section, etc...]
# Actually re.split with a capture group splits into [text_before, match1, text_between1, match2, ...]
# Better to find all sections using regex
sections = re.findall(r'    <section class="section.*?.*?</section>', content, flags=re.DOTALL)

# Map sections by their content keywords
sec_map = {}
for s in sections:
    if "KI-Import" in s: sec_map['ai'] = s
    elif "1. Branding" in s: sec_map['1'] = s
    elif "2. Allgemeine Angaben" in s: sec_map['2'] = s
    elif "3. Stellenbeschreibung" in s: sec_map['3'] = s
    elif "4. Gefährdungsbeurteilung" in s: sec_map['4'] = s
    elif "5. Persönliche Schutzausrüstung" in s: sec_map['5'] = s
    elif "6. Allgemeine Sicherheitsunterweisung" in s: sec_map['6'] = s
    elif "7. Tätigkeitsspezifische Unterweisung" in s: sec_map['7'] = s
    elif "8. Verkehrswege" in s: sec_map['8'] = s
    elif "9. Arbeitsmedizinische Vorsorge" in s: sec_map['9'] = s
    elif "10. Organisation" in s: sec_map['10'] = s
    elif "11. Bewertung" in s: sec_map['11'] = s

tab_basis = f"""
    <div id="tab-basis" class="tab-content active">
{sec_map['ai']}
{sec_map['1']}
{sec_map['2']}
    </div>
"""

tab_doc1 = f"""
    <div id="tab-doc1" class="tab-content">
{sec_map['4']}
{sec_map['5']}
{sec_map['9']}
{sec_map['10']}
{sec_map['11']}
      <div style="padding: 20px 0;">
        <button class="primary" type="button" onclick="generateArbeitssicherheitDoc()">Dokument 1 exportieren (Arbeitssicherheit)</button>
      </div>
    </div>
"""

tab_doc2 = f"""
    <div id="tab-doc2" class="tab-content">
{sec_map['3']}
{sec_map['8']}
      <div style="padding: 20px 0;">
        <button class="primary" type="button" onclick="generateStellenbeschreibungDoc()">Dokument 2 exportieren (Stellenbeschreibung)</button>
      </div>
    </div>
"""

tab_doc3 = f"""
    <div id="tab-doc3" class="tab-content">
{sec_map['6']}
{sec_map['7']}
      <div style="padding: 20px 0;">
        <button class="primary" type="button" onclick="generateUnterweisungDoc()">Dokument 3 exportieren (Unterweisung)</button>
      </div>
    </div>
"""

# Replace all sections in the original file with the new tabs
start_idx = content.find(sec_map['ai'])
last_sec = sec_map['11']
end_idx = content.find(last_sec) + len(last_sec)

new_content = content[:start_idx] + tab_basis + tab_doc1 + tab_doc2 + tab_doc3 + content[end_idx:]

# Add switchTab function to script
js_to_add = """
    function switchTab(tabId, btn) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
      $(tabId).classList.add('active');
      btn.classList.add('active');
    }
"""
new_content = new_content.replace('const $ = (id) => document.getElementById(id);', 'const $ = (id) => document.getElementById(id);\n' + js_to_add)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("HTML restructuring completed.")
