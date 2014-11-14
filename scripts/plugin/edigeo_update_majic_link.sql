-- Lien commune <--> geo_commune
UPDATE [PREFIXE]geo_commune set commune= p.commune FROM [PREFIXE]commune p WHERE p.annee='[ANNEE]' AND p.commune=SUBSTRING(geo_commune.geo_commune,1,4)||'[DEPDIR]'||SUBSTRING(geo_commune.geo_commune,5,3) AND geo_commune.annee='[ANNEE]';
UPDATE [PREFIXE]commune SET geo_commune=g.geo_commune FROM [PREFIXE]geo_commune g WHERE g.commune=commune.commune AND g.annee='[ANNEE]';
