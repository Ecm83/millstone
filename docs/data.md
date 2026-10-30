# Datos — cómo reproducir los corpus de `data/raw/`

Los corpus no van en el repo (derechos de las transcripciones; cada una
pertenece a su fuente). Aquí está de dónde viene cada fichero y cómo
obtenerlo. Todo lo medido es reproducible una vez bajados.

| fichero | corpus | fuente |
|---|---|---|
| `ZL3b-n.txt` | Voynich (ZL) | IVTFF — transcripción Zandbergen–Landini, voynich.nu |
| `IT2a-n.txt` | Voynich (Takahashi) | IVTFF — Takeshi Takahashi, voynich.nu |
| `culpeper.txt` | Inglés 1653 | Culpeper, *Physical Directory* (dominio público) |
| `protoelam*` | Proto-Elamita | CDLI transliterations (MDP series), cdli.earth |
| `lineara*` | Lineal A | GORILA/SigLA |
| `indus*` | Indus | ICIT / concordancia de Mahadevan |
| `rongorongo/` | Rongorongo | corpus XML de Thomas Barthel |
| `cuneiform.atf` | Sumerio | CDLI ATF (sux + proto-cuneiforme) |
| `copiale-cipher.txt` | Copiale cifrado | su.se — descargado (ver abajo) |
| `copiale-german.txt` | Copiale descifrado | su.se — descargado (ver abajo) |
| `linguaignota.txt` | Lingua Ignota | hildegardiana.es, glosario extraído |
| `litany.txt` | Letanía latina | la.wikisource.org/wiki/Litaniae_Sanctorum |
| `hiv1.fasta` | Genoma HIV-1 | NCBI eutils — descargado (ver abajo) |

## Descarga automatizada

```powershell
scripts/fetch_data.ps1   # baja copiale, hiv1, litany, linguaignota
scripts/reproduce.ps1    # stats + battery de todos los corpus en out/
```

## Comandos verificados (PowerShell)

```powershell
# Copiale — transcripción + alemán descifrado (Universidad de Estocolmo)
Invoke-WebRequest "https://www.su.se/download/18.4347052c19c47d1ff802df4/1771944422949/copiale-transcription%20(1).txt" -OutFile data/raw/copiale-cipher.txt
Invoke-WebRequest "https://www.su.se/download/18.4347052c19c47d1ff802df0/1771943955387/copiale-deciphered.txt" -OutFile data/raw/copiale-german.txt

# Genoma HIV-1 (NCBI)
Invoke-WebRequest "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NC_001802.1&rettype=fasta&retmode=text" -OutFile data/raw/hiv1.fasta
```

`linguaignota.txt` se extrajo del glosario de hildegardiana.es
(columna de palabras inventadas, ~1.011 entradas); `litany.txt` de la
letanía de Wikisource latina (bloque Kyrie→Amen).

Las transcripciones IVTFF del Voynich (ZL3b-n / IT2a-n) están en
voynich.nu; los demás corpus en sus repositorios de referencia citados
en `docs/corpora/`.

## Mínimo viable sin datos

`pytest` corre verde sin `data/raw/` (79 tests, los dependientes de
corpus se saltan) — los controles sintéticos de `ingest/synthetic.py`
bastan para calibrar el motor.
