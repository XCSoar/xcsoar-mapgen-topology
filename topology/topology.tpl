* filename, range, icon, label_index, r, g, b, pen_width, label_range, label_important_range, alpha
* range is GetMapScale()/1000. Layer is drawn at that scale and closer.
* OSM Alps is much denser than the old HighRes shapefiles. Heavy layers
* are pulled in so a 6–8 km overview does not paint 25k+ medium roads,
* and so cities/rivers are not cached at 50 km.
city_area_large,25,,,208,210,70,1,0,0,255
city_area_small,2,,,208,210,70,1,0,0,255
forest_area_large,8,,,20,126,34,1,0,0,100
forest_area_small,2,,,20,126,34,1,0,0,100
water_area_large,30,,2,99,155,166,1,12,0,255
water_area_small,3,,2,89,155,166,1,3,0,255
water_lines,15,,2,98,157,251,1,8,0,255
roadbig_line,15,,,218,109,130,3,15,0,255
roadmedium_line,5,,,229,156,44,2,5,0,255
roadsmall_line,2,,,183,147,38,1,2,0,220
railway_line,10,,,64,64,64,1,10,0,255
power_line,5,,,190,0,0,2,5,0,255
city_point,15,,1,223,223,0,1,15,10,255
town_point,10,,1,223,223,0,1,10,3,255
suburb_point,3,,1,223,223,0,1,3,0,255
village_point,3,,1,223,223,0,1,3,0,255
building_area_large,5,,,150,140,130,1,0,0,255
* Airport stack, OSM Carto colours, grounds first then pavement then buildings.
* aerodrome #e9e7e2  apron #dadae0  taxi/runway/helipad #bbc  hangar #d9d0c9
aerodrome_area,8,,3,233,231,226,1,8,0,255
apron_area,5,,,218,218,224,1,0,0,255
taxiway_area,5,,,187,187,204,1,0,0,255
hangar_area,5,,,217,208,201,1,0,0,255
terminal_area,5,,,195,187,181,1,0,0,255
airstrip_area,10,,3,187,187,204,1,1,1,255
* Peaks: 3500 m+ always; 2000–3500 m only if the local high point.
* Passes: Col/Passo/Pass/Joch. 2000 m+ always; 1000–2000 m if local high point.
peak_point_high,15,mountain_top,1,80,80,80,1,10,4,255
peak_point,8,mountain_top,1,80,80,80,1,6,0,255
pass_point_high,15,mountain_pass,1,90,90,90,1,10,4,255
pass_point,8,mountain_pass,1,90,90,90,1,5,2,255
