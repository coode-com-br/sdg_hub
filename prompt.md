Crie um prompt Golden Path para:

- Criar um notebook em: `examples/knowledge_tuning/enhanced_summary_knowledge_tuning`
- Pré-processar PDFs em lote usando Docling
- Chunk (default) automaticamente
- Usando flow com qualidade controlada
- Preenchimento de `icl_*` de forma automática via script
- Automático por PDF (gerar ICL diferente para cada documento sem intervenção)
- 1 template ICL Golden Path por domínio
- Usar filtro de faithfulness
- Golden Path pt-BR
- Para qualidade, mantenha `icl_*` no mesmo idioma alvo (pt-BR) no seed dataset
- Criar `.env` já fechado para:
  - Provider vLLM
    - INFERENCE_MODEL: "RedHatAI/gpt-oss-20b"
    - URL: "http://granite-ai-inference-server-ocp.apps.cluster-jzfpx.jzfpx.sandbox2518.opentlc.com/v1"
    - API_KEY: "1234"
  - Valores mínimos para rodar pt-BR de primeira
- 100% aderente ao framework `SDG_HUB`, com o mínimo de desenvolvimento customizado

# 6

Tem uma pasta: `examples/knowledge_tuning/multilingual`
Sua tarefa é entender de forma "Golden Path", e explicar como configurar para português do Brasil.

# 5

Explique o filtro de faithfulness

# 4

Usando qualidade mais controlada, o preenchimento dos `icl_*` podem ser automáticos?

# 3

Foque em qualidade + simplicidade.
Pelo que entendi, para qualidade, é obrigatório campos (icl\_\*)?

# 2

Foque no projeto SDG: https://github.com/Red-Hat-AI-Innovation-Team/sdg_hub.
Como tenho muitos documentos preciso que os dados sintéticos sejam gerados o mais automático possível.
Sua tarefa é entender de forma "Golden Path", e explicar como gerar dados sintéticos:

- A partir de arquivos PDFs
- Mais automático possível

# 1

O projeto `https://github.com/instructlab` fez o anuncio abaixo.
Sobre os projetos: `SDG` e `Training`, sua tarefa é entender e explicar:

- Quais os objetivos de cada um
- Quais as diferenças entre eles
- Como eles se complementam

```anuncio
Community Announcement (Sept 2, 2025)

Over the past year, we’ve been honored by your creativity, insights, and shared passion for advancing generative AI through InstructLab. Whether you added a new “knowledge” via pull request, offered feedback, joined a community call, or helped translate documentation, you’ve shaped our project in meaningful ways. Thank you.

To better align with evolving technical needs, we’re announcing an evolution for the InstructLab community. We will be refactoring the project by separating the components out to improve its maintainability and usability, primarily as a framework SDK for model tuning.
What's Changing

To enhance the long-term viability and efficiency of the InstructLab project, a strategic decision has been made to relocate its foundational building blocks into separate, dedicated project repositories. This carefully considered shift is anticipated to yield substantial benefits, primarily in the areas of maintainability and independent component maturation. This independent development will foster greater agility, allowing for more focused improvements and faster iteration cycles for individual parts of the project.
Looking Ahead

We’re excited about this next chapter and believe it will lead to more robust, flexible, and powerful tools for the generative AI community. We encourage you to follow the individual component projects in their new homes and continue contributing to their growth.

SDG: https://github.com/Red-Hat-AI-Innovation-Team/sdg_hub

Training: https://github.com/Red-Hat-AI-Innovation-Team/training_hub
```
