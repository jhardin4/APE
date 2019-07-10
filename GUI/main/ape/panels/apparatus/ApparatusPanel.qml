import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Controls 1.4 as C1
import QtQuick.Layouts 1.3
import ape.apparatus 1.0

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
    anchors.margins: 5

    AppImageTreeView {
      id: treeView
      Layout.fillWidth: true
      Layout.fillHeight: true
      model: treeModel
    }

    Button {
      text: qsTr("Refresh")
      onClicked: appImageLoader.refresh()
    }
  }
}
