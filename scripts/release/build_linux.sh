#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-dev}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DIST_DIR="$ROOT_DIR/dist/release"

cd "$ROOT_DIR"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

pyinstaller --noconfirm --onefile --name vk_publisher-linux src/main.py

mkdir -p "$DIST_DIR"
cp dist/vk_publisher-linux "$DIST_DIR/"
cp README.md "$DIST_DIR/"
[[ -f .env.example ]] && cp .env.example "$DIST_DIR/.env.example"

cat > "$DIST_DIR/start.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$DIR/vk_publisher-linux"
EOF
chmod +x "$DIST_DIR/start.sh"

ARCHIVE="vk_publisher-${TAG}-linux.tar.gz"
tar -czf "$ARCHIVE" -C "$DIST_DIR" .
sha256sum "$ARCHIVE" > "${ARCHIVE}.sha256"

echo "Built: $ARCHIVE"
