import QtQuick 2.0
pragma Singleton

QtObject {
  id: root

  readonly property color white1: "white"

  //readonly property string font1: bebas.name

  //   readonly property FontLoader bebas: FontLoader {
  //    source: ResourcePaths.fontPath + "/Bebas.ttf"
  //  }


  /*readonly property QtObject controls: QtObject {
    readonly property int button1: scaleFont(18)
    readonly property int toggleButton1: scaleFont(11)
    readonly property int label1: scaleFont(18)
    readonly property int textField1: scaleFont(20)
    readonly property int tabButton1: scaleFont(12)
    readonly property int slider1: scaleFont(20)
    readonly property int radioButton1: scaleFont(18)
    readonly property int tableView: scaleFont(14)
  }*/
  function dp(size) {
    return ~~(size * 1.0)
  }


  /*readonly property QtObject general: QtObject {
    readonly property string background: getJpgIcon("splashscreen",
                                                    "dark_background")
  }*/
  function getPngIcon(category, name) {
    return ResourcePaths.iconPath + "/" + category + "/png/" + name + ".png"
  }

  function getJpgIcon(category, name) {
    return ResourcePaths.iconPath + "/" + category + "/jpg/" + name + ".jpg"
  }

  function getSvgIcon(category, name) {
    return ResourcePaths.iconPath + "/" + category + "/svg/" + name + ".svgz"
  }

  readonly property int halfMargin: 3
  readonly property int singleMargin: 5
  readonly property int doubleMargin: 10

  readonly property int singleSpacing: 5
  readonly property int doubleSpacing: 10

  readonly property int thinBorder: 1
  readonly property int thickBorder: 2

  readonly property int smallRadius: 2
  readonly property int bigRadius: 5
}
