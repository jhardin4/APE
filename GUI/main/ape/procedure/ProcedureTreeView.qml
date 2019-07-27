import QtQuick 2.0
import QtQuick.Controls 1.4 as C1
import ape.controls 1.0
import ape.procedure 1.0

ApeTreeView {
  id: root

  property var selectedProcedure: []
  autoExpand: false

  onCurrentIndexChanged: root.selectedProcedure = model.getProcedureName(
                           currentIndex)

  C1.TableViewColumn {
    title: qsTr("Procedure")
    role: "display"
    width: root.width - 20
    resizable: false
  }
}
