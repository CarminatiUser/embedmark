# Contrato da linguagem na versão 0.4

Este documento descreve o comportamento implementado no núcleo. A entrada utiliza sintaxe inspirada em HTML/CSS, com regras próprias e suporte limitado. O parser HTML é tolerante à marcação; não é um validador completo de conformidade HTML.

## Estrutura

Um documento deve conter exatamente um `<screen>`. Os atributos `width` e `height` são inteiros de 1 a 8191; quando ausentes, usam 240 e 430. Parâmetros explícitos de configuração/CLI sobrescrevem essas dimensões depois da validação. Os blocos `<style>` são processados na ordem do documento.

| Tag | Comportamento |
|---|---|
| `screen` | Define a resolução de projeto; a tela gerada tem fundo preto. CSS para o ID da raiz não é aplicado e gera aviso |
| `div`, `container` | Cria objeto LVGL e preserva seus descendentes; sem dimensão explícita, preenche a área de conteúdo do pai |
| `label` | Cria texto; mantém conteúdo, inclusive espaços; markup interno é convertido em texto com aviso |
| `button` | Cria botão e seus filhos; texto direto vira um label; misturar texto direto e filhos é erro |

Um label de botão sem posição explícita é centralizado. Quando há `left`, `top`, `margin-left` ou `margin-top`, sua posição é preservada. Estilos próprios do label têm prioridade sobre a tipografia herdada do botão.

Componentes aceitam o atributo `id`. IDs podem ser omitidos; se fornecidos, devem ser únicos, não vazios e sem espaços/caracteres de controle. O gerador usa símbolos internos como `ui_node_1`, sem incorporar IDs ao código C. Um ID que não seja um identificador CSS simples precisará de escape CSS para ser selecionado; por exemplo `#\31 bad` para `id="1bad"`.

Tags desconhecidas geram aviso e sua subárvore é descartada. Atributos não suportados também são diagnosticados. A versão não interpreta `onclick`, JavaScript, arquivos CSS externos nem atributos `style` inline.

## Seletores e combinação de regras

Somente um seletor simples por ID é suportado em cada regra. Seletores de classe, tag, descendência e listas de seletores geram aviso.

Regras repetidas são combinadas por propriedade: a última declaração válida prevalece. Declarações `!important` prevalecem sobre declarações normais; entre duas importantes, vence a última. A expansão de propriedades abreviadas respeita essa mesma ordem.

## Valores e propriedades

Comprimentos aceitam números ou `px`. Percentuais, `em`, `rem`, `calc()` e `auto` não são interpretados. Valores devem ser finitos e caber no intervalo definido. Coordenadas calculadas fora de ±8191 interrompem a tradução. Esse limite corresponde ao LVGL 8.3 com coordenadas padrão e evita valores reservados para porcentagens e tamanhos especiais; o tradutor o mantém mesmo se o firmware habilitar coordenadas grandes.

| Propriedade | Comportamento |
|---|---|
| `left`, `top` | Posição relativa à área de conteúdo do pai; aceita valores negativos |
| `width`, `height` | Dimensões independentes e não negativas; zero é preservado; label sem tamanho usa seu conteúdo |
| `padding` e `padding-*` | Aplica os quatro lados, com escala horizontal em left/right e vertical em top/bottom |
| `margin` e `margin-*` | Expande 1–4 valores; left/top deslocam a posição; right/bottom não nulos geram aviso por ausência de fluxo |
| `color` | Cor do texto; herdada pelos filhos quando não definida |
| `background-color`, `background` | Cor de fundo sólida; `background` é somente um alias para cor |
| `font-size` | Valor positivo; herdado antes da escala; seleciona a fonte disponível de tamanho mais próximo |
| `text-align` | `left`, `center` ou `right`; herdado pelos filhos |
| `border-width`, `border-color`, `border-radius` | Borda sólida e raio não negativos; largura e raio escalam pelo eixo vertical |
| `border` | Forma limitada `<largura> solid <cor>` |
| `opacity` | Número de 0 a 1; não aceita unidade |
| `display` | `block` ou `none`; `none` aplica a flag LVGL de objeto oculto |

Font-weight, Flexbox, Grid, gradientes, imagens, sombras e animações não estão implementados. Propriedades desconhecidas são avisadas; valores inválidos de propriedades conhecidas são erros. `--strict` transforma a presença de qualquer aviso em falha.

As formas abreviadas de padding/margin seguem: um valor para todos os lados; dois para vertical/horizontal; três para superior/horizontal/inferior; quatro para superior/direita/inferior/esquerda. Não há colapso de margens ou fluxo de irmãos.

## Cores

Aceitos: `#RGB`, `#RRGGBB`, `rgb(r,g,b)` com componentes inteiros entre 0 e 255 e nomes da paleta em `translator/color_utils.py`. Valores inválidos não são substituídos silenciosamente por branco. Transparência é definida por `opacity`; `rgba()` e a palavra `transparent` não fazem parte deste contrato.

## Escala e fontes

As escalas são `largura_display/largura_projeto` e `altura_display/altura_projeto`. Posições e comprimentos são truncados em direção a zero após a escala, preservando a convenção anterior. A fonte usa o maior fator entre os dois e é mapeada ao tamanho mais próximo; empates escolhem o maior. Esse ajuste por eixos pode alterar proporções e não equivale a um layout responsivo de navegador.

Catálogo padrão: 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 32, 38 e 48. As fontes usadas devem ser habilitadas na configuração LVGL. O gerador emite verificações de compilação para elas e para LVGL 8.3.x. Um catálogo externo substitui o catálogo padrão para os labels gerados; tamanhos e cobertura passam a ser os declarados nele.

Os bytes UTF-8 do texto são preservados em strings C escapadas. Caracteres NUL são rejeitados. A cobertura padrão é a dos arquivos Montserrat do LVGL 8.3.11, que não inclui todos os acentos portugueses. Caracteres ausentes da fonte selecionada geram diagnóstico `font.glyphs`; isso não significa perda dos bytes de entrada. A opção `--font-manifest` e o catálogo TCC Sans PT estão descritos no [guia de fontes](FONTES.md).

## Diagnósticos e saída

Os diagnósticos têm `severity`, `code`, `message` e, quando disponíveis, `line`, `column` e `element_id`. Posições são baseadas em 1. Erros de declarações CSS são associados à posição no HTML de origem; diagnósticos de fonte/layout podem ter apenas o ID.

O resultado da API reúne código C, header, árvore, estilos, layout, fontes utilizadas e diagnósticos. A saída JSON usa `schema_version: 1`; o campo aditivo `fonts` descreve as fontes usadas e, para fontes externas, os arquivos C que o firmware deve compilar. Nenhuma validação de entrada malsucedida substitui os arquivos de saída existentes. A [API do firmware](API_FIRMWARE.md) define acesso por ID, eventos e ciclo de vida da tela.
