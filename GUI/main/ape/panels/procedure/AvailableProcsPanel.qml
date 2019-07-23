import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Controls 1.4 as C1
import QtQuick.Layouts 1.3
import ape.core 1.0
import ape.controls 1.0
import ape.procedure 1.0

GroupBox {
  property Item proclistView: null

  title: qsTr("Procedures")

  RowLayout {
    anchors.fill: parent

    ProcedureTreeView {
      id: treeView
      Layout.fillWidth: true
      Layout.fillHeight: true
      model: procedureModel

      onSelectedProcedureChanged: {
        if (selectedProcedure.length > 0) {
          var device = treeView.selectedProcedure[0]
          var proc = treeView.selectedProcedure[1]
          var reqs = nodeHandler.procInterface.getRequirements(device, proc)
          procReqView.model = reqs
        } else {
          procReqView.model = []
        }
      }
    }

    ColumnLayout {
      Button {
        text: qsTr("Add")
        enabled: treeView.selectedProcedure.length > 0
        onClicked: {
          var row = proclistView.currentRow
          nodeHandler.procInterface.addProcedure(treeView.selectedProcedure[0],
                                                 treeView.selectedProcedure[1],
                                                 procReqView.model)
          nodeHandler.procInterface.refreshProclist()
          proclistView.selectRow(row)
        }
      }

      Button {
        text: qsTr("Run")
        enabled: treeView.selectedProcedure.length > 0
        onClicked: {
          nodeHandler.procInterface.do(treeView.selectedProcedure[0],
                                       treeView.selectedProcedure[1], {

                                       })
          nodeHandler.appInterface.refreshProclog()
        }
      }
    }

    RequirementsTableView {
      id: procReqView
      Layout.fillHeight: true
      Layout.fillWidth: true

      onValueUpdate: {
        var newModel = JSON.parse(JSON.stringify(model))
        newModel[row]["value"] = value
        newModel[row]["modified"] = true
        model = newModel
      }
    }
  }
}
