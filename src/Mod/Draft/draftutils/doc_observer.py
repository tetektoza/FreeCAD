import FreeCAD as App
from PySide6.QtCore import QObject, Signal
from PySide6.QtCore import QTimer
from bimcommands import BimViews

document_locked = False  # Start locked

if App.GuiUp:
    import FreeCADGui as Gui
    from draftutils.todo import ToDo

    class _Draft_DocObserver():

        def __init__(self):
            print("DRAFT DOCOBSERVER")
            self.bim_views = BimViews.BIM_Views()
        # See: /src/Gui/DocumentObserverPython.h

        def _delay_update_if_unlocked(self):
            global document_locked
            if document_locked:
                #print("Document is locked — skipping update.")
                return
            ToDo.delay(self.bim_views.update, None)

        def slotDeletedDocument(self, gui_doc):
            print("slotDeletedDocument")
            document_locked = False
            ToDo.delay(self.bim_views.update, None)
        
        def slotFinishOpenDocument(self):
            global document_locked
            print("slotFinishOpenDocument — unlocking")
            document_locked = False
            ToDo.delay(self.bim_views.update, None)

        def slotDeletedObject(self, viewprovider_obj):
            print("slotDeletedObject")
            self._delay_update_if_unlocked()

        # def slotBeforeChangeObject(self, obj, prop):
        #     ToDo.delay(self.bim_views.update, None)

        # def slotCreatedObject(self, viewprovider_obj):
        #     ToDo.delay(self.bim_views.update, None)

        def slotChangedObject(self, viewprovider_obj, prop):
            #print("SLOT CHANGED OBJECT")
            self._delay_update_if_unlocked()

        # def slotChangedDocument(self, gui_doc, prop):
        #     ToDo.delay(self.bim_views.update, None)

        def slotCloseTransaction(self, abort):
            print("slotCloseTransaction")
            self._delay_update_if_unlocked()
        def slotCommitTransaction(self, doc):
            print("slotCommitTransaction")
            self._delay_update_if_unlocked()

        def slotRecomputedDocument(self, doc):
            print("slotRecomputedDocument")
            self._delay_update_if_unlocked()

        def slotActivateDocument(self, doc):
            global document_locked
            print("slotActivateDocument")
            document_locked = True
            ToDo.delay(self.bim_views.update, None)

        def slotCreatedDocument(self, doc):
            global document_locked
            document_locked = True
            # print("slotCreatedDocument")
            ToDo.delay(self.bim_views.update, None)
    _doc_observer = None

    def get_doc_observer():
        return _doc_observer

    def _doc_observer_start():
        global _doc_observer
        if _doc_observer is None:
            _doc_observer = _Draft_DocObserver()
            Gui.addDocumentObserver(_doc_observer)

    def _doc_observer_stop():
        global _doc_observer
        try:
            if _doc_observer is not None:
                Gui.removeDocumentObserver(_doc_observer)
        except:
            pass
        _doc_observer = None

    def _finish_command_on_doc_close(gui_doc):
        """Finish the active Draft or BIM command if the related document has been
        closed. Only works for commands that have set `App.activeDraftCommand.doc`
        and use a task panel.
        """
        if getattr(App, "activeDraftCommand", None) \
                and getattr(App.activeDraftCommand, "doc", None) == gui_doc.Document \
                and getattr(App.activeDraftCommand, "ui", None):
            if hasattr(App.activeDraftCommand.ui, "reject"):
                ToDo.delay(App.activeDraftCommand.ui.reject, None)
            elif hasattr(App.activeDraftCommand.ui, "escape"):
                ToDo.delay(App.activeDraftCommand.ui.escape, None)
