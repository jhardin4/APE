import QtQuick 2.0
import ape.nodes 1.0

QtObject {
  id: root
  readonly property bool guiRunning: guiNode.running

  readonly property QtObject d: QtObject {
  }

  function startGUI() {
    guiNode.start()
  }

  function stopGUI() {
    guiNode.stop()
  }

  readonly property GuiNode guiNode: GuiNode {
    l2gAddress: "tcp://127.0.0.1:5577"
    a2gAddress: "tcp://127.0.0.1:5579"
    g2peAddress: "tcp://127.0.0.1:5580"

    Component.onCompleted: startGUI()
  }
}
