#!/bin/bash
# ============================================
# LUA OBFUSCATOR MAX v4.0 — Termux Setup
# GitHub → Download → Obfuscate → Download
# ============================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     LUA OBFUSCATOR MAX v4.0 — Termux Auto-Setup              ║${NC}"
echo -e "${CYAN}║     GitHub → Download → Obfuscate → Download                 ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect environment
if [ -d "/data/data/com.termux" ]; then
    echo -e "${GREEN}[✓] Termux detected!${NC}"
    DOWNLOAD_DIR="/sdcard/Download"
else
    echo -e "${YELLOW}[!] Regular Linux/macOS${NC}"
    DOWNLOAD_DIR="$HOME/Downloads"
fi

# Update & install
echo -e "${BLUE}[1/3] Update packages...${NC}"
pkg update -y 2>/dev/null || sudo apt update -y 2>/dev/null || true

echo -e "${BLUE}[2/3] Install Python...${NC}"
pkg install python -y 2>/dev/null || sudo apt install python3 -y 2>/dev/null || true

# Setup workspace
echo -e "${BLUE}[3/3] Setup workspace...${NC}"
WORK_DIR="$HOME/lua-obfuscator-max"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Check if tool file exists (user should copy from GitHub download)
if [ ! -f "lua_obfuscator_max.py" ]; then
    echo ""
    echo -e "${MAGENTA}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║  ⚠️  FILE TOOL BELUM ADA                                     ║${NC}"
    echo -e "${MAGENTA}╠══════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${MAGENTA}║  CARA MENDAPATKAN FILE:                                      ║${NC}"
    echo -e "${MAGENTA}║                                                              ║${NC}"
    echo -e "${MAGENTA}║  1. Buka GitHub repo: github.com/YOUR_USERNAME/             ║${NC}"
    echo -e "${MAGENTA}║     lua-obfuscator-max                                       ║${NC}"
    echo -e "${MAGENTA}║                                                              ║${NC}"
    echo -e "${MAGENTA}║  2. Klik tombol hijau [<> Code] → Download ZIP              ║${NC}"
    echo -e "${MAGENTA}║                                                              ║${NC}"
    echo -e "${MAGENTA}║  3. Extract ZIP ke $DOWNLOAD_DIR          ║${NC}"
    echo -e "${MAGENTA}║                                                              ║${NC}"
    echo -e "${MAGENTA}║  4. Copy lua_obfuscator_max.py ke folder ini:               ║${NC}"
    echo -e "${MAGENTA}║     cp $DOWNLOAD_DIR/lua_obfuscator_max.py $WORK_DIR/       ║${NC}"
    echo -e "${MAGENTA}║                                                              ║${NC}"
    echo -e "${MAGENTA}║  5. Jalankan setup lagi:                                     ║${NC}"
    echo -e "${MAGENTA}║     ./setup.sh                                               ║${NC}"
    echo -e "${MAGENTA}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 1
fi

chmod +x lua_obfuscator_max.py

# Create alias
SHELL_RC=""
if [ -f "$HOME/.bashrc" ]; then SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then SHELL_RC="$HOME/.zshrc"; fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "lua-obfuscator-max" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# === LUA OBFUSCATOR MAX v4.0 ===" >> "$SHELL_RC"
        echo "alias luaobf='cd $WORK_DIR && python3 lua_obfuscator_max.py'" >> "$SHELL_RC"
        echo "alias luaobf-max='cd $WORK_DIR && python3 lua_obfuscator_max.py --max'" >> "$SHELL_RC"
        echo -e "${GREEN}[✓] Alias ditambahkan${NC}"
    fi
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ SETUP SELESAI!                                           ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  Tool:     $WORK_DIR/lua_obfuscator_max.py                   ║${NC}"
echo -e "${GREEN}║  Download: $DOWNLOAD_DIR                                     ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  📥 WORKFLOW (Input & Output di Download):                   ║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║  1. Taruh file .lua di folder Download                       ║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║  2. Obfuscate (auto output ke Download):                     ║${NC}"
echo -e "${GREEN}║     python3 lua_obfuscator_max.py -i script.lua --max        ║${NC}"
echo -e "${GREEN}║     → Output: $DOWNLOAD_DIR/script_protected.lua            ║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║  3. Batch (semua .lua di Download):                          ║${NC}"
echo -e "${GREEN}║     python3 lua_obfuscator_max.py -d $DOWNLOAD_DIR --max    ║${NC}"
echo -e "${GREEN}║     → Output: $DOWNLOAD_DIR/obfuscated/                     ║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║  4. Custom path:                                             ║${NC}"
echo -e "${GREEN}║     python3 lua_obfuscator_max.py -i in.lua -o out.lua --max ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
