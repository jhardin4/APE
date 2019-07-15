import QtQuick 2.0
import QtQuick.Controls 1.4 as C1

C1.TableView {
  id: tableView

  C1.TableViewColumn {
    title: qsTr("Key")
    role: "key"
    width: tableView.width / 2
    resizable: true
  }

  C1.TableViewColumn {
    title: qsTr("Value")
    role: "value"
    width: tableView.width / 2 - 2
    resizable: true
  }
}
