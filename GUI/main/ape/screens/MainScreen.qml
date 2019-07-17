import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Controls 1.4 as C1
import QtQuick.Layouts 1.3
import ape.core 1.0
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

  ColumnLayout {
    anchors.fill: parent

    MorphingContainer {
      id: container
      Layout.fillWidth: true
      Layout.fillHeight: true
      visible: nodeHandler.guiRunning

      ApparatusPanel {
        id: apparatusPanel
      }

      ProcedurePanel {
        id: procedurePanel
      }

      Item {
        id: utilitiesPanel
      }

      Settings {
        property alias currentIndex: container.currentIndex
      }
    }

    Button {
      Layout.alignment: Qt.AlignRight
      text: qsTr("Stop GUI")
      visible: nodeHandler.guiRunning

      onClicked: nodeHandler.stopGUI()
    }
  }
}
