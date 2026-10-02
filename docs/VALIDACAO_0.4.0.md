# Entrega e validação da versão 0.4.0

Execuções realizadas em **2 de outubro de 2026**, no macOS arm64. O produto entregue reúne núcleo Python, extensão desktop do VS Code e laboratório separado para ESP32-C6/ST7789T. O pacote de instalação é `release/tcc-ui-translator-0.4.0.vsix`.

## Resultado da entrega

A extensão foi instalada a partir do VSIX em perfis novos e testada em um VS Code real, versão 1.139.1. O teste confirmou que a instância ativada veio da instalação do pacote e estava em modo Production, sem usar a cópia de desenvolvimento.

O núcleo e a distribuição passaram em 155 testes Python; a extensão passou em 16 testes automatizados; o laboratório passou em 17 testes. São **188 testes**, além dos fluxos executados no VS Code, das instalações limpas e das compilações ESP-IDF descritas abaixo.

O código está pronto para a etapa de publicação da versão delimitada pelo [contrato da linguagem](LINGUAGEM.md). O envio ao Marketplace depende da conta do publicador. A aparência e a interação no display físico permanecem sem validação, pois nenhuma placa foi acessada ou gravada nesta rodada.

## Matriz de resultados

| Área | Verificação executada | Resultado |
|---|---|---|
| Núcleo | Parsing, estilos, layout, configuração, IDs, geração C/header, API, CLI, protocolo JSON e falhas | 148 testes aprovados, sem testes ignorados |
| LVGL real | Compilação, eventos, glifos, transições e 100 ciclos de criação/destruição | Aprovado com LVGL 8.3.11 no computador |
| Distribuição Python | Hashes de dependências, caminhos de arquivos, preservação/recuperação do bundle | 7 testes aprovados |
| Instalação do wheel | Ambientes limpos Python 3.10.22, 3.11.15, 3.12.2, 3.13.3 e 3.14.8 | Aprovados; sem instalação editável ou importação do projeto de origem |
| Backend dentro do VSIX | Seis entradas válidas e uma inválida nas mesmas cinco versões do Python | Aprovado; dependências externas ao pacote desabilitadas |
| Extensão | Processo Python, limites, cancelamento, timeout, arquivos, fontes, colisões e recuperação | 16 testes aprovados |
| VS Code — pasta confiável | Comandos, exemplo, guia, geração, acentos, Problems, alterações não salvas, proteção de buffers/arquivos e múltiplas pastas | Aprovado tanto em desenvolvimento quanto com o VSIX instalado |
| VS Code — pasta restrita | Guia e exemplo acessíveis; tradução bloqueada com confiança efetivamente desativada | Aprovado em ambos os modos de instalação |
| Conteúdo do VSIX | 102 entradas, 79 arquivos do backend conferidos por hash, 18 arquivos do núcleo idênticos ao wheel | Aprovado; 338 KiB aproximadamente |
| Firmware | Seis interfaces válidas importadas e compiladas com ESP-IDF 5.4.3 | Aprovado; contador restaurado na entrega |
| Entrada inválida no laboratório | Rejeição sem substituir a saída anterior | Aprovado |
| Testes do laboratório | Importação, preservação, recuperação e backups simulados | 17 aprovados; sem acessar dispositivos |
| Dependências | Auditoria das cinco bibliotecas Python e da árvore npm | Nenhuma vulnerabilidade conhecida reportada pelas consultas desta data |
| Estilo e tipos | Ruff/formatação Python; TypeScript em modo estrito | Aprovados |

A execução LVGL no computador não mede o consumo real de RAM/energia do microcontrolador nem certifica o display. O firmware do laboratório usa a instalação local ESP-IDF `v5.4.3-dirty`, com modificação preexistente em OpenThread preservada. O aviso não impediu os builds; não foi certificado um SDK limpo em outro computador.

## Requisitos e evidências

| ID | Critério de aceitação do produto | Evidência |
|---|---|---|
| RF01 | Traduzir o subconjunto documentado para C/header LVGL 8.3 | `tests/test_core.py`, `tests/test_c_compile.py`, seis exemplos |
| RF02 | Fornecer diagnósticos claros, com posição quando disponível | Testes do núcleo/protocolo e painel Problems no VS Code |
| RF03 | Manter a última saída válida após erro e preservar alterações manuais | Testes da CLI, escrita transacional e integração no editor |
| RF04 | Configurar dimensões, orientação e fontes sem editar o tradutor | Instalações limpas com preset custom/paisagem; casos de fontes |
| RF05 | Expor acesso aos objetos por ID e permitir eventos fora do código gerado | Runtime LVGL, controlador do contador e 100 ciclos |
| RF06 | Criar exemplo, validar e gerar pelo VS Code | Dois perfis reais e pacote VSIX instalado |
| RF07 | Tratar pastas com espaços/acentos, múltiplas pastas e conteúdo não salvo | Suíte do Extension Host |
| RNF01 | Impedir execução em workspace restrito e não interpretar argumentos por shell | Perfil realmente restrito e testes do processo |
| RNF02 | Distribuir dependências/versionamento de maneira reproduzível | Lockfiles, wheel, manifesto do backend, hashes e verificador do pacote |
| RNF03 | Compilar as interfaces no firmware de referência | Matriz ESP-IDF do laboratório |
| RF08 | Exibir e interagir corretamente no display físico | **Pendente**: executar o roteiro e anexar foto/log |

## Arquivos da entrega

- `release/tcc-ui-translator-0.4.0.vsix`: extensão instalável.
- `release/tcc_ui_translator-0.4.0-py3-none-any.whl`: pacote Python instalável.
- `release/tcc_ui_translator-0.4.0.tar.gz`: distribuição de fontes do núcleo.
- `release/SHA256SUMS`: identificação dos artefatos.
- [Instalações limpas Python](validation/0.4.0/clean-python-install.json).
- [Verificação do conteúdo e backend do VSIX](validation/0.4.0/package-verification.json).
- [Teste do VSIX instalado](validation/0.4.0/installed-extension-verification.json).
- [Testes do núcleo](validation/0.4.0/core-tests.json).
- [Auditoria Python](validation/0.4.0/runtime-dependency-audit.json) e [auditoria npm](validation/0.4.0/extension-dependency-audit.json).
- [Resultados do firmware](../../tcc-ui-validation/docs/VALIDACAO.md).

Os registros JSON preservam versões, configurações, resultados e hashes. Caminhos do projeto foram normalizados nos registros copiados para a documentação. Logs completos permanecem em `build/` e no laboratório, fora do Git.

## Reprodução

```sh
# Núcleo; LVGL_DIR aponta para os fontes reais do LVGL 8.3.11
LVGL_DIR=/caminho/lvgl CC=cc HOST_CC=cc python -m pytest -q tests tools/tests
ruff check translator tests tools
ruff format --check translator tests tools

# Extensão: usar Node.js 24 LTS e dependências do lockfile
cd extension
npm ci
npm test
npm run test:integration
npm run package
```

Depois de empacotar, na raiz:

```sh
python tools/verify_release.py release/tcc-ui-translator-0.4.0.vsix --python python3
node tools/verify_installed_extension.cjs release/tcc-ui-translator-0.4.0.vsix --report release/installed-extension-verification.json
```

No laboratório, `./lab validate` reproduz as importações/compilações. Esses comandos não gravam dispositivos. Para reproduzir compilação e execução LVGL no macOS local, foram usados LLVM Clang 20.1.6, `HOST_CFLAGS='-isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk'` e `HOST_LDFLAGS='-fuse-ld=/Library/Developer/CommandLineTools/usr/bin/ld'`.

## Pendências fora desta validação de código

1. Confirmar o identificador do publicador e enviar o VSIX pelo procedimento de [publicação](PUBLICACAO.md).
2. Confirmar a pinagem, executar a demonstração na tela física e guardar foto/log. O perfil padrão é o ativo no projeto original; a alternativa “Arthur” está disponível no menu do laboratório.
3. Executar a matriz remota de sistemas quando houver repositório remoto. Os workflows para Linux, Windows e macOS estão preparados; apenas macOS foi executado nesta entrega.
4. Reescrever o TCC como produto usando estas evidências, sem apresentar a validação física ou a publicação como concluídas.

Flexbox/Grid, JavaScript, imagens, LVGL 9, múltiplas saídas com namespaces e editor visual não fazem parte da versão 0.4.0. Os antigos helpers experimentais de Flexbox/dimensões automáticas agora falham com explicação, em vez de devolver resultados incorretos; a linguagem aceita pelo pipeline não mudou por isso.
