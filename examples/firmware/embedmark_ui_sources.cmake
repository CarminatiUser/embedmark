# Inclua este fragmento no main/CMakeLists.txt antes de idf_component_register.
# Acrescente ${EMBEDMARK_UI_SOURCES} a SRCS e ${EMBEDMARK_UI_INCLUDE_DIR} a INCLUDE_DIRS.
set(EMBEDMARK_UI_INCLUDE_DIR "${CMAKE_CURRENT_LIST_DIR}")
set(EMBEDMARK_UI_SOURCES
    "${CMAKE_CURRENT_LIST_DIR}/ui_generated.c"
    "${CMAKE_CURRENT_LIST_DIR}/ui_controller.c"
    "${CMAKE_CURRENT_LIST_DIR}/embedmark_sans_pt_14.c"
    "${CMAKE_CURRENT_LIST_DIR}/embedmark_sans_pt_20.c"
    "${CMAKE_CURRENT_LIST_DIR}/embedmark_sans_pt_24.c"
)
