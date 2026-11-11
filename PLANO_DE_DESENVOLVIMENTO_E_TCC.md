# Plano de desenvolvimento do produto e conclusão do TCC

Plano original de setembro/outubro de 2026, com atualização de acompanhamento em **11/11/2026**. Os diagnósticos iniciais e marcos antigos abaixo preservam o contexto de cada rodada; não devem ser lidos como a situação atual do produto.

## Situação em 11/11/2026

- **Distribuição:** a versão 0.4.2 está publicada no Marketplace sob MIT, com instalação verificada e matriz de testes de software aprovada. Veja o [registro da versão](docs/VALIDACAO_0.4.2.md).
- **Hardware:** o contador gerado pelo núcleo 0.4.2 foi executado na Waveshare ESP32-C6-LCD-1.47. Foram aprovadas 143 verificações por console, com 50 ciclos de recriação e 10 ciclos de alternância entre padrão e interface, além da confirmação visual e fotografia. Veja a [validação física](docs/VALIDACAO_FISICA_2026-11-11.md).
- **Escopo:** RF08 está atendido no cenário ensaiado, com eventos por console. Não foram validados todos os exemplos na placa, toque ou botão físico, outros periféricos ou estabilidade prolongada. Medições de desempenho/consumo e avaliação com participantes não foram realizadas nesse ensaio.
- **Reprodução:** o protocolo e as evidências estão públicos; o firmware completo do laboratório isolado `embedmark-validation-waveshare` permanece local e separado deste repositório.
- **TCC e vídeo:** o documento do TCC é mantido separadamente. Este plano não certifica seu fechamento editorial. O vídeo de demonstração será gravado posteriormente pelo autor; as evidências atuais são registros seriais, configuração, confirmação visual e fotografia.

### Contexto das entregas iniciais

A versão 0.4.0 foi entregue com núcleo Python, extensão instalável do VS Code e laboratório de firmware. Consulte primeiro o [registro de entrega e validação](docs/VALIDACAO_0.4.0.md): 188 testes automatizados, pacote instalado no VS Code, cinco versões do Python e seis exemplos compilados com ESP-IDF. Publicação na conta do autor, execução física na tela e reescrita do documento permanecem nas próximas etapas.

Este documento conserva o plano amplo original. Centralização integral de esquemas/modelos e ampliações da linguagem são evoluções internas; não representam funcionalidades prometidas pelo contrato da versão 0.4.0. As caixas ainda abertas identificam esse trabalho futuro ou evidências externas que não foram produzidas. O código da versão entregue e seus critérios de aceitação estão no registro acima.

O produto é uma ferramenta para gerar interfaces LVGL a partir de uma linguagem simplificada inspirada em HTML e CSS. O tradutor Python é o núcleo; a extensão do VS Code é a interface de uso; o motor de layout é um módulo interno. Essa organização mantém uma única entrega central para o TCC.

Este plano organiza o trabalho solicitado. A primeira rodada de correções do núcleo foi concluída em 28/09/2026: veja [implementação e verificações](docs/CORRECOES_2026-09-28.md). Caixas marcadas identificam entregas concluídas nesta rodada; as demais permanecem pendentes. A compilação dos arquivos gerados não certifica o firmware nem substitui os testes físicos de aceitação.

A etapa seguinte entregou a versão 0.3.0: acesso por ID, eventos no controlador de exemplo, ciclo de vida da tela e fontes com acentos. A suíte agora tem 101 testes aprovados, incluindo execução com LVGL real e 100 ciclos de criação/destruição. Veja o [registro da integração](docs/INTEGRACAO_0.3.0.md). O exemplo completo foi preparado para o firmware, mas a validação na placa permanece pendente.

O laboratório de validação `embedmark-validation` agora está em um repositório local separado, com ESP32-C6, ST7789T 172 × 320, ESP-IDF 5.4.3 e LVGL 8.3.11. Esse material externo não está incluído nesta publicação, e seu endereço público não foi confirmado. O firmware completo compilou tanto para o contador com fontes portuguesas quanto para outro exemplo importado; seis testes do importador passaram. Drivers e configuração foram extraídos da referência sem alterá-la. D09 está parcialmente atendido por inspeção e compilação; a confirmação da pinagem/entrada na placa, D10 e a aceitação física de F03 seguem pendentes. Nenhum dispositivo foi gravado nesta preparação.

## 1. Estado observado antes das correções

- Existem 11 módulos Python, aproximadamente 2.151 linhas, dois exemplos HTML e uma saída C armazenada.
- Há separação inicial entre parsers, configuração, layout e geração LVGL, que pode ser aproveitada.
- Nesta cópia não foram encontrados suíte de testes, configuração de integração contínua, pacote Python instalável, estrutura de extensão ou diretório `.git`.
- A documentação anuncia capacidades que não atravessam todo o fluxo de tradução e apresenta estimativas de desempenho sem medição.
- O firmware local registra ESP-IDF 5.4.3, LVGL 8.3.11 e alvo ESP32-C6 em `dependencies.lock`. Essa é a base inicial proposta para reprodução; não foi realizado novo build ou teste físico nesta análise.
- O TCC foi revisado editorialmente, mas a reescrita como produto e a validação experimental permanecem pendentes.

### Problemas concretos encontrados

“Reproduzido” significa verificação pontual por chamada direta aos módulos, sem compilação do C. “Inspeção” significa leitura do fluxo atual.

| Prioridade | Problema | Evidência | Correção esperada |
|---|---|---|---|
| P0 | `margin` produz chaves `padding-*` | Inspeção de `css_parser.py:84` | Separar as duas propriedades e testar expansão de 1, 2, 3 e 4 valores |
| P0 | Regras sucessivas do mesmo seletor substituem o conjunto anterior | Inspeção de `css_parser.py:162` | Combinar declarações por propriedade, respeitando a ordem definida no subconjunto |
| P0 | Elemento sem ID faz desaparecer também seus descendentes | Reproduzido; `lvgl_generator.py:204` | Identificadores internos automáticos e preservação da árvore |
| P0 | IDs podem gerar identificadores inválidos ou duplicados em C | Reproduzido com `1bad`, `a-b` e `a_b` | Tabela de símbolos, validação de IDs e nomes internos únicos |
| P0 | Altura isolada não é emitida | Reproduzido; `lvgl_generator.py:155` | Tratar largura e altura independentemente |
| P0 | Padding calculado não chega à saída | Reproduzido; gerador fixa padding dos estilos em zero | Aplicar os quatro lados e definir sua interação com filhos |
| P0 | Cores inválidas passam para C | Reproduzido: `#GGGGGG` vira `0xGGGGGG`; RGB acima de 255 é aceito | Validar formato e intervalos, emitindo diagnóstico |
| P0 | Configurações aceitas não têm efeito ou efeito incompleto | Inspeção: largura/altura da CLI não são usadas em `main.py`; preset custom tem tamanho fixo | Definir precedência e conectar configurações ao processamento |
| P1 | JSON exportado contém layout vazio | Inspeção de `cli.py:146` | Exportar o resultado real da mesma tradução, sem refazer o parsing |
| P1 | Apenas o primeiro bloco `<style>` é lido | Inspeção de `main.py:77` | Definir suporte a múltiplos blocos e sua ordem |
| P1 | Propriedades são aceitas e depois ignoradas | Inspeção do parser, layout e gerador: exemplos incluem margin, font-weight, display e bordas | Implementar o que entrar no contrato e diagnosticar o restante |
| P1 | Flexbox existe em módulo auxiliar, mas não integra o fluxo principal | Inspeção de `containers.py` e `main.py` | Retirar promessa de suporte; avaliar integração em versão posterior |
| P1 | Métricas usam constantes arbitrárias | `utils.py`: bytes por objeto, tempo por objeto e tamanho do texto C tratado como ROM | Retirar conclusões de desempenho e substituir por medições quando necessárias |
| P1 | CLI exige entrada até para listar displays; quiet ainda imprime mensagens | Inspeção de `cli.py` | Subcomandos independentes, saída previsível e códigos de erro coerentes |
| P1 | Guia de firmware inclui arquivo `.c` e usa inicialização genérica | Inspeção de `ESP_IDF_INTEGRATION.md` | Projeto de referência compilável, `.c`/`.h` separados e inicialização real da placa |

Outros pontos a verificar durante a correção: dimensões nulas ou negativas, nomes reservados em C, colisão com `scr` e labels de botões, caracteres de controle no texto, fontes habilitadas no firmware, caracteres portugueses, estilos de labels internos de botões, herança de estilos e reutilização da tela sem vazamentos.

## 2. Escopo proposto da primeira versão

### Entrega obrigatória

- Traduzir a linguagem documentada para `.c` e `.h` compatíveis com a versão LVGL escolhida.
- Suportar tela, contêiner, rótulo e botão com comportamento visual definido.
- Tratar posições, dimensões, cores, tipografia disponível, alinhamento, bordas e espaçamentos incluídos no contrato.
- Preservar hierarquia e fornecer erros e avisos compreensíveis, com localização quando possível.
- Configurar dimensões de projeto e display sem editar o código do tradutor.
- Permitir integração com aplicação: nomes públicos estáveis e ponto documentado para registrar eventos. A lógica da aplicação permanece no firmware; não incluir execução de JavaScript.
- Fornecer extensão desktop do VS Code para configurar, validar e gerar a interface.
- Entregar exemplos, manual e projeto de referência para ESP32-C6/ST7789 172 × 320.
- Gerar evidências de testes e uma versão identificável que corresponda ao TCC.

### Evoluções posteriores

Editor visual drag-and-drop, navegador HTML/CSS completo, Grid, Flexbox completo, JavaScript, múltiplas versões principais do LVGL, compilação e gravação automáticas na placa, catálogo amplo de componentes e suporte generalizado a diferentes hardwares.

Preview visual poderá ser avaliado depois da geração estável. Uma prévia em navegador deverá ser identificada como aproximação; sua aparência não comprova o resultado no LVGL. Uma prévia fiel exige integração com um ambiente LVGL adequado.

## 3. Etapas e critérios de conclusão

P0 = bloqueia a base confiável. P1 = necessário para a versão apresentável e distribuível. P2 = melhoria posterior. A ordem é por dependência, sem datas artificiais antes de conhecermos o prazo da defesa e a disponibilidade para testar a placa.

### Etapa A — Preservar a base e especificar o produto — P0

- [x] A01. Preservar o código atual e identificar sua relação com o firmware que já foi utilizado.
- [x] A02. Estabelecer repositório e versão inicial; configurar exclusões de caches, ambientes, builds e credenciais.
- [x] A03. Definir objetivo do produto, usuário principal e fluxo completo de uso.
- [x] A04. Definir matriz de compatibilidade inicial: Python, LVGL 8.3.11, ESP-IDF 5.4.3, ESP32-C6 e display de referência; registrar versões realmente testadas.
- [x] A05. Especificar tags, atributos, seletores, unidades, valores, defaults e restrições aceitos.
- [x] A06. Decidir precedência entre arquivo, configuração de projeto e parâmetros; definir escala, coordenadas relativas ao pai e política de extrapolação da tela.
- [x] A07. Definir requisitos e critérios de aceitação identificados para vincular implementação, testes e TCC.

**Pronto quando:** existe uma base recuperável e um contrato de funcionalidades verificável, sem promessas ambíguas.

### Etapa B — Corrigir o núcleo e criar testes de regressão — P0

- [x] B01. Corrigir margin/padding e expansão de 1–4 valores; preservar ordem entre shorthands e propriedades individuais.
- [x] B02. Corrigir combinação de regras do mesmo ID e validar a gramática de seletores suportados.
- [x] B03. Preservar elementos sem IDs; rejeitar IDs de usuário duplicados com mensagem clara.
- [x] B04. Gerar identificadores C válidos, determinísticos e sem colisão, inclusive com símbolos internos.
- [x] B05. Corrigir dimensões independentes e validar zero, negativos, unidades e valores não finitos.
- [x] B06. Implementar espaçamentos do contrato: padding nos quatro lados, margin-left/top e diagnóstico para margens que exigem fluxo; fatores horizontal e vertical corrigidos.
- [x] B07. Validar cores, opacidade, bordas e fontes; garantir diagnóstico para opções sem suporte.
- [x] B08. Definir tratamento dos labels dos botões para preservar conteúdo e estilos sem duplicação.
- [x] B09. Corrigir configuração customizada, opções da CLI, exportação JSON e leitura dos blocos de estilo.
- [x] B10. Tratar texto UTF-8 e escape C; verificar aspas, barras, quebras e caracteres de controle.
- [x] B11. Criar testes de regressão junto com cada correção; incluir entradas válidas e inválidas.
- [x] B12. Compilar saídas representativas contra o LVGL escolhido, além de comparar o conteúdo gerado.

**Pronto quando:** falhas P0 estão corrigidas, seus testes passam e os exemplos de referência geram C compilável. A comparação textual sozinha não aprova essa etapa.

### Etapa C — Organizar o código como software distribuível — P1

- [x] C01. Transformar o núcleo em pacote Python instalável, com metadados, imports de pacote e comando estável.
- [x] C02. Separar biblioteca, entrada/saída em arquivos e CLI; evitar dependência do diretório de execução.
- [ ] C03. Definir modelos consistentes para elementos, estilos, layout, configurações e diagnósticos.
- [x] C04. Retornar código, layout e diagnósticos em um único resultado de tradução.
- [ ] C05. Centralizar o catálogo de funcionalidades para que parser, validação, manual e extensão compartilhem o mesmo contrato.
- [x] C06. Remover duplicações e opções inoperantes; classificar módulos experimentais e código sem integração.
- [x] C07. Padronizar estilo, tipos, documentação de funções e mensagens; configurar verificações automáticas proporcionais ao projeto.
- [x] C08. Estabilizar tratamento de erros, logs, códigos de saída e gravação da saída; preservar a última saída válida quando a entrada falhar.
- [x] C09. Definir compatibilidade de dependências e ambiente reproduzível, incluindo dependências de desenvolvimento.
- [x] C10. Revisar cache de estilos, repetição de traduções e ciclo de vida da interface gerada.
- [x] C11. Criar integração contínua para testes Python, verificações de qualidade e compilação C de referência.

**Pronto quando:** uma instalação limpa consegue usar a biblioteca e o comando, com resultados determinísticos e diagnósticos estruturados.

### Etapa D — Exemplos, manual e integração com hardware — P1

- [x] D01. Revisar os dois exemplos atuais; eliminar uso não explicado de propriedades ignoradas e conferir coordenadas dentro dos contêineres.
- [x] D02. Criar exemplos graduais: tela mínima, texto, botão, hierarquia, estilos, ajuste de resolução e painel completo.
- [x] D03. Incluir exemplos de erro com diagnóstico esperado e orientação de correção.
- [x] D04. Guardar entrada, configuração e resultado esperado dos exemplos usados como testes.
- [x] D05. Criar manual de tags e propriedades, valores aceitos, restrições e exemplos pequenos por recurso.
- [x] D06. Consolidar os vários resumos Markdown em documentação com navegação simples e informação coerente.
- [x] D07. Substituir afirmações de fidelidade, RAM, ROM e desempenho por descrições verificadas ou limitações explícitas.
- [x] D08. Entregar integração por `.h` e `.c`, CMake e configuração de fontes; separar código gerado de código do usuário.
- [x] D09. Perfil Waveshare conferido no ensaio de 11/11/2026: driver, inicialização LVGL, pinagem e eventos por console; sem touch ou botão físico ensaiado.
- [ ] D10. Parcial: contador executado no hardware, com protocolo, fotografia e logs públicos. O firmware completo do laboratório ainda precisa ser disponibilizado para reprodução integral a partir deste repositório.

**Pronto quando:** alguém consegue seguir o guia, gerar e compilar uma interface e reproduzir a demonstração no hardware de referência.

### Etapa E — Extensão do VS Code — P1

A extensão consumirá o núcleo por uma interface estável, evitando uma segunda implementação do parser e do layout. A proposta inicial é uma extensão TypeScript que chama o tradutor Python com argumentos e recebe diagnósticos estruturados.

- [x] E01. Criar estrutura da extensão, manifesto, comandos, configurações e identidade visual básica.
- [x] E02. Implementar criação de exemplo no editor e seleção da entrada, saída e dimensões na pasta do projeto.
- [x] E03. Implementar comandos “Validar interface” e “Gerar código LVGL”.
- [x] E04. Exibir erros e avisos no painel Problems, associados ao arquivo e à posição disponíveis.
- [x] E05. Oferecer snippets, sugestões e ajuda sobre os recursos realmente suportados.
- [x] E06. Configurar Python/ambiente do tradutor e detectar dependências ausentes com instrução de solução; definir distribuição e atualização do núcleo.
- [x] E07. Tratar progresso, cancelamento, timeout e falhas do processo; mostrar resultado e abrir os arquivos gerados.
- [x] E08. Preservar caminhos com espaços e caracteres acentuados, projetos com múltiplas pastas e arquivos ainda não salvos.
- [x] E09. Respeitar Workspace Trust e limitar execução em projetos não confiáveis; passar argumentos sem montar comandos de shell a partir do conteúdo da interface.
- [x] E10. Criar testes da extensão e do fluxo integrado com o tradutor.
- [x] E11. Instalação limpa e execução local aprovadas; matriz da versão 0.4.2 aprovada para a extensão em Linux, macOS e Windows, conforme registro de 09/11/2026.
- [x] E12. Empacotar uma versão `.vsix` e validar instalação local.

**Pronto quando:** o usuário instala a extensão, configura o ambiente, abre um exemplo, recebe diagnósticos e gera a saída sem editar o código da ferramenta.

### Etapa F — Validar o produto e reunir evidências — P1

- [x] F01. Montar matriz requisito → caso de teste → resultado → evidência.
- [x] F02. Executar testes de parsing, estilos, hierarquia, layout, geração, CLI e extensão.
- [ ] F03. Parcial: seis exemplos compilados no ESP-IDF na rodada anterior; contador gerado pela versão 0.4.2 executado fisicamente em 11/11/2026. A execução física dos demais exemplos não foi documentada.
- [ ] F04. Parcial: cores, enquadramento, acentos e ausência de cortes conferidos no padrão e no contador da Waveshare. Não foi feita uma avaliação visual completa de todos os exemplos e dimensões.
- [x] F05. Registrar versão do código, ferramentas, configuração, entradas, resultados e limitações de cada execução.
- [ ] F06. Instalação e fluxo automatizado aprovados; definir com o orientador se haverá avaliação com participantes e executar o procedimento correspondente.
- [ ] F07. Só comparar tempo/esforço com procedimento definido, tarefas equivalentes e limitações registradas; não usar estimativas do `utils.py` como dados experimentais.
- [ ] F08. Medir memória ou desempenho apenas se fizerem parte dos objetivos finais, usando instrumentos apropriados ao firmware.
- [x] F09. Corrigir falhas encontradas e repetir somente os testes afetados e a regressão necessária.

**Pronto quando:** os requisitos essenciais têm evidência de atendimento e as limitações restantes estão registradas, sem tratar planejamento como resultado.

### Etapa G — Publicar a versão do produto — P1

- [x] G01. Nome EmbedMark, identificador `embedmark` e publicador `arthur-carminati` confirmados no Marketplace em 09/11/2026.
- [x] G02. Licença proprietária registrada na entrega inicial. Em 09/11/2026, por decisão expressa do autor, o código original passou à licença MIT na versão 0.4.2; atribuições e licenças de terceiros foram preservadas.
- [x] G03. README, ícone, instruções, limitações, changelog e links públicos do repositório e suporte disponíveis.
- [x] G04. Inspecionar conteúdo do pacote e compatibilidade entre versão da extensão e do núcleo.
- [x] G05. Publicação realizada pela conta do autor, sem credenciais no repositório ou pacote.
- [x] G06. Versão 0.4.1 publicada no Marketplace, com download e instalação pelo catálogo verificados. Atualização 0.4.2 sob licença MIT publicada; download e instalação pelo catálogo também verificados.
- [x] G07. Registrar versão, commit, pacote e instruções para reproduzir a versão usada no TCC.

**Pronto quando:** a versão pública instala e completa o fluxo de referência. O `.vsix` validado serve como distribuição local durante a preparação do lançamento.

### Etapa H — Reescrever e fechar o TCC como produto — P1

Esta etapa começa na A e acompanha o desenvolvimento. Resultados e conclusão são fechados após F; informações da versão publicada, após G.

- [ ] H01. Fechar título coerente com a entrega e adequar a modalidade/formalização ao modelo institucional aplicável.
- [ ] H02. Reescrever introdução, problema, público-alvo, justificativa e objetivos em torno do produto.
- [ ] H03. Apresentar requisitos, critérios de aceitação e delimitação de escopo.
- [ ] H04. Atualizar comparação com ferramentas existentes usando critérios que sustentem as decisões de projeto.
- [ ] H05. Explicar arquitetura do núcleo e extensão, mantendo o motor de layout como módulo interno.
- [ ] H06. Descrever decisões relevantes, implementação e integração; transferir listagens extensas para apêndices quando adequado.
- [ ] H07. Incluir manual/catálogo da linguagem e instruções de uso, conforme a observação de Debatin.
- [ ] H08. Substituir resultados esperados por resultados executados e discutidos; vincular cada objetivo às evidências.
- [ ] H09. Atualizar resumo, abstract, conclusão, limitações e trabalhos futuros.
- [ ] H10. Conferir referências e todas as afirmações de custo, desempenho, economia e fidelidade.
- [ ] H11. Refazer a verificação de figuras, listas, referências cruzadas e paginação após a reescrita.
- [ ] H12. Preparar apresentação e demonstração com a mesma versão do produto, incluindo alternativa gravada para falhas de infraestrutura.

**Pronto quando:** título, texto, código, extensão, manual e demonstração descrevem o mesmo produto e o mesmo conjunto de funcionalidades comprovadas.

Notas da primeira rodada: A05 está registrado em `docs/LINGUAGEM.md`; B06 está parcial (padding nos quatro lados e margin-left/top); C07/C08/C09/C11 têm base implementada, mas precisam da consolidação prevista; D02 inclui três exemplos graduais e dois painéis; D08 tem header/guia corrigidos, mas integração física permanece pendente. O pacote foi instalado e executado fora do projeto em um ambiente virtual novo com Python 3.12.14. Os nomes de versão do firmware são os encontrados na referência local, não uma nova validação de toda a matriz. A suíte local concluiu 82 testes, incluindo compilação de objetos C com LVGL 8.3.11.

## 4. Ordem recomendada e marcos

Atualização 0.3: C10 e D08 foram entregues para uma instância de tela. A API está documentada, os estilos são reaproveitados e o controlador fica separado da saída gerada. O teste local inclui fontes e eventos, e o laboratório separado já compila com ESP-IDF. D09/D10 e F03 ainda precisam de confirmação e execução na placa. A extensão poderá consumir a CLI e os diagnósticos já disponíveis.

1. **M0 — Escopo fechado:** concluir A e estrutura inicial de H.
2. **M1 — Núcleo confiável:** concluir B, testes de regressão e compilação de referência.
3. **M2 — Produto utilizável fora do editor:** concluir C e exemplos/guia essenciais de D.
4. **M3 — Extensão instalável:** concluir E com `.vsix` e fluxo completo.
5. **M4 — Produto validado:** concluir D e F com evidências no hardware.
6. **M5 — Lançamento:** concluir G.
7. **M6 — TCC e defesa:** fechar H usando os resultados e a versão identificada.

A documentação e os testes acompanham as correções; não ficam reservados ao final. O desenvolvimento da extensão depende de um contrato estável do núcleo, e a publicação depende da validação da versão candidata.

## 5. Relação com as observações da banca

| Observação | Atendimento planejado |
|---|---|
| Rever título; arquitetura ou biblioteca | H01, com título centrado na ferramenta e arquitetura explicada no desenvolvimento |
| Documento pouco claro | A03, H02–H06: problema, usuário, requisitos e fluxo completo antes dos detalhes internos |
| Reescrever como produto | A, C, D, E e H: especificação, implementação, distribuição, uso e validação |
| Dois trabalhos em um | Núcleo tradutor, layout interno e extensão como interface do mesmo produto |
| Afirmações perigosas; custo/desempenho | D07, F07–F08 e H10: evidência ou delimitação explícita |
| Especificar o ESP32 utilizado | A04, D09–D10 e F05: ESP32-C6 e configuração concreta do display |
| Manual dos elementos HTML | A05, D05, E05 e H07 |
| Extensão do VS Code | E e G, agora parte da entrega pretendida pelo autor |
| Capa, índices e imagens | Revisão editorial já realizada; nova conferência em H11 após mudanças de conteúdo |

## 6. Definição de produto pronto

- [x] Instalação reproduzível em ambiente limpo.
- [x] Recursos documentados implementados de ponta a ponta.
- [x] Entradas inválidas produzem diagnósticos; não desaparecem silenciosamente.
- [x] Exemplos oficiais geram saída compilável na versão LVGL anunciada.
- [x] Demonstração do contador registrada na Waveshare em 11/11/2026, com fotografia e logs; vídeo ainda não gravado.
- [x] Extensão publicada e instalação da versão pública 0.4.2 verificada, conforme registro de 09/11/2026.
- [x] Manual, exemplos, dependências, licença e versão organizados.
- [ ] TCC vincula requisitos, testes e resultados da versão entregue.

## 7. Referências para a implementação da extensão

Consultadas em 28 de setembro de 2026:

- [API de extensões do VS Code](https://code.visualstudio.com/api/): recursos e integração com o editor.
- [Testes de extensões](https://code.visualstudio.com/api/working-with-extensions/testing-extension): execução no Extension Development Host.
- [Workspace Trust](https://code.visualstudio.com/api/extension-guides/workspace-trust): comportamento em workspaces com confiança restrita.
- [Empacotamento e publicação](https://code.visualstudio.com/api/working-with-extensions/publishing-extension): VSIX, publisher e publicação no Marketplace.

Os requisitos de publicação devem ser reconferidos no momento do lançamento.
