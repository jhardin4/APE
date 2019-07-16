import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Controls 1.4 as C1
import QtQuick.Layouts 1.3
import ape.core 1.0
import ape.controls 1.0
import ape.apparatus 1.0

Item {
  id: root
  Layout.fillWidth: true
  Layout.fillHeight: true

  AppImageTreeModel {
    id: treeModel
    appInterface: nodeHandler.appInterface
  }

  RowLayout {
    anchors.fill: parent
    anchors.margins: Style.singleMargin

    ColumnLayout {

      GroupBox {
        Layout.fillWidth: true
        Layout.fillHeight: true
        title: qsTr("Apparatus")

        AppImageTreeView {
          id: treeView
          anchors.fill: parent
          model: treeModel
        }
      }
    }

    ColumnLayout {
      Layout.fillWidth: false

      DataPanel {
        Layout.fillWidth: true
      }

      OperationsPanel {
        Layout.fillWidth: true
      }

      FindAndReplacePanel {
        Layout.fillWidth: true
      }

      GroupBox {
        Layout.fillWidth: true
        Layout.fillHeight: true

        title: qsTr("Watchlist")

        WatchTableView {
          id: watchTableView
          anchors.fill: parent
          model: treeModel.watched

          Binding {
            target: nodeHandler.appInterface
            property: "watched"
            value: treeModel.watched
          }

          Timer {
            id: refreshTimer
            interval: 1000
            repeat: true
            running: watchTableView.rowCount > 0 && nodeHandler.guiRunning
            onTriggered: nodeHandler.appInterface.fetchWatched()
          }
        }
      }
    }
  }
}
