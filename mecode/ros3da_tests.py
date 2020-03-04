from main import G

layer_height = 0.5 #in mm
print_feed = 2.887 #in mm/s
travel_feed = 10 #in mm/s
com_port = 7
good_press = 0.1


g = G(print_lines=True,outfile='ros3da_pattern_v4_121119.pgm')
g.rename_axis(z='A')
g.feed(travel_feed)
g.absolute()
#g.home() #temp
#g.move(z=layer_height) #temp
#g.rect(25.4*3,25.4*2) #temp

# Frequency measurement
g.move(x=4,y=5)
g.move(z=layer_height)
g.feed(print_feed)
width1, length1 = g.line_frequency(freq=[0.5,0.75,1.0,1.25,1.5,1.75,2.0],padding=4,length=20,com_port=com_port,pressure=good_press,travel_feed=travel_feed)

# Spanning measurement
g.move(x=28,y=5)
g.move(z=layer_height)
g.feed(print_feed)
width2, length2 = g.line_span(padding=3.6,dwell=1,distances=[8,16,24,32,40],com_port=com_port,pressure=good_press,travel_feed=travel_feed)

# Width Measurement
g.move(x=25.4*3-25-4,y=4)
g.move(z=layer_height)
g.feed(print_feed)
width3, length3 = g.line_width(padding=6.4,width=10,com_port=com_port,pressures=[good_press,good_press*1.2,good_press*1.4],spacing=[6,5,4,3,2,2.5,1.5,1.0,0.5],travel_feed=travel_feed)

# Crossing measurement
g.move(x=4,y=39.4)
g.move(z=layer_height)
g.feed(print_feed)
length4 = g.line_crossing(dwell=1,feeds=[1,5,10],length=30,com_port=com_port,pressure=good_press,travel_feed=travel_feed)

g.abs_move(x=-180.5615,y=112.0630)
#g.view()
#g.view(backend='vpython',nozzle_cam=False,nozzle_dims=[1.0,5.0],substrate_dims=[25.4*1.5,-25.4,-1.0,25.4*3,1,25.4*2],fast_forward=10)
g.teardown()