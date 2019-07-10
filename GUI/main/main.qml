import QtQuick 2.9
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import QtQuick.Window 2.0
import Qt.labs.settings 1.0
import ape 1.0
import ape.handlers 1.0
import ape.screens 1.0

ApplicationWindow {
  id: root
  visible: true
  width: 640
  height: 480
  title: qsTr("APE GUI")

  Component.onCompleted: {
    for (var i = 0; i < Qt.application.screens.length; ++i) {
      var screen = Qt.application.screens[i]
      if (screen.serialNumber === windowSettings.screen) {
        root.screen = screen
        return
      }
    }
  }

  QtObject {
    id: d
    function prepareClose() {
      nodeHandler.stopGUI()
      windowSettings.screen = String(root.screen.serialNumber)
    }
  }

  onClosing: d.prepareClose()

  Connections {
    target: appHelper
    onAboutToQuit: d.prepareClose()
  }

  MainScreen {
    anchors.fill: parent
  }

  Settings {
    id: windowSettings
    category: "window"
    property alias width: root.width
    property alias height: root.height
    property alias x: root.x
    property alias y: root.y
    property string screen: ""
  }

  NodeHandler {
    id: nodeHandler
  }
}
