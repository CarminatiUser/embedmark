# Validação da versão 0.4.1 — 09/11/2026

A versão **0.4.1 foi publicada e está disponível no [Marketplace do VS Code](https://marketplace.visualstudio.com/items?itemName=arthur-carminati.embedmark)**. O identificador é `arthur-carminati.embedmark`, do publicador Arthur Carminati. A consulta pública sem autenticação confirmou a versão com estado validado e público em 09/11/2026.

## Código e pacote verificados

- Código da distribuição: [commit 4a4de131](https://github.com/CarminatiUser/embedmark/commit/4a4de1315673af881a70325a40eef7f0976bf44b).
- Pacote: `embedmark-0.4.1.vsix`, 349.696 bytes, 102 entradas no arquivo VSIX.
- SHA-256 do pacote enviado: `fda540bffc09f7d6ce1e499b85dd564843898e8fa9dd037b6a7842ca2b2f8b76`.
- Versões da extensão e do núcleo: 0.4.1; protocolo JSON: 1.
- Backend com cinco dependências Python e 79 arquivos verificados por hash; nenhum `node_modules`, ambiente virtual ou configuração pessoal incluído.

## Verificações executadas

| Verificação | Resultado |
| --- | --- |
| Núcleo e ferramentas Python no macOS | 156 testes aprovados, sem testes ignorados |
| Compilação e execução com LVGL 8.3.11 real | Incluídas na suíte; eventos, glifos e 100 ciclos de criação/destruição verificados |
| TypeScript e testes unitários da extensão no macOS | Compilação e 20 testes aprovados |
| Extensão em VS Code real | Perfis confiável e restrito aprovados |
| Instalação do VSIX em perfis isolados | Instalação, versão e execução aprovadas nos dois perfis |
| Backend extraído do VSIX, sem bibliotecas do usuário | Seis exemplos válidos gerados; exemplo inválido recusado |
| Auditoria npm após instalação limpa | Zero vulnerabilidades reportadas em 09/11/2026 |
| Inventário após atualização do empacotador | Mesmos 100 arquivos de conteúdo antes e depois; sem dependências de desenvolvimento |
| GitHub Actions | Seis trabalhos aprovados: Python 3.10/3.12/3.14 e extensão em Linux/macOS/Windows |

Os resultados do ambiente remoto estão na [execução 42654341014](https://github.com/CarminatiUser/embedmark/actions/runs/42654341014), vinculada ao commit da distribuição. A conferência de formatação e análise estática usa o mesmo escopo do workflow: `translator`, `tests` e `tools`.

Os perfis de teste verificaram comandos, guia, exemplo, validação, geração, fontes, conteúdo não salvo do editor, proteção de arquivos alterados, diagnósticos e projetos com múltiplas pastas. Em modo restrito, a execução do tradutor permaneceu bloqueada e o guia e o exemplo continuaram acessíveis.

## Verificação da distribuição pública

O VSIX foi baixado do próprio Marketplace, sem autenticação. Seu tamanho e SHA-256 coincidiram exatamente com o pacote testado e enviado. Em seguida, o VS Code instalou `arthur-carminati.embedmark@0.4.1` diretamente pelo catálogo em um perfil temporário, e a listagem de extensões confirmou a versão. O perfil pessoal do autor não foi alterado por esse teste.

## Dependências de empacotamento

O empacotador passou para `@vscode/vsce` 4.1.0. O arquivo de versões fixadas inclui `@azure/identity` 4.14.1, `@azure/msal-node` 7.2.1 e `qs` 6.17.1. Um override limitado ao empacotador fixa `minimatch` 11.0.5. O inventário de arquivos foi comparado antes e depois dessa alteração, e o pacote produzido foi instalado e exercitado no VS Code.

Essas dependências são ferramentas de desenvolvimento; não acompanham a extensão instalada. A auditoria é uma observação na data indicada, não uma garantia de ausência de vulnerabilidades futuras.

## Limites

Os testes não representam uma nova validação física do ESP32-C6 ou do display ST7789T. A extensão gera a interface; configuração do hardware, driver, comunicação SPI, gravação e observação da tela continuam pertencendo ao firmware e ao ensaio físico. Os registros da [versão 0.4.0](VALIDACAO_0.4.0.md) permanecem preservados como histórico.
