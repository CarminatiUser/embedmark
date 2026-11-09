# API de integração — versão 0.4.1

A API de integração foi introduzida na versão 0.3 e mantém o mesmo contrato na 0.4.1. A saída C expõe uma tela principal e seus componentes com ID. O firmware continua responsável pela inicialização do LVGL 8.3, display, temporização, entrada do usuário e acesso sincronizado ao LVGL.

## Criar, encontrar e atualizar

```c
#include "ui_generated.h"

lv_obj_t *screen = screen_main_create();
if (screen != NULL) {
    lv_obj_t *label = screen_main_get_object("contador");
    if (label != NULL) lv_label_set_text(label, "Ações: 10");
}
```

| Função | Contrato |
|---|---|
| `screen_main_create()` | Cria e carrega a tela na primeira chamada; as seguintes reutilizam a mesma instância, mantendo valores e eventos. Retorna a raiz ou `NULL` se não há display ou se uma transição/animação impede recarregar a tela |
| `screen_main_get()` | Retorna a raiz existente ou `NULL`; não cria nem carrega uma tela |
| `screen_main_get_object(id)` | Busca pelo ID original, inclusive o ID de `screen`. Retorna `NULL` para ID inexistente, `NULL`, componente excluído ou tela inexistente |
| `screen_main_destroy()` | Exclui a tela e seus descendentes quando ela está inativa e fora de transições/animações. Retorna `false` se ainda não pode excluí-la; retorna `true` também quando ela já não existe |

IDs são comparados como strings UTF-8 exatas. Eles não se tornam nomes de variáveis C. Componentes sem ID continuam existindo, mas não são encontrados pela busca. Remover um objeto ou seu ancestral com as APIs LVGL invalida as entradas correspondentes da tabela. Recriar a tela após a destruição constrói novos objetos; ponteiros guardados pelo aplicativo precisam ser obtidos novamente.

## Registrar eventos sem editar código gerado

```c
static void on_click(lv_event_t *event)
{
    (void)event;
    lv_obj_t *label = screen_main_get_object("contador");
    if (label != NULL) lv_label_set_text(label, "Ação recebida");
}

/* Após criar a tela; registre uma vez por instância do botão. */
lv_obj_t *button = screen_main_get_object("incrementar");
if (button != NULL) lv_obj_add_event_cb(button, on_click, LV_EVENT_CLICKED, NULL);
```

O exemplo `examples/firmware/ui_controller.c` implementa um contador, evita duplicar callbacks quando `ui_controller_start()` é repetido e limpa sua referência ao botão quando ele é excluído. Os valores são reiniciados na criação de uma nova instância. Ao atingir o limite de `uint32_t`, o contador volta a zero. A geração não altera esse controlador.

Eventos podem vir de um dispositivo de entrada registrado no LVGL ou da própria aplicação. O teste automatizado envia eventos LVGL; isso não comprova que a placa tenha touch, botões ou drivers de entrada configurados.

## Destruir e recriar

```c
/* tela_alternativa é uma tela válida, existente, pertencente ao mesmo display. */
lv_scr_load(tela_alternativa);
if (screen_main_destroy()) {
    /* Referências antigas deixaram de ser válidas. */
}
/* Quando necessário: */
screen_main_create();
```

A API não apaga a tela ativa para deixar o display sem uma tela. Transições com `lv_scr_load_anim()` devem terminar antes da destruição. Não remova os callbacks internos de exclusão, não altere os IDs da tabela e não reparentalize componentes gerados para fora da tela: a API pressupõe a hierarquia que ela criou.

Os estilos compartilhados são inicializados uma vez e permanecem durante a vida do LVGL. Destruir/recriar libera os objetos, sem realocar esses estilos a cada ciclo. Na versão 0.4.1, permanecem as limitações da API introduzida na 0.3: não há descarregamento do módulo, reinicialização por `lv_deinit()`/`lv_init()`, múltiplas instâncias, namespaces para vincular várias saídas geradas ou proteção contra esgotamento de memória do LVGL. Todas as chamadas devem ocorrer no contexto/proteção usado pelo firmware para acessar o LVGL.

## Compatibilidade

Regere C e header juntos, usando a mesma versão do gerador. Chamadas antigas que apenas executam `screen_main_create();` continuam válidas; desde a versão 0.3, a função retorna um ponteiro e reutiliza a tela existente. Essa mudança foi preservada na 0.4.1. Um header da versão 0.2 não corresponde à API introduzida na 0.3. O JSON mantém `schema_version: 1` e o campo aditivo `fonts`, introduzido na 0.3, com as fontes realmente utilizadas.
