import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.1
import ape.controls 1.0

Item {
  id: root
  ColumnLayout {
    anchors.fill: parent

    VerticalFiller {
    }

    RowLayout {
      Layout.alignment: Qt.AlignHCenter

      Button {
        text: qsTr("Start GUI")
        visible: !nodeHandler.guiRunning

        onClicked: nodeHandler.startGUI()
      }

      Button {
        text: qsTr("Stop GUI")
        visible: nodeHandler.guiRunning

        onClicked: nodeHandler.stopGUI()
      }
    }

    VerticalFiller {
    }
  }
}
