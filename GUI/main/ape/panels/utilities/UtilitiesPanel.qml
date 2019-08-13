import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.1
import ape.core 1.0
import ape.controls 1.0
import ape.utilities 1.0
import Qt.labs.settings 1.0

Item {
  id: root

  MotionDevices {
    id: motionDevices
    appInterface: nodeHandler.appInterface
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: Style.singleMargin

    MotionControlPanel {
      id: motionControlPanel
      Layout.fillWidth: true
    }

    CameraControlPanel {
      id: cameraControlPanel
      Layout.fillWidth: true
      Layout.fillHeight: enabled
    }

    PlotPanel {
      id: plotPanel
      Layout.fillWidth: true
      Layout.fillHeight: enabled
    }

    Item {
      visible: !(cameraControlPanel.enabled || plotPanel.enabled)
      Layout.fillWidth: true
      Layout.fillHeight: true //!(cameraControlPanel.enabled || plotPanel.enabled)
    }
  }

  Settings {
    id: settings
    category: "utilities"
    property alias motionControlEnabled: motionControlPanel.checked
    property alias cameraControlEnabled: cameraControlPanel.checked
    property alias plotPanelEnabled: plotPanel.checked
  }
}
