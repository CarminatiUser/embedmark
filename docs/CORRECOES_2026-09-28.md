# Correções do núcleo em 28 de setembro de 2026

> Registro histórico anterior à adoção do nome EmbedMark em 14/10/2026. Os nomes de arquivos, comandos e resultados abaixo foram preservados para rastreabilidade; consulte o [guia de publicação atual](PUBLICACAO.md) para os novos pacotes.

O foco desta revisão foi tornar verificáveis as correções do tradutor. A extensão do VS Code, publicação e testes físicos permanecem nas etapas seguintes.

## Implementado

- Separação correta de margin/padding, expansão de 1–4 valores, combinação de regras e precedência de declarações importantes.
- Diagnóstico de propriedades/seletores/tags sem suporte e rejeição de valores inválidos, dimensões incorretas e IDs duplicados.
- Identificadores C internos determinísticos; preservação de componentes sem ID e seus descendentes.
- Altura/largura independentes, inclusive zero; aplicação dos quatro lados de padding, bordas, raio, opacidade e ocultação.
- Margin-left/top como deslocamento no layout absoluto; aviso explícito para right/bottom não nulos.
- Filhos dos botões preservados, com seus próprios estilos; herança de tipografia e centralização apenas na ausência de posição explícita.
- Cores validadas e strings C com escape UTF-8/controle; aviso para glifos ausentes da fonte padrão.
- Configuração customizada, precedência das dimensões de projeto e múltiplos blocos de estilo.
- Limite de coordenadas de ±8191, conferido contra os headers LVGL, evitando valores reservados para tamanhos especiais.
- Resultado único da tradução, com árvore, estilos, layout, código, header e diagnósticos.
- CLI instalável, modo de validação, modo estrito, diagnósticos JSON, quiet e listagem de presets independente da entrada.
- Preservação da saída quando a entrada é inválida e proteção contra caminhos de saída que substituam a entrada.
- Remoção das estimativas arbitrárias de desempenho/memória dos relatórios utilizáveis.
- Exemplos revisados e novos casos mínimos de hierarquia, espaçamento e erro.
- Testes de regressão e workflow de verificação automática preparado.

## Verificado localmente

- 82 testes aprovados, incluindo as regressões e os testes de CLI/API.
- Cinco exemplos válidos compilados para objetos C pelo compilador `riscv32-esp-elf-gcc` 14.2.0, usando os headers reais do LVGL 8.3.11.
- Entrada com nomes problemáticos e texto UTF-8 também compilada.
- Fonte desabilitada causa falha de compilação com orientação sobre qual opção habilitar.
- Ruff verificou os módulos e testes sem problemas, incluindo a formatação.
- Pacote wheel instalado em ambiente virtual novo com Python 3.12.14; biblioteca, exemplo empacotado, CLI e geração C/header/JSON executados fora da pasta do projeto.

A compilação dos arquivos não é o build completo do firmware nem uma comprovação de aparência no display. A execução física e a validação da instalação em outros sistemas continuam pendentes. O compilador padrão do macOS estava impedido pela licença pendente do Xcode; foi utilizado o compilador independente da Espressif já instalado, sem alterar licenças ou configurações do sistema.

## Pendências preservadas

Fontes customizadas com acentos, contrato público de acesso aos objetos/eventos, ciclo de vida das telas, maior cobertura de layout e dispositivos, extensão, lançamento público e validação acadêmica. Font-weight e fluxo CSS permanecem fora do subconjunto implementado. A suíte automatizada remota ainda não foi executada.

Uma cópia de segurança completa da base anterior foi guardada no workspace do TCC, em `backups/tcc-ui-translator_antes_das_correcoes_2026-09-28.zip`. Os arquivos de saída locais foram regenerados com a versão 0.2.0.
