# 1

Como arquiteto senior, apenas analise e entenda o projeto `https://github.com/Red-Hat-AI-Innovation-Team/sdg_hub`.
Nos próximos passos faremos um building de synthetic data generation pipelines using composable blocks and flows.
Meu ambiente de trabalho é o OpenShift AI, e JupyterLab.

# 2

Apenas analise e entenda a documentação `https://deepwiki.com/Red-Hat-AI-Innovation-Team/sdg_hub/4.5-multi-language-support`.
Nos próximos passos usaremos a linguagem português do Brasil.

# 3

Apenas analise e entenda o `.env`. Ele está corretamente configurado?

# 4

Apenas analise e entenda os notebooks abaixo. Nos próximos passos vamos executar estes notebooks:

- `examples/knowledge_tuning/enhanced_summary_knowledge_tuning/document_pre_processing.ipynb`
- `examples/knowledge_tuning/enhanced_summary_knowledge_tuning/knowledge_generation.ipynb`.

# 5

Não usaremos o `seed_data.jsonl` gerado pelo passo anterior (`document_pre_processing`), porque o campo `icl` do notebook está com dados fixos do exemplo, que nada tem a ver com o conteúdo dos documentos em `data_dir = "document_collection/"`.

## Tarefa

Objetivo: Não ter o trabalho manual de formar o dicionário de icl. Usar exatamente a arquitetura que as empresas implementam em escala: o próprio LLM definindo seus pares de perguntas/respostas para orientar a extração em grande volume.

Em `document_pre_processing.ipynb`:

- Usar o litellm (que já é dependência do sdg_hub) para ler um parágrafo limpo de cada documento, gerar as três perguntas perfeitamente adequadas ao documento e injetá-las no seed_data.
- Pegar automaticamente as linhas reais e coerentes de cada documento.
- Envia isso pro modelo (OpenShift/vLLM via litellm).
- Força ele a responder num formato JSON válido extraindo o resumo e 3 perguntas coerentes.
- Anexar no seed_data.map para ser processado pelo `knowledge_generation.ipynb` de forma redonda, em ótimo Português do Brasil.
