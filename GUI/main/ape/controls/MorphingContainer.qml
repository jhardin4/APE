import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3

Item {
  id: root
  property int bigWidth: 1500
  property var titles: [qsTr("Apparatus"), qsTr("Procedure"), qsTr("Utilities")]
  property alias currentIndex: bar.currentIndex
  default property alias containerData: layout.data

  QtObject {
    id: d
    property bool big: root.width > root.bigWidth

    //onBigChanged: changeBig()
    function changeBig() {
      {
        if (big) {
          while (layout2.children.length > 0) {
            layout2.children[0].parent = layout
          }
        } else {
          while (layout.children.length > 0) {
            layout.children[0].parent = layout2
          }
          var previousIndex = bar.currentIndex
          bar.currentIndex = -1
          bar.currentIndex = previousIndex
        }
      }
    }
  }

  Component.onCompleted: d.changeBig()

  Item {
    id: container
    anchors.fill: parent
    visible: layout.children.length > 0

    RowLayout {
      id: layout
      anchors.fill: parent
    }
  }

  Item {
    id: container2
    anchors.fill: parent
    visible: layout2.children.length > 0

    RowLayout {
      id: topBar
      anchors.left: parent.left
      anchors.right: parent.right
      visible: nodeHandler.guiRunning

      TabBar {
        id: bar
        Layout.fillWidth: true

        Repeater {
          model: root.titles

          TabButton {
            text: modelData
          }
        }
      }
    }

    StackLayout {
      id: layout2
      anchors.top: topBar.bottom
      anchors.left: parent.left
      anchors.right: parent.right
      anchors.bottom: parent.bottom
      currentIndex: bar.currentIndex
    }
  }
}
