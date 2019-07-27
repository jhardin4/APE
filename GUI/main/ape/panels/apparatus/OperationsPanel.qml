import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import Qt.labs.settings 1.0

GroupBox {
  title: qsTr("Operations")

  GridLayout {
    anchors.fill: parent
    Button {
      Layout.fillWidth: true
      text: qsTr("Connect All Devices")
      onClicked: {
        nodeHandler.procInterface.createUserDevice()
        nodeHandler.appInterface.connectAll(simulationCheck.checked)
        nodeHandler.appInterface.refreshAppImage()
        nodeHandler.appInterface.refreshProclog()
        nodeHandler.procInterface.refreshEprocs()
      }
    }

    Button {
      Layout.fillWidth: true
      text: qsTr("Disconnect All Devices")
      onClicked: {
        nodeHandler.appInterface.disconnectAll()
        nodeHandler.appInterface.refreshAppImage()
        nodeHandler.appInterface.refreshProclog()
      }
    }

    CheckBox {
      id: simulationCheck
      text: qsTr("Simulation")
    }
  }

  Settings {
    property alias simulationMode: simulationCheck.checked
  }
}
