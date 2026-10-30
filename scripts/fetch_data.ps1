# fetch_data.ps1 — descarga los corpus con URL verificada a data/raw/
# Los demás (IVTFF, CDLI, GORILA, Barthel, ICIT...) se bajan de sus
# fuentes citadas en docs/data.md — son de terceros y no se redistribuyen.
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force data/raw | Out-Null

Write-Host "== copiale (su.se)"
Invoke-WebRequest "https://www.su.se/download/18.4347052c19c47d1ff802df4/1771944422949/copiale-transcription%20(1).txt" -OutFile data/raw/copiale-cipher.txt
Invoke-WebRequest "https://www.su.se/download/18.4347052c19c47d1ff802df0/1771943955387/copiale-deciphered.txt" -OutFile data/raw/copiale-german.txt

Write-Host "== hiv1 (NCBI eutils)"
Invoke-WebRequest "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NC_001802.1&rettype=fasta&retmode=text" -OutFile data/raw/hiv1.fasta

Write-Host "== litany (la.wikisource)"
$p = Invoke-WebRequest "https://la.wikisource.org/wiki/Litaniae_Sanctorum" -UseBasicParsing
($p.Content -replace '<[^>]+>', "`n") | Out-File -Encoding utf8 data/raw/_lit_raw.txt
python -X utf8 -c "
import re
lines = [l.strip() for l in open('data/raw/_lit_raw.txt',encoding='utf-8') if l.strip()]
start = next(i for i,l in enumerate(lines) if l.lower().startswith(('kyrie','christe')))
body = []
for l in lines[start:]:
    if l == 'Amen' and len(body) > 20:
        body.append(l); break
    if re.match(r'^[A-ZVR][a-zA-Z .,()]+$', l) and 2 < len(l) < 80:
        body.append(l)
open('data/raw/litany.txt','w',encoding='utf-8').write(chr(10).join(body))
print(len(body), 'lineas')
"
Remove-Item data/raw/_lit_raw.txt -ErrorAction SilentlyContinue

Write-Host "== lingua ignota (hildegardiana.es)"
$g = Invoke-WebRequest "http://www.hildegardiana.es/367lengua/03p02.html" -UseBasicParsing
($g.Content -replace '<[^>]+>', " " -replace '&[a-zA-Z#0-9]+;', ' ') | Out-File -Encoding utf8 data/raw/_li_raw.txt
python -X utf8 -c "
import re
text = open('data/raw/_li_raw.txt',encoding='utf-8').read()
words = []
for line in text.splitlines():
    m = re.match(r'^\s*(\d{1,4})\s+([A-Z][A-Za-züöïë ]*?)\s*[,((]', line)
    if m:
        w = re.sub(r'[^A-Za-z]', '', m.group(2)).lower()
        if len(w) >= 2 and int(m.group(1)) < 1200:
            words.append(w)
open('data/raw/linguaignota.txt','w',encoding='utf-8').write(chr(10).join(words))
print(len(words), 'palabras')
"
Remove-Item data/raw/_li_raw.txt -ErrorAction SilentlyContinue

Write-Host "== listo. Resto de corpus: docs/data.md"
