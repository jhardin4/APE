import QtQuick 2.2
import QtQuick.Controls 1.4 as C1
import ape.core 1.0

C1.TableView {
  id: root

  selectionMode: C1.SelectionMode.SingleSelection

  signal valueUpdate(int row, string key, string value)

  QtObject {
    id: d

    function selectRow(row) {
      root.selection.clear()
      root.selection.select(row)
    }
  }

  C1.TableViewColumn {
    title: qsTr("Requirement")
    role: "key"
    width: root.width / 2
    resizable: true
  }

  C1.TableViewColumn {
    title: qsTr("Value")
    role: "value"
    width: root.width / 2 - 2
    resizable: true

    delegate: Item {
      property bool editing: false

      MouseArea {
        anchors.fill: parent
        visible: !editing
        onClicked: d.selectRow(styleData.row)
        onDoubleClicked: {
          d.selectRow(styleData.row)
          editing = true
        }
      }

      Text {
        anchors.fill: parent
        anchors.leftMargin: Style.singleMargin
        verticalAlignment: Text.AlignVCenter
        text: String(styleData.value)
        elide: styleData.elideMode
        visible: !editing
        color: styleData.textColor
      }

      TextInput {
        anchors.fill: parent
        anchors.leftMargin: Style.singleMargin
        verticalAlignment: Text.AlignVCenter
        text: String(styleData.value)
        selectByMouse: true
        visible: editing
        color: "red"

        onEditingFinished: {
          editing = false
          var key = root.model[styleData.row]["key"]
          root.valueUpdate(styleData.row, key, text)
        }

        onVisibleChanged: {
          if (visible) {
            selectAll()
            forceActiveFocus()
          }
        }
      }
    }
  }
}
