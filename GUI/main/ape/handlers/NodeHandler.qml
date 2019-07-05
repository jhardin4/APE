import QtQuick 2.0
import ape.nodes 1.0

QtObject {
  id: root
  property bool running: appaNode.running

  readonly property QtObject d: QtObject {
  }

  readonly property Launcher launcher: Launcher {

    Component.onCompleted: start()
    Component.onDestruction: stop()
  }

  readonly property AppaNode appaNode: AppaNode {
    launcher: root.launcher
  }
}
