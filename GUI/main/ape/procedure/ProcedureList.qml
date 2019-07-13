import QtQuick 2.0

QtObject {
  id: root

  //  readonly property var procList: [{
  //      "name": "system_On",
  //      "requirements": [{
  //          "key": "foo",
  //          "value": "bar"
  //        }]
  //    }, {
  //      "name": "gantry_Run",
  //      "requirements": []
  //    }]
  property var procList: []

  function addProcedure(name, rawReqs) {
    var list = root.procList
    var reqs = []
    for (var i in rawReqs) {
      if (rawReqs[i].value !== "") {
        var newItem = JSON.parse(JSON.stringify(rawReqs[i]))
        delete newItem["modified"]
        reqs.push(newItem)
      }
    }
    list.push({
                "name": name,
                "requirements": reqs
              })
    root.procList = list
  }

  function updateRequirements(index, reqs) {
    if (index < 0 || index >= root.procList.length) {
      return
    }
    var list = root.procList
    list[index].requirements = reqs
    root.procList = list
  }

  function moveUp(index) {
    if (index <= 0 || index >= root.procList.length) {
      return
    }
    _swapItems(index - 1, index)
  }

  function moveDown(index) {
    if (index < 0 || index >= (root.procList.length - 1)) {
      return
    }
    _swapItems(index + 1, index)
  }

  function remove(index) {
    if (index < 0 || index >= root.procList.length) {
      return
    }
    var list = root.procList
    procList.splice(index, 1)
    root.procList = list
  }

  function _swapItems(index1, index2) {
    var list = procList
    var tmp = list[index1]
    list[index1] = list[index2]
    list[index2] = tmp
    root.procList = list
  }
}
