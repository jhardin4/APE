import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Controls 1.4 as C1
import QtQuick.Layouts 1.3
import ape.controls 1.0
import ape.apparatus 1.0
import ape.core 1.0

Item {
  id: root

  AppImageTreeModel {
    id: treeModel
    appInterface: appInterface
  }

  AppInterface {
    id: appInterface
    guiNode: nodeHandler.guiNode
  }

  Connections {
    target: nodeHandler.guiNode
    onRunningChanged: {
      if (nodeHandler.guiRunning) {
        appInterface.refresh()
      }
    }
  }

  Component.onCompleted: {
    if (nodeHandler.guiRunning) {
      appInterface.refresh()
    }
  }

  RowLayout {
    anchors.fill: parent
    anchors.margins: Style.singleMargin

    ColumnLayout {
      RowLayout {
        Button {
          text: qsTr("Template")
          //onClicked: appInterface.refresh()
        }
        Button {
          text: qsTr("Refresh")
          onClicked: appInterface.refresh()
        }
      }

      AppImageTreeView {
        id: treeView
        Layout.fillWidth: true
        Layout.fillHeight: true
        model: treeModel
      }
    }

    ColumnLayout {

      GroupBox {
        title: qsTr("Find and Replace")
        GridLayout {
          columns: 2

          Label {
            text: qsTr("Find")
          }

          Label {
            text: qsTr("Replace")
          }

          TextField {
            id: findTextField
            selectByMouse: true
          }

          TextField {
            id: replaceTextField
          }

          Button {
            Layout.columnSpan: 2
            Layout.fillWidth: true
            enabled: findTextField.text && replaceTextField.text
            text: qsTr("Execute")
            onClicked: {
              appInterface.findAndReplace(findTextField.text,
                                          replaceTextField.text)
              findTextField.text = ""
              replaceTextField.text = ""
            }
          }
        }
      }

      Button {
        text: qsTr("Connect All Devices")
        onClicked: appInterface.connectAll(true)
      }

      Button {
        text: qsTr("Disconnect All Devices")
        onClicked: appInterface.disconnectAll()
      }

      VerticalFiller {
      }
    }
  }
}
