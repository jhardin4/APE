from Core import material

SE1700 = material()
SE1700.add_property('density', 1.1, 'g/cc')
SE1700['names'] = ['SE1700', 'PDMS', 'silicone']
SE1700['descriptors'] = ['adhesive', 'thermoset', 'thermal cure']

partA = material()
partA['names'] = ['SE1700 part A', 'SE1700', 'PDMS', 'silicone']

partB = material()
partB['names'] = ['SE1700 part B', 'SE1700', 'PDMS', 'silicone']

SE1700.add_comp(partA, mass_perc=90, use_name='part A')
SE1700.add_comp(partB, mass_perc=10, use_name='part B')
SE1700.save('Materials//SE1700.json')
