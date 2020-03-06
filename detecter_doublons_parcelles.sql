set search_path to cadastre;
select * from geo_parcelle where geo_parcelle in (
    select geo_parcelle from geo_parcelle group by geo_parcelle, geom having count(*) > 1
)
order by geo_parcelle;
