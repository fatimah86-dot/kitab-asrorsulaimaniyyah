#!/usr/bin/env bash
# mulai_malam.sh — OCR + Latin Pesantren + terjemah Indonesia untuk satu kitab PDF pindaian,
# lewat Gemini (endpoint kompatibel-OpenAI). Halaman demi halaman, bisa dilanjutkan.
#
#   export KITAB_API_KEY="kunci-anda"
#   ./mulai_malam.sh <pdf> <base_url> <model> [pekerja=8] [halaman_per_permintaan=1] [timeout_dtk=600]
#
# Contoh (perintah yang sama dengan yang Anda tulis):
#   ./mulai_malam.sh kitab/asrorul-sulaimaniyah.pdf \
#       "https://generativelanguage.googleapis.com/v1beta/openai/" "gemini-2.5-pro" 8 1 600
#
# Hasil ada di hasil/ (TERJEMAHAN.md, STATUS.md, halaman/, gambar/). Terputus di tengah jalan?
# Jalankan ulang perintah yang sama — halaman yang sudah selesai dilewati.
# Opsi tambahan lewat variabel lingkungan: lihat README.md.
set -Eeuo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bantuan() {
  cat <<'TEKS'
Pemakaian:
  export KITAB_API_KEY="kunci-anda"
  ./mulai_malam.sh <pdf> <base_url> <model> [pekerja=8] [halaman_per_permintaan=1] [timeout_dtk=600]

Contoh:
  ./mulai_malam.sh kitab/asrorul-sulaimaniyah.pdf \
      "https://generativelanguage.googleapis.com/v1beta/openai/" "gemini-2.5-pro" 8 1 600

Variabel lingkungan opsional:
  KITAB_TES_SAJA=1     hanya uji kunci/model/endpoint lalu berhenti (hampir tanpa biaya)
  KITAB_MULAI / KITAB_AKHIR   kerjakan sebagian halaman saja, mis. KITAB_AKHIR=3 untuk uji coba
  KITAB_ATURAN=kajian|penuh   kajian (bawaan) atau terjemah penuh
  KITAB_ULANG_SEMUA=1  kerjakan ulang semua halaman (abaikan hasil sebelumnya)
  KITAB_KELUARAN=hasil folder hasil     KITAB_JUDUL="..."  judul dokumen
TEKS
}

galat() {
  echo "⛔ $*" >&2
  exit 2
}

periksa_angka() { # nama nilai min maks
  if ! [[ "$2" =~ ^[0-9]+$ ]] || (( 10#$2 < $3 || 10#$2 > $4 )); then
    galat "$1 harus bilangan bulat $3–$4 (diterima: '$2')"
  fi
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  bantuan
  exit 0
fi
if (( $# < 3 || $# > 6 )); then
  bantuan >&2
  echo >&2
  galat "Butuh 3–6 argumen: pdf, base_url, model, [pekerja], [halaman_per_permintaan], [timeout_dtk]."
fi

PDF="$1"
BASE_URL="$2"
MODEL="$3"
PEKERJA="${4:-8}"
HALAMAN="${5:-1}"
TIMEOUT="${6:-600}"

[[ -n "${KITAB_API_KEY:-}" ]] || galat 'KITAB_API_KEY belum diisi. Jalankan dulu: export KITAB_API_KEY="kunci-anda"'
[[ -f "$PDF" ]] || galat "Berkas PDF tidak ditemukan: $PDF"
[[ "$BASE_URL" =~ ^https?://[^[:space:]]+$ ]] || galat "base_url harus diawali http:// atau https:// (diterima: '$BASE_URL')"
[[ -n "$MODEL" ]] || galat "nama model kosong"
periksa_angka "pekerja" "$PEKERJA" 1 64
periksa_angka "halaman_per_permintaan" "$HALAMAN" 1 20
periksa_angka "timeout_dtk" "$TIMEOUT" 5 3600

# Pilih Python yang sudah punya paket: venv lokal → python3 sistem → buat venv lokal (sekali saja).
CEK='import requests, importlib.util as u; assert u.find_spec("pymupdf") or u.find_spec("fitz")'
if [[ -x "$DIR/.venv-kitab/bin/python" ]] && "$DIR/.venv-kitab/bin/python" -c "$CEK" 2>/dev/null; then
  PY="$DIR/.venv-kitab/bin/python"
elif command -v python3 >/dev/null 2>&1 && python3 -c "$CEK" 2>/dev/null; then
  PY="python3"
else
  command -v python3 >/dev/null 2>&1 || galat "python3 tidak ditemukan. Pasang Python 3.9+ terlebih dahulu."
  echo "→ Menyiapkan lingkungan Python (sekali saja, sekitar 1 menit)…"
  python3 -m venv "$DIR/.venv-kitab" || galat "Gagal membuat venv. Di Debian/Ubuntu: sudo apt install python3-venv"
  "$DIR/.venv-kitab/bin/pip" install -q --disable-pip-version-check -r "$DIR/requirements.txt" \
    || galat "Gagal memasang paket dari requirements.txt (periksa koneksi internet)."
  PY="$DIR/.venv-kitab/bin/python"
fi

echo "=== MULAI MALAM ==="
echo "PDF        : $PDF"
echo "Endpoint   : $BASE_URL"
echo "Model      : $MODEL"
echo "Pekerja    : $PEKERJA · halaman/permintaan: $HALAMAN · timeout: $TIMEOUT dtk"
echo "Kunci API  : terpasang (${#KITAB_API_KEY} karakter; tidak ditampilkan)"
echo

case "${KITAB_TES_SAJA:-0}" in
  1 | true | TRUE | ya | yes)
    exec "$PY" "$DIR/tools/kitab_pipeline.py" tes "$BASE_URL" "$MODEL" --timeout "$TIMEOUT"
    ;;
esac

exec "$PY" "$DIR/tools/kitab_pipeline.py" proses "$PDF" "$BASE_URL" "$MODEL" \
  --pekerja "$PEKERJA" --halaman-per-permintaan "$HALAMAN" --timeout "$TIMEOUT"
