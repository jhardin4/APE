import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Controls 1.4 as C1
import QtQuick.Layouts 1.3
import ape.core 1.0
import ape.controls 1.0
import ape.procedure 1.0

Item {
  id: root

  ProcedureModel {
    id: procedureModel
    appInterface: nodeHandler.appInterface
  }

  RowLayout {
    anchors.fill: parent

    ColumnLayout {
      ProcedureTreeView {
        id: treeView
        Layout.fillWidth: true
        Layout.fillHeight: true
        model: procedureModel
      }
    }
  }
}
