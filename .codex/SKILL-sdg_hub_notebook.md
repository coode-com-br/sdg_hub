# sdg_hub_notebook

## Objetivo

Construir imagem de base, `sdg_hub_notebook`, para executar o projeto `sdg_hub` em plataforma Red Hat OpenShift.

Projeto `sdg_hub`:

- https://github.com/Red-Hat-AI-Innovation-Team/sdg_hub

## Placa GPU

A placa GPU utilizada tem a seguinte configuração:

- NVIDIA-SMI 550.144.03
- Driver Version: 550.144.03
- CUDA Version: 12.4
- Name: NVIDIA L40S
- Max memory = 44.521 GB

## Dockerfile

Utilizar a imagem abaixo como imagem de base no Dockerfile:

- quay.io/opendatahub/workbench-images:cuda-jupyter-minimal-ubi9-python-3.12

Componentes já instalados na imagem de base:

- requires-python = "==3.12.\*"
- CUDA
- WORKDIR (volume persistente): `/opt/app-root/src`

### Tarefa

Em `container/Dockerfile`, utilizar imagem de base e instalar o projeto `sdg-hub` e `sdg-hub[examples]`, através de `container/pyproject.toml`.

- Rodar `uv sync` para instalar dependências
- Manter USER 1001 no final

## pyproject.toml

- Dependências: `sdg-hub`
- Dependências opcionais: `sdg-hub[examples]`

### Tarefa

Em `container/pyproject.toml` configurar as dependências.
