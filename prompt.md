Crie e execute a implementacao abaixo, sem deixar decisoes em aberto.

Objetivo:
Entregar um Golden Path pt-BR para SDG Hub com qualidade controlada e minimo de customizacao, criando:
1. Notebook: `examples/knowledge_tuning/enhanced_summary_knowledge_tuning/knowledge_generation_ptbr_golden_path.ipynb`
2. Arquivo: `examples/knowledge_tuning/enhanced_summary_knowledge_tuning/.env`

Escopo obrigatorio:
- Pre-processar PDFs em lote com Docling via `examples/knowledge_tuning/docparser_v2.py` + `examples/knowledge_tuning/docling_v2_config.yaml`.
- Chunk automatico com default Golden Path:
  - `chunk_size=1000`
  - `overlap=200`
- Usar flow de qualidade controlada:
  - `Extractive Summary Knowledge Tuning Dataset Generation Flow`
- Preencher `icl_*` automaticamente por script:
  - ICL diferente por PDF (sem intervencao manual)
  - `icl_document`, `icl_query_1`, `icl_query_2`, `icl_query_3`
- Aplicar 1 template ICL Golden Path por dominio (com fallback `General`).
- Manter `icl_*` no idioma alvo pt-BR.
- Executar com filtro de faithfulness ativo (nao remover blocos de avaliacao/filtro do flow).
- Aderencia total ao SDG_HUB (usar APIs/framework existentes; evitar framework paralelo).

Decisoes fechadas (nao alterar):
1. Flow padrao: `Extractive Summary Knowledge Tuning Dataset Generation Flow`.
2. Estrategia de ICL automatico: gerar por PDF via LLM e replicar para todos os chunks do mesmo PDF.
3. Idioma alvo: `SDG_LANG="Portuguese (Brazil)"`, `SDG_LANG_CODE="pt"`.
4. Variaveis de ambiente: formato nativo SDG_HUB (`VLLM_*`) com comentario de mapeamento para INFERENCE_*.

Conteudo minimo do `.env` (obrigatorio):
```dotenv
MODEL_PROVIDER=hosted_vllm
LITELLM_MODE=PRODUCTION

# Mapeamento solicitado:
# INFERENCE_MODEL=RedHatAI/gpt-oss-20b
# URL=http://granite-ai-inference-server-ocp.apps.cluster-jzfpx.jzfpx.sandbox2518.opentlc.com/v1
# API_KEY=1234

VLLM_MODEL=hosted_vllm/RedHatAI/gpt-oss-20b
VLLM_API_BASE=http://granite-ai-inference-server-ocp.apps.cluster-jzfpx.jzfpx.sandbox2518.opentlc.com/v1
VLLM_API_KEY=1234

SDG_LANG=Portuguese (Brazil)
SDG_LANG_CODE=pt
TRANSLATED_FLOWS_DIR=./translated_flows_pt

TRANSLATOR_MODEL=hosted_vllm/RedHatAI/gpt-oss-20b
TRANSLATOR_API_BASE=http://granite-ai-inference-server-ocp.apps.cluster-jzfpx.jzfpx.sandbox2518.opentlc.com/v1
TRANSLATOR_API_KEY=1234
VERIFIER_MODEL=hosted_vllm/RedHatAI/gpt-oss-20b
VERIFIER_API_BASE=http://granite-ai-inference-server-ocp.apps.cluster-jzfpx.jzfpx.sandbox2518.opentlc.com/v1
VERIFIER_API_KEY=1234

SEED_DATA_PATH=sdg_demo_output/seed_data.jsonl
OUTPUT_DATA_FOLDER=output_data_ptbr
MAX_CONCURRENCY=10
NUMBER_OF_SUMMARIES=10
ENABLE_REASONING=false
RUN_ON_VALIDATION_SET=false
```

Implementacao obrigatoria no notebook:
1. Carregar `.env` com `python-dotenv`.
2. Descobrir flows com `FlowRegistry.discover_flows()`.
3. Resolver traducao pt-BR com fallback automatico:
   - buscar `<Flow Name> (Portuguese (Brazil))`
   - se nao existir, usar `translate_flow(...)` com variaveis `TRANSLATOR_*` e `VERIFIER_*`
4. Ingerir PDFs em lote de `document_collection/*.pdf`.
5. Rodar parsing Docling em lote via `docparser_v2.py` para gerar `.md`.
6. Chunkar markdown com defaults (`1000/200`) para todos os arquivos.
7. Gerar ICL por PDF automaticamente:
   - selecionar trecho representativo do PDF
   - aplicar template por dominio (1 template por dominio)
   - pedir ao LLM retorno estruturado com:
     - `icl_document`
     - `icl_query_1`
     - `icl_query_2`
     - `icl_query_3`
   - validar nao vazio e pt-BR; fallback para template de dominio em caso de falha
8. Montar `seed_data.jsonl` com schema do flow:
   - `document`
   - `document_outline`
   - `domain`
   - `icl_document`
   - `icl_query_1`
   - `icl_query_2`
   - `icl_query_3`
9. Configurar modelo de inferencia no flow com `flow.set_model_config(...)` usando `VLLM_*`.
10. Executar `dry_run(sample_size=2)` e depois `generate(...)`.
11. Salvar outputs em `OUTPUT_DATA_FOLDER`.
12. Validar evidencias de qualidade e faithfulness.

Regras de qualidade obrigatorias:
- Nao remover etapas de faithfulness do flow.
- Garantir `icl_*` em pt-BR no seed dataset.
- Garantir ICL distinto por PDF.
- Garantir compatibilidade com API OpenAI-style do endpoint informado.
- Minimizar customizacao: reutilizar SDG Hub, Docling e utilitarios existentes.

Testes obrigatorios (com evidencias no notebook):
1. Teste de schema:
   - confirmar colunas obrigatorias do seed dataset.
2. Teste de ICL por PDF:
   - `n_unique(icl_document) >= n_pdfs_processados`.
3. Teste de idioma:
   - amostragem comprovando `icl_*` em pt-BR.
4. Teste de flow:
   - `dry_run(sample_size=2)` sem erro.
   - `generate(...)` com colunas esperadas.
5. Teste de faithfulness:
   - output final apenas com amostras aprovadas (`YES` no campo de julgamento correspondente do flow).

Formato de entrega esperado:
- Mostrar diff dos arquivos criados/alterados.
- Incluir instrucoes de execucao local (ordem de celulas/comandos).
- Relatar limitacoes e suposicoes.
- Nao pedir decisoes adicionais ao usuario.
