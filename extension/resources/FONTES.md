# Fontes com acentos e catálogos externos

O tradutor preserva texto UTF-8. Para exibir um caractere, a fonte utilizada também precisa conter seu glifo. A versão 0.3 permite selecionar um catálogo externo por `--font-manifest` ou `TranslationConfig(font_catalog=FontCatalog.load(caminho))`.

## Exemplo em português

```sh
tcc-ui examples/05_interacao.html --font-manifest examples/fonts/fontes.json --strict -o output/interacao/ui_generated.c
```

O catálogo TCC Sans PT inclui fontes de 14, 20 e 24 pixels, ASCII imprimível e `áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇºª°•`. Os tamanhos solicitados são ajustados para o mais próximo disponível no catálogo, com preferência pelo maior em caso de empate. Ele não inclui emojis, todos os símbolos das fontes LVGL, nem marcas combinantes de acentos; utilize os caracteres acentuados precompostos indicados.

Compile os arquivos `tcc_font_pt_14.c`, `tcc_font_pt_20.c` e `tcc_font_pt_24.c` junto ao aplicativo e mantenha `OFL.txt` com eles. O C gerado declara as fontes com `LV_FONT_DECLARE`; não as inclui como arquivos `.c` e não precisa habilitar equivalentes Montserrat embutidos para os labels gerados. O tema ou outros componentes do firmware podem continuar exigindo sua fonte padrão LVGL.

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
      "symbol": "tcc_font_exemplo_16",
      "source": "tcc_font_exemplo_16.c",
      "ranges": [[32, 126], [231, 231]]
    }
  ]
}
```

`size` deve ser um inteiro entre 1 e 512. Tamanhos, símbolos e arquivos são únicos no catálogo. Símbolos usam o prefixo `tcc_font_`, seguido de letras ASCII, números ou `_`. `source` contém somente o nome do arquivo `.c`, sem diretórios. Cada intervalo de `ranges` é inclusivo e contém pontos de código Unicode válidos; no exemplo, 231 representa `ç`.

O catálogo descreve fontes externas; o tradutor não abre, valida, converte ou copia automaticamente o C indicado em `source`. A aplicação precisa fornecer esses símbolos ao compilador/linker. O diagnóstico de cobertura usa os intervalos declarados da fonte selecionada: metadados incorretos não comprovam que o arquivo realmente contenha os glifos. O teste do catálogo fornecido neste projeto consulta cada glifo nas tabelas reais das três fontes.

## Reprodução e atribuição

As fontes TCC Sans PT são versões bitmap derivadas de Montserrat Medium 7.200, obtida do [LVGL v8.3.11](https://github.com/lvgl/lvgl/blob/v8.3.11/scripts/built_in_font/Montserrat-Medium.ttf). O TTF e sua declaração de copyright original de 2011 estão preservados em `tools/fonts`, sob SIL Open Font License 1.1. As fontes derivadas são distribuídas sob a mesma licença; a autoria de Montserrat é dos autores do projeto Montserrat.

SHA-256 do TTF: `421f26b23e2be6b98373d32acd3cb2897b154d4bf0a77d26534ce476e4cbed53`.

O [conversor oficial LVGL](https://github.com/lvgl/lv_font_conv) foi fixado em 1.5.3, com lockfile local. Para reproduzir os arquivos já incluídos no projeto:

```sh
npm ci --prefix tools/fonts --ignore-scripts
python tools/fonts/generate.py
```

A geração usa quatro bits por pixel, sem compressão, e preserva os dados de kerning do conversor. Node.js e o conversor são necessários apenas para regenerar as fontes; traduzir interfaces usa Python e os arquivos de fonte existentes.
