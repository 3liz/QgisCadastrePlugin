INSERT INTO geo_label (object_rid, fon, hei, tyu, cef, csp, di1, di2, di3, di4, tpa, hta, vta, atr, ogr_obj_lnk, ogr_obj_lnk_layer, ogr_atr_val, ogr_angle, ogr_font_size, x_label, y_label, geom)
SELECT object_rid, fon, hei, tyu, cef, csp, di1, di2, di3, di4, tpa, hta, vta, atr, ogr_obj_lnk, ogr_obj_lnk_layer, ogr_atr_val, ogr_angle, ogr_font_size, ST_X(geom), ST_Y(geom), geom
FROM id_s_obj_z_1_2_2
