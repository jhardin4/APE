import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3

GroupBox {
  title: qsTr("Find and Replace")
  GridLayout {
    anchors.fill: parent
    columns: 2

    Label {
      text: qsTr("Find")
    }

    Label {
      text: qsTr("Replace")
    }

    TextField {
      id: findTextField
      Layout.fillWidth: true
      selectByMouse: true
    }

    TextField {
      Layout.fillWidth: true
      id: replaceTextField
    }

    Button {
      Layout.columnSpan: 2
      Layout.fillWidth: true
      enabled: findTextField.text && replaceTextField.text
      text: qsTr("Execute")
      onClicked: {
        appInterface.findAndReplace(findTextField.text, replaceTextField.text)
        findTextField.text = ""
        replaceTextField.text = ""
      }
    }
  }
}
