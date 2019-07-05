import QtQuick 2.0
import pathpilot.core 1.0

Rectangle {
  property bool vertical: false
  id: root
  height: vertical ? 50 : 1
  width: vertical ? 1 : 200
  color: Colors.gray1
}
