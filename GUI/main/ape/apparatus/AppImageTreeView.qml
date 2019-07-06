import QtQuick 2.0
import QtQuick.Controls 1.4 as C1

C1.TreeView {
  id: root

  selectionMode: C1.SelectionMode.SingleSelection
  headerVisible: false
  backgroundVisible: false


  /*rowDelegate: Rectange {
    height: 25
    color: "white"
  }*/
  itemDelegate: AppImageTreeViewItemDelegate {
  }

  C1.TableViewColumn {
    title: qsTr("Items")
    role: "name"
    width: root.width - 5
    resizable: false
  }
}
