DROP TABLE IF EXISTS geo_label;
ALTER TABLE id_s_obj_z_1_2_2 RENAME TO geo_label;
ALTER TABLE geo_label ADD COLUMN x_label numeric;
ALTER TABLE geo_label ADD COLUMN y_label numeric;
UPDATE geo_label SET x_label = ST_X(geom);
UPDATE geo_label SET y_label = ST_Y(geom);
