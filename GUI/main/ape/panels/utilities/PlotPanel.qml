import QtQuick 2.3
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.1
import ape.base 1.0
import ape.controls 1.0
import ape.utilities 1.0

UtilityGroupBox {
  id: root
  title: qsTr("Plot")
  ready: plot.toolpaths.length > 0

  ToolPathPlot {
    id: plot

    appInterface: nodeHandler.appInterface
  }

  ColumnLayout {
    anchors.fill: parent
    visible: root.enabled

    Image {
      id: plotImage
      Layout.fillWidth: true
      Layout.fillHeight: true
      fillMode: Image.PreserveAspectFit
      smooth: true
      mipmap: true
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
