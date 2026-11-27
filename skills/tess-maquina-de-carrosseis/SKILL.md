---
name: tess-maquina-de-carrosseis
description: >-
  Produz carrosséis em série para a empresa, com método TESS: define a identidade visual do perfil
  (cores, fontes, grade, estilos de lâmina), planeja uma série de 4 a 12 carrosséis a partir dos
  pilares de conteúdo e gera as lâminas como HTML pronto para exportar em imagem (1080×1350), com
  texto, legenda e calendário de publicação. Use quando o empresário disser "quero produzir carrosséis
  toda semana", "monta minha máquina de conteúdo", "cria a identidade dos meus posts", "faz os
  carrosséis do mês" ou "gera as imagens do carrossel". Não use para um carrossel avulso só em texto
  (use tess-storyteller-carrossel) nem para escolher temas (use tess-buscar-temas).
---

# Máquina de Carrosséis TESS

Você monta uma linha de produção de carrosséis com identidade consistente, para a empresa publicar com regularidade sem começar do zero toda semana.

## Antes de começar

Leia `compartilhado/voz-tess.md`, `compartilhado/metodo-tess.md` e o perfil da empresa.

## Etapa 1: identidade visual do perfil (uma vez)

Pergunte cores e fontes da marca da empresa, ou o site/perfil de referência. Defina:

- paleta de 1 cor de fundo, 1 cor de texto, 1 cor de destaque (contraste mínimo 4,5:1 para texto);
- 2 fontes (título e texto) disponíveis no Google Fonts;
- 5 estilos de lâmina: capa, texto, lista, número em destaque, chamada final;
- grade: margens de 96 px, título até 3 linhas, corpo até 6 linhas.

A identidade visual é a da empresa do cliente.

## Etapa 2: série

1. Pilares (educar, provar, bastidores, oferta) e proporção.
2. De 4 a 12 carrosséis com tema, gancho, objetivo e data.
3. Texto de cada carrossel com a estrutura de `tess-storyteller-carrossel`.

## Etapa 3: produção

- Gere um arquivo HTML por carrossel, com cada lâmina em um `<section>` de 1080×1350 px, fontes carregadas e sem dependência de imagem externa.
- Para exportar: abrir no navegador e capturar cada lâmina, ou usar um navegador sem interface com captura por elemento, quando disponível.
- Entregar legenda e texto alternativo por carrossel.

## Entrega

- Pasta com os HTML das lâminas e um `calendario.md` (ou planilha TESS) com data, tema, pilar, legenda e status.

## Cuidados

- Texto mínimo de 28 px na lâmina; contraste conferido.
- Imagem de terceiros só com licença de uso.

## Próximo passo

Ofereça `tess-videos-curtos` para transformar os melhores carrosséis em vídeo.
