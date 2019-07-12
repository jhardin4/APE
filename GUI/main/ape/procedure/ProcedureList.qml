import QtQuick 2.0

QtObject {
  id: root

  property var procList: []

  function addProcedure(name, rawReqs) {
    var list = procList
    var reqs = []
    for (var i in rawReqs) {
      if (rawReqs[i].value !== "") {
        reqs.push(rawReqs[i])
      }
    }
    list.push({
                "name": name,
                "requirements": reqs
              })
    procList = list
  }

  function moveUp(index) {}
  function moveDown(index) {}
}
