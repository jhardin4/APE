import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.1
import ape.controls 1.0
import ape.utilities 1.0

GroupBox {
  title: qsTr("Camera Control")
  id: root
  property bool ready: ueyeDevices.devices.length > 0
  visible: ready

  UEyeDevices {
    id: ueyeDevices
    appInterface: nodeHandler.appInterface
  }

  ColumnLayout {
    anchors.fill: parent

    UEyeView {
      id: view
      Layout.fillWidth: true
      Layout.fillHeight: true
      implicitHeight: 640
      implicitWidth: 480
      running: runningButton.checked
      camId: deviceCombo.currentIndex

      Label {
        anchors.centerIn: parent
        text: qsTr(
                "No UEye driver loaded.\nCheck the PYUEYE_DLL_PATH environment variable.")
        horizontalAlignment: Text.AlignHCenter
        visible: !view.driverLoaded
      }
    }

    RowLayout {
      enabled: view.driverLoaded
      Layout.alignment: Qt.AlignHCenter
      Label {
        text: qsTr("Device:")
      }

      ComboBox {
        id: deviceCombo
        model: [0, 1, 2]
        enabled: !view.running
      }

      Button {
        id: runningButton
        text: checked ? qsTr("Close") : qsTr("Open")
        checkable: true
        checked: view.running
      }
    }
  }
}
