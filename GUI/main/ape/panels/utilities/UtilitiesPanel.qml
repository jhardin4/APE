import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.1
import ape.core 1.0
import ape.controls 1.0
import ape.utilities 1.0

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
      Layout.fillWidth: true
    }

    CameraControlPanel {
      Layout.fillWidth: true
    }

    VerticalFiller {
    }
  }
}
