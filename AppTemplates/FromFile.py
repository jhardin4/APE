import json


def FromFile(apparatus, filename):
    with open(filename, 'r') as oldApp:
        oldAppData = json.load(oldApp)
    # Clear the proclog
    apparatus.proglog = []
    apparatus['proclog'] = apparatus.proglog
    # Replace the current device and information
    apparatus['devices'] = oldAppData['devices']
    apparatus['information'] = oldAppData['information']
