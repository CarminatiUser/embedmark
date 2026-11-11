# Evidências do ensaio físico de 11/11/2026

Este diretório reúne uma cópia documental preparada para publicação do ensaio realizado na **Waveshare ESP32-C6-LCD-1.47**, com interface gerada pelo **EmbedMark 0.4.2** e firmware de laboratório **0.1.0**. Consulte o [relatório completo](../../VALIDACAO_FISICA_2026-11-11.md) para configuração, procedimento e limites.

| Arquivo | Conteúdo |
|---|---|
| [result.json](result.json) | 143 verificações individuais aprovadas, zero falhas, duração total de 42,59 s e estado final |
| [events.jsonl](events.jsonl) | 631 eventos: abertura, comandos, respostas e verificações com tempos relativos |
| [serial-rx.log](serial-rx.log) | 10.168 bytes recebidos da placa, preservados byte a byte |
| [visual-validation.json](visual-validation.json) | Confirmação visual complementar e proveniência das fotografias |
| [manifest.json](manifest.json) | Configuração, hashes dos artefatos locais e histórico das alterações de publicação |
| [IMG_6242-preview.png](IMG_6242-preview.png) | Prévia da fotografia selecionada para o TCC, com metadados de captura removidos |
| [SHA256SUMS](SHA256SUMS) | Hashes dos arquivos públicos; os tamanhos estão no manifesto. O próprio arquivo de hashes não se inclui |

O resultado `passed_serial_only` é a conclusão da etapa automática. Seu campo de validação visual pendente foi preservado, pois essa etapa não observa o painel. A confirmação complementar de cores, enquadramento e textos está no registro visual separado. A fotografia mostra **Ações: 3**; o histórico dos eventos está nos logs.

## Alterações na cópia pública

- Em `result.json` e em um evento de abertura de `events.jsonl`, o valor da porta foi substituído por `<PORTA_LOCAL_OMITIDA>`. Nenhuma verificação, resposta ou marca de tempo foi alterada.
- O manifesto usa o nome relativo `embedmark-validation-waveshare`, sem o caminho pessoal da máquina. A seção `files` identifica artefatos que continuam locais; ela não indica que os binários e fontes correspondentes foram distribuídos aqui.
- O registro visual foi adaptado para apontar à fotografia publicada e identificar explicitamente os originais que permaneceram locais. Os estados de confirmação e as observações foram preservados.
- A prévia PNG original continha metadados EXIF e XMP, incluindo localização. A cópia pública remove os blocos originais `eXIf`, `iTXt`, `tEXt` e `zTXt` que estiverem presentes e insere um EXIF mínimo contendo somente `Orientation=6`, necessário para preservar a exibição em retrato. Não permanecem localização, identificação da câmera, datas ou outros campos EXIF/XMP. **Os bytes comprimidos `IDAT`, as dimensões nativas e todos os pixels são idênticos aos da prévia de origem.** A imagem nativa tem 1400 × 1050 pixels e é apresentada em 1050 × 1400 pela orientação. Não houve recorte, mudança de cores ou tratamento generativo.

O SHA-256 da prévia de origem é `ba9a807b57dcc4b0d91546925a76ca0fe4b499a1669934859eb0d8e0338e7b7c`. O hash da cópia sem metadados consta no manifesto, no registro visual e em `SHA256SUMS`; ele é diferente porque o arquivo deixou de conter aqueles blocos. A imagem publicada deriva de IMG_6242, uma fotografia adicional do mesmo ensaio. IMG_6241 foi a primeira confirmação fotográfica; não é a imagem publicada neste diretório.

Não foram copiados backup de flash, firmware, ELF, fotografias HEIC ou PNGs de tamanho integral, logs de compilação/gravação/backup com caminhos e identificadores do dispositivo, credenciais ou código de outros protótipos. Os originais foram mantidos no acervo local. O manifesto registra seus hashes quando necessários para rastreabilidade, sem expor os arquivos.

## Conferência documental

As 143 verificações de `result.json` correspondem às 143 entradas de verificação de `events.jsonl`. Há um bloco de 50 recriações acompanhadas de incremento e 10 ciclos padrão/interface. A duração de 42,59 s inclui a janela inicial de 3,5 s. Os 25 artefatos identificados no manifesto local foram conferidos por tamanho e SHA-256 durante a preparação desta cópia.

Para conferir a integridade dos arquivos deste diretório, sem usar a placa:

```sh
shasum -a 256 -c SHA256SUMS
```

O firmware completo do laboratório permanece em projeto separado. Este conjunto permite examinar as evidências publicadas e sua integridade; não fornece sozinho uma reprodução integral do firmware. Nenhum novo ensaio foi executado durante a organização destes arquivos.
