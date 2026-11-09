# Comece por aqui

O produto inclui a extensão do VS Code, o núcleo Python e um laboratório separado para a tela ESP32-C6/ST7789T.

Este repositório disponibiliza o código original, a documentação e os exemplos sob a [licença MIT](LICENSE). As dependências e fontes mantêm suas próprias licenças. A pasta local `release/` e o laboratório separado não estão incluídos no repositório público.

1. Procure **EmbedMark**, do publicador **Arthur Carminati**, no painel Extensões do VS Code e selecione **Instalar**. O identificador é `arthur-carminati.embedmark`; a [página oficial](https://marketplace.visualstudio.com/items?itemName=arthur-carminati.embedmark) também oferece acesso à instalação.
2. Tenha Python 3.10 ou superior instalado. As bibliotecas Python necessárias já estão no pacote.
3. Abra uma pasta confiável, execute **EmbedMark: Criar exemplo de contador**, salve o HTML e use **EmbedMark: Validar interface** ou **EmbedMark: Gerar interface LVGL**.
4. Para testar na placa, siga o README do laboratório local separado `embedmark-validation`, caso disponha desse projeto. Seu endereço público ainda não foi confirmado.

- [Uso, contrato e limitações](README.md)
- [Guia da extensão](extension/README.md)
- [Resultados verificados](docs/VALIDACAO_0.4.0.md)
- [Pacote e publicação](docs/PUBLICACAO.md)
- [Manual HTML/CSS](docs/LINGUAGEM.md)
- [Plano do TCC](PLANO_DE_DESENVOLVIMENTO_E_TCC.md)

A validação física da tela e a publicação no Marketplace têm registros próprios. Uma compilação aprovada não substitui a observação do display real.
