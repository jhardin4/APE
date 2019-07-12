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

  ProcedureList {
    id: procList
  }

  ColumnLayout {
    anchors.fill: parent

    RowLayout {
      ProcedureTreeView {
        id: treeView
        Layout.fillWidth: true
        Layout.fillHeight: true
        model: procedureModel

        onSelectedProcedureChanged: {
          if (selectedProcedure.length > 0) {
            var device = treeView.selectedProcedure[0]
            var proc = treeView.selectedProcedure[1]
            var reqs = nodeHandler.appInterface.getRequirements(device, proc)
            procReqView.model = reqs
          } else {
            procReqView.model = []
          }
        }
      }

      ColumnLayout {
        Button {
          text: qsTr("Create")
          enabled: false
        }
        Button {
          text: qsTr("Add")
          enabled: treeView.selectedProcedure.length > 0
          onClicked: {
            procList.addProcedure(treeView.selectedProcedure.join('_'),
                                  procReqView.model)
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
          model = newModel
        }
      }
    }

    RowLayout {

      C1.TableView {
        id: tableView
        Layout.fillHeight: true
        Layout.fillWidth: true
        model: procList.procList

        C1.TableViewColumn {
          title: qsTr("Procedures")
          role: "name"
          width: tableView.width
        }
      }

      ColumnLayout {
        Button {
          text: qsTr("Remove")
          enabled: tableView.currentRow > -1
        }
        Button {
          text: qsTr("Move Up")
          enabled: tableView.currentRow > 0
          onClicked: procList.moveUp()
        }
        Button {
          text: qsTr("Move Down")
          enabled: (tableView.currentRow > -1)
                   && (tableView.currentRow < tableView.rowCount - 1)
          onClicked: procList.moveDown()
        }
      }

      RequirementsTableView {
        Layout.fillWidth: true
        Layout.fillHeight: true


        /* model: [{
            "key": "foo",
            "value": "bar"
          }, {
            "key": "asd",
            "value": "fasd"
          }]*/
        onValueUpdate: {
          var newModel = JSON.parse(JSON.stringify(model))
          newModel[row]["value"] = value
          model = newModel
        }

        model: (tableView.currentRow
                > -1) ? procList.procList[tableView.currentRow].requirements : []
      }
    }
  }
}
