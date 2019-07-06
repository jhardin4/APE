import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import ape.apparatus 1.0

Item {
  id: root

  AppImageTreeModel {
    id: treeModel
    guiNode: nodeHandler.guiNode
  }

  RowLayout {
    anchors.fill: parent
    anchors.margins: 5

    AppImageTreeView {
      id: treeView
      Layout.fillWidth: true
      Layout.fillHeight: true
    }

    Button {
      text: qsTr("Refresh")
      onClicked: treeModel.refresh()
    }
  }
}
