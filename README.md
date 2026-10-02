# TCC UI Translator

Ferramenta Python para gerar interfaces LVGL 8.3 a partir de uma linguagem simplificada inspirada em HTML e CSS. O núcleo interpreta a estrutura e os estilos, calcula um layout absoluto e gera arquivos C e header para integração ao firmware.

Versão **0.4.0**, com extensão desktop do VS Code, núcleo Python e laboratório ESP-IDF separado. A referência é ESP32-C6 com display ST7789T de 172 × 320 pixels. Outros presets apenas configuram dimensões; não representam suporte a drivers ou hardware já validado.

## Usar no VS Code

Instale o `.vsix` disponível na pasta `release` pelo menu **Extensions → Install from VSIX**. Requer VS Code 1.95 ou superior e Python 3.10 ou superior. O pacote inclui o tradutor e suas dependências Python; o usuário da extensão não precisa instalar bibliotecas com pip.

Abra uma pasta confiável e use a paleta de comandos:

- **TCC UI: Criar exemplo de contador** para começar com uma interface em português.
- **TCC UI: Validar interface** para ver erros e avisos em Problems.
- **TCC UI: Gerar interface LVGL** para preparar C/header, fontes usadas, licenças e CMake em uma pasta exclusiva.
- **TCC UI: Abrir guia de HTML/CSS suportado** para consultar o contrato da linguagem.

A extensão usa o conteúdo atual do editor, protege arquivos alterados manualmente e mantém a última saída válida quando a tradução falha. Configurações pertencem à pasta da interface, inclusive em workspaces com várias pastas. Consulte o [guia da extensão](extension/README.md), os [resultados verificados](docs/VALIDACAO_0.4.0.md) e as [instruções de publicação](docs/PUBLICACAO.md).

## Instalação e uso

Requer Python 3.10 ou superior. Na pasta do projeto:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
tcc-ui translator/sample_ui.html -o output/ui_generated.c --export-json output/ui_generated.json
```

No Windows, ative o ambiente com `.venv\Scripts\activate` em vez de `source`. A execução também está disponível como `python -m translator`. O comando antigo `python translator/main.py` continua gerando o exemplo padrão, com caminhos resolvidos a partir do próprio projeto.

A geração produz `ui_generated.c` e `ui_generated.h`. O JSON opcional contém a árvore, os estilos, o layout realmente calculado e os diagnósticos da mesma execução.

```sh
# Validar sem gravar código; --strict também rejeita avisos
tcc-ui examples/01_minima.html --validate --strict

# Configurar resolução física personalizada
tcc-ui translator/sample_ui.html -d custom --display-width 240 --display-height 320 -o output/custom.c

# Sobrescrever dimensões de projeto definidas em <screen>
tcc-ui translator/sample_ui.html --width 240 --height 430 -o output/design.c

# Consultar presets sem fornecer arquivo de entrada
tcc-ui --list-displays

# Diagnósticos JSON em stderr, para integração com ferramentas
tcc-ui examples/04_erros.html --validate --quiet --diagnostics-format json
```

`--quiet` oculta mensagens de sucesso e análise; erros e avisos continuam em stderr. Os códigos de saída são 0 para sucesso, 1 para falha de tradução/arquivo e 2 para erro de argumentos. `--check-perf` foi retirado: as antigas constantes por objeto não mediam desempenho.

## Uso como biblioteca

```python
from translator.config import TranslationConfig
from translator.main import UITranslator

translator = UITranslator(TranslationConfig(verbose=False))
result = translator.translate('<screen><label>Ola, LVGL!</label></screen>')
print(result.code)
print(result.computed_layout)
print([diagnostic.to_dict() for diagnostic in result.diagnostics])
```

`translate()` retorna `TranslationResult`. Entradas inválidas levantam `TranslationError`, que contém os diagnósticos. `translate_html()` mantém a interface que retorna apenas C. `translate_file()` mantém o retorno booleano e gera os arquivos. A CLI prepara o conjunto C/header/JSON antes de substituir a saída e restaura os arquivos anteriores se ocorrer uma falha de gravação. Isso não equivale a uma transação de sistema de arquivos resistente a falta de energia. Uma falha na validação não sobrescreve a última saída válida.

## Exemplos

| Arquivo | Objetivo |
|---|---|
| `examples/01_minima.html` | Tela e texto |
| `examples/02_espacamento.html` | Padding, borda e coordenadas relativas ao pai |
| `examples/03_hierarquia.html` | Pai sem ID, botão, regras repetidas e elemento oculto |
| `translator/sample_ui.html` | Painel de indicadores para a resolução de referência |
| `translator/advanced_example.html` | Contêineres com dimensões explícitas e posições locais |
| `examples/04_erros.html` | Entrada inválida intencional; deve retornar erro |
| `examples/05_interacao.html` | Contador em português; requer `--font-manifest examples/fonts/fontes.json` |

O código gerado fornece acesso aos componentes pelo ID e controle do ciclo de vida da tela. Eventos e lógica ficam no código da aplicação, usando a API LVGL. Esta versão não interpreta JavaScript. O exemplo `examples/firmware/ui_controller.c` registra o clique do botão e atualiza o contador, sem editar a saída do tradutor.

```sh
# Prepara código, controlador, fontes com acentos e fragmento CMake
python tools/prepare_demo.py
```

Os arquivos ficam em `output/interacao`. Consulte a [API do firmware](docs/API_FIRMWARE.md), o [guia de fontes](docs/FONTES.md) e a [integração ESP-IDF](ESP_IDF_INTEGRATION.md).

## Suporte e limitações

Consulte o [manual da linguagem](docs/LINGUAGEM.md) para o contrato completo. IDs são opcionais, mas os fornecidos devem ser únicos. Os nomes internos em C são independentes dos IDs, inclusive para nomes com hífen, acento ou que começam com número.

- Layout absoluto relativo à área de conteúdo do pai; não há fluxo CSS, Flexbox ou Grid.
- Padding é aplicado nos quatro lados. Margin-left e margin-top deslocam o objeto; valores não nulos de margin-right e margin-bottom geram aviso e não alteram esse layout.
- Fontes são selecionadas entre tamanhos Montserrat do LVGL. Font-weight não está implementado e gera aviso.
- O C gerado exige LVGL 8.3.x e informa no build quais fontes precisam estar habilitadas.
- UTF-8 é preservado. `--font-manifest` seleciona um catálogo externo com tamanhos, símbolos C e cobertura Unicode. Caracteres ausentes da fonte selecionada geram aviso. O catálogo fornecido traz acentos portugueses nos tamanhos 14, 20 e 24.
- Elementos/propriedades sem suporte geram avisos; valores inválidos para recursos suportados geram erro.
- `screen_main_create()` reutiliza a tela existente. `screen_main_get_object()` encontra componentes pelo ID; `screen_main_destroy()` exclui a tela depois que outra estiver ativa e as transições tiverem terminado. A aplicação controla a navegação e registra seus eventos.
- Uma saída gerada representa uma instância de tela. Vincular várias saídas no mesmo firmware exige suporte a namespaces, ainda pendente.
- Não há garantia de equivalência com um navegador, nem resultados medidos de desempenho, consumo ou economia de tempo.

## Integração e desenvolvimento

- [Laboratório local para testar na tela ESP32-C6/ST7789T](../tcc-ui-validation/README.md) — firmware separado compilado; validação física pendente.
- [Integração com o firmware](ESP_IDF_INTEGRATION.md)
- [Registro de correções e verificações](docs/CORRECOES_2026-09-28.md)
- [Integração e verificações da versão 0.3](docs/INTEGRACAO_0.3.0.md)
- [Validação e entrega da versão 0.4](docs/VALIDACAO_0.4.0.md)
- [Plano do produto, extensão e TCC](PLANO_DE_DESENVOLVIMENTO_E_TCC.md)

```sh
python -m pip install -r requirements-dev.lock
python -m pip install -e '.[dev]'
ruff check translator tests tools
ruff format --check translator tests tools
python -m pytest -q
```

O arquivo `requirements-dev.lock` registra as versões verificadas localmente com Python 3.12. A compatibilidade anunciada em outros ambientes ainda precisa ser confirmada pela matriz de testes.

Os testes de compilação precisam do código-fonte LVGL 8.3.x e de um compilador C. Sem eles, esses testes são explicitamente marcados como ignorados. Para executá-los:

```sh
LVGL_DIR=/caminho/para/lvgl CC=cc HOST_CC=cc python -m pytest -q
```

`CC` pode apontar para o compilador RISC-V da Espressif. `HOST_CC` deve ser um compilador nativo capaz de gerar executáveis para o computador. Sem `HOST_CC`, o teste de execução LVGL é explicitamente ignorado. `HOST_CFLAGS` e `HOST_LDFLAGS` permitem configurar SDK e linker locais.

A suíte compila o código gerado e também executa uma aplicação com LVGL real e display em memória: valida IDs, eventos, cobertura das fontes, exclusão e 100 ciclos de recriação. Essa execução não testa o firmware ESP-IDF completo nem o display físico. O workflow em `.github/workflows/tests.yml` prepara as verificações para Python 3.10 e 3.12; ainda precisa ser executado no repositório remoto.
