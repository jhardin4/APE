import QtQuick 2.9
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import QtQuick.Window 2.0
import Qt.labs.settings 1.0
import ape 1.0
import ape.handlers 1.0

ApplicationWindow {
  visible: true
  width: 640
  height: 480
  title: qsTr("APE")

  MainPanel {
    anchors.fill: parent
  }

  NodeHandler {
    id: nodeHandler
  }
}
