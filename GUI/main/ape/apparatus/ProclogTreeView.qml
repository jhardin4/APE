import QtQuick 2.0
import QtQuick.Controls 1.4 as C1
import QtQuick.Controls 2.2
import ape.controls 1.0
import ape.core 1.0
import ape.apparatus 1.0

ApeTreeView {
  id: root
  autoExpand: true

  C1.TableViewColumn {
    title: qsTr("Name")
    role: "name"
    width: root.width / 2 - 50
    resizable: true
  }

  C1.TableViewColumn {
    title: qsTr("ID")
    role: "id"
    width: 40
    resizable: true
  }

  C1.TableViewColumn {
    title: qsTr("Info")
    role: "value"
    width: root.width / 2 - 3
    resizable: true
    delegate: ValueItemDelegate {
      table: root
      editRole: AppImageTreeModel.ValueRole
    }
  }
}
