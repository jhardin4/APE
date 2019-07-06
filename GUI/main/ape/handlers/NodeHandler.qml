import QtQuick 2.0
import ape.nodes 1.0

QtObject {
  id: root
  readonly property bool apeRunning: appaNode.running && procExecNode.running
  readonly property bool guiRunning: guiNode.running

  readonly property QtObject d: QtObject {
  }

  function startAPE() {
    launcher.start()
    appaNode.start()
    procExecNode.start()
  }

  function stopAPE() {
    stopGUI()
    appaNode.stop()
    procExecNode.stop()
    launcher.stop()
  }

  function startGUI() {
    guiNode.start()
  }

  function stopGUI() {
    guiNode.stop()
  }

  readonly property Launcher launcher: Launcher {
  }

  readonly property AppaNode appaNode: AppaNode {
    launcher: root.launcher
  }

  readonly property ProcExecNode procExecNode: ProcExecNode {
    launcher: root.launcher
  }

  readonly property GuiNode guiNode: GuiNode {
    launcher: root.launcher
  }
}
