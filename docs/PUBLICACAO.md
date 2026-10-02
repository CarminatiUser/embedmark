# Pacote da extensão e publicação

A versão 0.4.0 é entregue como `release/tcc-ui-translator-0.4.0.vsix`, acompanhada do pacote Python, hashes e registros de verificação. O envio ao Marketplace é uma etapa posterior; não foi feito automaticamente.

## Instalar o pacote local

No VS Code, abra Extensions, use o menu de três pontos e escolha **Install from VSIX**. Selecione o arquivo da pasta `release`. Tenha Python 3.10 ou superior instalado; a extensão inclui as bibliotecas Python necessárias. Node.js, pip e ESP-IDF não são requisitos para usar a extensão já empacotada.

Abra uma pasta confiável e use **TCC UI: Criar exemplo de contador**. Salve o HTML e execute **Validar interface** e **Gerar interface LVGL**. Se o Python não for encontrado, configure **TCC UI Translator: Python Path** com o caminho do executável, sem argumentos adicionais.

O ESP-IDF é necessário apenas para compilar/gravar um firmware, conforme o [laboratório da tela](../../tcc-ui-validation/README.md).

## Identidade do publicador

O manifesto utiliza `arthur-carminati` como **identificador proposto**, sem afirmar que a conta existe ou que está disponível. Antes do envio, entre na sua conta do Marketplace e confirme/crie o publicador. O campo `publisher` do pacote deve corresponder exatamente a essa conta.

Se o identificador escolhido for diferente, altere somente esse metadado e gere outro pacote:

```sh
cd extension
npm pkg set publisher=IDENTIFICADOR_REAL
npm run package
```

O código original mantém direitos reservados em `LICENSE`/`LICENSE.txt`; as licenças das dependências e das fontes estão incluídas. Nenhuma licença aberta foi aplicada automaticamente ao seu código. Um repositório público e URLs de suporte podem ser acrescentados quando forem definidos; não foram inventados endereços remotos.

## Enviar ao Marketplace

Acesse o painel de gerenciamento de extensões da sua conta, selecione o publicador correto, crie uma extensão do VS Code e envie o `.vsix`. A documentação oficial descreve o [envio manual de um pacote VSIX e o cadastro do publicador](https://code.visualstudio.com/api/working-with-extensions/publishing-extension). A conta, a identidade do publicador e a aprovação do serviço não são verificadas pela compilação local.

## Reproduzir a distribuição

Para desenvolver/empacotar, use Python 3.10+ e Node.js 24 LTS. Na pasta raiz:

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

Para verificar o conteúdo de um `.vsix` e executar o núcleo incluído sem pacotes Python do usuário:

```sh
python tools/verify_release.py release/tcc-ui-translator-0.4.0.vsix --python python3 --report release/package-verification.json
```

Os testes do VS Code usam perfis e pastas temporários, sem instalar a extensão na configuração pessoal. O comando de verificação da instalação real do `.vsix` está em `tools/verify_installed_extension.cjs`.

## Limites dos resultados

A versão foi preparada e testada no macOS deste computador. A matriz automatizada para Linux, Windows e macOS está configurada no repositório, mas só pode receber resultado remoto depois que o código for enviado a um serviço de integração contínua. Consulte [VALIDACAO_0.4.0.md](VALIDACAO_0.4.0.md) para as execuções efetivamente concluídas. A validação física do display permanece no roteiro do laboratório.
