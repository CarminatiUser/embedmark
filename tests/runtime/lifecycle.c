#include "ui_generated.h"
#include "ui_controller.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

LV_FONT_DECLARE(tcc_font_pt_14);
LV_FONT_DECLARE(tcc_font_pt_20);
LV_FONT_DECLARE(tcc_font_pt_24);

static lv_color_t buffer[172 * 16];
static lv_color_t framebuffer[172 * 320];
static lv_disp_draw_buf_t draw_buffer;
static lv_disp_drv_t driver;

static void flush(lv_disp_drv_t *display, const lv_area_t *area, lv_color_t *pixels)
{
    for (int y = area->y1; y <= area->y2; ++y) {
        for (int x = area->x1; x <= area->x2; ++x) {
            assert(x >= 0 && x < 172 && y >= 0 && y < 320);
            framebuffer[y * 172 + x] = *pixels++;
        }
    }
    lv_disp_flush_ready(display);
}

static void capture_if_requested(void)
{
    const char *path = getenv("TCC_TEST_CAPTURE");
    if (path == NULL) return;
    FILE *image = fopen(path, "wb");
    assert(image != NULL);
    fprintf(image, "P6\n172 320\n255\n");
    for (int i = 0; i < 172 * 320; ++i) {
        uint32_t pixel = lv_color_to32(framebuffer[i]);
        unsigned char rgb[] = {(pixel >> 16) & 255, (pixel >> 8) & 255, pixel & 255};
        assert(fwrite(rgb, 1, 3, image) == 3);
    }
    assert(fclose(image) == 0);
}

static void advance(uint32_t elapsed)
{
    lv_tick_inc(elapsed);
    lv_timer_handler();
}

int main(void)
{
    lv_init();
    assert(screen_main_create() == NULL);
    assert(screen_main_get() == NULL);
    assert(screen_main_get_object("contador") == NULL);
    assert(screen_main_destroy());

    lv_disp_draw_buf_init(&draw_buffer, buffer, NULL, 172 * 16);
    lv_disp_drv_init(&driver);
    driver.hor_res = 172;
    driver.ver_res = 320;
    driver.flush_cb = flush;
    driver.draw_buf = &draw_buffer;
    lv_disp_t *display = lv_disp_drv_register(&driver);
    assert(display != NULL);
    lv_obj_t *fallback = lv_scr_act();

    assert(ui_controller_start());
    lv_obj_t *root = screen_main_get();
    assert(root == lv_scr_act());
    assert(root == screen_main_get_object("painel"));
    assert(screen_main_get_object(NULL) == NULL);
    assert(screen_main_get_object("desconhecido") == NULL);
    assert(screen_main_create() == root);
    assert(ui_controller_start());
    lv_obj_t *button = screen_main_get_object("incrementar");
    lv_obj_t *counter = screen_main_get_object("contador");
    assert(button && counter);
    for (int i = 0; i < 3; ++i) lv_event_send(button, LV_EVENT_CLICKED, NULL);
    assert(strcmp(lv_label_get_text(counter), "Ações: 3") == 0);
    assert(lv_obj_get_style_text_font(counter, LV_PART_MAIN) == &tcc_font_pt_20);
    lv_obj_update_layout(root);
    assert(lv_obj_get_width(counter) == 148);
    assert(lv_obj_get_height(counter) > 0);
    assert(!screen_main_destroy());
    assert(screen_main_get() == root);
    advance(30);
    capture_if_requested();

    /* Remover um ancestral invalida também os acessos aos descendentes. */
    lv_obj_del(screen_main_get_object("conteudo"));
    assert(screen_main_get_object("conteudo") == NULL);
    assert(screen_main_get_object("contador") == NULL);
    assert(screen_main_get_object("incrementar") == NULL);
    assert(!ui_controller_start());
    lv_scr_load(fallback);
    assert(screen_main_destroy());
    assert(screen_main_get() == NULL);
    assert(screen_main_get_object("titulo") == NULL);
    assert(screen_main_destroy());

    /* Exclusão externa também limpa a tabela de IDs. */
    assert(ui_controller_start());
    root = screen_main_get();
    lv_scr_load(fallback);
    lv_obj_del(root);
    assert(screen_main_get() == NULL);
    assert(screen_main_get_object("painel") == NULL);

    /* Destino de transição com atraso não pode ser destruído. */
    assert(ui_controller_start());
    root = screen_main_get();
    lv_scr_load(fallback);
    lv_scr_load_anim(root, LV_SCR_LOAD_ANIM_MOVE_LEFT, 100, 50, false);
    assert(!screen_main_destroy());
    assert(screen_main_create() == NULL);
    advance(60);
    advance(120);
    assert(screen_main_get() == lv_scr_act());
    assert(!screen_main_destroy());

    /* Origem da transição fica protegida até a conclusão. */
    lv_scr_load_anim(fallback, LV_SCR_LOAD_ANIM_MOVE_RIGHT, 100, 0, false);
    advance(1);
    assert(!screen_main_destroy());
    advance(150);
    assert(screen_main_destroy());
    advance(30);

    /* Após o aquecimento, os ciclos não acumulam objetos ou memória LVGL. */
    assert(ui_controller_start());
    lv_scr_load(fallback);
    assert(screen_main_destroy());
    advance(30);
    lv_mem_monitor_t before, after;
    lv_mem_monitor(&before);
    for (int i = 0; i < 100; ++i) {
        assert(ui_controller_start());
        assert(ui_controller_start());
        lv_event_send(screen_main_get_object("incrementar"), LV_EVENT_CLICKED, NULL);
        assert(strcmp(lv_label_get_text(screen_main_get_object("contador")), "Ações: 1") == 0);
        lv_scr_load(fallback);
        assert(screen_main_destroy());
        advance(30);
    }
    lv_mem_monitor(&after);
    assert(after.free_size == before.free_size);
    assert(lv_mem_test() == LV_RES_OK);
    lv_disp_remove(display);
    puts("LVGL real: IDs, eventos, exclusões, transições e 100 ciclos aprovados.");
    return 0;
}
