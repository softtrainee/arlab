MANAGERS = []
def open_manager(man, **kw):
#    if view is None:
#        view = 'edit_traits'

    if man in MANAGERS:
        try:
            man.ui.control.Raise()
        except AttributeError:
#            getattr(man, view)()
            man.edit_traits(**kw)
    else:
        man.edit_traits(**kw)
#        getattr(man, view)()
#        man.edit_traits()

        MANAGERS.append(man)
