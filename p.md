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

Em `document_pre_processing.ipynb`, implementar:

- Carregar e processar em Markdown todos os arquivos dentro do diretório `data_dir`.
- O sistema agrupa os chunks sabendo de qual "arquivo fonte" eles vieram.
- Para cada arquivo fonte, ele pega 1 parágrafo representativo formata um prompt para o LLM via litellm.
- O LLM retorna o objeto JSON (com o documento, as 3 queries perfeitamente adequadas ao documento, na linguagem configurada em `SDG_LANG` e `SDG_LANG_CODE`, domínio etc.).
- Esse objeto de referência fica guardado temporariamente na memória, e em seguida, o código aplica aquele "ICL template" para todos os chunks que nasceram daquele mesmo arquivo.
- Tudo isso é acumulado para formar um gigantesco objeto Hugging Face Dataset, que por fim, é exportado em escala para o seed_data.jsonl único!
