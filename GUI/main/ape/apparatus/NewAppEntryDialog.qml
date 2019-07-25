import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.2
import QtQuick.Dialogs 1.2
import ape.core 1.0
import ape.controls 1.0

Dialog {
  id: newEntryDialog
  readonly property string key: baseText + "/" + text
  property alias text: nameInput.text
  property string baseText: ""

  onVisibleChanged: {
    if (visible) {
      nameInput.text = ""
      nameInput.forceActiveFocus()
    }
  }

  title: qsTr("Add new App Entry")
  contentItem: Rectangle {
    implicitWidth: container.width + Style.doubleMargin
    implicitHeight: container.height + Style.doubleMargin

    ColumnLayout {
      id: container
      x: Style.singleMargin
      y: Style.singleMargin

      GridLayout {
        columns: 2
        Text {
          Layout.fillWidth: true
          text: qsTr("To:")
        }
        Text {
          Layout.fillWidth: true
          text: newEntryDialog.baseText
        }

        Text {
          text: qsTr("Name:")
        }
        TextField {
          id: nameInput
          Layout.fillWidth: true
          Layout.preferredWidth: 400
          selectByMouse: true
          validator: RegExpValidator {
            regExp: /([0-9A-Za-z_]\/?)+/
          }

          Keys.onReturnPressed: okButton.clicked()
        }
      }

      RowLayout {
        HorizontalFiller {
        }
        Button {
          id: okButton
          text: qsTr("Ok")
          enabled: nameInput.text !== ""
          onClicked: newEntryDialog.accept()
        }
        Button {
          text: qsTr("Cancel")
          onClicked: newEntryDialog.close()
        }
      }
    }
  }
}
