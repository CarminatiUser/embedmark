# Validação da versão 0.4.2 — 09/11/2026

> **Atualização de acompanhamento — 11/11/2026:** Após esta rodada de software, o [ensaio físico documentado em 11/11/2026](VALIDACAO_FISICA_2026-11-11.md) utilizou o núcleo 0.4.2 na placa Waveshare ESP32-C6-LCD-1.47, com ESP32-C6FH4. Foram aprovadas 143 verificações com eventos por console, acompanhadas de confirmação visual e da fotografia IMG_6242. Esse registro atende RF08 no cenário ensaiado, sem comprovar touch ou entrada por botão físico. As contagens, os hashes e os limites da rodada de 09/11/2026 permanecem preservados abaixo.

> **Acompanhamento — 12/11/2026:** A [montagem com LCD externo](VALIDACAO_MONTAGEM_2026-11-12.md) recebeu um ensaio próprio, com 143 verificações seriais e confirmação visual do contador, além da conferência do fluxo de geração na extensão. Não foram alterados o pacote, o código ou os resultados históricos desta versão.

A versão **0.4.2 está publicada no [Marketplace do VS Code](https://marketplace.visualstudio.com/items?itemName=arthur-carminati.embedmark)**. Esta atualização adota a **licença MIT** para o código original do EmbedMark. O identificador permanece `arthur-carminati.embedmark`, do publicador Arthur Carminati. O fluxo funcional e as dependências permanecem iguais aos da versão 0.4.1.

## Código e pacote verificados

- Código da distribuição: [commit b5427f71](https://github.com/CarminatiUser/embedmark/commit/b5427f71118ca95b5c32de9e4bb7a8800faea31f).
- Pacote: `embedmark-0.4.2.vsix`, 349.963 bytes, 102 entradas.
- SHA-256: `49a2a505278852748d43a438babbe1900dd2b0b9283a607c6f925e41fe7c8ca5`.
- Extensão e núcleo: 0.4.2; protocolo JSON: 1.
- As licenças da raiz, da extensão e do núcleo incluído no VSIX contêm o mesmo texto MIT, com copyright de Arthur Felipe Carminati.
- Os nove arquivos de licença e autoria de terceiros conferidos conservaram os hashes anteriores. As fontes EmbedMark Sans PT mantêm a SIL Open Font License 1.1.
- Os pacotes Python wheel e sdist 0.4.2 foram gerados localmente com `License-Expression: MIT`; não foram publicados no PyPI.

## Verificações desta versão

| Verificação | Resultado |
| --- | --- |
| Núcleo e ferramentas Python no macOS | 156 testes aprovados, sem testes ignorados |
| Compilação e execução com LVGL 8.3.11 real | Aprovadas dentro da suíte do núcleo |
| TypeScript e testes unitários da extensão | Compilação e 20 testes aprovados |
| Extensão em VS Code real | Perfis confiável e restrito aprovados |
| Instalação do VSIX em perfis isolados | Instalação e verificações aprovadas nos dois perfis |
| Backend extraído do VSIX | Seis exemplos válidos gerados; exemplo inválido recusado |
| Auditoria npm após instalação limpa | Zero vulnerabilidades reportadas em 09/11/2026 |
| Dependências de desenvolvimento | 174 entradas do lock inalteradas |
| GitHub Actions | Seis trabalhos aprovados: Python 3.10/3.12/3.14 e extensão em Linux/macOS/Windows |

Os resultados remotos estão na [execução 42686491112](https://github.com/CarminatiUser/embedmark/actions/runs/42686491112), vinculada ao commit da distribuição. A análise estática e a conferência de formatação também passaram. A auditoria de dependências registra o resultado da consulta nessa data; não constitui garantia sobre vulnerabilidades futuras.

## Distribuição pública

A consulta pública sem autenticação confirmou a versão 0.4.2. O pacote baixado do Marketplace apresentou o mesmo tamanho e SHA-256 do arquivo testado e enviado, com licença MIT nos metadados e nos arquivos de licença do código original. A instalação pelo catálogo, usando `arthur-carminati.embedmark@0.4.2`, foi verificada em um perfil temporário do VS Code, sem alterar o perfil pessoal do autor.

O repositório GitHub identifica a licença como MIT. O README, os guias e a descrição do repositório refletem o código aberto. As licenças de terceiros continuam separadas em `THIRD_PARTY.md` e nos arquivos incluídos na distribuição.

## Histórico e limites

A primeira publicação, na versão 0.4.1, permanece documentada em [VALIDACAO_0.4.1.md](VALIDACAO_0.4.1.md). Seus hashes e registros não foram substituídos pelos desta atualização. Os resultados da [avaliação 0.4.0](VALIDACAO_0.4.0.md) também permanecem históricos.

Esta rodada não acrescenta validação física do ESP32-C6 ou do display ST7789T. O laboratório separado e a demonstração física mantêm seu escopo próprio; a licença MIT do produto não altera automaticamente os termos de componentes de terceiros ou de projetos separados.
