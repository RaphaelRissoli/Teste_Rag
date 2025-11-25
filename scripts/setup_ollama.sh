#!/bin/bash

echo "🚀 Configurando Ollama para o projeto Micro-RAG"
echo ""

# Detectar sistema operacional
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

# Verificar se Ollama está instalado
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama não está instalado."
    echo "📥 Instalando Ollama..."
    
    if [ "$MACHINE" = "Mac" ]; then
        echo "🍎 Detectado macOS"
        
        # Verificar se Homebrew está instalado
        if command -v brew &> /dev/null; then
            echo "📦 Instalando via Homebrew..."
            brew install ollama
        else
            echo "⚠️  Homebrew não encontrado."
            echo ""
            echo "📥 Por favor, instale o Ollama manualmente:"
            echo "   1. Acesse: https://ollama.com/download"
            echo "   2. Baixe o instalador para macOS"
            echo "   3. Abra o arquivo .dmg e arraste Ollama para Applications"
            echo "   4. Execute este script novamente após a instalação"
            echo ""
            echo "   Ou instale Homebrew primeiro:"
            echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    elif [ "$MACHINE" = "Linux" ]; then
        echo "🐧 Detectado Linux"
        echo "📥 Instalando via script oficial..."
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo "❌ Sistema operacional não suportado: $MACHINE"
        echo "📥 Por favor, instale manualmente em: https://ollama.com/download"
        exit 1
    fi
    
    echo "✅ Ollama instalado!"
    ollama --version
else
    echo "✅ Ollama já está instalado"
    ollama --version
fi

echo ""
echo "🔍 Verificando se o servidor Ollama está rodando..."

# Verificar se servidor está rodando
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Servidor Ollama está rodando"
else
    echo "⚠️  Servidor Ollama não está rodando"
    echo "🔄 Iniciando servidor Ollama em background..."
    ollama serve &
    sleep 3
    
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Servidor iniciado com sucesso"
    else
        echo "❌ Erro ao iniciar servidor. Tente manualmente: ollama serve"
        exit 1
    fi
fi

echo ""
echo "📦 Baixando modelos necessários..."
echo ""

# Baixar modelo de embeddings
echo "📥 Baixando nomic-embed-text (para embeddings)..."
ollama pull nomic-embed-text

# Baixar modelo de LLM (perguntar qual)
echo ""
echo "Escolha o modelo de LLM para geração:"
echo "1) llama3.2 (leve e rápido)"
echo "2) qwen2.5:7b (recomendado para português)"
echo "3) mistral (boa qualidade)"
echo "4) llama3.1:8b (maior, melhor qualidade)"
read -p "Escolha (1-4) [padrão: 1]: " choice

case $choice in
    2)
        echo "📥 Baixando qwen2.5:7b..."
        ollama pull qwen2.5:7b
        MODEL="qwen2.5:7b"
        ;;
    3)
        echo "📥 Baixando mistral..."
        ollama pull mistral
        MODEL="mistral"
        ;;
    4)
        echo "📥 Baixando llama3.1:8b..."
        ollama pull llama3.1:8b
        MODEL="llama3.1:8b"
        ;;
    *)
        echo "📥 Baixando llama3.2..."
        ollama pull llama3.2
        MODEL="llama3.2"
        ;;
esac

echo ""
echo "✅ Configuração concluída!"
echo ""
echo "📝 Modelos instalados:"
ollama list
echo ""
echo "🧪 Testando modelo de LLM..."
ollama run $MODEL "Responda apenas: OK" --verbose
echo ""
echo "✨ Setup completo! Agora você pode usar Ollama no projeto."
echo ""
echo "💡 Dica: Configure o .env com:"
echo "   OLLAMA_LLM_MODEL=$MODEL"
echo "   OLLAMA_EMBEDDING_MODEL=nomic-embed-text"