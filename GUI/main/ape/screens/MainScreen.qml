import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Controls 1.4 as C1
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
    id: stack
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.bottom: parent.bottom
    anchors.top: topBar.bottom
    currentIndex: bar.currentIndex
    visible: nodeHandler.guiRunning // && container.target === stack

    ApparatusPanel {
      id: apparatusPanel
    }

    ProcedurePanel {
      id: procedurePanel
    }

    Item {
      id: utilitiesPanel
    }
  }
  //  Item {
  //    id: container
  //    property Item target: splitView
  //    function switchParent() {
  //      if (container.target === stack) {
  //        container.target = splitView
  //      } else {
  //        container.target = stack
  //      }
  //      apparatusPanel.parent = container.target
  //      procedurePanel.parent = container.target
  //      utilitiesPanel.parent = container.target
  //      if (container.target === stack) {
  //        splitView.removeItem(apparatusPanel)
  //        splitView.removeItem(procedurePanel)
  //        splitView.removeItem(utilitiesPanel)
  //      } else {
  //        splitView.addItem(apparatusPanel)
  //        splitView.addItem(procedurePanel)
  //        splitView.addItem(utilitiesPanel)
  //      }
  //    }
  //    Component.onCompleted: switchParent()
  //  }
  //  C1.SplitView {
  //    id: splitView
  //    anchors.left: parent.left
  //    anchors.right: parent.right
  //    anchors.bottom: parent.bottom
  //    anchors.top: topBar.bottom
  //    anchors.fill: parent
  //    orientation: Qt.Horizontal
  //    visible: container.target === splitView
  //  }
  //  Button {
  //    text: "Switch"
  //    onClicked: container.switchParent()
  //  }
}
