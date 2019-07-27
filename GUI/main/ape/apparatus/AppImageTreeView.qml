import QtQuick 2.0
import QtQuick.Controls 1.4 as C1
import QtQuick.Controls 2.2
import ape.controls 1.0
import ape.core 1.0
import ape.apparatus 1.0

ApeTreeView {
  id: root
  property var editingIndex: null
  autoExpand: false

  onDoubleClicked: {
    if (model.flags(index) & Qt.ItemIsEditable) {
      root.editingIndex = index
    } else if (model.flags(index) & Qt.ItemIsTristate) {
      d.prepareNewEntry()
    }
  }

  QtObject {
    id: d

    function prepareNewEntry() {
      newEntryDialog.baseText = root.model.data(root.currentIndex,
                                                AppImageTreeModel.KeyRole)
      newEntryDialog.open()
    }

    function addNewEntry() {
      nodeHandler.appInterface.createAppEntry(newEntryDialog.key)
      nodeHandler.appInterface.refreshAppImage()
    }

    function removeEntry() {
      var key = root.model.data(root.currentIndex, AppImageTreeModel.KeyRole)
      nodeHandler.appInterface.removeAppEntry(key)
      nodeHandler.appInterface.refreshAppImage()
    }

    function copyValue() {
      var value = root.model.data(root.currentIndex,
                                  AppImageTreeModel.ValueRole)
      nodeHandler.appEntryValueCopied(value)
    }

    function copyName() {
      var name = root.model.data(root.currentIndex, AppImageTreeModel.NameRole)
      nodeHandler.appEntryValueCopied(name)
    }

    function copyReference() {
      var ref = root.model.data(root.currentIndex, AppImageTreeModel.KeyRole)
      nodeHandler.appEntryValueCopied("@" + ref)
    }
  }

  itemDelegate: Item {
    height: 20
    Text {
      anchors.fill: parent
      anchors.leftMargin: Style.singleMargin
      verticalAlignment: Text.AlignVCenter
      text: styleData.value
      color: styleData.textColor
      elide: Text.ElideRight
    }
  }

  MouseArea {
    anchors.fill: parent
    acceptedButtons: Qt.RightButton
    onClicked: {
      editMenu.open()
      editMenu.x = mouse.x
      editMenu.y = mouse.y
      mouse.accepted = false
    }
  }

  Menu {
    id: editMenu
    MenuItem {
      text: qsTr("Add New Entry")
      enabled: root.currentIndex.valid ? root.model.flags(
                                           root.currentIndex) & Qt.ItemIsTristate : false
      onClicked: d.prepareNewEntry()
    }

    MenuItem {
      text: qsTr("Remove Entry")
      enabled: root.currentIndex.valid ? root.currentIndex.parent.valid : false
      onClicked: d.removeEntry()
    }

    MenuItem {
      text: qsTr("Copy Value to Requirements")
      enabled: root.currentIndex.valid ? root.model.flags(
                                           root.currentIndex) & Qt.ItemIsEditable : false
      onClicked: d.copyValue()
    }

    MenuItem {
      text: qsTr("Copy Reference to Requirements")
      enabled: Boolean(root.currentIndex.valid)
      onClicked: d.copyReference()
    }

    MenuItem {
      text: qsTr("Copy Name to Requirements")
      enabled: Boolean(root.currentIndex.valid)
      onClicked: d.copyName()
    }
  }

  NewAppEntryDialog {
    id: newEntryDialog
    onAccepted: d.addNewEntry(key)
  }

  C1.TableViewColumn {
    title: qsTr("Key")
    role: "name"
    width: root.width / 2 - 50
    resizable: true
  }

  C1.TableViewColumn {
    title: qsTr("Value")
    role: "value"
    width: root.width / 2 - 3
    resizable: true
    delegate: ValueItemDelegate {
      table: root
      editRole: AppImageTreeModel.ValueRole
    }
  }

  C1.TableViewColumn {
    title: qsTr("Watch")
    role: "watch"
    width: 50
    resizable: false

    delegate: Item {
      property QtObject model: styleData.index.model

      C1.CheckBox {
        visible: model ? model.flags(
                           styleData.index) & Qt.ItemIsEditable : false
        anchors.centerIn: parent
        checked: styleData.value
        onClicked: model.setData(styleData.index, checked,
                                 AppImageTreeModel.WatchRole)
      }
    }
  }
}
