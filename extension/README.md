# EmbedMark

Gere interfaces **C para LVGL 8.3** usando um subconjunto explícito de HTML/CSS. A extensão inclui o tradutor, suas dependências e fontes com acentos em português. O preset padrão descreve uma tela de **172 × 320 pixels**.

A extensão gera o código da interface. O projeto de firmware continua responsável pelo driver do display, inicialização do LVGL e eventos da aplicação. HTML de páginas web, JavaScript, Flexbox e CSS completo não são suportados. O guia incluído descreve a linguagem aceita.

## Requisitos

- VS Code desktop 1.95 ou superior, em Windows, macOS ou Linux. Os testes automatizados da extensão abrangem os três sistemas; os resultados de cada versão estão no [GitHub Actions](https://github.com/CarminatiUser/embedmark/actions/workflows/tests.yml).
- Python 3.10 ou superior disponível como `python3` (macOS/Linux) ou `python` (Windows). Se necessário, configure **EmbedMark: Python Path** com o caminho do executável, sem argumentos.
- Pasta marcada como confiável no VS Code para executar validação ou geração.
- Firmware com LVGL 8.3 para compilar os arquivos produzidos.

Não é necessário executar `pip install`. O backend incluído executa localmente, sem enviar seu HTML a serviços externos. A extensão não coleta telemetria e não grava firmware na placa.

## Primeiro uso

1. Na aba **Extensões**, procure **EmbedMark**, do publicador **Arthur Carminati** (`arthur-carminati.embedmark`), e selecione **Instalar**. Também é possível abrir a [página no Marketplace](https://marketplace.visualstudio.com/items?itemName=arthur-carminati.embedmark).
2. Abra a pasta do seu projeto e execute **EmbedMark: Criar exemplo de contador**.
3. Salve o HTML na pasta do projeto.
4. Execute **EmbedMark: Validar interface**. Eventuais problemas aparecem no painel **Problemas**, identificados como **EmbedMark**.
5. Execute **EmbedMark: Gerar interface LVGL**.

A saída padrão fica em `generated/<nome-do-html>/`. O comando usa o conteúdo atual do editor, inclusive alterações ainda não salvas. Um documento sem nome deve ser salvo antes de gerar. Se o conteúdo mudar durante a geração, execute novamente. A validação pode analisar um exemplo ainda sem nome.

A pasta gerada contém `ui_generated.c`, `ui_generated.h`, as fontes C utilizadas, avisos de licença, `fontes.json`, `translation.json` e `sources.cmake`. O arquivo oculto `.embedmark-output.json` identifica a origem e registra hashes para proteger alterações manuais. Não remova esse registro.

Ao gerar novamente, apenas uma saída íntegra da mesma interface pode ser substituída. Se você adicionou ou editou arquivos nessa pasta, preserve suas alterações em outro local ou escolha outra pasta em **Output Directory**. A geração nunca substitui silenciosamente código escrito à mão. Mantenha callbacks, drivers e lógica da aplicação fora da pasta gerada.

## Migração da versão anterior

EmbedMark substitui o nome TCC UI Translator. Se você já instalou o pacote antigo, desative-o ou desinstale-o antes de usar EmbedMark. Nas configurações do usuário e do projeto, troque o prefixo `tccUiTranslator.` por `embedmark.` mantendo os valores; os comandos agora pertencem à categoria **EmbedMark** e os trechos HTML usam o prefixo `embedmark-`.

Uma pasta com o registro antigo `.tcc-ui-output.json` continua protegida pelos mesmos hashes e pela identificação do HTML de origem. Na próxima geração bem-sucedida, o registro é substituído por `.embedmark-output.json`. Arquivos editados, arquivos extras, registros conflitantes ou uma geração cancelada impedem a migração sem apagar a saída existente. Não renomeie nem remova esses registros manualmente.

A geração utiliza o bloqueio novo `.embedmark-lock` e o bloqueio legado `.tcc-ui-lock` para evitar gravações simultâneas por versões diferentes. O arquivo `sources.cmake` oferece `EMBEDMARK_UI_SOURCES` e mantém `TCC_UI_SOURCES` como alias de compatibilidade para projetos existentes. Os arquivos e símbolos das fontes incluídas agora usam `embedmark_sans_pt_`; prefira a lista CMake gerada em vez de enumerar nomes de fontes no firmware.

## Integração no firmware

Adicione os arquivos C da pasta gerada ao componente de sua aplicação, ou inclua `sources.cmake` e use a lista `EMBEDMARK_UI_SOURCES`. Inclua a pasta gerada entre os diretórios de cabeçalhos. Exemplo ESP-IDF, adaptando o caminho ao seu projeto:

```cmake
include("${CMAKE_CURRENT_LIST_DIR}/generated/contador/sources.cmake")
idf_component_register(
  SRCS "main.c" ${EMBEDMARK_UI_SOURCES}
  INCLUDE_DIRS "." "generated/contador"
  REQUIRES lvgl
)
```

Depois de inicializar o LVGL e registrar o display:

```c
#include "ui_generated.h"

lv_obj_t *screen = screen_main_create();
if (screen == NULL) {
    return; /* Tente novamente depois que a transição atual terminar. */
}
lv_obj_t *button = screen_main_get_object("incrementar");
/* Registre o callback da sua aplicação em button. */
```

Execute chamadas LVGL na mesma tarefa ou sob o bloqueio usado pelo seu firmware. `screen_main_create()` reutiliza a tela existente; `screen_main_destroy()` recusa destruir uma tela ativa. Carregue outra tela antes de destruí-la. Botões gerados precisam de callbacks e de um dispositivo de entrada ou eventos programáticos no firmware; a extensão não presume que o display tenha touch.

## Configurações

Todas as configurações estão no grupo **EmbedMark**. Configurações de interface se aplicam à pasta do HTML em projetos com múltiplas pastas.

| Configuração | Uso |
| --- | --- |
| Display Preset | Dimensões de referência: ST7789, ST7735, ILI9341, SSD1306 ou personalizadas. Não configura hardware. |
| Orientation | Retrato ou paisagem. Não gira o driver físico. |
| Display Width / Height | Dimensões do preset `custom`, antes da orientação. |
| Design Width / Height | Sobrescrevem a área de desenho; `null` usa o elemento `screen`. |
| Strict | Ativado por padrão. Bloqueia construções sem suporte e glifos ausentes. |
| Font Manifest | Vazio usa EmbedMark Sans PT incluída; `builtin` usa Montserrat LVGL; ou indique seu catálogo JSON. |
| Output Directory | Pasta exclusiva dentro do projeto. Aceita `${fileBasenameNoExtension}`. |
| Python Path | Caminho do executável Python, sem argumentos. |
| Timeout Seconds | Limite de execução, de 5 a 120 segundos. |

Caminhos relativos de fontes e Python são resolvidos a partir da pasta do projeto do HTML. Sem um projeto aberto, a pasta do HTML é a base. A saída não pode ser a raiz do projeto, conter o HTML de entrada ou atravessar links simbólicos. Fontes externas devem conter os arquivos C e seus avisos de licença junto do catálogo. Montserrat padrão do LVGL não contém todos os acentos; prefira o catálogo incluído para português.

## Ajuda e diagnóstico

- **EmbedMark: Abrir guia de HTML/CSS suportado** abre o manual incluído.
- Digite `embedmark-screen`, `embedmark-button` ou `embedmark-label` no editor HTML para inserir um trecho.
- O canal **EmbedMark** no painel Saída registra o resultado e os diagnósticos.
- **Python não encontrado:** ajuste Python Path para o executável instalado.
- **Arquivo gerado foi alterado:** preserve a mudança e use outra saída, ou restaure a versão gerada anterior.
- **Pasta em uso:** se nenhum comando estiver ativo, verifique uma execução interrompida antes de remover o arquivo `.embedmark-lock` ou `.tcc-ui-lock` indicado. Uma pasta `.embedmark-backup-*` ou `.tcc-ui-backup-*` deve ser preservada até conferir a recuperação.
- **Cor, orientação ou corte incorreto na placa:** confira a resolução configurada e o driver físico. A geração não altera pinagem, offset, RGB/BGR ou backlight.

Validação do código não substitui teste físico de cor, leitura, alinhamento e interação no display. Não há emulação do navegador ou promessa de equivalência com CSS completo.

## Licenças e publicação

O pacote oficial pode ser instalado e usado gratuitamente no VS Code. O código-fonte da ferramenta está disponível para consulta, com direitos reservados ao autor; não é software de código aberto. O código de interface gerado e os exemplos podem ser incorporados às suas aplicações. Os termos completos estão em [LICENSE.txt](https://github.com/CarminatiUser/embedmark/blob/main/extension/LICENSE.txt). As fontes incluídas preservam a SIL Open Font License e as dependências Python preservam suas respectivas licenças e atribuições no pacote.

O publicador é **Arthur Carminati** (`arthur-carminati`) e o identificador completo da extensão é `arthur-carminati.embedmark`. Consulte também o [repositório](https://github.com/CarminatiUser/embedmark), o [manual da linguagem](https://github.com/CarminatiUser/embedmark/blob/main/docs/LINGUAGEM.md) e o [canal de problemas](https://github.com/CarminatiUser/embedmark/issues).

Referências oficiais: [instalação e uso de extensões](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace), [Workspace Trust](https://code.visualstudio.com/docs/editing/workspaces/workspace-trust), [publicação de extensões](https://code.visualstudio.com/api/working-with-extensions/publishing-extension).

## Desenvolvimento e empacotamento

Este repositório usa Node.js 22 ou superior apenas para desenvolver e empacotar a extensão; o usuário final não precisa instalar Node.js. Execute `npm ci`, `npm test` e `npm run test:integration` na pasta `extension`. O teste de integração usa perfis temporários, separados do perfil pessoal, para testar pastas confiáveis e restritas. Em macOS ele usa a instalação em `/Applications/Visual Studio Code.app`; em outro ambiente, defina `VSCODE_EXECUTABLE_PATH` ou permita ao executor obter uma versão de teste. `EMBEDMARK_TEST_PYTHON` seleciona o Python dos testes.

`npm run package` reconstrói o backend a partir do código do repositório e das dependências com hashes fixados, confere suas versões e gera `release/embedmark-0.4.1.vsix`. `EMBEDMARK_BUILD_PYTHON` seleciona o Python usado para empacotar; por padrão é usado o ambiente `.venv` do repositório, quando presente. `EMBEDMARK_BUNDLE_OFFLINE=1` reutiliza os wheels já verificados em `build/wheels`. Estes procedimentos documentam a manutenção pelo titular e não ampliam os direitos da licença. O uso do pacote instalado funciona sem rede após Python estar disponível.
