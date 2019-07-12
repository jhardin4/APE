import QtQuick 2.0
import QtQuick.Controls 1.4 as C1

C1.TableView {
  id: root

  C1.TableViewColumn {
    title: qsTr("Requirement")
    role: "key"
    width: root.width / 2
    resizable: true
  }

  C1.TableViewColumn {
    title: qsTr("Value")
    role: "value"
    width: root.width / 2
    resizable: true
  }
}
