import QtQuick 2.0

Item {
  id: root

  Text {
    anchors.fill: parent
    text: styleData.value
    color: styleData.textColor
    elide: Text.ElideRight
  }
}
