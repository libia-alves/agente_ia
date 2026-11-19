#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export LANGFLOW_CONFIG_DIR="$PWD/.langflow"
export LANGFLOW_DATABASE_URL="sqlite:///$LANGFLOW_CONFIG_DIR/langflow.db"
export TMPDIR="$LANGFLOW_CONFIG_DIR/tmp"
mkdir -p "$TMPDIR"
# Carrega credenciais e opções no ambiente antes de iniciar o servidor.
set -a
source .env
set +a
# A chave do cliente autentica contra o banco e não precisa estar no ambiente do servidor.
unset LANGFLOW_API_KEY
langflow_bin=.venv/bin/langflow
if [[ ! -x "$langflow_bin" && -x .langflow/python313/bin/langflow ]]; then
    langflow_bin=.langflow/python313/bin/langflow
fi
exec "$langflow_bin" run --host 127.0.0.1 --port 7860
