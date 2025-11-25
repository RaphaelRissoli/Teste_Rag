RAG_PROMPT="""
Abaixo estão trechos recuperados de documentos relevantes para a pergunta do usuário.
Utilize essas informações para compor sua resposta.

--- INÍCIO DO CONTEXTO ---
{contexto}
--- FIM DO CONTEXTO ---

Pergunta do Usuário: {question}

Instruções para a resposta:
- Sintetize as informações do contexto acima para responder à pergunta.
- Se o contexto contiver dados conflitantes, aponte a divergência.
- Responda diretamente à pergunta, sem preâmbulos desnecessários como "Com base no contexto...".
- Mantenha o tom técnico e objetivo.

"""