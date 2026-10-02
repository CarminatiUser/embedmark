#ifndef TCC_UI_CONTROLLER_H
#define TCC_UI_CONTROLLER_H
#include <stdbool.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Chamar depois da inicialização LVGL/display, no mesmo contexto de acesso. */
bool ui_controller_start(void);
#ifdef __cplusplus
}
#endif
#endif
