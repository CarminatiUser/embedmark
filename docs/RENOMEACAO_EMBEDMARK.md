# Adoção do nome EmbedMark

Em 14/10/2026, o autor escolheu **EmbedMark** como identidade do produto. A versão continua **0.4.0** durante a preparação da primeira publicação. O publicador proposto continua `arthur-carminati`; o envio ao Marketplace permanece uma etapa separada.

## Identidade atual

| Elemento | Nome |
|---|---|
| Produto | EmbedMark |
| Distribuição Python e comando principal | `embedmark` |
| Nome exibido no VS Code | EmbedMark |
| Identificador da extensão | `embedmark` |
| Identificador completo proposto | `arthur-carminati.embedmark` |
| Pacote instalável | `embedmark-0.4.0.vsix` |
| Pasta principal | `Downloads/embedmark` |
| Laboratório da tela | `Downloads/embedmark-validation` |
| Fontes derivadas do exemplo | EmbedMark Sans PT |
| Símbolos das fontes | `embedmark_sans_pt_14`, `embedmark_sans_pt_20`, `embedmark_sans_pt_24` |

## Compatibilidade

O comando antigo `tcc-ui` permanece como alias do comando `embedmark`. O módulo Python `translator` e a classe `UITranslator` conservam seus nomes internos, de forma que imports existentes continuam válidos. Catálogos de fontes com prefixo `tcc_font_` continuam aceitos; novos catálogos usam `embedmark_`.

As fontes bitmap mantêm a origem Montserrat Medium 7.200, a atribuição dos autores do projeto Montserrat e a licença SIL OFL 1.1. Somente a identidade dos arquivos derivados e seus símbolos foram alterados; a reprodução confirmou arquivos idênticos aos gerados com os novos nomes.

Os registros de testes, hashes, pacotes anteriores e textos históricos mantêm os nomes usados quando foram produzidos. Uma evidência de TCC UI Translator não é apresentada como resultado de um pacote EmbedMark reconstruído.

Na extensão, comandos e configurações agora usam `embedmark.*`. Desative a extensão anterior, se estiver instalada, e troque o prefixo `tccUiTranslator.` nas configurações existentes, preservando os valores. Os registros de saída `.tcc-ui-output.json` continuam sendo lidos e verificados; a migração para `.embedmark-output.json` só ocorre após uma geração bem-sucedida. Alterações manuais, arquivos adicionais, origem diferente ou registros conflitantes bloqueiam a substituição. O cancelamento preserva a saída anterior. O bloqueio legado permanece em uso junto ao novo para impedir gravações simultâneas por versões distintas. A lista CMake atual é `EMBEDMARK_UI_SOURCES`, com o alias `TCC_UI_SOURCES` preservado.

## Verificações do núcleo

- 156 testes Python e ferramentas aprovados, sem testes ignorados, incluindo compilação C contra LVGL real, fontes e 100 ciclos de criação/destruição em memória.
- Análise estática e formatação aprovadas.
- Instalação editável do pacote `embedmark` e execução das duas entradas de terminal (`embedmark` e `tcc-ui`) verificadas.
- Exemplo em português validado em modo estrito.
- Reprodução das três fontes C, catálogo e licença confirmada byte a byte.

O [registro estruturado](validation/embedmark-2026-10-14/core-tests.json) delimita ambiente e escopo. A publicação no Marketplace e a observação da tela física não são resultados destas verificações.

## Entrega e verificação dos novos artefatos

Em **14/10/2026**, foram produzidos os três artefatos com a identidade EmbedMark, mantendo a versão 0.4.0:

Os artefatos e relatórios desta seção permanecem na pasta local `release/`, ignorada pelo Git. Os caminhos identificam evidências da entrega local e não são links de download; esses arquivos não integram a publicação do código para consulta.

| Artefato | Finalidade |
|---|---|
| `release/embedmark-0.4.0.vsix` | Instalação da extensão no VS Code |
| `release/embedmark-0.4.0-py3-none-any.whl` | Instalação separada do núcleo Python |
| `release/embedmark-0.4.0.tar.gz` | Distribuição do código-fonte Python |

A execução atual reúne **197 testes aprovados**: 156 do núcleo e ferramentas, 20 da extensão e 21 do laboratório. Os testes da extensão incluem a migração de saídas antigas, a recusa de sobrescrita de alterações manuais e a recuperação após cancelamento. Essa contagem é separada das verificações de instalação descritas a seguir.

- O relatório local `release/embedmark-package-verification.json` aprovou o conteúdo do novo VSIX, os hashes de 79 arquivos incluídos e a correspondência de 18 arquivos do núcleo com o wheel. Com Python 3.12.2, seis exemplos válidos foram processados e o exemplo inválido foi rejeitado.
- O relatório local `release/embedmark-installed-extension-verification.json` confirmou a ativação do VSIX instalado como `arthur-carminati.embedmark`, nos perfis confiável e restrito. Ambos concluíram com sucesso. O SHA-256 do VSIX verificado é `0e790754bbb0bd2ba6e1ac1d91f6254a1015c507cb06119c262722f59cdff005`.
- O relatório local `release/embedmark-wheel-verification.json` registra a instalação em um ambiente Python 3.12.2 isolado, sem rede e sem importar o código do repositório. Os comandos `embedmark` e `tcc-ui` informaram a versão 0.4.0, validaram o exemplo em português em modo estrito e produziram arquivos C e header idênticos. A verificação de dependências não encontrou inconsistências.

O registro da entrega `release/DELIVERY.json`, o arquivo de hashes `release/SHA256SUMS` e as instruções de instalação `release/LEIA-ME.txt` identificam os artefatos locais atuais. Os metadados anteriores foram preservados em `release/history/2026-10-02/CONTEXTO.txt`, incluindo o reempacotamento de 14/10 realizado ainda com o nome antigo. Arquivos de distribuição com os prefixos `tcc-ui-translator-` e `tcc_ui_translator-`, assim como os relatórios sem o prefixo `embedmark-`, permanecem históricos.

As verificações desta entrega ocorreram no macOS. Os testes anteriores em cinco versões Python e os seis builds ESP-IDF continuam registrados no histórico; não foram repetidos nesta rodada de distribuição. O sdist foi construído e teve seu hash registrado; a instalação isolada foi verificada a partir do wheel. A publicação no Marketplace, a confirmação da identidade do publisher `arthur-carminati`, a execução da matriz remota nos demais sistemas e a observação do display físico permanecem pendentes.
