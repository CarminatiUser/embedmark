# Demonstração do contador: do HTML ao display

Este guia apresenta o fluxo do **EmbedMark 0.4.2** no VS Code e sua relação com a execução em um firmware. O contador foi ensaiado na [Waveshare com display integrado, em 11/11/2026](VALIDACAO_FISICA_2026-11-11.md), e na [montagem com nanoESP32-C6 e LCD externo, em 12/11/2026](VALIDACAO_MONTAGEM_2026-11-12.md). As configurações e evidências dos dois ensaios são distintas.

## 1. Criar a interface

Instale o [EmbedMark pelo Marketplace](https://marketplace.visualstudio.com/items?itemName=arthur-carminati.embedmark), tenha Python 3.10 ou superior disponível e abra uma pasta confiável no VS Code. Se necessário, ajuste **EmbedMark: Python Path** para o executável Python, sem argumentos.

Na paleta de comandos (`Cmd+Shift+P` no macOS ou `Ctrl+Shift+P` no Windows/Linux), execute **EmbedMark: Criar exemplo de contador**. Salve como `contador.html` dentro da pasta aberta. O exemplo descreve uma tela de **172 × 320 pixels**, o texto “Ações: 0”, o botão “Adicionar ação” e seus estilos.

Para este exemplo, mantenha o preset **st7789**, orientação **portrait**, dimensões de projeto **Design Width/Height** em `null` e **Font Manifest** vazio. A extensão usa o catálogo incluído EmbedMark Sans PT, com acentos. Preset e orientação definem o layout gerado; não configuram os pinos nem a rotação do driver físico. Consulte o [manual da linguagem](LINGUAGEM.md) para os limites do HTML/CSS aceito.

## 2. Validar e gerar

Execute **EmbedMark: Validar interface** e confira o painel Problemas. Em seguida, execute **EmbedMark: Gerar interface LVGL**. Com a configuração padrão, a saída fica em `generated/contador/`:

- `ui_generated.c` e `ui_generated.h`: implementação e API da interface;
- fontes `embedmark_sans_pt_*.c`, `fontes.json` e licença das fontes;
- `translation.json`: resultado da tradução;
- `sources.cmake`: lista de fontes para integrar ao projeto;
- `.embedmark-output.json`: registro de proteção contra sobrescrita de alterações manuais.

Mantenha callbacks, drivers e lógica da aplicação fora da pasta gerada. Para mudar a aparência, altere o HTML/CSS e gere novamente. O conteúdo atual do editor é usado; salve-o também para manter o arquivo de demonstração correspondente à saída.

## 3. Integrar no firmware

A extensão não compila nem grava o ESP32-C6. O firmware precisa inicializar o display e o LVGL, compilar os arquivos gerados e as fontes, criar a tela e registrar os eventos. Veja a [integração ESP-IDF](../ESP_IDF_INTEGRATION.md) e a [API do firmware](API_FIRMWARE.md).

Nos ensaios, o firmware foi preparado em laboratórios locais separados, que não estão incluídos neste repositório. Para mostrar o resultado em outra placa, prepare essa integração e confira a pinagem, o driver, as fontes e o mecanismo de entrada. O desenho de um botão não implica suporte a touch.

## 4. Demonstrar no console do laboratório

Os comandos abaixo pertencem ao firmware de demonstração ensaiado; não são comandos da extensão e não são adicionados automaticamente ao C gerado. Com esse firmware já preparado, abra seu console USB Serial/JTAG e aguarde a inicialização. A abertura da conexão pode reiniciar o microcontrolador.

| Comando | Efeito no laboratório |
|---|---|
| `h` | Exibe a ajuda |
| `g` | Seleciona a tela gerada |
| `r` | Destrói e recria a interface, zerando o contador; não reinicia o microcontrolador |
| `c` | Envia um evento de clique ao botão da interface |
| `a` | Alterna o incremento automático e informa ON/OFF |
| `p` | Seleciona o padrão de cores |

Para uma apresentação curta, deixe o automático **OFF**, envie `g` e `r`, observe zero, envie `c` três vezes com pausas para mostrar **0 → 1 → 2 → 3** e envie `r` para retornar a zero. Se o automático estiver ON, use `a` uma vez e confirme OFF. Os eventos vêm do console, sem touch ou botão físico.

O fluxo demonstra a descrição da interface, sua geração e a execução do resultado integrado ao firmware. Não mede economia de tempo, consumo ou desempenho. Os relatórios dos ensaios identificam os resultados observados e suas limitações.
