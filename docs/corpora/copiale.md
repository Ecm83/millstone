# Copiale — cifrado homofónico descifrado (Knight, Megyesi, Schaefer 2011)

**Fuente**: su.se — `copiale-cipher.txt` (transcripción, ~90 códigos-cifra),
`copiale-german.txt` (alemán descifrado, ground truth del mismo documento).

**Por qué importa**: es el único cifrado real descifrado del panel — el
control que faltaba para la clase "codebook". La pregunta: ¿un cifrado
verdadero firma como el Voynich?

## Estructura

El cifrado no tiene espacios de palabra: schema `symbol→line→page→corpus`
(sin `word`). Símbolos = códigos ASCII de la transcripción (`grr`, `lam`,
`bar`, `*o*` logogramas, `?` incierto, `#` catchwords excluidos).
El alemán entra por `plaintext` (`--format copiale-de`).

## Medido (batería, N=10k)

Nivel símbolo-por-línea, granularidad comparable al Voynich letras/línea:

| métrica | Voynich letras | Copiale cifrado |
|---|---|---|
| hapax | 0,079 | 0,108 |
| heaps_beta | 0,080 | 0,124 |
| timm | 1,000 | 0,911 |
| families | 1,0 | 1,09 |
| outdeg | 0,776 | 0,685 |
| echo_z3 | **−188,7** | **+46,9** |

`copiale-de` a nivel palabra: hapax 0,44 | heaps 0,57 | families 7,0 |
outdeg 0,80 — clase lengua natural, junto a Culpeper.

## Lectura

La sustitución homofónica preserva la estadística de n-gramas del
plaintext: el mismo trigrama alemán reaparece → eco verbatim fuertemente
positivo (+47). El Voynich hace lo contrario: a nivel letra suprime
colisiones con un déficit extremo (−189 vs nulo). **Un stream de texto
cifrado no se parece al Voynich** — dato en contra de toda hipótesis de
sustitución de texto natural.

Comandos:

```bash
python -m millstone data/raw/copiale-cipher.txt --format copiale battery
python -m millstone data/raw/copiale-german.txt --format copiale-de battery --unit word
python -m millstone data/raw/ZL3b-n.txt battery --group line   # letras/línea
```
