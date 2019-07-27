import QtQuick 2.0
import pathpilot.core 1.0

Item {
  property var icon: IconObject {
  }
  property alias image: image
  id: root
  implicitWidth: image.width
  implicitHeight: image.height

  Image {
    id: image
    source: icon.source
    sourceSize: icon.size
    width: icon.size.width
    height: icon.size.height
  }
}
