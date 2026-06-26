#!/bin/bash
# ============================================
# LUA OBFUSCATOR MAX v4.0 — Termux Setup
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     LUA OBFUSCATOR MAX v4.0 — Termux Auto-Setup              ║${NC}"
echo -e "${CYAN}║     Ultra Security Edition                                   ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running in Termux
if [ -d "/data/data/com.termux" ]; then
    echo -e "${GREEN}[✓] Termux environment detected!${NC}"
else
    echo -e "${YELLOW}[!] Not in Termux, but setup will continue...${NC}"
fi

# Update packages
echo -e "${BLUE}[1/5] Updating packages...${NC}"
pkg update -y && pkg upgrade -y

# Install Python
echo -e "${BLUE}[2/5] Installing Python...${NC}"
pkg install python -y

# Install git
echo -e "${BLUE}[3/5] Installing Git...${NC}"
pkg install git -y

# Create working directory
echo -e "${BLUE}[4/5] Setting up workspace...${NC}"
mkdir -p ~/lua-obfuscator-max
cd ~/lua-obfuscator-max

# Check if files exist
if [ ! -f "lua_obfuscator_max.py" ]; then
    echo -e "${YELLOW}[!] lua_obfuscator_max.py not found in current directory${NC}"
    echo -e "${YELLOW}[!] Please copy lua_obfuscator_max.py to this directory first${NC}"
    echo ""
    echo -e "${CYAN}Usage after setup:${NC}"
    echo -e "  cd ~/lua-obfuscator-max"
    echo -e "  python3 lua_obfuscator_max.py -i input.lua -o output.lua --max"
    echo ""
    exit 1
fi

# Make executable
chmod +x lua_obfuscator_max.py

# Create alias
echo -e "${BLUE}[5/5] Creating shortcut alias...${NC}"

SHELL_RC=""
if [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "lua-obfuscator-max" "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# LUA OBFUSCATOR MAX v4.0" >> "$SHELL_RC"
        echo "alias luaobf='cd ~/lua-obfuscator-max && python3 lua_obfuscator_max.py'" >> "$SHELL_RC"
        echo -e "${GREEN}[✓] Alias 'luaobf' added to $(basename $SHELL_RC)${NC}"
    fi
fi

# Create example test file
cat > ~/lua-obfuscator-max/test_input.lua << 'EOF'
-- Test Lua Script
local function calculateArea(radius)
    local pi = 3.14159265359
    local area = pi * radius * radius
    return area
end

local function factorial(n)
    if n <= 1 then return 1 end
    return n * factorial(n - 1)
end

local function main()
    local circleArea = calculateArea(7.5)
    local fact5 = factorial(5)
    print("Circle area: " .. string.format("%.2f", circleArea))
    print("Factorial of 5: " .. fact5)
end

main()
EOF

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Setup Complete!                                          ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  Directory: ~/lua-obfuscator-max                             ║${NC}"
echo -e "${GREEN}║  Tool:     lua_obfuscator_max.py                             ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  BASIC USAGE:                                                ║${NC}"
echo -e "${GREEN}║    python3 lua_obfuscator_max.py -i input.lua -o out.lua     ║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║  MAXIMUM SECURITY:                                           ║${NC}"
echo -e "${GREEN}║    python3 lua_obfuscator_max.py -i in.lua -o out.lua --max ║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║  WITH WATERMARK:                                             ║${NC}"
echo -e "${GREEN}║    python3 lua_obfuscator_max.py -i in.lua -o out.lua \      ║${NC}"
echo -e "${GREEN}║      --watermark "MyScript v1.0" --max                        ║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║  TEST:                                                       ║${NC}"
echo -e "${GREEN}║    python3 lua_obfuscator_max.py -i test_input.lua \         ║${NC}"
echo -e "${GREEN}║      -o test_protected.lua --max -v                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Quick test:${NC}"
echo -e "  cd ~/lua-obfuscator-max"
echo -e "  python3 lua_obfuscator_max.py -i test_input.lua -o test_protected.lua --max -v"
echo ""
