﻿-- FORMATAGE DONNEES : DEBUT;
-- création des index pour optimisation;
CREATE INDEX idx_voie_codvoi ON ${PREFIXE}voie (codvoi);
CREATE INDEX idx_lots_comptecommunal ON ${PREFIXE}lots (annee, ccodep, ccodir, ccocom, dnuprol);
-- traitement: parcelle;
INSERT INTO ${PREFIXE}parcelle
(
 parcelle, annee, ccodep, ccodir, ccocom, ccopre, ccosec, dnupla, dcntpa, dsrpar, dnupro, jdatat, dreflf, gpdl, cprsecr, ccosecr, dnuplar, dnupdl, gurbpa,
 dparpi, ccoarp, gparnf, gparbat, parrev, gpardp, fviti, dnvoiri, dindic, ccovoi, ccoriv, ccocif, gpafpd, ajoutcoherence,
 comptecommunal, pdl, voie
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,15),' ','0') AS parcelle,
  '${ANNEE}' AS annee,
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,3) AS ccopre,
  SUBSTRING(tmp,10,2) AS ccosec,
  SUBSTRING(tmp,12,4) AS dnupla,
  to_number(SUBSTRING(tmp,22,9),'000000000') AS dcntpa,
  SUBSTRING(tmp,31,1) AS dsrpar,
  SUBSTRING(tmp,32,6) AS dnupro,
  CASE WHEN trim(SUBSTRING(tmp,38,8))='' THEN NULL ELSE to_date(SUBSTRING(tmp,38,8),'DDMMYYYY') END AS jdatat,
  SUBSTRING(tmp,46,5) AS dreflf,
  SUBSTRING(tmp,51,1) AS gpdl,
  SUBSTRING(tmp,52,3) AS cprsecr,
  SUBSTRING(tmp,55,2) AS ccosecr,
  SUBSTRING(tmp,57,4) AS dnuplar,
  CASE WHEN trim(SUBSTRING(tmp,61,3))='' THEN NULL ELSE SUBSTRING(tmp,61,3) END AS dnupdl,
  CASE WHEN SUBSTRING(tmp,64,1) IS NULL THEN ' ' ELSE SUBSTRING(tmp,64,1) END AS gurbpa,
  SUBSTRING(tmp,65,4) AS dparpi,
  CASE WHEN SUBSTRING(tmp,69,1) IS NULL THEN ' ' ELSE SUBSTRING(tmp,69,1) END AS ccoarp,
  CASE WHEN (SUBSTRING(tmp,70,1) IS NULL OR SUBSTRING(tmp,70,1) != '1') THEN '0' ELSE SUBSTRING(tmp,70,1) END AS gparnf,
  CASE WHEN (SUBSTRING(tmp,71,1) IS NULL OR SUBSTRING(tmp,71,1) != '1') THEN '0' ELSE SUBSTRING(tmp,71,1) END AS gparbat,
  SUBSTRING(tmp,72,12) AS parrev,
  CASE WHEN SUBSTRING(tmp,84,01) IS NULL THEN '0' WHEN SUBSTRING(tmp,84,01)  !=  '1' THEN '0' ELSE SUBSTRING(tmp,84,01) END AS gpardp,
  SUBSTRING(tmp,85,01) AS fviti,
  SUBSTRING(tmp,86,4) AS dnvoiri,
  SUBSTRING(tmp,90,1) AS dindic,
  SUBSTRING(tmp,91,5) AS ccovoi,
  SUBSTRING(tmp,96,4) AS ccoriv,
  SUBSTRING(tmp,100,4) AS ccocif,
  SUBSTRING(tmp,104,1) AS gpafpd,
  'N',
  REPLACE(REPLACE('${ANNEE}'||SUBSTRING(tmp,1,2)||SUBSTRING(tmp,32,6),' ', '0'),'+','¤') AS comptecommunal,
  CASE WHEN trim(SUBSTRING(tmp,61,3))='' THEN NULL ELSE REPLACE('${ANNEE}'||SUBSTRING(tmp,1,6)||SUBSTRING(tmp,52,9)||SUBSTRING(tmp,61,3),' ', '0') END AS pdl,
  CASE WHEN trim(SUBSTRING(tmp,91,5))='' THEN NULL ELSE REPLACE('${ANNEE}'||SUBSTRING(tmp,1,6)||SUBSTRING(tmp,91,5),' ', '0') END AS voie
FROM ${PREFIXE}nbat WHERE SUBSTRING(tmp,20,2) ='10';
-- traitement: suf;
INSERT INTO ${PREFIXE}suf
(
 suf, annee,ccodep, ccodir, ccocom, ccopre, ccosec, dnupla, ccosub, dcntsf, dnupro, gnexps, drcsub, drcsuba, ccostn, cgrnum, dsgrpf, dclssf, cnatsp,
 drgpos, ccoprel, ccosecl, dnuplal, dnupdl, dnulot, rclsi, gnidom, topja, datja, postel,
 parcelle, comptecommunal, pdl
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,15)||CASE WHEN SUBSTRING(tmp,16,2) IS NULL THEN '' ELSE trim(SUBSTRING(tmp,16,2)) END,' ','0') AS suf,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,3) AS ccopre,
  SUBSTRING(tmp,10,2) AS ccosec,
  SUBSTRING(tmp,12,4) AS dnupla,
  CASE WHEN SUBSTRING(tmp,16,2) IS NULL THEN '' ELSE trim(SUBSTRING(tmp,16,2)) END AS ccosub,
  CASE WHEN trim(SUBSTRING(tmp,22,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,22,9),'999999999') END AS dcntsf,
  SUBSTRING(tmp,31,6) AS dnupro,
  CASE WHEN trim(SUBSTRING(tmp,37,2))='' THEN NULL ELSE SUBSTRING(tmp,37,2) END AS gnexps,
  CASE WHEN trim(SUBSTRING(tmp,39,10))='' THEN NULL ELSE to_number(SUBSTRING(tmp,39,10),'9999999999')/100 END AS drcsub,
  CASE WHEN trim(SUBSTRING(tmp,49,10))='' THEN NULL ELSE to_number(SUBSTRING(tmp,49,10),'9999999999')/100 END AS drcsuba,
  SUBSTRING(tmp,59,1) AS ccostn,
  CASE WHEN trim(SUBSTRING(tmp,60,2))='' THEN NULL ELSE SUBSTRING(tmp,60,2) END AS cgrnum,
  CASE WHEN trim(SUBSTRING(tmp,62,2))='' THEN NULL ELSE trim(SUBSTRING(tmp,62,2)) END AS dsgrpf,
  SUBSTRING(tmp,64,2) AS dclssf,
  CASE WHEN trim(SUBSTRING(tmp,66,5))='' THEN NULL ELSE trim(SUBSTRING(tmp,66,5)) END AS cnatsp,
  SUBSTRING(tmp,71,1) AS drgpos,
  SUBSTRING(tmp,72,3) AS ccoprel,
  SUBSTRING(tmp,75,2) AS ccosecl,
  SUBSTRING(tmp,77,4) AS dnuplal,
  CASE WHEN trim(SUBSTRING(tmp,81,3))='' THEN NULL ELSE SUBSTRING(tmp,81,3) END AS dnupdl,
  SUBSTRING(tmp,84,7) AS dnulot,
  SUBSTRING(tmp,91,46) AS rclsi,
  SUBSTRING(tmp,137,1) AS gnidom,
  SUBSTRING(tmp,138,1) AS topja,
  CASE WHEN trim(SUBSTRING(tmp,139,8))='' THEN NULL ELSE to_date(SUBSTRING(tmp,139,8),'DDMMYYYY') END AS datja,
  SUBSTRING(tmp,147,1) AS postel,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,15),' ', '0') AS parcelle,
  REPLACE(REPLACE('${ANNEE}'||SUBSTRING(tmp,1,2)||SUBSTRING(tmp,31,6),' ', '0'),'+','¤') AS comptecommunal,
  CASE WHEN  trim(SUBSTRING(tmp,81,3))='' THEN NULL ELSE REPLACE('${ANNEE}'||SUBSTRING(tmp,1,6)||SUBSTRING(tmp,72,9)||SUBSTRING(tmp,81,3),' ', '0') END AS pdl
FROM ${PREFIXE}nbat WHERE
 SUBSTRING(tmp,20,2) ='21';
-- traitement: sufexoneration;
INSERT INTO ${PREFIXE}sufexoneration
(
 sufexoneration, annee, ccodep, ccodir, ccocom, ccopre, ccosec, dnupla, ccosub, rnuexn, vecexn, ccolloc, pexn, gnexts, jandeb, jfinex, fcexn, fcexna, rcexna,
 rcexnba, mpexnba, suf
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,15)||CASE WHEN SUBSTRING(tmp,16,2) IS NULL THEN '' ELSE trim(SUBSTRING(tmp,16,2)) END||SUBSTRING(tmp,18,2),' ','0') AS sufexoneration,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,3) AS ccopre,
  SUBSTRING(tmp,10,2) AS ccosec,
  SUBSTRING(tmp,12,4) AS dnupla,
  CASE WHEN SUBSTRING(tmp,16,2) IS NULL THEN '' ELSE trim(SUBSTRING(tmp,16,2)) END AS ccosub,
  SUBSTRING(tmp,18,2) AS rnuexn,
  CASE WHEN trim(SUBSTRING(tmp,22,10))='' THEN NULL ELSE to_number(SUBSTRING(tmp,22,10),'9999999999')/100 END AS vecexn,
  CASE WHEN trim(SUBSTRING(tmp,32,2))='' THEN NULL ELSE trim(SUBSTRING(tmp,32,2)) END AS ccolloc,
  CASE WHEN trim(SUBSTRING(tmp,34,5))='' THEN NULL ELSE to_number(SUBSTRING(tmp,34,5),'99999') END AS pexn,
  CASE WHEN trim(SUBSTRING(tmp,39,2))='' THEN NULL ELSE trim(SUBSTRING(tmp,39,2)) END AS gnexts,
  SUBSTRING(tmp,41,4) AS jandeb,
  SUBSTRING(tmp,45,4) AS jfinex,
  SUBSTRING(tmp,49,10) AS fcexn,
  SUBSTRING(tmp,59,10) AS fcexna,
  SUBSTRING(tmp,69,10) AS rcexna,
  CASE WHEN trim(SUBSTRING(tmp,79,10))='' THEN NULL ELSE to_number(SUBSTRING(tmp,79,10),'9999999999')/100 END AS rcexnba,
  SUBSTRING(tmp,90,10) AS mpexnba,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,15)||CASE WHEN SUBSTRING(tmp,16,2) IS NULL THEN '' ELSE trim(SUBSTRING(tmp,16,2)) END,' ', '0') AS suf
FROM ${PREFIXE}nbat WHERE SUBSTRING(tmp,20,2) ='30';
-- traitement: suftaxation;
INSERT INTO ${PREFIXE}suftaxation
(
 suftaxation, annee,ccodep, ccodir, ccocom, ccopre, ccosec, dnupla, ccosub, c1majposa, c1bisufad, c2majposa, c2bisufad, c3majposa, c3bisufad, c4majposa, c4bisufad, cntmajtc,
 suf
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,15)||CASE WHEN SUBSTRING(tmp,16,2) IS NULL THEN '' ELSE trim(SUBSTRING(tmp,16,2)) END,' ','0') AS suftaxation,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,3) AS ccopre,
  SUBSTRING(tmp,10,2) AS ccosec,
  SUBSTRING(tmp,12,4) AS dnupla,
  CASE WHEN SUBSTRING(tmp,16,2) IS NULL THEN '' ELSE trim(SUBSTRING(tmp,16,2)) END AS ccosub,
  CASE WHEN trim(SUBSTRING(tmp,23,10))='' THEN NULL ELSE to_number(SUBSTRING(tmp,23,10),'9999999999')/100 END AS c1majposa,
  CASE WHEN trim(SUBSTRING(tmp,34,10))='' THEN NULL ELSE to_number(SUBSTRING(tmp,34,10),'9999999999')/100 END AS c1bisufad,
  CASE WHEN trim(SUBSTRING(tmp,45,10))='' THEN NULL ELSE to_number(SUBSTRING(tmp,45,10),'9999999999')/100 END AS c2majposa,
  CASE WHEN trim(SUBSTRING(tmp,56,10))='' THEN NULL ELSE to_number(SUBSTRING(tmp,56,10),'9999999999')/100 END AS c2bisufad,
  CASE WHEN trim(SUBSTRING(tmp,67,10))='' THEN NULL ELSE to_number(SUBSTRING(tmp,67,10),'9999999999')/100 END AS c3majposa,
  CASE WHEN trim(SUBSTRING(tmp,78,10))='' THEN NULL ELSE to_number(SUBSTRING(tmp,78,10),'9999999999')/100 END AS c3bisufad,
  CASE WHEN trim(SUBSTRING(tmp,89,10))='' THEN NULL ELSE to_number(SUBSTRING(tmp,89,10),'9999999999')/100 END AS c4majposa,
  CASE WHEN trim(SUBSTRING(tmp,100,10))='' THEN NULL ELSE to_number(SUBSTRING(tmp,100,10),'9999999999')/100 END  AS c4bisufad,
  CASE WHEN trim(SUBSTRING(tmp,110,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,110,9),'999999999') END cntmajtc,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,15)||CASE WHEN SUBSTRING(tmp,16,2) IS NULL THEN '' ELSE trim(SUBSTRING(tmp,16,2)) END,' ', '0') AS suf
FROM ${PREFIXE}nbat WHERE SUBSTRING(tmp,20,2) ='36';
-- traitement: local00;
INSERT INTO ${PREFIXE}local00
(
 local00, annee, ccodep, ccodir, ccocom, invar, ccopre, ccosec, dnupla, dnubat, descr, dniv, dpor, ccoriv, ccovoi, dnvoiri, dindic, ccocif, dvoilib, cleinvar,
 locinc, parcelle, voie
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,7,10),' ','0') AS local00,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,10) AS invar,
  SUBSTRING(tmp,36,3) AS ccopre,
  SUBSTRING(tmp,39,2) AS ccosec,
  SUBSTRING(tmp,41,4) AS dnupla,
  SUBSTRING(tmp,46,2) AS dnubat,
  SUBSTRING(tmp,48,2) AS descr,
  SUBSTRING(tmp,50,2) AS dniv,
  SUBSTRING(tmp,52,5) AS dpor,
  SUBSTRING(tmp,57,4) AS ccoriv,
  SUBSTRING(tmp,62,5) AS ccovoi,
  SUBSTRING(tmp,67,4) AS dnvoiri,
  SUBSTRING(tmp,71,1) AS dindic,
  SUBSTRING(tmp,72,4) AS ccocif,
  SUBSTRING(tmp,76,30) AS dvoilib,
  SUBSTRING(tmp,106,1) AS cleinvar,
  SUBSTRING(tmp,107,1) AS locinc,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,6)||SUBSTRING(tmp,36,9),' ', '0') AS parcelle,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,6)||SUBSTRING(tmp,62,5),' ', '0') AS voie
FROM ${PREFIXE}bati WHERE SUBSTRING(tmp,31,2) ='00';
-- traitement: local10;
INSERT INTO ${PREFIXE}local10
(
 local10, annee,ccodep, ccodir, ccocom, invar, gpdl, dsrpar, dnupro, jdatat, dnufnl, ccoeva, ccitlv, dteloc, gtauom, dcomrd, ccoplc, cconlc, dvltrt,
 ccoape, cc48lc, dloy48a, top48a, dnatlc, dnupas, gnexcf, dtaucf, cchpr, jannat, dnbniv, hlmsem, postel, dnatcg, jdatcgl, dnutbx, dvltla,
 janloc, ccsloc, fburx, gimtom, cbtabt, jdtabt, jrtabt, jacloc,
 comptecommunal
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,7,10),' ','0') AS local10,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,10) AS invar,
  SUBSTRING(tmp,36,1) AS gpdl,
  SUBSTRING(tmp,37,1) AS dsrpar,
  SUBSTRING(tmp,38,6) AS dnupro,
  CASE WHEN trim(SUBSTRING(tmp,44,8))='' THEN NULL ELSE to_date(SUBSTRING(tmp,44,8),'DDMMYYYY') END AS jdatat,
  SUBSTRING(tmp,52,6) AS dnufnl,
  CASE WHEN trim(SUBSTRING(tmp,58,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,58,1)) END AS ccoeva,
  SUBSTRING(tmp,59,1) AS ccitlv,
  CASE WHEN trim(SUBSTRING(tmp,60,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,60,1)) END AS dteloc,
  SUBSTRING(tmp,61,2) AS gtauom,
  SUBSTRING(tmp,63,3) AS dcomrd,
  SUBSTRING(tmp,66,1) AS ccoplc,
  CASE WHEN trim(SUBSTRING(tmp,67,2))='' THEN NULL ELSE trim(SUBSTRING(tmp,67,2)) END AS cconlc,
  CASE WHEN trim(SUBSTRING(tmp,69,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,69,9),'999999999') END AS dvltrt,
  SUBSTRING(tmp,78,4) AS ccoape,
  SUBSTRING(tmp,82,2) AS cc48lc,
  CASE WHEN trim(SUBSTRING(tmp,84,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,84,9),'999999999') END AS dloy48a,
  CASE WHEN trim(SUBSTRING(tmp,93,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,93,1)) END AS top48a,
  CASE WHEN trim(SUBSTRING(tmp,94,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,94,1)) END AS dnatlc,
  SUBSTRING(tmp,95,8) AS dnupas,
  SUBSTRING(tmp,103,2) AS gnexcf,
  SUBSTRING(tmp,105,3) AS dtaucf,
  SUBSTRING(tmp,108,1) AS cchpr,
  SUBSTRING(tmp,109,4) AS jannat,
  SUBSTRING(tmp,113,2) AS dnbniv,
  CASE WHEN trim(SUBSTRING(tmp,115,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,115,1)) END AS hlmsem,
  SUBSTRING(tmp,116,1) AS postel,
  SUBSTRING(tmp,117,2) AS dnatcg,
  NULL AS jdatcgl,
  SUBSTRING(tmp,127,6) AS dnutbx,
  SUBSTRING(tmp,133,9) AS dvltla,
  SUBSTRING(tmp,142,4) AS janloc,
  SUBSTRING(tmp,146,2) AS ccsloc,
  CASE WHEN trim(SUBSTRING(tmp,148,1))='' THEN NULL ELSE to_number(SUBSTRING(tmp,148,1),'9') END  AS fburx,
  SUBSTRING(tmp,149,1) AS gimtom,
  SUBSTRING(tmp,150,2) AS cbtabt,
  SUBSTRING(tmp,152,4) AS jdtabt,
  SUBSTRING(tmp,156,4) AS jrtabt,
  SUBSTRING(tmp,160,4) AS jacloc,
  REPLACE(REPLACE('${ANNEE}'||SUBSTRING(tmp,1,2)||SUBSTRING(tmp,38,6),' ', '0'),'+','¤') AS comptecommunal
FROM ${PREFIXE}bati WHERE SUBSTRING(tmp,31,2) ='10';
UPDATE ${PREFIXE}local10 SET
  ccopre = local00.ccopre,
  ccosec = local00.ccosec,
  dnupla = local00.dnupla,
  ccoriv = local00.ccoriv,
  ccovoi = local00.ccovoi,
  dnvoiri = local00.dnvoiri,
  local00=local10.annee||local10.invar,
  parcelle = REPLACE(local10.annee||local10.ccodep||local10.ccodir||local10.ccocom||local00.ccopre||local00.ccosec||local00.dnupla,' ', '0'),
  voie= REPLACE(local10.annee||local10.ccodep||local10.ccodir||local10.ccocom||local00.ccovoi,' ', '0')
FROM ${PREFIXE}local00
WHERE local00.invar = local10.invar AND local00.annee='${ANNEE}' AND local10.annee='${ANNEE}';
-- traitement: pev;
INSERT INTO ${PREFIXE}pev
(
 pev, annee, ccodep, ccodir, ccocom, invar, dnupev, ccoaff, ccostb, dcapec, dcetlc, dcsplc, dsupot, dvlper, dvlpera, gnexpl, libocc, ccthp, retimp,
 dnuref, rclsst, gnidom, dcsglc, ccogrb, cocdi, cosatp, gsatp, clocv, dvltpe, dcralc,
 local10
 )
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,7,10)||SUBSTRING(tmp,28,3),' ','0') AS pev,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,10) AS invar,
  SUBSTRING(tmp,28,3) AS dnupev,
  CASE WHEN trim(SUBSTRING(tmp,36,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,36,1)) END AS ccoaff,
  SUBSTRING(tmp,37,1) AS ccostb,
  SUBSTRING(tmp,38,2) AS dcapec,
  CASE WHEN trim(SUBSTRING(tmp,40,3))='' THEN NULL ELSE to_number(SUBSTRING(tmp,40,3),'999')/100 END AS dcetlc,
  SUBSTRING(tmp,43,3) AS dcsplc,
  CASE WHEN trim(SUBSTRING(tmp,46,6))='' THEN NULL ELSE to_number(SUBSTRING(tmp,46,6),'999999') END AS dsupot,
  CASE WHEN trim(SUBSTRING(tmp,52,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,52,9),'999999999') END AS dvlper,
  CASE when trim(SUBSTRING(tmp,61,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,61,9),'999999999') END AS dvlpera,
  CASE WHEN trim(SUBSTRING(tmp,70,2))='' THEN NULL ELSE trim(SUBSTRING(tmp,70,2)) END AS gnexpl,
  SUBSTRING(tmp,72,30) AS libocc,
  SUBSTRING(tmp,102,1) AS ccthp,
  SUBSTRING(tmp,103,1) AS retimp,
  SUBSTRING(tmp,104,3) AS dnuref,
  SUBSTRING(tmp,107,32) AS rclsst,
  SUBSTRING(tmp,139,1) AS gnidom,
  SUBSTRING(tmp,140,3) AS dcsglc,
  SUBSTRING(tmp,143,1) AS ccogrb,
  SUBSTRING(tmp,144,4) AS cocdi,
  SUBSTRING(tmp,148,3) AS cosatp,
  SUBSTRING(tmp,151,1) AS gsatp,
  SUBSTRING(tmp,152,1) AS clocv,
  CASE WHEN trim(SUBSTRING(tmp,153,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,153,9),'999999999') END AS dvltpe,
  SUBSTRING(tmp,162,3) AS dcralc,
  '${ANNEE}'||SUBSTRING(tmp,7,10) AS local10
FROM ${PREFIXE}bati WHERE SUBSTRING(tmp,31,2) ='21';
-- traitement: pevexoneration;
INSERT INTO ${PREFIXE}pevexoneration
(
 pevexoneration, annee,ccodep, ccodir, ccocom, invar, Janbil, dnupev, dnuexb, ccolloc, pexb, gnextl, jandeb, janimp, vecdif, vecdifa, fcexb, fcexba, rcexba,
 dvldif2, dvldif2a, fcexb2, fcexba2, rcexba2,
 pev
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,7,10)||SUBSTRING(tmp,28,3)||SUBSTRING(tmp,33,3)||CASE WHEN SUBSTRING(tmp,24,4) IS NOT NULL THEN trim(SUBSTRING(tmp,24,4)) ELSE SUBSTRING(tmp,24,4) END, ' ','0') AS pevexoneration,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,10) AS invar,
  CASE WHEN SUBSTRING(tmp,24,4) IS NOT NULL THEN trim(SUBSTRING(tmp,24,4)) ELSE SUBSTRING(tmp,24,4) END AS janbil,
  SUBSTRING(tmp,28,3) AS dnupev,
  SUBSTRING(tmp,33,3) AS dnuexb,
  CASE WHEN trim(SUBSTRING(tmp,36,2))='' THEN NULL ELSE trim(SUBSTRING(tmp,36,2)) END AS ccolloc,
  CASE WHEN trim(SUBSTRING(tmp,38,5))='' THEN NULL ELSE to_number(SUBSTRING(tmp,38,5),'99999')/100 END AS pexb,
  CASE WHEN trim(SUBSTRING(tmp,43,2))='' THEN NULL ELSE trim(SUBSTRING(tmp,43,2)) END AS gnextl,
  SUBSTRING(tmp,45,4) AS jandeb,
  SUBSTRING(tmp,49,4) AS janimp,
  SUBSTRING(tmp,53,9) AS vecdif,
  SUBSTRING(tmp,63,9) AS vecdifa,
  SUBSTRING(tmp,73,9) AS fcexb,
  SUBSTRING(tmp,83,9) AS fcexba,
  SUBSTRING(tmp,93,9) AS rcexba,
  CASE WHEN trim(SUBSTRING(tmp,103,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,103,9),'999999999') END AS dvldif2,
  CASE WHEN trim(SUBSTRING(tmp,113,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,113,9),'999999999') END AS dvldif2a,
  CASE WHEN trim(SUBSTRING(tmp,123,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,123,9),'999999999') END AS fcexb2,
  CASE WHEN trim(SUBSTRING(tmp,133,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,133,9),'999999999') END AS fcexba2,
  CASE WHEN trim(SUBSTRING(tmp,143,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,143,9),'999999999') END AS rcexba2,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,7,10)||SUBSTRING(tmp,28,3),' ', '0') AS pev
FROM ${PREFIXE}bati WHERE SUBSTRING(tmp,31,2) ='30';
-- traitement: pevtaxation;
INSERT INTO ${PREFIXE}pevtaxation
(
 pevtaxation, annee,ccodep, ccodir, ccocom, invar, janbil, dnupev, co_vlbai, co_vlbaia, co_bipevla, de_vlbai, de_vlbaia, de_bipevla, re_vlbai, re_vlbaia,
 re_bipevla, gp_vlbai, gp_vlbaia, gp_bipevla, bateom, baomec,
 pev
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,7,10)||SUBSTRING(tmp,28,3), ' ', '0') AS pevtaxation,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,10) AS invar,
  SUBSTRING(tmp,24,4) AS janbil,
  SUBSTRING(tmp,28,3) AS dnupev,
  CASE WHEN trim(SUBSTRING(tmp,36,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,36,9),'999999999') END  AS co_vlbai,
  CASE WHEN trim(SUBSTRING(tmp,46,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,46,9),'999999999') END  AS co_vlbaia,
  CASE WHEN trim(SUBSTRING(tmp,56,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,56,9),'999999999') END  AS co_bipevla,
  CASE WHEN trim(SUBSTRING(tmp,66,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,66,9),'999999999') END  AS de_vlbai,
  CASE WHEN trim(SUBSTRING(tmp,76,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,76,9),'999999999') END  AS de_vlbaia,
  CASE WHEN trim(SUBSTRING(tmp,86,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,86,9),'999999999') END  AS de_bipevla,
  CASE WHEN trim(SUBSTRING(tmp,96,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,96,9),'999999999') END  AS re_vlbai,
  CASE WHEN trim(SUBSTRING(tmp,106,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,106,9),'999999999') END  AS re_vlbaia,
  CASE WHEN trim(SUBSTRING(tmp,116,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,116,9),'999999999') END  AS re_bipevla,
  CASE WHEN trim(SUBSTRING(tmp,126,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,126,9),'999999999') END  AS gp_vlbai,
  CASE WHEN trim(SUBSTRING(tmp,136,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,136,9),'999999999') END  AS gp_vlbaia,
  CASE WHEN trim(SUBSTRING(tmp,146,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,146,9),'999999999') END  AS gp_bipevla,
  CASE WHEN trim(SUBSTRING(tmp,156,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,156,9),'999999999') END  AS bateom,
  CASE WHEN trim(SUBSTRING(tmp,166,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,166,9),'999999999') END  AS baomec,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,7,10)||SUBSTRING(tmp,28,3),' ', '0') AS pev
FROM ${PREFIXE}bati WHERE SUBSTRING(tmp,31,2) ='36';
-- traitement: pevprincipale;
INSERT INTO ${PREFIXE}pevprincipale
(
 pevprincipale, annee,ccodep, ccodir, ccocom, invar, dnupev, dnudes, dep1_cconad, dep1_dsueic, dep1_dcimei, dep2_cconad, dep2_dsueic, dep2_dcimei, dep3_cconad,
 dep3_dsueic, dep3_dcimei, dep4_cconad, dep4_dsueic, dep4_dcimei, geaulc, gelelc, gesclc, ggazlc, gasclc, gchclc, gvorlc, gteglc, dnbbai, dnbdou,
 dnblav, dnbwc, deqdha, dnbppr, dnbsam, dnbcha, dnbcu8, dnbcu9, dnbsea, dnbann, dnbpdc, dsupdc, dmatgm, dmatto, jannat, detent, dnbniv,
 pev
 )
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,7,10)||SUBSTRING(tmp,28,3)||CASE WHEN SUBSTRING(tmp,33,3) IS NOT NULL THEN trim(SUBSTRING(tmp,33,3)) ELSE SUBSTRING(tmp,33,3) END,' ','0') AS pevprincipale,
  '${ANNEE}' as annee,
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,10) AS invar,
  SUBSTRING(tmp,28,3) AS dnupev,
  CASE WHEN SUBSTRING(tmp,33,3) IS NOT NULL THEN trim(SUBSTRING(tmp,33,3)) ELSE SUBSTRING(tmp,33,3) END AS dnudes,
  CASE WHEN trim(SUBSTRING(tmp,36,2))='' THEN NULL ELSE trim(SUBSTRING(tmp,36,2)) END AS dep1_cconad,
  CASE WHEN trim(SUBSTRING(tmp,38,6))='' THEN NULL ELSE to_number(SUBSTRING(tmp,38,6),'999999') END AS dep1_dsueic,
  CASE WHEN trim(SUBSTRING(tmp,44,2))='' THEN NULL ELSE to_number(SUBSTRING(tmp,44,2),'99')/10 END AS dep1_dcimei,
  CASE WHEN trim(SUBSTRING(tmp,46,2))='' THEN NULL ELSE trim(SUBSTRING(tmp,46,2)) END AS dep2_cconad,
  CASE WHEN trim(SUBSTRING(tmp,48,6))='' THEN NULL ELSE to_number(SUBSTRING(tmp,48,6),'999999') END AS dep2_dsueic,
  CASE WHEN trim(SUBSTRING(tmp,54,2))='' THEN NULL ELSE to_number(SUBSTRING(tmp,54,2),'99')/10 END AS dep2_dcimei,
  CASE WHEN trim(SUBSTRING(tmp,56,2))='' THEN NULL ELSE trim(SUBSTRING(tmp,56,2)) END AS dep3_cconad,
  CASE WHEN trim(SUBSTRING(tmp,58,6))='' THEN NULL ELSE to_number(SUBSTRING(tmp,58,6),'999999') END AS dep3_dsueic,
  CASE WHEN trim(SUBSTRING(tmp,64,2))='' THEN NULL ELSE to_number(SUBSTRING(tmp,64,2),'99')/10 END AS dep3_dcimei,
  CASE WHEN trim(SUBSTRING(tmp,66,2))='' THEN NULL ELSE trim(SUBSTRING(tmp,66,2)) END AS dep4_cconad,
  CASE WHEN trim(SUBSTRING(tmp,68,6))='' THEN NULL ELSE to_number(SUBSTRING(tmp,68,6),'999999') END AS dep4_dsueic,
  CASE WHEN trim(SUBSTRING(tmp,74,2))='' THEN NULL ELSE to_number(SUBSTRING(tmp,74,2),'99')/10 END AS dep4_dcimei,
  SUBSTRING(tmp,76,1) AS geaulc,
  SUBSTRING(tmp,77,1) AS gelelc,
  SUBSTRING(tmp,78,1) AS gesclc,
  SUBSTRING(tmp,79,1) AS ggazlc,
  SUBSTRING(tmp,80,1) AS gasclc,
  SUBSTRING(tmp,81,1) AS gchclc,
  SUBSTRING(tmp,82,1) AS gvorlc,
  SUBSTRING(tmp,83,1) AS gteglc,
  SUBSTRING(tmp,84,2) AS dnbbai,
  SUBSTRING(tmp,86,2) AS dnbdou,
  SUBSTRING(tmp,88,2) AS dnblav,
  SUBSTRING(tmp,90,2) AS dnbwc,
  CASE WHEN trim(SUBSTRING(tmp,92,3))='' THEN NULL ELSE to_number(SUBSTRING(tmp,92,3),'999') END AS deqdha,
  SUBSTRING(tmp,95,2) AS dnbppr,
  SUBSTRING(tmp,97,2) AS dnbsam,
  SUBSTRING(tmp,99,2) AS dnbcha,
  SUBSTRING(tmp,101,2) AS dnbcu8,
  SUBSTRING(tmp,103,2) AS dnbcu9,
  SUBSTRING(tmp,105,2) AS dnbsea,
  SUBSTRING(tmp,107,2) AS dnbann,
  SUBSTRING(tmp,109,2) AS dnbpdc,
  CASE WHEN trim(SUBSTRING(tmp,111,6))='' THEN NULL ELSE to_number(SUBSTRING(tmp,111,6),'999999') END AS dsupdc,
  SUBSTRING(tmp,117,2) AS dmatgm,
  SUBSTRING(tmp,119,2) AS dmatto,
  SUBSTRING(tmp,121,4) AS jannat,
  SUBSTRING(tmp,125,1) AS detent,
  SUBSTRING(tmp,126,2) AS dnbniv,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,7,10)||SUBSTRING(tmp,28,3),' ', '0') AS pev
FROM ${PREFIXE}bati WHERE SUBSTRING(tmp,31,2) ='40';
-- traitement: pevprofessionnelle;
INSERT INTO ${PREFIXE}pevprofessionnelle
(
 pevprofessionnelle, annee, ccodep, ccodir, ccocom, invar, dnupev, dnudes, vsupot, vsurz1, vsurz2, vsurz3, vsurzt, vsurb1, vsurb2,
 pev
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,7,10)||SUBSTRING(tmp,28,3)||SUBSTRING(tmp,33,3), ' ', '0') AS pevprofessionnelle,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,10) AS invar,
  SUBSTRING(tmp,28,3) AS dnupev,
  SUBSTRING(tmp,33,3) AS dnudes,
  SUBSTRING(tmp,36,9) AS vsupot,
  SUBSTRING(tmp,45,9) AS vsurz1,
  SUBSTRING(tmp,54,9) AS vsurz2,
  SUBSTRING(tmp,63,9) AS vsurz3,
  CASE WHEN trim(SUBSTRING(tmp,72,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,72,9),'999999999') END AS vsurzt,
  SUBSTRING(tmp,82,9) AS vsurb1,
  SUBSTRING(tmp,91,9) AS vsurb2,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,7,10)||SUBSTRING(tmp,28,3),' ', '0') AS pev
FROM ${PREFIXE}bati WHERE SUBSTRING(tmp,31,2) ='50';
-- traitement: pevdependances;
INSERT INTO ${PREFIXE}pevdependances
(
 pevdependances, annee, ccodep, ccodir, ccocom, invar, dnupev, dnudes, dsudep, cconad, asitet, dmatgm, dmatto, detent, geaulc, gelelc, gchclc, dnbbai, dnbdou,
 dnblav, dnbwc, deqtlc, dcimlc, dcetde, dcspde,
 pev
)
select
  REPLACE('${ANNEE}'||SUBSTRING(tmp,7,10)||SUBSTRING(tmp,28,3)||SUBSTRING(tmp,33,3), ' ', '0') AS pevdependances,
  '${ANNEE}' AS annee,
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,10) AS invar,
  SUBSTRING(tmp,28,3) AS dnupev,
  SUBSTRING(tmp,33,3) AS dnudes,
  CASE WHEN trim(SUBSTRING(tmp,36,6))='' THEN NULL ELSE to_number(SUBSTRING(tmp,36,6),'999999') END AS dsudep,
  CASE WHEN trim(SUBSTRING(tmp,42,2))='' THEN NULL ELSE trim(SUBSTRING(tmp,42,2)) END AS cconad,
  SUBSTRING(tmp,44,6) AS asitet,
  SUBSTRING(tmp,50,2) AS dmatgm,
  SUBSTRING(tmp,52,2) AS dmatto,
  SUBSTRING(tmp,54,1) AS detent,
  SUBSTRING(tmp,55,1) AS geaulc,
  SUBSTRING(tmp,56,1) AS gelelc,
  SUBSTRING(tmp,57,1) AS gchclc,
  SUBSTRING(tmp,58,2) AS dnbbai,
  SUBSTRING(tmp,60,2) AS dnbdou,
  SUBSTRING(tmp,62,2) AS dnblav,
  SUBSTRING(tmp,64,2) AS dnbwc,
  CASE WHEN trim(SUBSTRING(tmp,66,3))='' THEN NULL ELSE to_number(SUBSTRING(tmp,66,3),'999') END AS deqtlc,
  CASE WHEN trim(SUBSTRING(tmp,69,2))='' THEN NULL ELSE to_number(SUBSTRING(tmp,69,2),'99')/10 END AS dcimlc,
  CASE WHEN trim(SUBSTRING(tmp,71,3))='' THEN NULL ELSE to_number(SUBSTRING(tmp,71,3),'999')/100 END AS dcetde,
  SUBSTRING(tmp,74,3) AS dcspde,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,7,10)||SUBSTRING(tmp,28,3),' ', '0') AS pev
FROM ${PREFIXE}bati WHERE SUBSTRING(tmp,31,2) ='60';
-- traitement: proprietaire;
INSERT INTO ${PREFIXE}proprietaire
(
 proprietaire, annee, ccodep, ccodir, ccocom, dnupro, dnulp, ccocif, dnuper, ccodro, ccodem, gdesip, gtoper, ccoqua, gnexcf, dtaucf, dnatpr, ccogrm, dsglpm, dforme,
 ddenom, gtyp3, gtyp4, gtyp5, gtyp6, dlign3, dlign4, dlign5, dlign6, ccopay, ccodep1a2, ccodira, ccocom_adr, ccovoi, ccoriv, dnvoiri, dindic,
 ccopos, dnirpp, dqualp, dnomlp, dprnlp, jdatnss, dldnss, epxnee, dnomcp, dprncp, topcdi, oriard, fixard, datadr, topdec, datdec, dsiren, ccmm,
 topja, datja, anospi, cblpmo, gtodge, gpctf, gpctsb, jmodge, jandge, jantfc, jantbc,
 comptecommunal
)
SELECT
  REPLACE(REPLACE('${ANNEE}'||SUBSTRING(tmp,1,2)||SUBSTRING(tmp,7,6)||SUBSTRING(tmp,13,2)||SUBSTRING(tmp,19,6), ' ', '0'),'+','¤') AS proprietaire,
  '${ANNEE}' AS annee,
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,6) AS dnupro,
  SUBSTRING(tmp,13,2) AS dnulp,
  SUBSTRING(tmp,15,4) AS ccocif,
  SUBSTRING(tmp,19,6) AS dnuper,
  CASE WHEN trim(SUBSTRING(tmp,25,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,25,1)) END AS ccodro,
  CASE WHEN trim(SUBSTRING(tmp,26,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,26,1)) END AS ccodem,
  SUBSTRING(tmp,27,1) AS gdesip,
  CASE WHEN trim(SUBSTRING(tmp,28,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,28,1)) END AS gtoper,
  CASE WHEN trim(SUBSTRING(tmp,29,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,29,1)) END AS ccoqua,
  SUBSTRING(tmp,30,2) AS gnexcf,
  SUBSTRING(tmp,32,3) AS dtaucf,
  CASE WHEN trim(SUBSTRING(tmp,35,3))='' THEN NULL ELSE trim(SUBSTRING(tmp,35,3)) END AS dnatpr,
  CASE WHEN trim(SUBSTRING(tmp,38,2))='' THEN NULL ELSE trim(SUBSTRING(tmp,38,2)) END AS ccogrm,
  SUBSTRING(tmp,40,10) AS dsglpm,
  SUBSTRING(tmp,50,7) AS dforme,
  SUBSTRING(tmp,57,60) AS ddenom,
  CASE WHEN trim(SUBSTRING(tmp,117,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,117,1)) END AS gtyp3,
  CASE WHEN trim(SUBSTRING(tmp,118,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,118,1)) END AS gtyp4,
  CASE WHEN trim(SUBSTRING(tmp,119,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,119,1)) END AS gtyp5,
  CASE WHEN trim(SUBSTRING(tmp,120,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,120,1)) END AS gtyp6,
  SUBSTRING(tmp,121,30) AS dlign3,
  SUBSTRING(tmp,151,36) AS dlign4,
  SUBSTRING(tmp,187,30) AS dlign5,
  SUBSTRING(tmp,217,32) AS dlign6,
  SUBSTRING(tmp,249,3) AS ccopay,
  SUBSTRING(tmp,252,2) AS ccodep1a2,
  SUBSTRING(tmp,254,1) AS ccodira,
  SUBSTRING(tmp,255,3) AS ccocom_adr,
  SUBSTRING(tmp,258,5) AS ccovoi,
  SUBSTRING(tmp,263,4) AS ccoriv,
  SUBSTRING(tmp,267,4) AS dnvoiri,
  SUBSTRING(tmp,271,1) AS dindic,
  SUBSTRING(tmp,272,5) AS ccopos,
  SUBSTRING(tmp,277,10) AS dnirpp,
  SUBSTRING(tmp,287,3) AS dqualp,
  SUBSTRING(tmp,290,30) AS dnomlp,
  SUBSTRING(tmp,320,15) AS dprnlp,
  CASE WHEN trim(SUBSTRING(tmp,335,10))='' THEN NULL WHEN SUBSTRING(tmp,335,10)='00/00/0000' THEN NULL ELSE to_date(SUBSTRING(tmp,335,10),'DD/MM/YYYYY') END AS jdatnss,
  SUBSTRING(tmp,345,58) AS dldnss,
  SUBSTRING(tmp,403,3) AS epxnee,
  SUBSTRING(tmp,406,30) AS dnomcp,
  SUBSTRING(tmp,436,15) AS dprncp,
  SUBSTRING(tmp,451,1) AS topcdi,
  SUBSTRING(tmp,452,1) AS oriard,
  SUBSTRING(tmp,453,1) AS fixard,
  SUBSTRING(tmp,454,8) AS datadr,
  SUBSTRING(tmp,462,1) AS topdec,
  SUBSTRING(tmp,463,4) AS datdec,
  SUBSTRING(tmp,467,10) AS dsiren,
  SUBSTRING(tmp,477,1) AS ccmm,
  SUBSTRING(tmp,478,1) AS topja,
  CASE WHEN trim(SUBSTRING(tmp,479,8))='' THEN NULL ELSE to_date(SUBSTRING(tmp,479,8),'DDMMYYYY') END AS datja,
  SUBSTRING(tmp,491,3) AS anospi,
  SUBSTRING(tmp,494,1) AS cblpmo,
  SUBSTRING(tmp,495,1) AS gtodge,
  SUBSTRING(tmp,496,1) AS gpctf,
  SUBSTRING(tmp,497,1) AS gpctsb,
  SUBSTRING(tmp,498,2) AS jmodge,
  SUBSTRING(tmp,500,4) AS jandge,
  SUBSTRING(tmp,504,4) AS jantfc,
  SUBSTRING(tmp,508,4) AS jantbc,
  REPLACE(REPLACE('${ANNEE}'||SUBSTRING(tmp,1,2)||SUBSTRING(tmp,7,6),' ', '0'),'+','¤') AS comptecommunal
FROM ${PREFIXE}prop WHERE trim(SUBSTRING(tmp,7,6)) != '';
-- création: comptecommunal à partir de proprietaire;
INSERT INTO ${PREFIXE}comptecommunal
  (comptecommunal, annee, ccodep, ccodir, ccocom, dnupro, ajoutcoherence)
SELECT
  REPLACE(REPLACE('${ANNEE}'||ccodep||dnupro,' ', '0'),'+','¤') AS comptecommunal,
  '${ANNEE}',
  ccodep,
  ccodir,
  ccocom,
  dnupro,
  'N'
FROM ${PREFIXE}proprietaire
where annee='${ANNEE}' group by ccodep, ccodir, ccocom, dnupro;
-- traitement: pdl;
INSERT INTO ${PREFIXE}pdl
(
 pdl, annee, ccodep, ccodir, ccocom, ccopre, ccosec, dnupla, dnupdl, dnivim, ctpdl, dmrpdl, gprmut, dnupro, ccocif,
 parcelle, comptecommunal
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,18),' ', '0') AS pdl,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,3) AS ccopre,
  SUBSTRING(tmp,10,2) AS ccosec,
  SUBSTRING(tmp,12,4) AS dnupla,
  SUBSTRING(tmp,16,3) AS dnupdl,
  SUBSTRING(tmp,28,1) AS dnivim,
  CASE WHEN trim(SUBSTRING(tmp,29,3))='' THEN NULL ELSE trim(SUBSTRING(tmp,29,3)) END AS ctpdl,
  SUBSTRING(tmp,62,20) AS dmrpdl,
  SUBSTRING(tmp,82,1) AS gprmut,
  SUBSTRING(tmp,83,6) AS dnupro,
  SUBSTRING(tmp,94,4) AS ccocif,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,15),' ', '0') AS parcelle,
  REPLACE(REPLACE('${ANNEE}'||SUBSTRING(tmp,1,2)||SUBSTRING(tmp,83,6),' ', '0'),'+','¤') AS comptecommunal
FROM ${PREFIXE}pdll WHERE SUBSTRING(tmp,26,2) ='10';
-- traitement: parcellecomposante;
INSERT INTO ${PREFIXE}parcellecomposante
(
 parcellecomposante, annee, ccodep, ccodir, ccocom, ccopre, ccosec, dnupla, dnupdl, ccoprea, ccoseca, dnuplaa, ccocif,
 pdl, parcelle,parcellea
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,18)||SUBSTRING(tmp,28,9),' ', '0') AS parcellecomposante,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,3) AS ccopre,
  SUBSTRING(tmp,10,2) AS ccosec,
  SUBSTRING(tmp,12,4) AS dnupla,
  SUBSTRING(tmp,16,3) AS dnupdl,
  SUBSTRING(tmp,28,3) AS ccoprea,
  SUBSTRING(tmp,31,2) AS ccoseca,
  SUBSTRING(tmp,33,4) AS dnuplaa,
  SUBSTRING(tmp,94,4) AS ccocif,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,18),' ', '0') AS pdl,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,15),' ', '0') AS parcelle,
  CASE WHEN trim(SUBSTRING(tmp,33,4)) ='' THEN null ELSE REPLACE('${ANNEE}'||SUBSTRING(tmp,1,6)||SUBSTRING(tmp,28,9),' ', '0') END parcellea
FROM ${PREFIXE}pdll WHERE SUBSTRING(tmp,26,2) ='20';
-- traitement: lots;
INSERT INTO ${PREFIXE}lots
(
 lots, annee, ccodep, ccodir, ccocom, ccopre, ccosec, dnupla, dnupdl, dnulot, cconlo, dcntlo, dnumql, ddenql, dfilot, datact, dnuprol, dreflf, ccocif,
 pdl, comptecommunal, parcelle
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,25),' ', '0') AS lots,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,7,3) AS ccopre,
  SUBSTRING(tmp,10,2) AS ccosec,
  SUBSTRING(tmp,12,4) AS dnupla,
  SUBSTRING(tmp,16,3) AS dnupdl,
  SUBSTRING(tmp,19,7) AS dnulot,
  CASE WHEN trim(SUBSTRING(tmp,28,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,28,1)) END AS cconlo,
  CASE WHEN trim(SUBSTRING(tmp,29,9))='' THEN NULL ELSE to_number(SUBSTRING(tmp,29,9),'999999999') END AS dcntlo,
  CASE WHEN trim(SUBSTRING(tmp,38,7))='' THEN NULL ELSE to_number(SUBSTRING(tmp,38,7),'9999999') END AS dnumql,
  CASE WHEN trim(SUBSTRING(tmp,45,7))='' THEN NULL ELSE to_number(SUBSTRING(tmp,45,7),'999999') END AS ddenql,
  SUBSTRING(tmp,52,20) AS dfilot,
  CASE WHEN trim(SUBSTRING(tmp,72,8))='' THEN NULL ELSE to_date(SUBSTRING(tmp,72,8),'DDMMYYYY') END AS datact,
  SUBSTRING(tmp,83,6) AS dnuprol,
  SUBSTRING(tmp,89,5) AS dreflf,
  SUBSTRING(tmp,94,4) AS ccocif,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,18),' ', '0') AS pdl,
  REPLACE(REPLACE('${ANNEE}'||SUBSTRING(tmp,1,2)||SUBSTRING(tmp,83,6),' ', '0'),'+','¤') AS comptecommunal,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,15),' ', '0') AS parcelle
FROM ${PREFIXE}pdll WHERE SUBSTRING(tmp,26,2) ='30';
-- traitement: lotslocaux;
INSERT INTO ${PREFIXE}lotslocaux
(
 lotslocaux, annee, ccodepl, ccodirl, ccocoml, ccoprel, ccosecl, dnuplal, dnupdl, dnulot, ccodebpb, ccodird, ccocomb, ccopreb, invloc, dnumql, ddenql,
 lots, local00, local10
)
SELECT DISTINCT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,25)||SUBSTRING(tmp,37,10),' ', '0') AS lotslocaux,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodepl,
  SUBSTRING(tmp,3,1) AS ccodirl,
  SUBSTRING(tmp,4,3) AS ccocoml,
  SUBSTRING(tmp,7,3) AS ccoprel,
  SUBSTRING(tmp,10,2) AS ccosecl,
  SUBSTRING(tmp,12,4) AS dnuplal,
  SUBSTRING(tmp,16,3) AS dnupdl,
  SUBSTRING(tmp,19,7) AS dnulot,
  SUBSTRING(tmp,28,2) AS ccodebpb,
  SUBSTRING(tmp,30,1) AS ccodird,
  SUBSTRING(tmp,31,3) AS ccocomb,
  SUBSTRING(tmp,34,3) AS ccopreb,
  SUBSTRING(tmp,37,10) AS invloc,
  SUBSTRING(tmp,47,7) AS dnumql,
  SUBSTRING(tmp,54,7) AS ddenql,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,25),' ', '0') AS lots,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,37,10),' ', '0') AS local00,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,37,10),' ', '0') AS local10
FROM ${PREFIXE}lloc;
-- traitement: commune;
INSERT INTO ${PREFIXE}commune
(
 commune, annee, ccodep, ccodir, ccocom, clerivili, libcom, typcom, ruract, carvoi, indpop, poprel, poppart, popfict, annul, dteannul, dtecreart, codvoi,
 typvoi, indldnbat, motclas
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,6),' ', '0') AS commune,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  SUBSTRING(tmp,11,1) AS clerivili,
  SUBSTRING(tmp,12,30) AS libcom,
  CASE WHEN trim(SUBSTRING(tmp,43,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,43,1)) END AS typcom,
  SUBSTRING(tmp,46,1) AS ruract,
  SUBSTRING(tmp,49,1) AS carvoi,
  SUBSTRING(tmp,50,1) AS indpop,
  to_number(SUBSTRING(tmp,53,7),'0000000') AS poprel,
  to_number(SUBSTRING(tmp,60,7),'9999999') AS poppart,
  to_number(SUBSTRING(tmp,67,7),'0000000') AS popfict,
  SUBSTRING(tmp,74,1) AS annul,
  SUBSTRING(tmp,75,7) AS dteannul,
  SUBSTRING(tmp,82,7) AS dtecreart,
  SUBSTRING(tmp,104,5) AS codvoi,
  SUBSTRING(tmp,109,1) AS typvoi,
  SUBSTRING(tmp,110,1) AS indldnbat,
  SUBSTRING(tmp,113,8) AS motclas
FROM ${PREFIXE}fanr WHERE SUBSTRING(tmp,4,3)  != ' ' AND trim(SUBSTRING(tmp,7,4))='';
-- traitement: voie;
INSERT INTO ${PREFIXE}voie
(
 voie, annee, ccodep, ccodir, ccocom, natvoiriv, ccoriv, clerivili, natvoi, libvoi, typcom, ruract, carvoi, indpop, poprel, poppart, popfict, annul, dteannul,
 dtecreart, codvoi, typvoi, indldnbat, motclas,
 commune
)
SELECT
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,6)||SUBSTRING(tmp,104,5),' ', '0') AS voie,
  '${ANNEE}',
  SUBSTRING(tmp,1,2) AS ccodep,
  SUBSTRING(tmp,3,1) AS ccodir,
  SUBSTRING(tmp,4,3) AS ccocom,
  CASE WHEN trim(SUBSTRING(tmp,7,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,7,1)) END AS natvoiriv,
  SUBSTRING(tmp,7,4) AS ccoriv,
  SUBSTRING(tmp,11,1) AS clerivili,
  SUBSTRING(tmp,12,4) AS natvoi,
  SUBSTRING(tmp,16,26) AS libvoi,
  CASE WHEN trim(SUBSTRING(tmp,43,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,43,1)) END AS typcom,
  SUBSTRING(tmp,46,1) AS ruract,
  CASE WHEN trim(SUBSTRING(tmp,49,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,49,1)) END AS carvoi,
  SUBSTRING(tmp,50,1) AS indpop,
  SUBSTRING(tmp,53,7) AS poprel,
  to_number(SUBSTRING(tmp,60,7),'0000000') AS poppart,
  to_number(SUBSTRING(tmp,67,7),'0000000') AS popfict,
  CASE WHEN trim(SUBSTRING(tmp,74,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,74,1)) END AS annul,
  SUBSTRING(tmp,75,7) AS dteannul,
  SUBSTRING(tmp,82,7) AS dtecreart,
  SUBSTRING(tmp,104,5) AS codvoi,
  CASE WHEN trim(SUBSTRING(tmp,109,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,109,1)) END AS typvoi,
  CASE WHEN trim(SUBSTRING(tmp,110,1))='' THEN NULL ELSE trim(SUBSTRING(tmp,110,1)) END AS indldnbat,
  SUBSTRING(tmp,113,8) AS motclas,
  REPLACE('${ANNEE}'||SUBSTRING(tmp,1,6),' ', '0') AS commune
FROM ${PREFIXE}fanr WHERE trim(SUBSTRING(tmp,4,3))  != '' AND trim(SUBSTRING(tmp,7,4))  != '';
-- purge des doublons : voie;
DELETE FROM ${PREFIXE}voie WHERE codvoi IN (SELECT codvoi FROM ${PREFIXE}voie WHERE annee='${ANNEE}' GROUP BY codvoi HAVING COUNT(*) > 1) AND annee='${ANNEE}';
-- ajout données manquantes : comptecommunal à partir de lots;
INSERT INTO ${PREFIXE}comptecommunal
 ( comptecommunal, annee, ccodep, ccodir, ccocom, dnupro, ajoutcoherence)
SELECT REPLACE(REPLACE(annee||ccodep||dnuprol,' ', '0'),'+','¤') AS comptecommunal, annee, ccodep, ccodir, ccocom, dnuprol,'O'
FROM ${PREFIXE}lots
WHERE   '-'||annee||'-'||ccodep||'-'||ccodir||'-'||ccocom||'-'||dnuprol||'-' NOT IN
    (
        SELECT '-'||l.annee||'-'||l.ccodep||'-'||l.ccodir||'-'||l.ccocom||'-'||l.dnuprol||'-'
        FROM ${PREFIXE}lots l, ${PREFIXE}comptecommunal c
        WHERE l.ccodep = c.ccodep AND l.dnuprol = c.dnupro AND l.annee='${ANNEE}' and c.annee='${ANNEE}'
    ) and annee='${ANNEE}'
GROUP BY annee, ccodep, ccodir, ccocom, dnuprol;
-- ajout données manquantes : parcelle à partir de local00;
INSERT INTO ${PREFIXE}parcelle
 ( parcelle, annee, ccodep, ccodir, ccocom, ccopre, ccosec, dnupla, ajoutcoherence, comptecommunal,voie)
SELECT
  REPLACE(annee||ccodep||ccodir||ccocom||ccopre||ccosec||dnupla,' ','0') as parcelle,
  annee,
  ccodep,
  ccodir,
  ccocom,
  ccopre,
  ccosec,
  dnupla,
  'O' ,
  REPLACE(annee||ccodep||dnupro,' ', '0'),
  REPLACE(annee||ccodep||ccodir||ccocom||ccovoi,' ', '0')
FROM ${PREFIXE}local10
WHERE invar not IN
    (
        SELECT invar
        FROM ${PREFIXE}local10 l, ${PREFIXE}parcelle p
        WHERE
            l.ccodep=p.ccodep AND l.ccodir=p.ccodir AND l.ccocom=p.ccocom AND l.ccopre=p.ccopre AND l.ccosec=p.ccosec AND
            l.dnupla=p.dnupla AND l.annee='${ANNEE}' AND p.annee='${ANNEE}'
    ) AND annee='${ANNEE}'
GROUP BY annee, ccodep, ccodir, ccocom, ccopre, ccosec, dnupla, dnupro, ccovoi;
-- ajout données manquantes : comptecommunal à partir de parcelles;
INSERT INTO ${PREFIXE}comptecommunal
 ( comptecommunal, annee, ccodep, ccodir, ccocom, dnupro, ajoutcoherence)
SELECT REPLACE(REPLACE(annee||ccodep||dnupro,' ', '0'),'+','¤') AS comptecommunal, annee, ccodep, ccodir, ccocom, dnupro,'O'
FROM ${PREFIXE}parcelle
WHERE   '-'||annee||'-'||ccodep||'-'||ccodir||'-'||ccocom||'-'||dnupro||'-' NOT IN
    (
        SELECT '-'||p.annee||'-'||p.ccodep||'-'||p.ccodir||'-'||p.ccocom||'-'||p.dnupro||'-'
        FROM ${PREFIXE}parcelle p, ${PREFIXE}comptecommunal c
        WHERE p.ccodep = c.ccodep AND p.dnupro = c.dnupro AND p.annee='${ANNEE}' and c.annee='${ANNEE}'
    ) and annee='${ANNEE}'
GROUP BY annee, ccodep, ccodir, ccocom, dnupro;
-- suppression des index pour optimisation;
DROP INDEX ${PREFIXE}idx_voie_codvoi;
DROP INDEX ${PREFIXE}idx_lots_comptecommunal;
-- FORMATAGE DONNEES : FIN;
