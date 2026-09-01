#!/usr/bin/env python
#-*- coding: utf-8 -*-

from PySide6 import QtCore

from .methods.core import PinguinoCore

########################################################################
class PinguinoEvents(PinguinoCore):

    #----------------------------------------------------------------------
    def __init__(self):
        """"""
        # Guard: when Shiboken's cooperative super().__init__() chain
        # reaches this class during QMainWindow.__init__(), the
        # prerequisites (configIDE, pinguinoAPI, main) don't exist yet.
        # We skip the heavy initialisation here and let PinguinoIDE call
        # us explicitly once everything is ready.
        if hasattr(self, 'configIDE'):
            PinguinoCore.__init__(self)


    #----------------------------------------------------------------------
    def connect_events(self):
        """"""

        # Triggers
        self.main.actionNew_file.triggered.connect(self.ide_new_file)
        self.main.actionNew_blocks_file.triggered.connect(self.PinguinoKIT.ide_new_file)
        self.main.actionOpen_file.triggered.connect(self.ide_open_files)
        self.main.actionSave_file.triggered.connect(self.ide_save_file)
        self.main.actionSave_as.triggered.connect(self.ide_save_as)
        self.main.actionSave_all.triggered.connect(self.ide_save_all)
        self.main.actionClose_file.triggered.connect(self.ide_close_file)
        self.main.actionClose_all.triggered.connect(self.ide_close_all)
        self.main.actionClose_others.triggered.connect(self.ide_close_others)
        self.main.actionPrint.triggered.connect(self.editor_print_file)
        self.main.actionQuit.triggered.connect(self.ide_close_ide)
        self.main.actionUndo.triggered.connect(self.editor_undo)
        self.main.actionRedo.triggered.connect(self.editor_redo)
        self.main.actionCut.triggered.connect(self.editor_cut)
        self.main.actionCopy.triggered.connect(self.editor_copy)
        self.main.actionPaste.triggered.connect(self.editor_paste)
        self.main.actionDelete.triggered.connect(self.editor_delete)
        self.main.actionSelect_all.triggered.connect(self.editor_select_all)
        self.main.actionComment_out_region.triggered.connect(self.editor_comment_region)
        self.main.actionComment_Uncomment_region.triggered.connect(self.editor_comment_uncomment)
        self.main.actionIndent.triggered.connect(self.editor_indent_region)
        self.main.actionDedent.triggered.connect(self.editor_dedent_region)
        # self.main.actionHex_code.triggered.connect(self.__show_hex_code__)
        self.main.actionMain_c.triggered.connect(self.ide_show_main_c)
        self.main.actionUser_c.triggered.connect(self.ide_show_user_c)
        self.main.actionDefine_h.triggered.connect(self.ide_show_define_h)
        self.main.actionHex.triggered.connect(self.ide_show_hex)
        self.main.actionReset_IDE_instalation.triggered.connect(self.ide_reset_instalation)


        # Toggle Tabs
        self.main.actionTabLog.toggled.connect(lambda :self.toggle_tab("Log"))
        self.main.actionTabFiles.toggled.connect(lambda :self.toggle_tab("Files"))
        self.main.actionTabBoards.toggled.connect(lambda :self.toggle_tab("Boards"))
        self.main.actionTabStdout.toggled.connect(lambda :self.toggle_tab("Stdout"))
        self.main.actionTabSearch.toggled.connect(lambda :self.toggle_tab("Search"))
        self.main.actionTabProject.toggled.connect(lambda :self.toggle_tab("Project"))
        self.main.actionTabShell.toggled.connect(lambda :self.toggle_tab("Shell"))
        self.main.actionTabSourceBrowser.toggled.connect(lambda :self.toggle_tab("SourceBrowser"))
        self.main.actionLibraryManager.toggled.connect(lambda :self.toggle_tab("LibraryManager"))
        self.main.actionTabPaths.toggled.connect(lambda :self.toggle_tab("Paths"))
        #self.main.actionTabICSP.toggled.connect(lambda :self.toggle_tab("ICSP"))


        # Perspective related events
        self.main.actionMenubar.toggled.connect(self.toggle_menubar)
        self.main.actionToolbars.toggled.connect(self.toggle_toolbars)
        self.main.actionToggle_horizontal_tool_area.triggered.connect(self.toggle_bottom_area)
        self.main.actionToggle_vertical_tool_area.triggered.connect(self.toggle_right_area)
        self.main.tabWidget_tools.currentChanged.connect(self.tab_right_changed)
        self.main.tabWidget_bottom.currentChanged.connect(self.tab_bottoms_changed)
        # self.main.actionToggle_editor_area.toggled.connect(self.toggle_editor_area)
        self.main.actionMove_vertical_tool_area.triggered.connect(self.toggle_side_vertical_area)


        # Settings related events
        self.main.actionAutocomplete.triggered.connect(self.switch_autocomplete)
        self.main.actionColor_theme.toggled.connect(self.switch_color_theme)
        self.main.action16x16.triggered.connect(self.resize_toolbar(16, self.main.action16x16))
        self.main.action24x24.triggered.connect(self.resize_toolbar(24, self.main.action24x24))
        self.main.action32x32.triggered.connect(self.resize_toolbar(32, self.main.action32x32))
        self.main.action48x48.triggered.connect(self.resize_toolbar(48, self.main.action48x48))


        # Child windows
        # self.main.actionLibrary_manager.triggered.connect(self.__show_libmanager__)
        # self.main.actionSet_paths.triggered.connect(self.__config_paths__)
        self.main.actionSelect_board.triggered.connect(self.set_tab_board)
        # self.main.actionView_Pinguino_code.triggered.connect(self.__show_pinguino_code__)
        self.main.actionInsert_Block.triggered.connect(self.__show_insert_block__)
        self.main.actionSubmit_bug_report.triggered.connect(self.__show_submit_bug__)
        # self.main.actionCheck_for_patches.triggered.connect(self.__show_patches__)


        # Pinguino related events
        self.main.actionCompile.triggered.connect(self.pinguino_compile)
        self.main.actionUpload.triggered.connect(self.pinguino_upload)
        self.main.actionUpload_hex_directly.triggered.connect(self.pinguino_upload_hex)
        self.main.actionIf_Compile_then_Upload.triggered.connect(self.pinguino_compile_and_upload)


        # Help
        self.main.actionGitPinguinoIde.triggered.connect(lambda :self.open_web_site("https://github.com/PinguinoIDE/pinguino-ide/releases/latest"))
        self.main.actionGitPinguinoLibraries.triggered.connect(lambda :self.open_web_site("https://github.com/PinguinoIDE/pinguino-libraries"))
        self.main.actionGitPinguinoCompilers.triggered.connect(lambda :self.open_web_site("https://github.com/PinguinoIDE/pinguino-compilers"))
        self.main.actionWebsite.triggered.connect(lambda :self.open_web_site("http://www.pinguino.cc/"))
        self.main.actionWiki.triggered.connect(lambda :self.open_web_site("http://wiki.pinguino.cc/"))
        self.main.actionForum.triggered.connect(lambda :self.open_web_site("http://forum.pinguino.cc/"))
        self.main.actionBlog.triggered.connect(lambda :self.open_web_site("http://blog.pinguino.cc/"))
        self.main.actionGroup.triggered.connect(lambda :self.open_web_site("https://groups.google.com/forum/#!forum/pinguinocard"))
        self.main.actionShop.triggered.connect(lambda :self.open_web_site("http://shop.pinguino.cc/"))
        self.main.actionAbout.triggered.connect(self.__show_about__)
        # self.main.actionCheck_for_updates.triggered.connect(self.need_update)


        # Events
        self.closeEvent = self.ide_close_ide
        # self.main.actionSwitch_ide.toggled.connect(self.switch_ide_mode)
        self.main.tabWidget_files.currentChanged.connect(self.ide_tab_changed)
        self.main.tabWidget_files.tabCloseRequested.connect(self.ide_tab_close)
        # self.main.tabWidget_bottom.customContextMenuRequested.connect(self.ide_tabs_context_menu)
        # self.main.tabWidget_tools.customContextMenuRequested.connect(self.ide_tabs_context_menu)
        # self.main.tabWidget_files.tabCloseRequested.connect(self.ide_tab_close)


        # Graphical mode
        self.main.actionSave_image.triggered.connect(self.editor_save_screen_image)
        self.main.lineEdit_blocks_search.textChanged.connect(self.PinguinoKIT.update_blocks_search_tab)
        self.main.actionExport_code_to_editor.triggered.connect(self.editor_export_pinguino_code)
        self.main.comboBox_blocks.activated.connect(lambda index: self.set_block_tab(self.main.comboBox_blocks.itemText(index)))
        self.main.actionGenerate_blocks.triggered.connect(self.PinguinoKIT.code_to_blocks)


        # Context menu
        self.main.tabWidget_files.contextMenuEvent = self.editor_tabfile_context_menu
        self.main.tabWidget_files.contextMenuEvent = self.editor_tabfile_context_menu


        # Initialize
        self.main.actionToolbars.setChecked(True)
        # self.main.actionConfirm_board.setChecked(self.configIDE.config("Features", "confirm_board", True))

        self.main.dockWidget_right.resizeEvent = self.tab_tools_resize
        self.main.dockWidget_bottom.resizeEvent = self.tab_tools_resize

        self.main.tabWidget_bottom.contextMenuEvent = self.ide_tabs_context_menu
        self.main.tabWidget_tools.contextMenuEvent = self.ide_tabs_context_menu
        self.main.toolBar.contextMenuEvent = self.ide_tabs_context_menu
        self.main.menubar.contextMenuEvent = self.ide_tabs_context_menu
