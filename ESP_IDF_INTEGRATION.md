# Integração com ESP-IDF e LVGL 8.3

A referência encontrada no firmware local é ESP32-C6, ESP-IDF 5.4.3, LVGL 8.3.11 e display ST7789T 172 × 320. A versão 0.3 foi compilada contra headers reais e executada com o LVGL no computador. O laboratório separado também teve o firmware completo compilado com ESP-IDF; a execução física na placa permanece pendente.

## Testar no laboratório separado

O projeto local `embedmark-validation` foi criado em `Downloads/embedmark-validation` a partir das configurações de `Downloads/tela_lcd/ESP32-C6-LCD-1.47-Test`. Ele não está incluído neste repositório, e seu endereço público ainda não foi confirmado. Ele contém o driver, LVGL, padrão de cores, contador com acentos e comandos para importar outra interface, compilar, copiar a flash e gravar uma porta explicitamente escolhida. O firmware original foi preservado. Os comandos abaixo pressupõem que esse laboratório esteja disponível como pasta irmã do EmbedMark.

```sh
cd ../embedmark-validation
./lab build
./lab ports
```

Confira a pinagem e identifique a porta conforme o README do laboratório antes de usar `./lab flash PORTA`. A configuração ativa do arquivo original e a alternativa comentada como “Arthur” têm pinos diferentes. Os resultados de compilação estão no arquivo local `embedmark-validation/docs/VALIDACAO.md`, fora deste repositório; o teste físico deve ser registrado separadamente.

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

6. Use o ambiente ESP-IDF configurado para o firmware e execute `idf.py build`. Depois, confira a interface na placa, incluindo acentos, resolução, clique e atualização do contador. Registre a configuração e os resultados. Nenhum firmware foi gravado automaticamente durante esta etapa.

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
