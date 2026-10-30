# reproduce.ps1 — corre la batería/veredictos sobre los corpus disponibles
# en data/raw/ y vuelca salida a out/. Requiere `pip install -e .` y datos.
$ErrorActionPreference = "Continue"
New-Item -ItemType Directory -Force out | Out-Null

$jobs = @(
    @{ name = "voynich-zl";   file = "data/raw/ZL3b-n.txt";        fmt = "ivtff" },
    @{ name = "voynich-tt";   file = "data/raw/IT2a-n.txt";        fmt = "ivtff" },
    @{ name = "culpeper";     file = "data/raw/culpeper.txt";      fmt = "plaintext" },
    @{ name = "rongorongo";   file = "data/raw/rongorongo";        fmt = "rongorongo" },
    @{ name = "cuneiform";    file = "data/raw/cuneiform.atf";     fmt = "cuneiform" },
    @{ name = "copiale-c";    file = "data/raw/copiale-cipher.txt";fmt = "copiale" },
    @{ name = "copiale-de";   file = "data/raw/copiale-german.txt";fmt = "copiale-de" },
    @{ name = "hiv1";         file = "data/raw/hiv1.fasta";        fmt = "fasta" },
    @{ name = "linguaignota"; file = "data/raw/linguaignota.txt";  fmt = "plaintext" },
    @{ name = "litany";       file = "data/raw/litany.txt";        fmt = "plaintext" }
)

foreach ($j in $jobs) {
    if (-not (Test-Path $j.file)) {
        Write-Host ">> $($j.name): falta $($j.file) — scripts/fetch_data.ps1 o docs/data.md"
        continue
    }
    Write-Host ">> $($j.name)"
    python -m millstone $j.file --format $j.fmt stats 2>&1 |
        Out-File "out/$($j.name).stats.txt" -Encoding utf8
    python -m millstone $j.file --format $j.fmt battery 2>&1 |
        Out-File "out/$($j.name).battery.txt" -Encoding utf8
}
Write-Host "== salida en out/"
