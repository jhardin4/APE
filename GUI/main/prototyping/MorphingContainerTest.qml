import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Controls 1.4 as C1
import QtQuick.Layouts 1.3
import ape.controls 1.0

Item {
  id: root
  MorphingContainer {
    anchors.fill: parent

    Rectangle {
      Layout.fillWidth: true
      Layout.fillHeight: true
      color: "orange"
    }
    Rectangle {
      Layout.fillWidth: true
      Layout.fillHeight: true
      color: "blue"
    }
    Rectangle {
      Layout.fillWidth: true
      Layout.fillHeight: true
      color: "green"
    }
  }
}
