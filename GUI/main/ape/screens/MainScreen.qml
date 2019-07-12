import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import ape.controls 1.0
import ape.panels.startup 1.0
import ape.panels.apparatus 1.0
import ape.panels.procedure 1.0
import Qt.labs.settings 1.0

Item {
  id: root

  StartupPanel {
    anchors.fill: parent
    visible: !nodeHandler.guiRunning
  }

  RowLayout {
    id: topBar
    anchors.left: parent.left
    anchors.right: parent.right
    visible: nodeHandler.guiRunning

    TabBar {
      id: bar
      Layout.fillWidth: true

      TabButton {
        text: qsTr("Apparatus")
      }

      TabButton {
        text: qsTr("Procedure")
      }

      TabButton {
        text: qsTr("Utilities")
      }
    }

    Button {
      text: qsTr("Close GUI")
      onClicked: nodeHandler.stopGUI()
    }
  }

  Settings {
    property alias tabIndex: bar.currentIndex
  }

  StackLayout {
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.bottom: parent.bottom
    anchors.top: topBar.bottom
    currentIndex: bar.currentIndex
    visible: nodeHandler.guiRunning

    ApparatusPanel {
    }

    ProcedurePanel {
    }

    Item {
      id: activityTab
    }
  }
}
