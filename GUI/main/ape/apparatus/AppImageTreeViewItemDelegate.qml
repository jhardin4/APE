import QtQuick 2.0

Item {
  id: root

  Row {
    anchors.fill: parent
    //spacing
    Text {
      text: styleData.value
      elide: styleData.elideMode
    }
  }
}
