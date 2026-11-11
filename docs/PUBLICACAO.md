# Pacote da extensão e publicação

O [repositório GitHub do EmbedMark](https://github.com/CarminatiUser/embedmark) disponibiliza o código original da ferramenta **sob a licença MIT**, com autoria de Arthur Felipe Carminati. A licença permite uso, modificação e redistribuição, inclusive comercial, mantendo os avisos de autoria e licença. Os termos completos estão em [LICENSE](../LICENSE). As bibliotecas e fontes de terceiros mantêm suas próprias licenças e atribuições.

A primeira publicação no [Marketplace do VS Code](https://marketplace.visualstudio.com/items?itemName=arthur-carminati.embedmark) ocorreu em 09/11/2026 na versão **0.4.1**, cujas evidências permanecem no [registro histórico](VALIDACAO_0.4.1.md). A versão **0.4.2 está publicada**, com licença MIT, desde 09/11/2026. O download e a instalação pelo catálogo foram verificados. O identificador permanece `arthur-carminati.embedmark`. Consulte as [evidências da versão 0.4.2](VALIDACAO_0.4.2.md).

Os pacotes e relatórios locais ficam em `release/`, ignorada pelo Git. Os registros da versão 0.4.0 e da adoção do nome EmbedMark em 14/10/2026 permanecem como histórico e não comprovam a validação de um pacote reconstruído.

## Instalar pelo Marketplace

No VS Code, abra **Extensões**, procure **EmbedMark**, do publicador **Arthur Carminati**, e selecione **Instalar**. Alternativamente:

```sh
code --install-extension arthur-carminati.embedmark
```

## Instalar o pacote local

No VS Code, abra Extensions, use o menu de três pontos e escolha **Install from VSIX**. Selecione o arquivo da pasta `release`. Tenha Python 3.10 ou superior instalado; a extensão inclui as bibliotecas Python necessárias. Node.js, pip e ESP-IDF não são requisitos para usar a extensão já empacotada.

Abra uma pasta confiável e use **EmbedMark: Criar exemplo de contador**. Salve o HTML e execute **Validar interface** e **Gerar interface LVGL**. Se o Python não for encontrado, configure **EmbedMark: Python Path** com o caminho do executável, sem argumentos adicionais.

O ESP-IDF é necessário apenas para compilar/gravar um firmware. O ensaio físico de 11/11/2026 utilizou o laboratório local isolado `embedmark-validation-waveshare`, separado do projeto anterior `embedmark-validation`. O firmware completo desses laboratórios não está incluído neste repositório. A configuração, os resultados e as evidências do ensaio estão no [relatório de validação física](VALIDACAO_FISICA_2026-11-11.md).

## Identidade do publicador

O publicador confirmado é **Arthur Carminati** (`arthur-carminati`), com acesso de proprietário verificado em 09/11/2026. O identificador completo é `arthur-carminati.embedmark`. A conta GitHub `CarminatiUser` e o publicador do Marketplace são identidades de serviços diferentes.

O campo `publisher` do manifesto e do VSIX deve permanecer igual ao publicador selecionado para o envio. `LICENSE` e `extension/LICENSE.txt` contêm os mesmos termos, e as licenças das dependências e fontes acompanham o pacote.

## Enviar ao Marketplace

Acesse o painel de gerenciamento de extensões da sua conta, selecione o publicador correto, crie uma extensão do VS Code e envie o `.vsix`. A documentação oficial descreve o [envio manual de um pacote VSIX e o cadastro do publicador](https://code.visualstudio.com/api/working-with-extensions/publishing-extension). A conta, a identidade do publicador e a aprovação do serviço não são verificadas pela compilação local.

## Reproduzir a distribuição

Para reproduzir ou desenvolver o produto de código aberto, use Python 3.10+ e Node.js 24 LTS. Na pasta raiz:

```sh
python3 -m venv .venv
# macOS/Linux; no Windows: .venv\Scripts\activate
source .venv/bin/activate
python -m pip install -r requirements-dev.lock
python -m pip install -e .
python tools/bundle_backend.py
cd extension
npm ci
npm test
npm run test:integration
npm run package
```

O empacotamento recompila a extensão e reúne novamente o núcleo e as dependências verificadas por hash. A primeira preparação requer rede para obter essas dependências. A extensão instalada não usa a rede para traduzir interfaces.

De volta à pasta raiz do repositório, para verificar o conteúdo de um `.vsix` e executar o núcleo incluído sem pacotes Python do usuário:

```sh
python tools/verify_release.py release/embedmark-0.4.2.vsix --python "$(python -c 'import sys; print(sys.executable)')" --report release/embedmark-package-verification.json
```

Os testes do VS Code usam perfis e pastas temporários, sem instalar a extensão na configuração pessoal. O comando de verificação da instalação real do `.vsix` está em `tools/verify_installed_extension.cjs`.

## Limites dos resultados

A versão foi preparada e testada originalmente no macOS do autor. A matriz automatizada para Linux, Windows e macOS é executada no [GitHub Actions](https://github.com/CarminatiUser/embedmark/actions/workflows/tests.yml), com resultados vinculados ao commit verificado e ao ambiente de execução. Consulte [VALIDACAO_0.4.0.md](VALIDACAO_0.4.0.md) para os registros históricos das verificações locais e [VALIDACAO_0.4.2.md](VALIDACAO_0.4.2.md) para a publicação sob MIT.

O [ensaio físico de 11/11/2026](VALIDACAO_FISICA_2026-11-11.md) confirmou a execução do contador gerado pelo núcleo 0.4.2 na Waveshare ESP32-C6-LCD-1.47: 143 verificações por console aprovadas, com conferência visual e fotografia. Esse resultado é separado dos testes de instalação do VSIX e não valida touch, outros hardwares ou desempenho. A atualização documental não modifica a versão publicada da extensão. O vídeo de demonstração será gravado posteriormente pelo autor.
