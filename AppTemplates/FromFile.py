import json


def FromFile(apparatus, filename):
    with open(filename, 'r') as oldApp:
        oldAppData = json.load(oldApp)
    # Clear the proclog
    apparatus.proclog = []
    apparatus['proclog'] = apparatus.proclog
    # Replace the current device and information
    apparatus['devices'] = oldAppData['devices']
    apparatus['information'] = oldAppData['information']
