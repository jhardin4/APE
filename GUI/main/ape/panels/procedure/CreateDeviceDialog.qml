import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2
import ape.core 1.0
import ape.controls 1.0
import ape.procedure 1.0

Dialog {
  id: root
  title: qsTr("Create new Device")
  property alias name: nameInput.text
  property alias type: typeCombo.currentText
  property alias requirements: reqTableView.model

  onVisibleChanged: {
    if (visible) {
      nameInput.text = ""
      nameInput.forceActiveFocus()
    }
  }

  ApeDevices {
    id: apeDevices
  }

  contentItem: Rectangle {
    implicitWidth: container.width + Style.doubleMargin
    implicitHeight: container.height + Style.doubleMargin

    ColumnLayout {
      id: container
      x: Style.singleMargin
      y: Style.singleMargin

      GridLayout {
        columns: 2

        Label {
          text: qsTr("Name:")
        }

        TextField {
          id: nameInput
          Layout.fillWidth: true
          Layout.preferredWidth: 400
          selectByMouse: true
          validator: RegExpValidator {
            regExp: /[A-Za-z_][0-9A-Za-z_]*/
          }
        }

        Label {
          text: qsTr("Type:")
        }

        ComboBox {
          id: typeCombo
          Layout.fillWidth: true
          model: apeDevices.devices

          onCurrentTextChanged: {
            console.log(currentText)
            var reqs = nodeHandler.procInterface.getDeviceRequirements(
                  currentText)
            reqTableView.model = reqs
          }
        }
      }

      RequirementsTableView {
        id: reqTableView
        Layout.fillHeight: true
        Layout.fillWidth: true
        Layout.preferredHeight: 400

        onValueUpdate: {
          var newModel = JSON.parse(JSON.stringify(model))
          newModel[row]["value"] = value
          newModel[row]["modified"] = true
          model = newModel
        }
      }

      RowLayout {
        HorizontalFiller {
        }
        Button {
          id: okButton
          text: qsTr("Ok")
          enabled: nameInput.text !== ""
          onClicked: root.accept()
        }
        Button {
          text: qsTr("Cancel")
          onClicked: root.close()
        }
      }
    }
  }
}
