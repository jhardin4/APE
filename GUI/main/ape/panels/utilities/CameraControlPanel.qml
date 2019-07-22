import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.1
import ape.controls 1.0
import ape.utilities 1.0

GroupBox {
  title: qsTr("Camera Control")
  id: root

  ColumnLayout {
    anchors.fill: parent

    UEyeView {
      id: view
      Layout.fillWidth: true
      Layout.fillHeight: true
      implicitHeight: 200
      implicitWidth: 200
      running: runningButton.checked
    }

    Button {
      id: runningButton
      text: checked ? qsTr("Close") : qsTr("Open")
      checkable: true
    }
  }
}
