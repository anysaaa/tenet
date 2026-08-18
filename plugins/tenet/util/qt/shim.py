
#
# this global is used to indicate whether Qt bindings for python are present
# and available for use by Tenet.
#

QT_AVAILABLE = False

#------------------------------------------------------------------------------
# PyQt5 <--> PySide2 <--> PySide6 Compatibility
#------------------------------------------------------------------------------
#
#    we use this file to shim/re-alias a few Qt API's to ensure compatibility
#    between the popular Qt frameworks. these shims serve to reduce the number
#    of compatibility checks in the plugin code that consumes them.
#
#    this file was critical for retaining compatibility with Qt4 frameworks
#    used by IDA 6.8/6.95, but it less important now. support for Qt 4 and
#    older versions of IDA will be deprecated.
#

USING_PYQT5 = False
USING_PYSIDE2 = False
USING_PYSIDE6 = False
USING_PYQT6 = False

#------------------------------------------------------------------------------
# PySide6 Compatibility (IDA 9.x / Qt6)
#------------------------------------------------------------------------------

# attempt to load PySide6 (the Qt6 bindings shipped with IDA 9.x)
if QT_AVAILABLE == False:
    try:
        import PySide6.QtGui as QtGui
        import PySide6.QtCore as QtCore
        import PySide6.QtWidgets as QtWidgets
        from PySide6 import shiboken6 as sip

        # PySide6 uses the new-style enum namespaces, but most code still
        # accesses them through the QtCore.Qt.* compatibility aliases.
        # Ensure legacy signal/slot aliases exist for cross-framework code.
        QtCore.pyqtSignal = QtCore.Signal
        QtCore.pyqtSlot = QtCore.Slot

        # importing went okay, PySide6 must be available for use
        QT_AVAILABLE = True
        USING_PYSIDE6 = True

    # import failed, PySide6 is not available
    except ImportError:
        pass

#------------------------------------------------------------------------------
# PyQt6 Compatibility
#------------------------------------------------------------------------------

if QT_AVAILABLE == False:
    try:
        import PyQt6.QtGui as QtGui
        import PyQt6.QtCore as QtCore
        import PyQt6.QtWidgets as QtWidgets
        from PyQt6 import sip

        # importing went okay, PyQt6 must be available for use
        QT_AVAILABLE = True
        USING_PYQT6 = True

    # import failed, PyQt6 is not available
    except ImportError:
        pass

#------------------------------------------------------------------------------
# PyQt5 Compatibility
#------------------------------------------------------------------------------

# attempt to load PyQt5
if QT_AVAILABLE == False:
    try:
        import PyQt5.QtGui as QtGui
        import PyQt5.QtCore as QtCore
        import PyQt5.QtWidgets as QtWidgets
        from PyQt5 import sip

        # importing went okay, PyQt5 must be available for use
        QT_AVAILABLE = True
        USING_PYQT5 = True

    # import failed, PyQt5 is not available
    except ImportError:
        pass

#------------------------------------------------------------------------------
# PySide2 Compatibility
#------------------------------------------------------------------------------

# if PyQt5 did not import, try to load PySide
if QT_AVAILABLE == False:
    try:
        import PySide2.QtGui as QtGui
        import PySide2.QtCore as QtCore
        import PySide2.QtWidgets as QtWidgets

        # alias for less PySide2 <--> PyQt5 shimming
        QtCore.pyqtSignal = QtCore.Signal
        QtCore.pyqtSlot = QtCore.Slot

        # importing went okay, PySide must be available for use
        QT_AVAILABLE = True
        USING_PYSIDE2 = True

    # import failed. No Qt / UI bindings available...
    except ImportError:
        pass

#------------------------------------------------------------------------------
# Qt Object Wrapping Shim
#------------------------------------------------------------------------------

def wrapinstance(ptr, cls):
    """
    Wrap a raw Qt/C++ pointer into a Python instance of the given class.

    This abstraction supports the different wrapping APIs exposed by
    PyQt5/PySide2 (sip) and PySide6 (shiboken6).
    """

    # shiboken6 (PySide6) expects integer pointer values, not c_void_p objects
    if USING_PYSIDE6:
        return sip.wrapInstance(int(ptr), cls)

    # PyQt5/PyQt6 sip.wrapinstance expects the same integer form
    return sip.wrapinstance(int(ptr), cls)

#------------------------------------------------------------------------------
# Qt6 Enum Compatibility Shims
#------------------------------------------------------------------------------

def _patch_enum_aliases():
    """
    Expose legacy Qt5-style enum names on the Qt6 modules for backward
    compatibility. This lets existing plugin code use names such as
    QtGui.QImage.Format_ARGB32 and QtCore.Qt.ShiftModifier without
    modification.
    """

    # PySide6 already provides many compatibility aliases, but not all of them.
    # Patch the remainder so the rest of the codebase can stay unchanged.
    if USING_PYSIDE6 or USING_PYQT6:
        if not hasattr(QtGui.QImage, "Format_ARGB32"):
            QtGui.QImage.Format_ARGB32 = QtGui.QImage.Format.Format_ARGB32
        if not hasattr(QtGui.QFont, "TypeWriter"):
            QtGui.QFont.TypeWriter = QtGui.QFont.StyleHint.TypeWriter
        if not hasattr(QtCore.Qt, "ShiftModifier"):
            QtCore.Qt.ShiftModifier = QtCore.Qt.KeyboardModifier.ShiftModifier
        if not hasattr(QtCore.Qt, "RightToolBarArea"):
            QtCore.Qt.RightToolBarArea = QtCore.Qt.ToolBarArea.RightToolBarArea

_patch_enum_aliases()