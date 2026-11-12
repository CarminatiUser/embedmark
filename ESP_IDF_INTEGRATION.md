# Integração com ESP-IDF e LVGL 8.3

A integração foi executada fisicamente em **11/11/2026** na placa **Waveshare ESP32-C6-LCD-1.47**, com ESP32-C6FH4, display ST7789 de 172 × 320 pixels, ESP-IDF 5.4.3 e LVGL 8.3.11. O contador foi regenerado pelo núcleo EmbedMark **0.4.2**, compilado e gravado no laboratório separado. O ensaio teve **143 verificações por console aprovadas**, além da confirmação visual de cores, enquadramento e acentos. Consulte o [relatório completo e seus limites](docs/VALIDACAO_FISICA_2026-11-11.md).

A [montagem com nanoESP32-C6 e LCD externo](docs/VALIDACAO_MONTAGEM_2026-11-12.md) foi ensaiada separadamente em **12/11/2026**, com perfil Arthur (**CS23**), 143 verificações seriais aprovadas e confirmação visual do contador. O [guia da demonstração](docs/DEMONSTRACAO.md) cobre o fluxo no editor e os comandos do laboratório. A tabela a seguir continua descrevendo exclusivamente a Waveshare.

## Perfil físico ensaiado

| Item | Configuração utilizada |
|---|---|
| Placa / chip / flash | Waveshare ESP32-C6-LCD-1.47 / ESP32-C6FH4 revisão 0.1 / 4 MB |
| Display / driver do laboratório | ST7789 / `Vernon_ST7789T`, 172 × 320 pixels |
| Comunicação | SPI2, 12 MHz, modo 0 |
| Pinagem do LCD | SCLK 7, MOSI 6, **CS 14**, DC 15, RST 21, BL 22 |
| Pixels / orientação | RGB565, BGR, `LV_COLOR_16_SWAP=0`; retrato, espelhamento X, deslocamentos X=34 e Y=0 |
| Iluminação | 50%, limitada no código do perfil |
| Console / eventos | USB Serial/JTAG como console principal; eventos enviados por software |

Essa placa não tem touch. O perfil antigo “Arthur”, com CS 23, não foi usado nesse ensaio. A montagem anterior com LCD externo e o protótipo empresarial descritos no TCC são configurações distintas; não se deve transferir sua pinagem para a Waveshare.

## Testar no laboratório separado

O ensaio utilizou o projeto local isolado `embedmark-validation-waveshare`, preparado a partir do laboratório anterior `embedmark-validation`, preservando o firmware de referência. Ele contém driver, LVGL, padrão de cores, contador com acentos e comandos para importar outra interface, compilar, copiar a flash e gravar uma porta explicitamente escolhida. O firmware completo não está incluído neste repositório; foram publicados o [relatório e o conjunto de evidências](docs/VALIDACAO_FISICA_2026-11-11.md), que não bastam para reconstruir o laboratório. Os comandos abaixo pressupõem que esse projeto completo esteja disponível como pasta irmã do EmbedMark.

```sh
cd ../embedmark-validation-waveshare
./lab build
./lab ports
```

Confira o perfil da placa e identifique a porta com `./lab ports` antes de usar `./lab flash PORTA`. Preserve um backup do firmware que pretende substituir. No laboratório Waveshare, `./lab import` regenera a interface a partir do HTML pelo núcleo Python; ele não copia automaticamente a saída C produzida pela extensão. Informe também o catálogo de fontes usado pela interface.

No firmware ensaiado, `p` mostra o padrão, `g` retorna à tela gerada, `c` envia `LV_EVENT_CLICKED`, `r` destrói e recria a interface e `a` alterna o incremento automático. `r` não reinicia o microcontrolador. A abertura do USB causou uma reinicialização inicial na sessão registrada, tratada por uma janela de inicialização de 3,5 segundos; não houve reinicialização posterior durante o ensaio. Esses comandos pertencem ao laboratório e não são acrescentados automaticamente ao firmware pelo EmbedMark.

## Exemplo completo com contador e acentos

1. Instale o tradutor e prepare os arquivos na pasta do projeto:

   ```sh
   python -m pip install -e .
   python tools/prepare_demo.py
   ```

2. Copie a pasta `output/interacao` para `main/embedmark_ui` do firmware. Ela contém C/header gerados, controlador do exemplo, três fontes C, catálogo, licença das fontes e fragmento CMake. Preserve `OFL.txt` com as fontes. O preparador protege um controlador modificado contra sobrescrita; `--output` permite preparar uma cópia em outro diretório.

3. No `main/CMakeLists.txt`, inclua o fragmento antes do registro existente:

   ```cmake
   include(embedmark_ui/embedmark_ui_sources.cmake)
   ```

   Acrescente `${EMBEDMARK_UI_SOURCES}` à lista `SRCS` e `${EMBEDMARK_UI_INCLUDE_DIR}` à lista `INCLUDE_DIRS` do `idf_component_register` já existente. Mantenha todos os fontes, includes e dependências do firmware. A referência local já declara `lvgl/lvgl: "~8.3.0"` em `main/idf_component.yml`; confira essa dependência no projeto em que integrar.

4. No aplicativo, inclua o controlador:

   ```c
   #include "ui_controller.h"
   ```

   Chame `ui_controller_start()` depois de inicializar LVGL e registrar o display, no contexto/tarefa ou sob a proteção de acesso já usada pelo firmware. Verifique o retorno booleano. Não há uma inicialização genérica que substitua os drivers, buffer, flush e temporização do seu projeto.

5. O controlador registra `LV_EVENT_CLICKED` e atualiza “Ações: N”. Para um clique físico, a placa precisa ter o dispositivo de entrada e o driver correspondentes configurados. Se a demonstração usar botão externo, conecte sua ação ao fluxo da aplicação/LVGL; o tradutor não configura GPIO nem assume que o display tenha touch.

6. Use o ambiente ESP-IDF configurado para o firmware e execute `idf.py build`. Após a gravação na placa escolhida, confira acentos, resolução, o mecanismo de entrada utilizado e a atualização do contador. Registre a configuração e os resultados. O preparador de exemplos apenas gera arquivos; a gravação é uma etapa separada do firmware.

O preparador gera tudo a partir de `examples/05_interacao.html`, `examples/fonts` e `examples/firmware`. O teste local executa esses mesmos fontes com LVGL real. O laboratório separado foi compilado por completo com ESP-IDF. Os passos desta seção são para integrar em outro firmware; essa integração adicional precisa de sua própria compilação e execução.

## Integração apenas da saída gerada

```sh
embedmark translator/sample_ui.html --strict -o output/ui_generated.c
```

Compile `ui_generated.c` como fonte do componente e inclua apenas `ui_generated.h` na aplicação. Chame `screen_main_create()` após a inicialização LVGL/display. Para as fontes padrão, habilite as opções `LV_FONT_MONTSERRAT_*` indicadas no C; no Kconfig ESP-IDF, confira as opções `CONFIG_LV_FONT_MONTSERRAT_*` correspondentes.

Com `--font-manifest`, compile também os arquivos C de fonte indicados no JSON e mantenha suas licenças. A declaração `LV_FONT_DECLARE` não substitui esses arquivos no link. Não inclua um arquivo `.c` dentro de outro.

## Ciclo de vida e eventos

`screen_main_create()` reutiliza a tela existente. `screen_main_get_object(id)` permite atualizar componentes e registrar eventos no código da aplicação. Para destruir a tela, carregue outra e espere as transições terminarem antes de chamar `screen_main_destroy()`. Referências a objetos excluídos devem ser obtidas novamente após a recriação.

Veja o contrato completo na [API do firmware](docs/API_FIRMWARE.md) e as instruções no [guia de fontes](docs/FONTES.md). As funções precisam do mesmo contexto/proteção de acesso usado pelo restante do firmware para o LVGL.

Presets alteram somente a resolução do layout. Selecionar ST7735, ILI9341 ou SSD1306 não instala um driver nem comprova compatibilidade com o hardware. Esta versão exige LVGL 8.3.x e não inclui migração para LVGL 9.
