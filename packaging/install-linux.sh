#!/usr/bin/env bash
set -euo pipefail
PREFIX="${PREFIX:-$HOME/.local}"
APP_DIR="$PREFIX/share/kdp-ai-factory"
BIN_DIR="$PREFIX/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$APP_DIR" "$BIN_DIR" "$DESKTOP_DIR"
cp KDP-AI-Factory-Linux "$APP_DIR/KDP-AI-Factory-Linux"
chmod +x "$APP_DIR/KDP-AI-Factory-Linux"
cat > "$BIN_DIR/kdp-ai-factory" <<EOF
#!/usr/bin/env bash
exec "$APP_DIR/KDP-AI-Factory-Linux" "$@"
EOF
chmod +x "$BIN_DIR/kdp-ai-factory"
cat > "$DESKTOP_DIR/kdp-ai-factory.desktop" <<EOF
[Desktop Entry]
Name=KDP AI Factory
Comment=Fábrica editorial com IA
Exec=$BIN_DIR/kdp-ai-factory
Terminal=false
Type=Application
Categories=Office;Publishing;
EOF
echo "KDP AI Factory instalado em $APP_DIR"
echo "Comando: kdp-ai-factory"
