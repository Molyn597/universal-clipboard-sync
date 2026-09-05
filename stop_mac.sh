#!/usr/bin/env bash
# ==============================================================================
# Universal Clipboard - macOS Stop Script
# Gracefully stops the clipboard synchronization daemon
# ==============================================================================

echo "========================================================"
echo "  Zastavuji Universal Clipboard Server (macOS)..."
echo "========================================================"
echo ""

# 1. Pokus o graceful shutdown přes HTTP API
if curl -s -X POST http://localhost:7890/api/shutdown >/dev/null 2>&1; then
    echo "[OK] Příkaz k ukončení byl odeslán přes API."
    sleep 1
fi

# 2. Ukončení zbývajícího procesu pokud ještě běží
PIDS=$(lsof -ti :7890 2>/dev/null || true)
if [ -n "$PIDS" ]; then
    echo "[INFO] Ukončuji proces na portu 7890 (PID: $PIDS)..."
    kill -9 $PIDS 2>/dev/null || true
fi

echo ""
echo "========================================================"
echo "  [HOTOVO] Synchronizační server byl zastaven."
echo "========================================================"
