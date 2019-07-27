import QtQuick 2.0

Item {
  default property alias data_: container.data
  property double referenceWidth: 1920
  property int contentWidth: 0
  property int contentHeight: 0
  property double scale: 1.0

  property double minAspectRatio: 16 / 10
  property double maxAspectRatio: 16 / 9

  id: root

  onWidthChanged: d.calculateContentSize()
  onHeightChanged: d.calculateContentSize()

  QtObject {
    id: d

    function calculateContentSize() {
      var aspectRatio = width / height
      var realWidth = width
      var realHeight = height
      if (aspectRatio > maxAspectRatio) {
        realWidth = height * maxAspectRatio
      } else if (aspectRatio < minAspectRatio) {
        realHeight = width / minAspectRatio
      }

      root.scale = realWidth / referenceWidth
      root.contentWidth = realWidth / scale
      root.contentHeight = realHeight / scale
    }
  }

  Item {
    id: container
    width: root.contentWidth
    height: root.contentHeight
    anchors.centerIn: root
    scale: root.scale
  }
}
