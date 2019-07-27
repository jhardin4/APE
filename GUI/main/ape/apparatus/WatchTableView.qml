import QtQuick 2.0
import QtQuick.Controls 1.4 as C1
import ape.apparatus 1.0

C1.TableView {
  id: root
  property var editingIndex: null
  readonly property bool editing: editingIndex !== null

  onDoubleClicked: {
    var index = model.index(row, 0)
    if (model.flags(index) & Qt.ItemIsEditable) {
      root.editingIndex = index
    }
  }

  C1.TableViewColumn {
    title: qsTr("Key")
    role: "key"
    width: root.width / 2
    resizable: true
  }

  C1.TableViewColumn {
    title: qsTr("Value")
    role: "value"
    width: root.width / 2 - 2
    resizable: true
    delegate: ValueItemDelegate {
      table: root
      editRole: WatchlistModel.ValueRole
    }
  }
}
