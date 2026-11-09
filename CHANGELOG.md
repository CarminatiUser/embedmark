# 0.4.1 — 09/11/2026

- Versão publicada no [Marketplace do VS Code](https://marketplace.visualstudio.com/items?itemName=arthur-carminati.embedmark) pelo publicador `arthur-carminati`, com download e instalação verificados.
- Uso gratuito da extensão oficial, mantendo o código-fonte proprietário disponível para consulta e as licenças dos componentes de terceiros.
- Ferramentas de empacotamento atualizadas e dependências de desenvolvimento corrigidas conforme auditoria npm.
- Documentação de instalação, links públicos e versões da extensão e do núcleo sincronizados.
- Teste de subprocesso corrigido para UTF-8 no Windows; protocolo e linguagem preservados.

# Identidade EmbedMark — 14/10/2026

- Produto renomeado para EmbedMark antes da publicação, mantendo a versão 0.4.0.
- Distribuição Python e comando principal `embedmark`; `tcc-ui` permanece como alias legado.
- Fontes derivadas passam a se chamar EmbedMark Sans PT, com símbolos `embedmark_sans_pt_*` e atribuições originais de Montserrat preservadas.
- Documentação e ferramentas de distribuição adotam a nova identidade. Os registros anteriores abaixo conservam os nomes usados em cada execução.

# 0.4.0 — 02/10/2026

- Extensão desktop do VS Code com validação, geração, exemplo, snippets e guia da linguagem.
- Núcleo e dependências Python incluídos no VSIX, com versões/hashes registrados e licenças preservadas.
- Diagnósticos em Problems; configurações por pasta; uso do conteúdo atual do editor; cancelamento e limite de execução.
- Proteção de saídas modificadas manualmente e preparação conjunta de código, fontes e CMake.
- Protocolo JSON 1 entre extensão e núcleo, com tipos/limites explícitos e validação estrita por padrão.
- Reversão de C/header/JSON em falhas de gravação pela CLI e API.
- Correções de strings C com trigraphs, Unicode inválido, aninhamento excessivo e localização de diagnósticos.
- Helpers experimentais de Flexbox/dimensões automáticas agora recusam operações não suportadas; não faziam parte do pipeline aceito.
- Pacote Python, pacote VSIX, testes de instalação e roteiro do firmware de referência.

Resultados executados e limites: [VALIDACAO_0.4.0.md](docs/VALIDACAO_0.4.0.md). Publicação no Marketplace e observação do display físico são etapas separadas.

# Versão 0.3.0 — integração com firmware

- API pública de acesso por ID, criação idempotente e destruição com proteção da tela ativa e de transições.
- Invalidação das referências quando componentes ou a tela são excluídos pelo LVGL.
- Catálogos de fontes externas, seleção por tamanho e diagnóstico de cobertura da fonte escolhida.
- Fontes TCC Sans PT com acentos, fontes de origem/licença e geração reproduzível.
- Exemplo de contador com eventos, código de aplicação separado e preparação do conjunto para o firmware.
- Teste executável com LVGL real, verificação dos glifos e 100 ciclos de criação/destruição.
- Mudança de contrato: `screen_main_create` retorna a raiz e reutiliza a instância existente. Regere C e header juntos.

# 0.2.0 — 28/09/2026

Correções do núcleo, pacote instalável, diagnósticos, exemplos revisados e testes de regressão. Detalhes em [registro da revisão](docs/CORRECOES_2026-09-28.md). Extensão e testes físicos pendentes.

O [changelog anterior à revisão](docs/historico/CHANGELOG_PRE_0.2.md) foi preservado como histórico.
