import QtQuick 2.0
import ape.nodes 1.0
import ape.apparatus 1.0
import ape.procedure 1.0

QtObject {
  id: root
  readonly property bool guiRunning: guiNode.running

  signal appEntryValueCopied(string value)

  function startGUI() {
    guiNode.start()
  }

  function stopGUI() {
    guiNode.stop()
  }

  function refreshAll() {
    appInterface.refreshAppImage()
    appInterface.refreshProclog()
    procInterface.refreshEprocs()
    procInterface.refreshProcedures()
    procInterface.refreshProclist()
  }

  readonly property GuiNode guiNode: GuiNode {
    l2gAddress: "tcp://127.0.0.1:5577"
    a2gAddress: "tcp://127.0.0.1:5579"
    g2peAddress: "tcp://127.0.0.1:5580"

    Component.onCompleted: startGUI()

    onRunningChanged: {
      if (running) {
        refreshAll()
      }
    }
  }

  readonly property AppInterface appInterface: AppInterface {
    id: appInterface
    guiNode: root.guiNode
  }

  readonly property ProcedureInterface procInterface: ProcedureInterface {
    id: procedureInterface
    guiNode: root.guiNode
  }
}
