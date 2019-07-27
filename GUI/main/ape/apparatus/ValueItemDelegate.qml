import QtQuick 2.2
import QtQuick.Controls 2.0
import ape.core 1.0

Item {
  id: root
  property var index: styleData.index ? styleData.index : table.model.index(
                                          styleData.row, 0)
  property bool editing: table.editingIndex === index
  property bool modified
  property Item table: null
  property int editRole: Qt.EditRole
  property bool isGroupNode: index.valid ? table.model.flags(
                                             index) & Qt.ItemIsTristate : false

  Text {
    anchors.fill: parent
    anchors.leftMargin: Style.singleMargin
    verticalAlignment: Text.AlignVCenter
    text: textInput.text
    color: root.isGroupNode ? "gray" : styleData.textColor
    elide: Text.ElideRight
    visible: !root.editing
  }

  TextInput {
    id: textInput
    property bool running: false
    anchors.fill: parent
    anchors.leftMargin: Style.singleMargin
    verticalAlignment: Text.AlignVCenter
    text: root.isGroupNode ? "+" : String(styleData.value)
    selectByMouse: true
    visible: root.editing
    enabled: visible
    color: Style.blue1

    onEditingFinished: {
      if (!running) {
        return
      }
      root.index.model.setData(root.index, text, root.editRole)
      running = false
      root.table.editingIndex = null
      text = Qt.binding(function () {
        return String(styleData.value) // restore binding when completed
      })
    }

    onVisibleChanged: {
      if (visible) {
        text = text // break binding while editing
        forceActiveFocus()
        selectAll()
        running = true
      }
    }
  }
}
