import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.1
import ape 1.0
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
        text: qsTr("Start APE")
        visible: !nodeHandler.running
        onClicked: nodeHandler.appaNode.start()
      }

      Button {
        text: qsTr("Stop APE")
        visible: nodeHandler.running
        onClicked: nodeHandler.appaNode.stop()
      }

      Button {
        text: qsTr("Start GUI")
        enabled: nodeHandler.running
      }
    }

    VerticalFiller {
    }
  }
}
