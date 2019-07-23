import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Controls 1.4 as C1
import QtQuick.Layouts 1.3
import ape.core 1.0
import ape.controls 1.0
import ape.procedure 1.0

Item {
  id: root
  Layout.fillWidth: true
  Layout.fillHeight: true

  ProcedureModel {
    id: procedureModel
    procInterface: nodeHandler.procInterface
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: Style.singleMargin

    AvailableProcsPanel {
      Layout.fillWidth: true
      Layout.fillHeight: true
      proclistView: proclistPanel.proclistView
    }

    ProclistPanel {
      id: proclistPanel
      Layout.fillWidth: true
      Layout.fillHeight: true
    }
  }
}
