from PyQt5.QtWidgets import QFileDialog


def FromFile():
    options = QFileDialog.Options()
    filename, _ = QFileDialog.getOpenFileName(
        None,
        "Select Apparatus Image",
        "",
        "All Files (*);;json (*.json)",
        options=options,
    )
    # Collect types
    # Collect Tool axes
    args = [filename]
    kwargs = {}
    return args, kwargs
