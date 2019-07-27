import QtQuick 2.0
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.1
import ape.base 1.0
import ape.controls 1.0
import ape.utilities 1.0

GroupBox {
  title: qsTr("Plot")
  id: root
  property bool ready: plot.toolpaths.length > 0
  visible: ready

  ToolPathPlot {
    id: plot

    appInterface: nodeHandler.appInterface
  }

  ColumnLayout {
    anchors.fill: parent
    Image {
      id: plotImage
      Layout.fillWidth: true
      Layout.fillHeight: true
    }

    RowLayout {
      Layout.alignment: Qt.AlignHCenter
      Button {
        text: qsTr("Plot")
        enabled: root.ready
        onClicked: {
          nodeHandler.procInterface.do("", "Toolpath_Plot", [{
                                                               "key": "newfigure",
                                                               "value": true
                                                             }])
          var imagePath = nodeHandler.appInterface.getValue(
                "information/ProcedureData/Toolpath_Plot/image_file_name")
          plotImage.source = ResourcePaths.rootPath + "/" + imagePath
        }
      }
    }
  }
}
