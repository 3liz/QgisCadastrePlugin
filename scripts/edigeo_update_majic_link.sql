-- Lien commune <--> geo_commune
UPDATE [PREFIXE]geo_commune set commune= p.commune FROM [PREFIXE]commune p WHERE p.annee='[ANNEE]' AND p.commune=SUBSTRING(geo_commune.geo_commune,1,4)||'[DEPDIR]'||SUBSTRING(geo_commune.geo_commune,5,3) AND geo_commune.annee='[ANNEE]';
UPDATE [PREFIXE]commune SET geo_commune=g.geo_commune FROM [PREFIXE]geo_commune g WHERE g.commune=commune.commune AND g.annee='[ANNEE]';

-- Lien parcelle <--> geo_parcelle
UPDATE [PREFIXE]geo_parcelle SET (parcelle, voie, comptecommunal) = (p.parcelle, p.voie, p.comptecommunal)
FROM [PREFIXE]parcelle p
WHERE p.annee='[ANNEE]' AND geo_parcelle.annee='[ANNEE]'
AND p.parcelle=SUBSTRING(geo_parcelle.geo_parcelle,1,4)||'[DEPDIR]'||SUBSTRING(geo_parcelle.geo_parcelle,5,12);
UPDATE [PREFIXE]parcelle SET geo_parcelle=g.geo_parcelle FROM [PREFIXE]geo_parcelle g WHERE g.parcelle=parcelle.parcelle AND g.annee='[ANNEE]';
