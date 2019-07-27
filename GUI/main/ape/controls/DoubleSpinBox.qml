import QtQuick 2.0
import QtQuick.Controls 2.2

SpinBox {
  id: spinbox
  from: 0.0
  to: 9999
  value: 1000
  stepSize: 100
  editable: true
  property int decimals: 1
  property real realValue: value / 100

  validator: DoubleValidator {
    bottom: Math.min(spinbox.from, spinbox.to)
    top: Math.max(spinbox.from, spinbox.to)
  }

  textFromValue: function (value, locale) {
    return Number(value / 100).toLocaleString(locale, 'f', spinbox.decimals)
  }

  valueFromText: function (text, locale) {
    return Number.fromLocaleString(locale, text) * 100
  }
}
