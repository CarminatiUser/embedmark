# Contador na montagem com LCD externo — 12/11/2026

Em **12 de novembro de 2026**, o contador do EmbedMark **0.4.2** foi executado na montagem do autor com **nanoESP32-C6 e LCD externo de 172 × 320 pixels**. O laboratório local isolado `embedmark-demo-nanoesp32c6` utiliza o perfil de pinagem denominado **Arthur**. Esta montagem é distinta da [Waveshare com display integrado ensaiada em 11/11](VALIDACAO_FISICA_2026-11-11.md).

## Configuração e resultados

| Item | Registro da rodada corrigida |
|---|---|
| Microcontrolador detectado | ESP32-C6 QFN40, revisão 0.1 |
| Gerador / firmware do laboratório | EmbedMark 0.4.2 / firmware 0.1.0, com versões independentes |
| Ambiente | ESP-IDF 5.4.3 e LVGL 8.3.11 |
| Pinagem do LCD | SCLK 7, MOSI 6, **CS 23**, DC 15, RST 21, BL 22 |
| Brilho configurado | 75% |
| Console | USB Serial/JTAG principal, pela porta USB nativa do ESP32-C6 |
| Eventos | Cliques enviados por software; automático desligado no início e no fim |
| Verificações pelo console | **143 aprovadas, zero falhas** |
| Blocos repetidos | 50 recriações seguidas de clique; 10 ciclos padrão de cores/tela gerada |
| Duração da rodada | **42,434 segundos**, incluindo a janela inicial de conexão |

A montagem possui uma conexão USB do ESP32-C6 e outra associada ao CH343. O console deste ensaio utiliza a primeira. A pinagem é específica da montagem conferida: **CS23 não deve ser transferido para o perfil Waveshare, que usa CS14**.

Na preparação inicial, foi selecionado indevidamente o perfil Waveshare. As respostas seriais passaram, mas o autor informou que a tela permanecia preta. Essa tentativa **não é considerada validação física bem-sucedida**. Depois da correção para o perfil Arthur, o protocolo foi repetido e produziu os resultados da tabela.

## Conferência visual e uso da extensão

Após a rodada corrigida, o autor confirmou que a tela externa exibia **“Ações: 3”**, com botão azul e textos legíveis. Essa observação complementa as verificações seriais, que não enxergam o painel. Posteriormente, o comando `r` recriou a interface e restabeleceu o contador em zero, com automático desligado, conforme o registro do console; não se atribui uma nova confirmação visual a esse último estado.

No perfil de demonstração do VS Code, a extensão **arthur-carminati.embedmark 0.4.2** validou e gerou o exemplo. O HTML, os arquivos C/H e as três fontes da pasta de demonstração foram comparados com os arquivos integrados ao firmware corrigido e são idênticos byte a byte. A extensão gera a interface; a integração, compilação e gravação pertencem ao laboratório. O [guia da demonstração](DEMONSTRACAO.md) explica essa separação e os comandos usados.

## Alcance e preservação dos registros

As 143 verificações são asserções do protocolo, não 143 cenários independentes, e não são somadas aos testes de software ou ao ensaio Waveshare. Os 42,434 segundos descrevem o procedimento, não desempenho do produto. Não houve avaliação de touch, botão físico, consumo, taxa de quadros ou estabilidade prolongada. A confirmação visual desta rodada se limita ao contador, botão e textos mencionados.

Este relato resume o resultado serial, a configuração e a confirmação visual preservados no acervo local. O firmware completo, os logs brutos, os identificadores do dispositivo, os caminhos pessoais e o backup da flash não são publicados aqui. Clonar o repositório do EmbedMark não fornece o laboratório completo para repetir o ensaio. A atualização é documental e não altera o código nem o pacote 0.4.2 distribuído no Marketplace.
