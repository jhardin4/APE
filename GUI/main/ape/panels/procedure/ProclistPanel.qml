import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Controls 1.4 as C1
import QtQuick.Layouts 1.3
import ape.core 1.0
import ape.controls 1.0
import ape.procedure 1.0

GroupBox {
  property alias proclistView: tableView
  title: qsTr("Proclist")

  ImportExportDialog {
    id: importExportDialog
  }

  RowLayout {
    anchors.fill: parent

    ColumnLayout {

      C1.TableView {
        id: tableView
        Layout.fillHeight: true
        Layout.fillWidth: true
        model: nodeHandler.procInterface.proclist

        function selectRow(row) {
          selection.clear()
          selection.select(row)
          currentRow = row
        }

        C1.TableViewColumn {
          title: qsTr("Procedures")
          role: "name"
          width: tableView.width - 2
        }
      }

      RowLayout {
        Button {
          text: qsTr("Execute")
          Layout.fillWidth: true
          enabled: tableView.currentRow > -1
          onClicked: {
            nodeHandler.procInterface.doProcedure(tableView.currentRow)
            nodeHandler.appInterface.refreshProclog()
          }
        }

        Button {
          text: qsTr("Execute All")
          Layout.fillWidth: true
          enabled: tableView.rowCount > 0
          onClicked: {
            nodeHandler.procInterface.doProclist()
            nodeHandler.appInterface.refreshProclog()
          }
        }
      }
    }

    ColumnLayout {
      Button {
        text: qsTr("Move Up")
        enabled: tableView.currentRow > 0
        onClicked: {
          var row = tableView.currentRow
          nodeHandler.procInterface.moveProcedureUp(row)
          nodeHandler.procInterface.refreshProclist()
          tableView.selectRow(row - 1)
        }
      }

      Button {
        text: qsTr("Move Down")
        enabled: (tableView.currentRow > -1)
                 && (tableView.currentRow < tableView.rowCount - 1)
        onClicked: {
          var row = tableView.currentRow
          nodeHandler.procInterface.moveProcedureDown(row)
          nodeHandler.procInterface.refreshProclist()
          tableView.selectRow(row + 1)
        }
      }

      Item {
        height: Style.singleSpacing
      }

      Button {
        text: qsTr("Remove")
        enabled: tableView.currentRow > -1
        onClicked: {
          nodeHandler.procInterface.removeProcedure(tableView.currentRow)
          nodeHandler.procInterface.refreshProclist()
        }
      }

      Button {
        text: qsTr("Clear")
        enabled: tableView.rowCount > 0
        onClicked: {
          nodeHandler.procInterface.clearProclist()
          nodeHandler.procInterface.refreshProclist()
        }
      }

      Item {
        height: Style.singleSpacing
      }

      Button {
        text: qsTr("Export...")
        onClicked: {
          importExportDialog.openMode = false
          importExportDialog.open()
        }
      }

      Button {
        text: qsTr("Import...")
        onClicked: {
          importExportDialog.openMode = true
          importExportDialog.open()
        }
      }
    }

    RequirementsTableView {
      id: reqTableView
      Layout.fillWidth: true
      Layout.fillHeight: true

      onValueUpdate: {
        var tableRow = tableView.currentRow
        var reqs = reqTableView.model
        reqs[row]["value"] = value
        nodeHandler.procInterface.updateProcedure(tableView.currentRow, reqs)
        nodeHandler.procInterface.refreshProclist()
        tableView.selectRow(tableRow)
      }

      model: (tableView.currentRow > -1) ? getModel(
                                             tableView.model[tableView.currentRow]) : []
      function getModel(base) {
        // extend requirements with additional default requirements
        var reqs = nodeHandler.procInterface.getRequirements(base["device"],
                                                             base["procedure"])
        var base_reqs = base["requirements"]
        for (var i = 0; i < base_reqs.length; ++i) {
          var found = false
          for (var j = 0; j < reqs.length; ++j) {
            if (reqs[j]["key"] == base_reqs[i]["key"]) {
              reqs[j]["value"] = base_reqs[i]["value"]
              found = true
              break
            }
          }
          if (!found) {
            reqs.push(base_reqs[i])
          }
        }
        return reqs
      }
    }
  }
}
