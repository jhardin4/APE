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
    loader: appImageLoader
  }

  AppImageLoader {
    id: appImageLoader
    guiNode: nodeHandler.guiNode
  }

  Connections {
    target: nodeHandler.guiNode
    onRunningChanged: {
      if (nodeHandler.guiRunning) {
        appImageLoader.refresh()
      }
    }
  }

  Component.onCompleted: {
    if (nodeHandler.guiRunning) {
      appImageLoader.refresh()
    }
  }

  RowLayout {
    anchors.fill: parent
    anchors.margins: Style.singleMargin

    ColumnLayout {
      RowLayout {
        Button {
          text: qsTr("Template")
          //onClicked: appImageLoader.refresh()
        }
        Button {
          text: qsTr("Refresh")
          onClicked: appImageLoader.refresh()
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
            onClicked: treeModel.findAndReplace(findTextField.text,
                                                replaceTextField.text)
          }
        }
      }

      Button {
        text: qsTr("Connect All Devices")
      }

      Button {
        text: qsTr("Disconnect All Devices")
      }

      VerticalFiller {
      }
    }
  }
}
