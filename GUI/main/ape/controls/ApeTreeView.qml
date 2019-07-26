import QtQuick 2.0
import QtQuick.Controls 1.4 as C1
import QtQuick.Controls 2.2
import QtQml.Models 2.3
import ape.controls 1.0
import ape.core 1.0
import ape.apparatus 1.0

C1.TreeView {
  id: root
  property bool autoExpand: true
  property var currentIndex: selection.currentIndex

  selectionMode: C1.SelectionMode.SingleSelection
  headerVisible: true
  backgroundVisible: false

  selection: ItemSelectionModel {
    model: root.model
  }

  function clearSelection() {
    selection.clear()
  }

  QtObject {
    id: d

    function expandAll() {
      /* NOTE: need to use internal modelAdapter, since index returned by external API seems to broken */
      var modelAdapter = root.__model
      for (var i = 0; i < modelAdapter.rowCount(); i++) {
        var index = modelAdapter.mapRowToModelIndex(i)
        modelAdapter.expand(index)
      }
    }
  }

  Connections {
    target: root.model
    ignoreUnknownSignals: true

    onModelReset: {
      if (root.autoExpand) {
        delayTimer.start()
      }
    }
  }

  Component.onCompleted: {
    if (root.autoExpand) {
      delayTimer.start()
    }
  }

  Timer {
    /* need to use this timer to make expanding work */
    id: delayTimer
    interval: 10
    repeat: false
    onTriggered: d.expandAll()
  }
}
