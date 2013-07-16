-- visible pour tous
insert into om_droit select nextval('om_droit_seq'), obj||action,5 from (select '_tab' as action UNION select '_' UNION select '_consulter') lst_act, 
(SELECT tablename as obj FROM pg_tables WHERE schemaname = current_schema and (tablename in ('commune','voie','parcelle','geo_parcelle','parcellecomposante','typcom', 'natvoiriv', 'carvoi', 'annul', 'typvoi', 'indldnbat','ccodro', 'ccodem', 'gtoper', 'ccoqua', 'dnatpr', 'ccogrm', 'gtyp3', 'gtyp4', 'gtyp5', 'gtyp6','gpdl', 'gnexps', 'cgrnum', 'dsgrpf', 'cnatsp', 'ccolloc', 'gnexts','ccoeva', 'dteloc', 'ccoplc', 'cconlc', 'cconad', 'dnatlc', 'ccoaff', 'gnexpl', 'ccolloc', 'gnextl', 'top48a', 'hlmsem','ctpdl', 'cconlo') or tablename like 'geo_%')) lst_obj order by obj, action;
-- visible pour utilisateur limité
insert into om_droit select nextval('om_droit_seq'), obj||action,4 from (select '_tab' as action UNION select '_' UNION select '_consulter') lst_act, 
(SELECT tablename as obj FROM pg_tables WHERE schemaname = current_schema and tablename in ('local00','local10','lotslocaux')) lst_obj order by obj, action;
-- visible pour utilisateur 
insert into om_droit select nextval('om_droit_seq'), obj||action,3 from (select '_tab' as action UNION select '_' UNION select '_consulter') lst_act, 
(SELECT tablename as obj FROM pg_tables WHERE schemaname = current_schema and tablename in ('comptecommunal','suf','sufexoneration','suftaxation','lots','pdl','lots','pev','pevdependances','pevexoneration','pevprincipale','pevprofessionnelle','pevtaxation')) lst_obj order by obj, action;
-- visible pour super utilisateur
insert into om_droit select nextval('om_droit_seq'), obj||action,2 from (select '_tab' as action UNION select '_' UNION select '_consulter') lst_act, 
(SELECT tablename as obj FROM pg_tables WHERE schemaname = current_schema and tablename in ('proprietaire')) lst_obj order by obj, action;

insert into om_droit values ( nextval('om_droit_seq'), 'anonyme',2);
insert into om_droit values ( nextval('om_droit_seq'), 'choixexercice',2);
insert into om_droit values ( nextval('om_droit_seq'), 'import_edigeo',2);
insert into om_droit values ( nextval('om_droit_seq'), 'import_majic3',2);
