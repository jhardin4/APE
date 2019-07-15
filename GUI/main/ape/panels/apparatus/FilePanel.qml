import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3

GroupBox {
  title: qsTr("File")

  RowLayout {
    anchors.fill: parent

    Text {
      text: qsTr("Path:")
    }
    TextField {
      Layout.fillWidth: true
    }
    Button {
      Layout.fillWidth: false
      text: "..."
    }
    Button {
      text: qsTr("Export")
    }
  }
}
