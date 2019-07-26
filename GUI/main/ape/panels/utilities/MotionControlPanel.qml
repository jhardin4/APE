import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.1
import ape.controls 1.0
import ape.utilities 1.0

GroupBox {
  title: qsTr("Motion Control")
  id: root

  QtObject {
    id: d
    function move(device, axis, distance, speed) {
      var reqs = [{
                    "key": 'RelAbs',
                    "value": 'Rel'
                  }, {
                    "key": 'motionmode',
                    "value": "cmd"
                  }]
      nodeHandler.procInterface.do(device, 'Set_Motion', reqs)
      reqs = [{
                "key": "point",
                "value": {

                }
              }, {
                "key": "speed",
                "value": speed
              }, {
                "key": 'motionmode',
                "value": "cmd"
              }]
      reqs[0]["value"][axis] = distance
      nodeHandler.procInterface.do(device, 'Move', reqs)
      nodeHandler.appInterface.refreshProclog()
    }
  }

  ColumnLayout {
    anchors.fill: parent

    RowLayout {
      Label {
        text: qsTr("Device:")
      }
      ComboBox {
        id: deviceCombo
        Layout.fillWidth: true
        model: motionDevices.devices
      }

      Label {
        text: qsTr("Velocity:")
      }

      DoubleSpinBox {
        id: velocitySpin
        from: 0
        to: 999999
        value: 1000
        stepSize: 100
      }

      Label {
        text: qsTr("Step:")
      }

      ComboBox {
        id: stepSizeCombo
        model: [0.1, 1, 10, 100]
        currentIndex: 1
      }
    }

    RowLayout {
      enabled: deviceCombo.currentIndex > -1

      Repeater {
        model: ["X", "Y", "Z", "A", "B", "C"]

        ColumnLayout {
          Button {
            Layout.fillWidth: true
            text: modelData + "+"
            onClicked: {
              var device = deviceCombo.currentText
              d.move(device, modelData, Number(stepSizeCombo.currentText),
                     velocitySpin.realValue)
            }
          }

          Button {
            Layout.fillWidth: true
            text: modelData + "-"
            onClicked: {
              var device = deviceCombo.currentText
              d.move(device, modelData, -Number(stepSizeCombo.currentText),
                     velocitySpin.realValue)
            }
          }
        }
      }
    }
  }
}
