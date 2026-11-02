-- Objects of another layer near a list of parcelles, for the spatial search of Lizmap:
-- one row per parcelle and object, among the objects selected by the user.
-- The table must be in the same database as the cadastre data. ST_DWithin uses the spatial indexes,
-- it is replaced by ST_Distance for Spatialite, which does not have it (see postgisToSpatialite).
-- Parameters:
-- * {parcelles}, the identifiers of the parcelles, quoted and separated by commas
-- * {table}, {cle}, {champ} and {geometrie}, the table of the layer, its primary key, the field giving
--   the code of the objects and its geometry column, quoted
-- * {objets}, the values of the primary key of the selected objects, quoted and separated by commas
-- * {distance}, the maximum distance between an object and a parcelle, in the unit of the geometries

SELECT
    gp.geo_parcelle AS parcelle,
    z.{champ} AS code
FROM parcelle_info gp
JOIN {table} z ON z.{cle} IN ({objets})
WHERE gp.geo_parcelle IN ({parcelles})
AND z.{champ} IS NOT NULL
AND ST_DWithin(z.{geometrie}, gp.geom, {distance})
