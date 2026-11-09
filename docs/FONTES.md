# Fontes com acentos e catálogos externos

O tradutor preserva texto UTF-8. Para exibir um caractere, a fonte utilizada também precisa conter seu glifo. O suporte a catálogos externos foi introduzido na versão 0.3 e é mantido na 0.4.1: na CLI, use `--font-manifest`; na API Python, use `TranslationConfig(font_catalog=FontCatalog.load(caminho))`. Sem essa seleção, a CLI e a API usam Montserrat do LVGL.

Na extensão do VS Code, **Font Manifest** vazia usa o catálogo EmbedMark Sans PT incluído. O valor `builtin` seleciona Montserrat do LVGL; um caminho absoluto ou relativo à pasta do projeto seleciona outro catálogo. A extensão já copia as fontes externas utilizadas durante **Gerar interface LVGL**; não é necessário executar os comandos de CLI deste guia para esse fluxo. Os comandos abaixo documentam o uso e a manutenção pelo titular a partir do repositório, conforme a licença da ferramenta.

## Exemplo em português

```sh
embedmark examples/05_interacao.html --font-manifest examples/fonts/fontes.json --strict -o output/interacao/ui_generated.c
```

O catálogo EmbedMark Sans PT inclui fontes de 14, 20 e 24 pixels, ASCII imprimível e `áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇºª°•`. Os tamanhos solicitados são ajustados para o mais próximo disponível no catálogo, com preferência pelo maior em caso de empate. Ele não inclui emojis, todos os símbolos das fontes LVGL, nem marcas combinantes de acentos; utilize os caracteres acentuados precompostos indicados.

Ao integrar a saída da CLI/API, forneça e compile os arquivos C das fontes utilizadas junto ao aplicativo e preserve seus avisos de licença. O catálogo incluído fornece `embedmark_sans_pt_14.c`, `embedmark_sans_pt_20.c` e `embedmark_sans_pt_24.c`, acompanhados de `OFL.txt`. Na saída da extensão, use a lista `EMBEDMARK_UI_SOURCES` de `sources.cmake`, que já inclui os arquivos copiados. O C gerado declara as fontes com `LV_FONT_DECLARE`; não as inclui como arquivos `.c` e não precisa habilitar equivalentes Montserrat embutidos para os labels gerados. O tema ou outros componentes do firmware podem continuar exigindo sua fonte padrão LVGL.

Para preparar código gerado, controlador, fontes e fragmento CMake em uma única pasta:

```sh
python tools/prepare_demo.py
```

O diretório padrão é `output/interacao`. O preparador recusa sobrescrever um controlador modificado. Para gerar em outro local, use `--output caminho`.

## Formato do catálogo

```json
{
  "schema_version": 1,
  "name": "Minha fonte",
  "fonts": [
    {
      "size": 16,
      "symbol": "embedmark_font_exemplo_16",
      "source": "embedmark_font_exemplo_16.c",
      "ranges": [[32, 126], [231, 231]]
    }
  ]
}
```

`size` deve ser um inteiro entre 1 e 512. Tamanhos, símbolos e arquivos são únicos no catálogo. Símbolos usam o prefixo `embedmark_`, seguido de letras ASCII, números ou `_`. O prefixo legado `tcc_font_` continua aceito para catálogos existentes. `source` contém somente o nome do arquivo `.c`, sem diretórios. Cada intervalo de `ranges` é inclusivo e contém pontos de código Unicode válidos; no exemplo, 231 representa `ç`.

O catálogo descreve fontes externas. O núcleo, usado diretamente pela CLI ou pela API Python, não abre, valida, converte ou copia automaticamente o C indicado em `source`; a integração precisa fornecer esses símbolos ao compilador/linker.

A extensão realiza uma etapa adicional: lê os arquivos C das fontes utilizadas na mesma pasta do catálogo, verifica nomes, tipo de arquivo e limite de tamanho e os copia para a saída protegida. Também inclui um `fontes.json` com as fontes utilizadas e os avisos de licença encontrados ao lado do catálogo com nomes como `OFL.txt`, `LICENSE`, `COPYING` e `NOTICE`. Mantenha os arquivos e os avisos necessários juntos; a extensão não converte fontes nem analisa o conteúdo C para comprovar seus glifos.

Em ambos os fluxos, o diagnóstico de cobertura usa os intervalos declarados da fonte selecionada: metadados incorretos não comprovam que o arquivo realmente contenha os glifos. O teste do catálogo fornecido neste projeto consulta cada glifo nas tabelas reais das três fontes.

## Reprodução e atribuição

As fontes EmbedMark Sans PT são versões bitmap derivadas de Montserrat Medium 7.200, obtida do [LVGL v8.3.11](https://github.com/lvgl/lvgl/blob/v8.3.11/scripts/built_in_font/Montserrat-Medium.ttf). O TTF e sua declaração de copyright original de 2011 estão preservados em `tools/fonts`, sob SIL Open Font License 1.1. As fontes derivadas são distribuídas sob a mesma licença; a autoria de Montserrat é dos autores do projeto Montserrat.

SHA-256 do TTF: `421f26b23e2be6b98373d32acd3cb2897b154d4bf0a77d26534ce476e4cbed53`.

O [conversor oficial LVGL](https://github.com/lvgl/lv_font_conv) foi fixado em 1.5.3, com lockfile local. Para reproduzir os arquivos já incluídos no projeto:

```sh
npm ci --prefix tools/fonts --ignore-scripts
python tools/fonts/generate.py
```

A geração usa quatro bits por pixel, sem compressão, e preserva os dados de kerning do conversor. Node.js e o conversor são necessários apenas para regenerar as fontes; traduzir interfaces usa Python e os arquivos de fonte existentes.
