import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3

GroupBox {
  title: qsTr("Operations")
  GridLayout {
    anchors.fill: parent
    Button {
      Layout.fillWidth: true
      text: qsTr("Refresh")
      onClicked: nodeHandler.appInterface.refresh()
    }
    Button {
      Layout.fillWidth: true
      text: qsTr("New from Template")
      onClicked: nodeHandler.appInterface.startTemplate(false)
    }
    Button {
      Layout.fillWidth: true
      text: qsTr("Connect All Devices")
      onClicked: {
        nodeHandler.appInterface.connectAll(true)
        nodeHandler.appInterface.refreshEprocs()
      }
    }

    Button {
      Layout.fillWidth: true
      text: qsTr("Disconnect All Devices")
      onClicked: nodeHandler.appInterface.disconnectAll()
    }
  }
}
