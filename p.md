# 1

Como arquiteto senior, apenas analise e entenda o projeto `https://github.com/Red-Hat-AI-Innovation-Team/sdg_hub`.
Nos próximos passos faremos um building **Golden Path** de synthetic data generation pipelines using composable blocks and flows.
O desenvolvimento deve ter 100% de compatibilidade com o framework `SDH_HUB`.
Ambiente de trabalho: OpenShift AI e JupyterLab.

# 2

Apenas analise e entenda a documentação `https://deepwiki.com/Red-Hat-AI-Innovation-Team/sdg_hub/4.5-multi-language-support`.
Nos próximos passos usaremos o framework para adaptar a linguagem português do Brasil.

# 3

Apenas analise e entenda o `.env`.
O `.env` está corretamente configurado?

# 4

Apenas analise e entenda os notebooks abaixo.
Nos próximos passos vamos adaptar esses notebooks para minha necessidade:

- `examples/knowledge_tuning/enhanced_summary_knowledge_tuning/document_pre_processing.ipynb`
- `examples/knowledge_tuning/enhanced_summary_knowledge_tuning/knowledge_generation.ipynb`.

# 5

Não usaremos o `seed_data.jsonl` gerado pelo notebook (`document_pre_processing`), porque o campo `icl` do notebook está com dados fixos do exemplo, que nada tem a ver com o conteúdo dos documentos em `data_dir = "document_collection/"`, que vamos usar.

## Tarefa

Objetivo: Não ter o trabalho manual de formar o dicionário de icl. Usar exatamente a arquitetura que as empresas implementam em escala: o próprio LLM definindo seus pares de perguntas/respostas para orientar a extração em grande volume. Enriquecer múltiplos documentos para a geração de dados sintéticos em larga escala.

Em `document_pre_processing.ipynb`, implementar:

## 🏗️ Pipeline de Processamento e Geração Dinâmica de ICL

### **Etapa 1: Setup e Configuração de Ambiente**

- **Setup do LLM via LiteLLM**: O sistema lê de forma automatizada as credenciais corporativas no arquivo `.env`, definindo o provedor e o endereço (ex: `Translator Model` ou o `vLLM Fallback - gpt-oss-20b`).
- **Captura de Idioma**: Neste mesmo passo, o sistema captura a linguagem desejada configurada nas variáveis globais `SDG_LANG` e `SDG_LANG_CODE` (ex: `Portuguese (Brazil)`, `pt-br`), que ditará o idioma das perguntas e sumários de base.

### **Etapa 2: Varredura e Processamento de Arquivos**

- **Leitura Cíclica (Batching)**: A biblioteca `glob` é acionada para varrer o diretório alvo (ex: `data_dir` / `document_collection`) buscando iterativamente por arquivos formatados.
- **Carregamento Markdown**: Todos os arquivos Markdown correspondentes à varredura são progressivamente abertos, lidos em memória e segmentados em blocos lógicos (_chunks_), preservando a estrutura nativa do documento original.

### **Etapa 3: Geração de Contexto Dinâmico (ICL)**

- **Amostragem Representativa**: Para cada documento fonte lido, o sistema captura o primeiro parágrafo denso e representativo (chunk inicial).
- **Prompt Dinâmico (LLM Call)**: Esse chunk é empacotado em um prompt robusto e enviado ao LLM via LiteLLM. A instrução força o modelo a agir como especialista e exige o retorno formatado restritamente em `JSON_OBJECT`.
- **Extração Intencional**: O modelo devolve o JSON perfeitamente estruturado contendo as 3 perguntas analíticas coerentes com o contexto, o resumo de uma linha (`document_outline`) e a taxonomia de domínio nativa no idioma alvo (`pt-br`).

### **Etapa 4: Agrupamento em Memória**

- **Injeção de Modelo (ICL Template)**: Com o objeto de respostas em mãos, o resultado é guardado temporariamente na memória como o "Template Referência" daquele arquivo correspondente.
- **Agrupamento Otimizado**: O script mapeia e atrela essas 3 perguntas de alto valor e o resumo recém-gerado a **todos** os outros chunks secundários que originaram daquele exato arquivo fonte.
- O processo (Etapa 2 a 4) se repete sistematicamente para o próximo documento da fila até esgotar o diretório.

### **Etapa 5: Entrega Consolidadada em Larga Escala**

- **Compilação do Dataset**: Toda a massa atômica de chunks processados, somada aos respectivos ICLs dinâmicos de cada arquivo-fonte, é fundida para instanciar um gigantesco e estruturado pacote `Hugging Face Dataset`.
- **Exportação Única do Pipeline**: Ao final, os dados enriquecidos são gravados simultaneamente num único superarquivo (o `seed_data.jsonl`). Esse formato de saída fornece o terreno perfeito e massivo para alimentar as etapas de _Tuning Workflow_ com contexto denso adaptado para casos como RH, Leis, TI ou Documentos Corporativos.
