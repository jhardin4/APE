import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import Qt.labs.platform 1.0
import Qt.labs.settings 1.0

FileDialog {
  id: fileDialog
  nameFilters: [qsTr("JSON files (*.json)"), qsTr("All files (*)")]
  title: openMode ? qsTr("Open Proclist File") : qsTr("Save Proclist File")
  folder: StandardPaths.writableLocation(StandardPaths.HomeLocation)
  property bool openMode: true
  fileMode: openMode ? FileDialog.OpenFile : FileDialog.SaveFile

  onAccepted: {
    settings.file = file
    if (openMode) {
      nodeHandler.procInterface.importFrom(file)
      nodeHandler.procInterface.refreshProcedures()
      nodeHandler.procInterface.refreshProclist()
    } else {
      nodeHandler.procInterface.saveAs(file)
    }
  }

  onVisibleChanged: {
    if (visible) {
      currentFile = settings.file
    }
  }

  Settings {
    id: settings
    category: "proclist_file"
    property alias folder: fileDialog.folder
    property url file: ""
  }
}
