#!/usr/bin/env python3
"""
Script de teste para verificar se Ollama está configurado corretamente
"""
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import requests
from langchain_ollama import ChatOllama

def test_ollama_server():
    """Testa se o servidor Ollama está rodando"""
    print("🔍 Testando servidor Ollama...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Servidor Ollama está rodando")
            print(f"📦 Modelos instalados: {len(models)}")
            for model in models:
                print(f"   - {model.get('name', 'unknown')}")
            return True
        else:
            print(f"❌ Servidor respondeu com código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor Ollama")
        print("💡 Execute: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_llm():
    """Testa geração de texto com LLM"""
    print("\n🧪 Testando geração de texto...")
    try:
        llm = ChatOllama(
            model="llama3.2",
            base_url="http://localhost:11434",
            temperature=0.3
        )
        
        response = llm.invoke("Responda apenas: OK")
        print(f"✅ LLM funcionando!")
        print(f"📝 Resposta: {response.content[:100]}")
        return True
    except Exception as e:
        print(f"❌ Erro ao testar LLM: {e}")
        print("💡 Verifique se o modelo está instalado: ollama list")
        return False

def test_embeddings():
    """Testa geração de embeddings"""
    print("\n🧪 Testando embeddings...")
    try:
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": "Teste de embedding"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            embedding = response.json().get("embedding", [])
            print(f"✅ Embeddings funcionando!")
            print(f"📊 Dimensões: {len(embedding)}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Erro ao testar embeddings: {e}")
        print("💡 Verifique se nomic-embed-text está instalado: ollama pull nomic-embed-text")
        return False

def main():
    print("=" * 50)
    print("🧪 Teste de Configuração Ollama")
    print("=" * 50)
    print()
    
    server_ok = test_ollama_server()
    
    if not server_ok:
        print("\n❌ Servidor não está rodando. Execute: ollama serve")
        return
    
    embeddings_ok = test_embeddings()
    llm_ok = test_llm()
    
    print("\n" + "=" * 50)
    if embeddings_ok and llm_ok:
        print("✅ Todos os testes passaram!")
        print("✨ Ollama está pronto para uso")
    else:
        print("⚠️  Alguns testes falharam")
        print("💡 Verifique os modelos instalados: ollama list")
    print("=" * 50)

if __name__ == "__main__":
    main()