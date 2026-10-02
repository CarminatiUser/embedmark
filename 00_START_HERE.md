# Comece por aqui

O produto inclui a extensão do VS Code, o núcleo Python e um laboratório separado para a tela ESP32-C6/ST7789T.

1. Instale o arquivo `.vsix` da pasta `release` usando **Extensions → Install from VSIX** no VS Code.
2. Tenha Python 3.10 ou superior instalado. As bibliotecas Python necessárias já estão no pacote.
3. Abra uma pasta confiável, execute **TCC UI: Criar exemplo de contador**, salve o HTML e use **TCC UI: Validar interface** ou **TCC UI: Gerar interface LVGL**.
4. Para testar na placa, siga o [laboratório de validação](../tcc-ui-validation/README.md).

- [Uso, contrato e limitações](README.md)
- [Guia da extensão](extension/README.md)
- [Resultados verificados](docs/VALIDACAO_0.4.0.md)
- [Pacote e publicação](docs/PUBLICACAO.md)
- [Manual HTML/CSS](docs/LINGUAGEM.md)
- [Plano do TCC](PLANO_DE_DESENVOLVIMENTO_E_TCC.md)

A validação física da tela e a publicação no Marketplace têm registros próprios. Uma compilação aprovada não substitui a observação do display real.
