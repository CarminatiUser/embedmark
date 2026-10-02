# Arquitetura do produto

O TCC UI Translator gera uma interface LVGL 8.3 a partir de um subconjunto documentado de HTML/CSS. O produto tem um único núcleo de tradução; a extensão e a linha de comando usam esse mesmo código.

## Fluxo de tradução

1. `HTMLParser` identifica a tela, a hierarquia, os IDs e as posições no texto de origem.
2. `CSSParser` reúne regras por ID e valida as propriedades incluídas no contrato.
3. O cálculo de layout aplica dimensões, posições, bordas, espaçamento, herança de texto e escala para o display.
4. `LVGLGenerator` gera C/header com símbolos internos, estilos compartilhados e a API pública de criação, consulta e destruição.
5. `TranslationResult` reúne código, árvore, layout, fontes e diagnósticos. Falhas são representadas por `TranslationError`.

O layout é absoluto e relativo à área de conteúdo do pai. O programa não implementa um navegador, JavaScript, Grid ou Flexbox. Componentes, propriedades e restrições estão no [manual](docs/LINGUAGEM.md).

## Extensão do VS Code

A extensão TypeScript recebe o conteúdo do editor e as configurações da pasta correspondente. Um processo Python separado executa `translator.bridge` com um pedido JSON e devolve uma resposta estruturada. O protocolo tem versão própria e valida configurações; a extensão verifica a versão do núcleo incluído.

O processo é iniciado sem shell, com Python isolado (`-I -S`) e bibliotecas fornecidas no pacote. Há limite de entrada/saída, cancelamento e tempo máximo. A tradução exige confiança no workspace. O guia e os snippets permanecem disponíveis sem executar o tradutor.

Os diagnósticos vão para Problems, com posições quando disponíveis. A geração prepara C/header, fontes usadas, licenças e fragmento CMake em uma pasta exclusiva. Um manifesto identifica o proprietário e os hashes dos arquivos para preservar alterações manuais. O controlador da aplicação fica fora dessa pasta.

## Código no firmware

A saída representa uma instância de tela e fornece `screen_main_create`, `screen_main_get`, `screen_main_get_object` e `screen_main_destroy`. As referências são invalidadas quando objetos são excluídos pelo LVGL. Eventos e comportamento da aplicação usam a API LVGL; o tradutor não configura GPIO, touch ou periféricos.

O [laboratório](../tcc-ui-validation/README.md) inicializa SPI, ST7789T, iluminação, buffers e temporização do LVGL no ESP32-C6. O controlador de exemplo conta eventos, e o padrão de calibração ajuda a verificar cores e geometria. O firmware original em `Downloads/tela_lcd` é uma referência preservada.

## Distribuição e verificação

- `pyproject.toml` define o pacote do núcleo.
- `requirements-runtime.lock` fixa versões e hashes das cinco dependências Python fornecidas na extensão.
- `tools/bundle_backend.py` verifica os wheels, preserva licenças e produz o catálogo de hashes do núcleo incluído.
- `extension/package-lock.json` fixa as ferramentas de compilação e empacotamento da extensão.
- Os testes cobrem núcleo, API/CLI, protocolo, gravação de arquivos, processo Python, integração com VS Code e compilação/execução do C com LVGL.
- A execução com LVGL no computador, a compilação ESP-IDF e a validação física são resultados distintos, registrados em [VALIDACAO_0.4.0.md](docs/VALIDACAO_0.4.0.md).

O [relato anterior de arquitetura](docs/historico/ARCHITECTURE.md) foi mantido como histórico; estimativas de recursos nele não são medições do produto.
