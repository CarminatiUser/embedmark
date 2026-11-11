# EmbedMark

Extensão para Visual Studio Code e núcleo Python para gerar interfaces **C para LVGL 8.3** a partir de um subconjunto documentado de HTML e CSS. O produto foi desenvolvido no TCC de **Ciência da Computação** de Arthur Felipe Carminati. O núcleo interpreta a estrutura e os estilos, calcula um layout absoluto e gera código e cabeçalhos para integração ao firmware.

Nome adotado em 14/10/2026; anteriormente TCC UI Translator. Registros históricos conservam a identidade usada nas respectivas execuções. Consulte o [registro da adoção do nome EmbedMark](docs/RENOMEACAO_EMBEDMARK.md).

Versão **0.4.2**, com extensão desktop do VS Code, núcleo Python e laboratório ESP-IDF separado. A validação física de 11/11/2026 utilizou a placa integrada **Waveshare ESP32-C6-LCD-1.47**, com ESP32-C6FH4 e display ST7789 de 172 × 320 pixels. Outros presets apenas configuram dimensões; não representam suporte a drivers ou hardware já validado.

## Disponibilidade

Este [repositório público](https://github.com/CarminatiUser/embedmark) reúne o código-fonte, a documentação e os exemplos do EmbedMark. O código original é **aberto sob a licença MIT**, permitindo uso, estudo, modificação e redistribuição, inclusive comercial, com preservação dos avisos de autoria e da licença.

A primeira publicação no [Marketplace do VS Code](https://marketplace.visualstudio.com/items?itemName=arthur-carminati.embedmark) ocorreu em 09/11/2026, na versão 0.4.1. A versão **0.4.2 está publicada**, com licença MIT, desde 09/11/2026. O download e a instalação pelo catálogo foram verificados. O identificador permanece `arthur-carminati.embedmark`, do publicador **Arthur Carminati**.

A pasta `release/` contém artefatos locais e não é versionada pelo Git. O pacote oficial da extensão pode ser instalado e usado gratuitamente. O [procedimento de empacotamento](docs/PUBLICACAO.md#reproduzir-a-distribuição) permite reproduzir a distribuição a partir do código aberto.

Consulte os [resultados da versão 0.4.2](docs/VALIDACAO_0.4.2.md).

Para conhecer o produto, comece pelo [manual de HTML/CSS](docs/LINGUAGEM.md), pelo [guia da extensão](extension/README.md) e pelos [exemplos](examples). A [arquitetura](ARCHITECTURE.md) descreve como a extensão e o núcleo se integram.

## Usar no VS Code

Requisitos: **VS Code 1.95 ou superior**, **Python 3.10 ou superior** e uma pasta de trabalho confiável. Na aba **Extensões**, procure **EmbedMark**, do publicador **Arthur Carminati**, e selecione **Instalar**. Você também pode abrir a [página oficial](https://marketplace.visualstudio.com/items?itemName=arthur-carminati.embedmark) ou usar `code --install-extension arthur-carminati.embedmark`. O pacote inclui o tradutor e suas dependências Python; Node.js e a instalação de bibliotecas com pip não são necessários para usar a extensão já empacotada.

Se o Python não for encontrado, configure **EmbedMark: Python Path** com o caminho do executável, sem argumentos. Se a extensão anterior TCC UI Translator estiver instalada, desative-a antes de usar o EmbedMark.

Abra uma pasta confiável e use a paleta de comandos:

- **EmbedMark: Criar exemplo de contador** para começar com uma interface em português.
- **EmbedMark: Validar interface** para ver erros e avisos em Problems.
- **EmbedMark: Gerar interface LVGL** para preparar C/header, fontes usadas, licenças e CMake em uma pasta exclusiva.
- **EmbedMark: Abrir guia de HTML/CSS suportado** para consultar o contrato da linguagem.

Salve o exemplo como `contador.html` dentro da pasta de trabalho antes de gerar. A saída padrão é `generated/contador/`, com `ui_generated.c`, `ui_generated.h`, fontes, licenças, `fontes.json`, `translation.json` e `sources.cmake`. Mantenha controladores e drivers fora dessa pasta; preserve o registro oculto `.embedmark-output.json`, usado na proteção contra sobrescrita.

A extensão usa o conteúdo atual do editor, protege arquivos alterados manualmente e mantém a última saída válida quando a tradução falha. Configurações pertencem à pasta da interface, inclusive em workspaces com várias pastas. Consulte o [guia da extensão](extension/README.md), os [resultados da versão 0.4.1](docs/VALIDACAO_0.4.1.md) e as [instruções de publicação](docs/PUBLICACAO.md).

## Primeiro HTML

Salve o exemplo abaixo como `minha_tela.html` e execute os comandos de validação e geração da extensão. A fonte com acentos é incluída no catálogo padrão da extensão.

```html
<screen id="painel" width="172" height="320">
  <label id="mensagem">Olá, EmbedMark!</label>
</screen>
<style>
  #mensagem {
    left: 12; top: 20; width: 148;
    font-size: 20; color: #FFFFFF;
  }
</style>
```

`screen` define as dimensões do desenho. O preset define o destino da tradução; no padrão `st7789` em orientação `portrait`, ambos medem 172 × 320. `Design Width` e `Design Height` com valor `null` respeitam o HTML. Presets e orientação não configuram pinos nem giram o driver físico. Consulte o [manual de HTML/CSS suportado](docs/LINGUAGEM.md) antes de adaptar uma interface.

## Usar pela linha de comando

O núcleo e a extensão podem ser utilizados, modificados e redistribuídos sob a licença MIT. Para utilizar a ferramenta dentro do editor, instale a extensão oficial; para executar o núcleo pela CLI ou integrá-lo a outro programa, siga os procedimentos abaixo.

Requer Python 3.10 ou superior. Para instalar o núcleo a partir do código-fonte, execute na pasta do projeto, em macOS/Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
embedmark translator/sample_ui.html -o output/ui_generated.c --export-json output/ui_generated.json
```

No Windows, crie o ambiente com `python -m venv .venv`. Ative-o com `.venv\Scripts\Activate.ps1` no PowerShell ou `.venv\Scripts\activate.bat` no Prompt de Comando, em vez de `source`. A execução também está disponível como `python -m translator`. O comando `tcc-ui` permanece como alias legado de `embedmark` para compatibilidade. O comando antigo `python translator/main.py` continua gerando o exemplo padrão, com caminhos resolvidos a partir do próprio projeto.

A geração produz `ui_generated.c` e `ui_generated.h`. O JSON opcional contém a árvore, os estilos, o layout realmente calculado e os diagnósticos da mesma execução.

```sh
# Validar sem gravar código; --strict também rejeita avisos
embedmark examples/01_minima.html --validate --strict

# Configurar dimensões personalizadas do destino, sem configurar hardware
embedmark translator/sample_ui.html -d custom --display-width 240 --display-height 320 -o output/custom.c

# Sobrescrever dimensões de projeto definidas em <screen>
embedmark translator/sample_ui.html --width 240 --height 430 -o output/design.c

# Consultar presets sem fornecer arquivo de entrada
embedmark --list-displays

# Diagnósticos JSON em stderr, para integração com ferramentas
embedmark examples/04_erros.html --validate --quiet --diagnostics-format json
```

Para o exemplo em português, selecione explicitamente o catálogo de fontes na CLI:

```sh
embedmark examples/05_interacao.html --font-manifest examples/fonts/fontes.json --strict -o output/contador/ui_generated.c
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
| [01_minima.html](examples/01_minima.html) | Tela e texto |
| [02_espacamento.html](examples/02_espacamento.html) | Padding, borda e coordenadas relativas ao pai |
| [03_hierarquia.html](examples/03_hierarquia.html) | Pai sem ID, botão, regras repetidas e elemento oculto |
| [sample_ui.html](translator/sample_ui.html) | Painel de indicadores para a resolução de referência |
| [advanced_example.html](translator/advanced_example.html) | Contêineres com dimensões explícitas e posições locais |
| [04_erros.html](examples/04_erros.html) | Entrada inválida intencional; deve retornar erro |
| [05_interacao.html](examples/05_interacao.html) | Contador em português; requer `--font-manifest examples/fonts/fontes.json` |

O código gerado fornece acesso aos componentes pelo ID e controle do ciclo de vida da tela. Eventos e lógica ficam no código da aplicação, usando a API LVGL. Esta versão não interpreta JavaScript. O exemplo [ui_controller.c](examples/firmware/ui_controller.c) registra o clique do botão e atualiza o contador, sem editar a saída do tradutor.

```sh
# Prepara código, controlador, fontes com acentos e fragmento CMake
python tools/prepare_demo.py
```

Os arquivos ficam em `output/interacao`. Consulte a [API do firmware](docs/API_FIRMWARE.md), o [guia de fontes](docs/FONTES.md) e a [integração ESP-IDF](ESP_IDF_INTEGRATION.md).

## Suporte e limitações

Consulte o [manual da linguagem](docs/LINGUAGEM.md) para o contrato completo. IDs são opcionais, mas os fornecidos devem ser únicos. Os nomes internos em C são independentes dos IDs, inclusive para nomes com hífen, acento ou que começam com número.

- Layout absoluto relativo à área de conteúdo do pai; não há fluxo CSS, Flexbox ou Grid.
- Padding é aplicado nos quatro lados. Margin-left e margin-top deslocam o objeto; valores não nulos de margin-right e margin-bottom geram aviso e não alteram esse layout.
- Fontes são selecionadas pelo tamanho mais próximo disponível no catálogo. A CLI usa Montserrat do LVGL por padrão; a extensão usa o catálogo EmbedMark Sans PT incluído. Font-weight não está implementado e gera aviso.
- O C gerado exige LVGL 8.3.x e informa no build quais fontes precisam estar habilitadas.
- UTF-8 é preservado. `--font-manifest` seleciona um catálogo externo com tamanhos, símbolos C e cobertura Unicode. Caracteres ausentes da fonte selecionada geram aviso. O catálogo fornecido traz acentos portugueses nos tamanhos 14, 20 e 24.
- Elementos/propriedades sem suporte geram avisos; valores inválidos para recursos suportados geram erro.
- `screen_main_create()` reutiliza a tela existente. `screen_main_get_object()` encontra componentes pelo ID; `screen_main_destroy()` exclui a tela depois que outra estiver ativa e as transições tiverem terminado. A aplicação controla a navegação e registra seus eventos.
- Uma saída gerada representa uma instância de tela. Vincular várias saídas no mesmo firmware exige suporte a namespaces, ainda pendente.
- Não há garantia de equivalência com um navegador, nem resultados medidos de desempenho, consumo ou economia de tempo.

O firmware deve inicializar o LVGL, configurar o driver e fornecer os eventos da aplicação. A extensão não grava a placa e não oferece uma prévia gráfica embutida. A execução gráfica com LVGL no computador verifica a interface e os eventos nesse ambiente; não emula o ESP32-C6, a comunicação SPI ou o display físico. O ensaio na placa, descrito abaixo, tem registros próprios e escopo limitado à configuração utilizada.

## Validação física

Em **11/11/2026**, o contador em português foi regenerado a partir do HTML pelo núcleo EmbedMark **0.4.2**, integrado ao firmware do laboratório e executado na **Waveshare ESP32-C6-LCD-1.47**, sem touch. O ambiente utilizou ESP-IDF 5.4.3 e LVGL 8.3.11; a identificação exata das versões, a pinagem e os hashes estão no [relatório da validação física](docs/VALIDACAO_FISICA_2026-11-11.md).

- **143 verificações por console aprovadas, sem falhas**, incluindo 50 ciclos de destruição/recriação da interface e 10 ciclos de alternância entre o padrão de cores e a tela gerada.
- Cores, orientação, borda completa e textos com acentos conferidos visualmente pelo autor; a fotografia registra o estado final **“Ações: 3”**.
- Cliques enviados por software pelo console USB Serial/JTAG, com atualização do contador e controle do modo automático. O ensaio não valida toque ou botão físico.
- Duração de **42,59 segundos**, incluindo 3,5 segundos de inicialização da conexão. Esse tempo descreve o ensaio, não uma medida de desempenho do tradutor ou da interface.

O [conjunto público de evidências](docs/validation/waveshare-2026-11-11/) reúne resultados, registros seriais, configuração e fotografia. No TCC, RF08 está **atendido no cenário ensaiado, com eventos por console**. As verificações físicas são distintas dos testes de software e da instalação da extensão; não comprovam todos os exemplos, outros displays, consumo, taxa de quadros ou estabilidade prolongada. O vídeo de demonstração será gravado posteriormente pelo autor.

## Integração e desenvolvimento

- [Validação física de 11/11/2026](docs/VALIDACAO_FISICA_2026-11-11.md) — configuração, protocolo, resultados e evidências do ensaio. O firmware completo foi preparado no laboratório local isolado `embedmark-validation-waveshare`, separado do laboratório anterior `embedmark-validation`; esses projetos não estão incluídos neste repositório. As evidências publicadas não substituem o projeto completo para recompilar e gravar a placa.
- [Integração com o firmware](ESP_IDF_INTEGRATION.md)
- [Registro de correções e verificações](docs/CORRECOES_2026-09-28.md)
- [Integração e verificações da versão 0.3](docs/INTEGRACAO_0.3.0.md)
- [Publicação e validação da versão 0.4.1](docs/VALIDACAO_0.4.1.md)
- [Histórico da validação da versão 0.4.0](docs/VALIDACAO_0.4.0.md)
- [Plano do produto, extensão e TCC](PLANO_DE_DESENVOLVIMENTO_E_TCC.md)

```sh
python -m pip install -r requirements-dev.lock
python -m pip install -e '.[dev]'
ruff check translator tests tools
ruff format --check translator tests tools
python -m pytest -q
```

O arquivo `requirements-dev.lock` registra as versões verificadas localmente com Python 3.12. A [validação da versão 0.4.2](docs/VALIDACAO_0.4.2.md) inclui a matriz aprovada para o núcleo em Python 3.10/3.12/3.14 e para a extensão em Linux/macOS/Windows; cada resultado corresponde ao commit e ao ambiente daquela execução.

Os testes de compilação precisam do código-fonte LVGL 8.3.x e de um compilador C. Sem eles, esses testes são explicitamente marcados como ignorados. Para executá-los:

```sh
LVGL_DIR=/caminho/para/lvgl CC=cc HOST_CC=cc python -m pytest -q
```

`CC` pode apontar para o compilador RISC-V da Espressif. `HOST_CC` deve ser um compilador nativo capaz de gerar executáveis para o computador. Sem `HOST_CC`, o teste de execução LVGL é explicitamente ignorado. `HOST_CFLAGS` e `HOST_LDFLAGS` permitem configurar SDK e linker locais.

A suíte compila o código gerado e também executa uma aplicação com LVGL real e display em memória: valida IDs, eventos, cobertura das fontes, exclusão e 100 ciclos de recriação. Essa execução não testa o firmware ESP-IDF completo nem o display físico. O workflow em `.github/workflows/tests.yml` verifica o núcleo em Python 3.10, 3.12 e 3.14 e a extensão em Linux, macOS e Windows. Consulte o [histórico de verificações no GitHub](https://github.com/CarminatiUser/embedmark/actions/workflows/tests.yml) para os resultados de cada commit e ambiente.

## Licença e atribuições

O código original do EmbedMark é **licenciado sob MIT**, com copyright de Arthur Felipe Carminati, conforme [LICENSE](LICENSE). A licença permite uso, modificação, distribuição, sublicenciamento e uso comercial, exigindo a preservação dos avisos de copyright e licença em cópias ou partes substanciais do software. O software é fornecido sem garantia, nos termos da licença. O pacote Python e a extensão identificam a licença como `MIT`, e o VSIX inclui os mesmos termos em [LICENSE.txt](extension/LICENSE.txt).

As dependências e fontes preservam suas próprias licenças, documentadas em [THIRD_PARTY.md](THIRD_PARTY.md). As fontes bitmap EmbedMark Sans PT derivam de Montserrat e mantêm a licença [SIL Open Font License 1.1](examples/fonts/OFL.txt) e a atribuição original.
