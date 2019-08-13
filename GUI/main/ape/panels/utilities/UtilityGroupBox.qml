import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.1

GroupBox {
  id: root
  property bool ready
  readonly property bool enabled: checked && ready
  property alias checked: enabledCheck.checked
  Layout.preferredHeight: enabled ? -1 : enabledCheck.height

  label: CheckBox {
    id: enabledCheck
    enabled: root.ready
    checked: true
    width: root.availableWidth
    text: root.title
  }
}
