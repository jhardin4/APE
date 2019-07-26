import QtQuick 2.2
import QtQuick.Controls 1.4 as C1
import ape.core 1.00

C1.TableView {
  id: root

  property var selectedProcedure: []

  onCurrentRowChanged: {
    if (currentRow < 0) {
      return
    }

    var data = root.model[currentRow]
    selectedProcedure = [data["device"], data["procedure"]]
  }

  function selectRow(row) {
    selection.clear()
    selection.select(row)
    currentRow = row
  }

  function clearSelection() {
    selection.clear()
    currentRow = -1
  }

  C1.TableViewColumn {
    title: qsTr("Procedures")
    role: "name"
    width: root.width - 2
  }
}
