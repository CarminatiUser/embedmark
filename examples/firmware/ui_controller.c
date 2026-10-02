/* Código da aplicação: este arquivo não é alterado pelo tradutor. */
#include "ui_generated.h"
#include "ui_controller.h"
#include <inttypes.h>
#include <stdint.h>

static uint32_t count;
static lv_obj_t *bound_button;

static void on_increment(lv_event_t *event)
{
    (void)event;
    lv_obj_t *label = screen_main_get_object("contador");
    if (label == NULL) return;
    count = count == UINT32_MAX ? 0 : count + 1;
    lv_label_set_text_fmt(label, "Ações: %" PRIu32, count);
}

static void on_button_deleted(lv_event_t *event)
{
    if (bound_button == lv_event_get_target(event)) bound_button = NULL;
}

bool ui_controller_start(void)
{
    if (screen_main_create() == NULL) return false;
    lv_obj_t *button = screen_main_get_object("incrementar");
    lv_obj_t *label = screen_main_get_object("contador");
    if (button == NULL || label == NULL) return false;
    if (bound_button == button) return true;
    count = 0;
    lv_label_set_text(label, "Ações: 0");
    lv_obj_add_event_cb(button, on_increment, LV_EVENT_CLICKED, NULL);
    lv_obj_add_event_cb(button, on_button_deleted, LV_EVENT_DELETE, NULL);
    bound_button = button;
    return true;
}
