--
-- PostgreSQL database dump openexemple
--

--
-- Name: om_collectivite; Type: TABLE; 
--

CREATE TABLE om_collectivite (
    om_collectivite integer NOT NULL,
    libelle character varying(100) NOT NULL,
    niveau character varying(1) NOT NULL
);


--
-- Name: om_collectivite_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_collectivite_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_droit; Type: TABLE; 
--

CREATE TABLE om_droit (
    om_droit integer NOT NULL,
    libelle character varying(100) NOT NULL,
    om_profil integer NOT NULL
);


--
-- Name: om_droit_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_droit_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_droit_seq; Type: SEQUENCE OWNED BY; 
--

ALTER SEQUENCE om_droit_seq OWNED BY om_droit.om_droit;


--
-- Name: om_etat; Type: TABLE; 
--

CREATE TABLE om_etat (
    om_etat integer NOT NULL,
    om_collectivite integer NOT NULL,
    id character varying(50) NOT NULL,
    libelle character varying(50) NOT NULL,
    actif boolean,
    orientation character varying(2) NOT NULL,
    format character varying(5) NOT NULL,
    footerfont character varying(20) NOT NULL,
    footerattribut character varying(20) DEFAULT ''::character varying NOT NULL,
    footertaille integer NOT NULL,
    logo character varying(30) NOT NULL,
    logoleft integer NOT NULL,
    logotop integer NOT NULL,
    titre text NOT NULL,
    titreleft integer NOT NULL,
    titretop integer NOT NULL,
    titrelargeur integer NOT NULL,
    titrehauteur integer NOT NULL,
    titrefont character varying(20) NOT NULL,
    titreattribut character varying(20) DEFAULT ''::character varying NOT NULL,
    titretaille integer NOT NULL,
    titrebordure character varying(20) NOT NULL,
    titrealign character varying(20) NOT NULL,
    corps text NOT NULL,
    corpsleft integer NOT NULL,
    corpstop integer NOT NULL,
    corpslargeur integer NOT NULL,
    corpshauteur integer NOT NULL,
    corpsfont character varying(20) NOT NULL,
    corpsattribut character varying(20) DEFAULT ''::character varying NOT NULL,
    corpstaille integer NOT NULL,
    corpsbordure character varying(20) NOT NULL,
    corpsalign character varying(20) NOT NULL,
    om_sql text NOT NULL,
    sousetat text DEFAULT ''::text NOT NULL,
    se_font character varying(20) NOT NULL,
    se_margeleft integer NOT NULL,
    se_margetop integer NOT NULL,
    se_margeright integer NOT NULL,
    se_couleurtexte character varying(11) NOT NULL
);


--
-- Name: om_etat_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_etat_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_lettretype; Type: TABLE; 
--

CREATE TABLE om_lettretype (
    om_lettretype integer NOT NULL,
    om_collectivite integer NOT NULL,
    id character varying(50) NOT NULL,
    libelle character varying(50) NOT NULL,
    actif boolean,
    orientation character varying(2) NOT NULL,
    format character varying(5) NOT NULL,
    logo character varying(30) NOT NULL,
    logoleft integer NOT NULL,
    logotop integer NOT NULL,
    titre text NOT NULL,
    titreleft integer NOT NULL,
    titretop integer NOT NULL,
    titrelargeur integer NOT NULL,
    titrehauteur integer NOT NULL,
    titrefont character varying(20) NOT NULL,
    titreattribut character varying(20) DEFAULT ''::character varying NOT NULL,
    titretaille integer NOT NULL,
    titrebordure character varying(20) NOT NULL,
    titrealign character varying(20) NOT NULL,
    corps text NOT NULL,
    corpsleft integer NOT NULL,
    corpstop integer NOT NULL,
    corpslargeur integer NOT NULL,
    corpshauteur integer NOT NULL,
    corpsfont character varying(20) NOT NULL,
    corpsattribut character varying(20) DEFAULT ''::character varying NOT NULL,
    corpstaille integer NOT NULL,
    corpsbordure character varying(20) NOT NULL,
    corpsalign character varying(20) NOT NULL,
    om_sql text NOT NULL
);


--
-- Name: om_lettretype_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_lettretype_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_parametre; Type: TABLE; 
--

CREATE TABLE om_parametre (
    om_parametre integer NOT NULL,
    libelle character varying(20) NOT NULL,
    valeur character varying(50) NOT NULL,
    om_collectivite integer NOT NULL
);


--
-- Name: om_parametre_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_parametre_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_parametre_seq; Type: SEQUENCE OWNED BY; 
--

ALTER SEQUENCE om_parametre_seq OWNED BY om_parametre.om_parametre;


--
-- Name: om_profil; Type: TABLE;
--

CREATE TABLE om_profil (
    om_profil integer NOT NULL,
    libelle character varying(100) NOT NULL,
    hierarchie integer DEFAULT 0 NOT NULL
);


--
-- Name: om_profil_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_profil_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_profil_seq; Type: SEQUENCE OWNED BY; 
--

ALTER SEQUENCE om_profil_seq OWNED BY om_profil.om_profil;


--
-- Name: om_sig_map; Type: TABLE; 
--

CREATE TABLE om_sig_map (
    om_sig_map integer NOT NULL,
    om_collectivite integer NOT NULL,
    id character varying(50) NOT NULL,
    libelle character varying(50) NOT NULL,
    actif boolean,
    zoom character varying(3) NOT NULL,
    fond_osm character varying(3) NOT NULL,
    fond_bing character varying(3) NOT NULL,
    fond_sat character varying(3) NOT NULL,
    layer_info character varying(3) NOT NULL,
    etendue character varying(60) NOT NULL,
    projection_externe character varying(60) NOT NULL,
    url text NOT NULL,
    om_sql text NOT NULL,
    maj character varying(3) NOT NULL,
    table_update character varying(30) NOT NULL,
    champ character varying(30) NOT NULL,
    retour character varying(50) NOT NULL,
    type_geometrie character varying(30),
    lib_geometrie character varying(50)
);


--
-- Name: om_sig_map_comp; Type: TABLE; 
--

CREATE TABLE om_sig_map_comp (
    om_sig_map_comp integer NOT NULL,
    om_sig_map integer NOT NULL,
    libelle character varying(50) NOT NULL,
    ordre integer NOT NULL,
    actif character varying(3),
    comp_maj character varying(3),
    type_geometrie character varying(30),
    comp_table_update character varying(30),
    comp_champ character varying(30)
);


--
-- Name: om_sig_map_comp_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_sig_map_comp_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_sig_map_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_sig_map_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_sig_map_wms; Type: TABLE; 
--

CREATE TABLE om_sig_map_wms (
    om_sig_map_wms integer NOT NULL,
    om_sig_wms integer NOT NULL,
    om_sig_map integer NOT NULL,
    ol_map character varying(50) NOT NULL,
    ordre integer NOT NULL,
    visibility character varying(3),
    panier character varying(3),
    pa_nom character varying(50),
    pa_layer character varying(50),
    pa_attribut character varying(50),
    pa_encaps character varying(3),
    pa_sql text,
    pa_type_geometrie character varying(30),
    sql_filter text,
    baselayer character varying(3),
    singletile character varying(3),
	maxzoomlevel integer
);


--
-- Name: om_sig_map_wms_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_sig_map_wms_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_sig_wms; Type: TABLE; 
--

CREATE TABLE om_sig_wms (
    om_sig_wms integer NOT NULL,
    libelle character varying(50) NOT NULL,
    om_collectivite integer NOT NULL,
    id character varying(50) NOT NULL,
    chemin character varying(255) NOT NULL,
    couches character varying(255) NOT NULL,
	cache_type character varying(3),
	cache_gfi_chemin character varying(255),
	cache_gfi_couches character varying(255)
);


--
-- Name: om_sig_wms_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_sig_wms_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_sousetat; Type: TABLE; 
--

CREATE TABLE om_sousetat (
    om_sousetat integer NOT NULL,
    om_collectivite integer NOT NULL,
    id character varying(50) NOT NULL,
    libelle character varying(50) NOT NULL,
    actif boolean,
    titre text NOT NULL,
    titrehauteur integer NOT NULL,
    titrefont character varying(20) NOT NULL,
    titreattribut character varying(20) DEFAULT ''::character varying NOT NULL,
    titretaille integer NOT NULL,
    titrebordure character varying(20) NOT NULL,
    titrealign character varying(20) NOT NULL,
    titrefond character varying(20) NOT NULL,
    titrefondcouleur character varying(11) NOT NULL,
    titretextecouleur character varying(11) NOT NULL,
    intervalle_debut integer NOT NULL,
    intervalle_fin integer NOT NULL,
    entete_flag character varying(20) NOT NULL,
    entete_fond character varying(20) NOT NULL,
    entete_orientation character varying(100) NOT NULL,
    entete_hauteur integer NOT NULL,
    entetecolone_bordure character varying(200) NOT NULL,
    entetecolone_align character varying(100) NOT NULL,
    entete_fondcouleur character varying(11) NOT NULL,
    entete_textecouleur character varying(11) NOT NULL,
    tableau_largeur integer NOT NULL,
    tableau_bordure character varying(20) NOT NULL,
    tableau_fontaille integer NOT NULL,
    bordure_couleur character varying(11) NOT NULL,
    se_fond1 character varying(11) NOT NULL,
    se_fond2 character varying(11) NOT NULL,
    cellule_fond character varying(20) NOT NULL,
    cellule_hauteur integer NOT NULL,
    cellule_largeur character varying(200) NOT NULL,
    cellule_bordure_un character varying(200) NOT NULL,
    cellule_bordure character varying(200) NOT NULL,
    cellule_align character varying(100) NOT NULL,
    cellule_fond_total character varying(20) NOT NULL,
    cellule_fontaille_total integer NOT NULL,
    cellule_hauteur_total integer NOT NULL,
    cellule_fondcouleur_total character varying(11) NOT NULL,
    cellule_bordure_total character varying(200) NOT NULL,
    cellule_align_total character varying(100) NOT NULL,
    cellule_fond_moyenne character varying(20) NOT NULL,
    cellule_fontaille_moyenne integer NOT NULL,
    cellule_hauteur_moyenne integer NOT NULL,
    cellule_fondcouleur_moyenne character varying(11) NOT NULL,
    cellule_bordure_moyenne character varying(200) NOT NULL,
    cellule_align_moyenne character varying(100) NOT NULL,
    cellule_fond_nbr character varying(20) NOT NULL,
    cellule_fontaille_nbr integer NOT NULL,
    cellule_hauteur_nbr integer NOT NULL,
    cellule_fondcouleur_nbr character varying(11) NOT NULL,
    cellule_bordure_nbr character varying(200) NOT NULL,
    cellule_align_nbr character varying(100) NOT NULL,
    cellule_numerique character varying(200) NOT NULL,
    cellule_total character varying(100) NOT NULL,
    cellule_moyenne character varying(100) NOT NULL,
    cellule_compteur character varying(100) NOT NULL,
    om_sql text NOT NULL
);


--
-- Name: om_sousetat_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_sousetat_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_tdb; Type: TABLE; 
--

CREATE TABLE om_tdb (
    om_tdb integer NOT NULL,
    login character varying(40) NOT NULL,
    bloc character varying(10) NOT NULL,
    "position" integer,
    om_widget integer NOT NULL
);


--
-- Name: om_tdb_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_tdb_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_utilisateur; Type: TABLE; 
--

CREATE TABLE om_utilisateur (
    om_utilisateur integer NOT NULL,
    nom character varying(30) NOT NULL,
    email character varying(40) NOT NULL,
    login character varying(30) NOT NULL,
    pwd character varying(100) NOT NULL,
    om_collectivite integer NOT NULL,
    om_type character varying(20) DEFAULT 'DB'::character varying NOT NULL,
    om_profil integer NOT NULL
);


--
-- Name: om_utilisateur_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_utilisateur_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_utilisateur_seq; Type: SEQUENCE OWNED BY; 
--

ALTER SEQUENCE om_utilisateur_seq OWNED BY om_utilisateur.om_utilisateur;


--
-- Name: om_widget; Type: TABLE; 
--

CREATE TABLE om_widget (
    om_widget integer NOT NULL,
    om_collectivite integer NOT NULL,
    libelle character varying(40) NOT NULL,
    lien character varying(80) NOT NULL,
    texte text NOT NULL,
    om_profil integer NOT NULL
);


--
-- Name: om_widget_seq; Type: SEQUENCE; 
--

CREATE SEQUENCE om_widget_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: om_collectivite_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_collectivite
    ADD CONSTRAINT om_collectivite_pkey PRIMARY KEY (om_collectivite);


--
-- Name: om_droit_libelle_om_profil_key; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_droit
    ADD CONSTRAINT om_droit_libelle_om_profil_key UNIQUE (libelle, om_profil);


--
-- Name: om_droit_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_droit
    ADD CONSTRAINT om_droit_pkey PRIMARY KEY (om_droit);


--
-- Name: om_etat_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_etat
    ADD CONSTRAINT om_etat_pkey PRIMARY KEY (om_etat);


--
-- Name: om_lettretype_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_lettretype
    ADD CONSTRAINT om_lettretype_pkey PRIMARY KEY (om_lettretype);


--
-- Name: om_parametre_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_parametre
    ADD CONSTRAINT om_parametre_pkey PRIMARY KEY (om_parametre);


--
-- Name: om_profil_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_profil
    ADD CONSTRAINT om_profil_pkey PRIMARY KEY (om_profil);


--
-- Name: om_sig_map_comp_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_sig_map_comp
    ADD CONSTRAINT om_sig_map_comp_pkey PRIMARY KEY (om_sig_map_comp);


--
-- Name: om_sig_map_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_sig_map
    ADD CONSTRAINT om_sig_map_pkey PRIMARY KEY (om_sig_map);


--
-- Name: om_sig_map_wms_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_sig_map_wms
    ADD CONSTRAINT om_sig_map_wms_pkey PRIMARY KEY (om_sig_map_wms);


--
-- Name: om_sig_wms_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_sig_wms
    ADD CONSTRAINT om_sig_wms_pkey PRIMARY KEY (om_sig_wms);


--
-- Name: om_sousetat_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_sousetat
    ADD CONSTRAINT om_sousetat_pkey PRIMARY KEY (om_sousetat);


--
-- Name: om_tdb_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_tdb
    ADD CONSTRAINT om_tdb_pkey PRIMARY KEY (om_tdb);


--
-- Name: om_utilisateur_login_key; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_utilisateur
    ADD CONSTRAINT om_utilisateur_login_key UNIQUE (login);


--
-- Name: om_utilisateur_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_utilisateur
    ADD CONSTRAINT om_utilisateur_pkey PRIMARY KEY (om_utilisateur);


--
-- Name: om_widget_pkey; Type: CONSTRAINT; 
--

ALTER TABLE ONLY om_widget
    ADD CONSTRAINT om_widget_pkey PRIMARY KEY (om_widget);


--
-- Name: om_droit_om_profil_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_droit
    ADD CONSTRAINT om_droit_om_profil_fkey FOREIGN KEY (om_profil) REFERENCES om_profil(om_profil);


--
-- Name: om_etat_om_collectivite_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_etat
    ADD CONSTRAINT om_etat_om_collectivite_fkey FOREIGN KEY (om_collectivite) REFERENCES om_collectivite(om_collectivite);


--
-- Name: om_lettretype_om_collectivite_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_lettretype
    ADD CONSTRAINT om_lettretype_om_collectivite_fkey FOREIGN KEY (om_collectivite) REFERENCES om_collectivite(om_collectivite);


--
-- Name: om_parametre_om_collectivite_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_parametre
    ADD CONSTRAINT om_parametre_om_collectivite_fkey FOREIGN KEY (om_collectivite) REFERENCES om_collectivite(om_collectivite);


--
-- Name: om_sig_map_comp_om_sig_map_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_sig_map_comp
    ADD CONSTRAINT om_sig_map_comp_om_sig_map_fkey FOREIGN KEY (om_sig_map) REFERENCES om_sig_map(om_sig_map);


--
-- Name: om_sig_map_om_collectivite_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_sig_map
    ADD CONSTRAINT om_sig_map_om_collectivite_fkey FOREIGN KEY (om_collectivite) REFERENCES om_collectivite(om_collectivite);


--
-- Name: om_sig_map_wms_om_sig_map_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_sig_map_wms
    ADD CONSTRAINT om_sig_map_wms_om_sig_map_fkey FOREIGN KEY (om_sig_map) REFERENCES om_sig_map(om_sig_map);


--
-- Name: om_sig_map_wms_om_sig_wms_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_sig_map_wms
    ADD CONSTRAINT om_sig_map_wms_om_sig_wms_fkey FOREIGN KEY (om_sig_wms) REFERENCES om_sig_wms(om_sig_wms);


--
-- Name: om_sig_wms_om_collectivite_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_sig_wms
    ADD CONSTRAINT om_sig_wms_om_collectivite_fkey FOREIGN KEY (om_collectivite) REFERENCES om_collectivite(om_collectivite);


--
-- Name: om_sousetat_om_collectivite_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_sousetat
    ADD CONSTRAINT om_sousetat_om_collectivite_fkey FOREIGN KEY (om_collectivite) REFERENCES om_collectivite(om_collectivite);


--
-- Name: om_tdb_om_widget_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_tdb
    ADD CONSTRAINT om_tdb_om_widget_fkey FOREIGN KEY (om_widget) REFERENCES om_widget(om_widget);


--
-- Name: om_utilisateur_om_collectivite_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_utilisateur
    ADD CONSTRAINT om_utilisateur_om_collectivite_fkey FOREIGN KEY (om_collectivite) REFERENCES om_collectivite(om_collectivite);


--
-- Name: om_utilisateur_om_profil_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_utilisateur
    ADD CONSTRAINT om_utilisateur_om_profil_fkey FOREIGN KEY (om_profil) REFERENCES om_profil(om_profil);


--
-- Name: om_widget_om_collectivite_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_widget
    ADD CONSTRAINT om_widget_om_collectivite_fkey FOREIGN KEY (om_collectivite) REFERENCES om_collectivite(om_collectivite);


--
-- Name: om_widget_om_profil_fkey; Type: FK CONSTRAINT; 
--

ALTER TABLE ONLY om_widget
    ADD CONSTRAINT om_widget_om_profil_fkey FOREIGN KEY (om_profil) REFERENCES om_profil(om_profil);


---
--- Data
---

INSERT INTO om_collectivite (om_collectivite, libelle, niveau) VALUES
(1, 'LIBREVILLE', '1'),
(2, 'MULTI', '2');

INSERT INTO om_parametre VALUES
(1, 'ville', 'LIBREVILLE', 1),
(2, 'ville', 'MULTI', 2);

INSERT INTO om_profil VALUES
(1, 'ADMINISTRATEUR', 5),
(2, 'SUPER UTILISATEUR', 4),
(3, 'UTILISATEUR', 3),
(4, 'UTILISATEUR LIMITE', 2),
(5, 'CONSULTATION', 1);

INSERT INTO om_droit VALUES
(1, 'om_utilisateur', 1),
(2, 'om_droit', 1),
(3, 'om_profil', 1),
(4, 'om_collectivite', 1),
(5, 'om_parametre', 2),
(6, 'om_etat', 2),
(7, 'om_sousetat', 2),
(8, 'om_lettretype', 2),
(9, 'gen', 1),
(10, 'om_sig_map', 2),
(11, 'om_sig_map_comp', 2),
(12, 'om_sig_map_wms', 2),
(13, 'om_sig_wms', 2),
(14, 'directory', 1),
(15, 'import', 1),
(16, 'edition', 3),
(17, 'reqmo', 2),
(18, 'password', 5),
(19, 'om_widget', 2),
(20, 'om_tdb', 2);

INSERT INTO om_utilisateur (om_utilisateur, nom, login, pwd, om_profil, email, om_collectivite) VALUES
(1, 'Administrateur', 'admin', '21232f297a57a5a743894a0e4a801fc3', 1, 'contact@openmairie.org', 1),
(2, 'Démonstration', 'demo', 'fe01ce2a7fbac8fafaed7c982a04e229', 1, 'contact@openmairie.org', 1);

INSERT INTO om_etat (om_etat, om_collectivite, id, libelle, actif, orientation, format, footerfont, footerattribut, footertaille, logo, logoleft, logotop, titre, titreleft, titretop, titrelargeur, titrehauteur, titrefont, titreattribut, titretaille, titrebordure, titrealign, corps, corpsleft, corpstop, corpslargeur, corpshauteur, corpsfont, corpsattribut, corpstaille, corpsbordure, corpsalign, om_sql, sousetat, se_font, se_margeleft, se_margetop, se_margeright, se_couleurtexte) VALUES
(1, 1, 'om_collectivite', 'om_collectivite gen le 12/11/2010', TRUE, 'P', 'A4', 'helvetica', 'I', 8, 'logopdf.png', 58, 7, 'le &aujourdhui', 41, 36, 130, 10, 'helvetica', 'B', 15, '0', 'C', E'[om_collectivite]\r\n[libelle]\r\n[niveau]', 7, 57, 195, 5, 'helvetica', '', 10, '0', 'J', 'select om_collectivite.om_collectivite as om_collectivite,om_collectivite.libelle as libelle,om_collectivite.niveau as niveau from &DB_PREFIXEom_collectivite where om_collectivite.om_collectivite=''&idx''', 'om_parametre.om_collectivite', 'helvetica', 8, 5, 5, '0-0-0');

INSERT INTO om_sousetat VALUES
(1, 1, 'om_parametre.om_collectivite', 'gen le 12/11/2010', TRUE, 'liste om_parametre', 10, 'helvetica', 'B', 10, '0', 'L', '0', '255-255-255', '0-0-0', 0, 5, '1', '1', '0|0|0', 7, 'TLB|TLB|LTBR', 'C|C|C', '255-255-255', '0-0-0', 195, '1', 10, '0-0-0', '243-246-246', '255-255-255', '1', 7, '65|65|65', 'TLB|TLB|LTBR', 'TLB|TLB|LTBR', 'C|C|C', '1', 10, 15, '255-255-255', 'TLB|TLB|LTBR', 'C|C|C', '1', 10, 5, '212-219-220', 'TLB|TLB|LTBR', 'C|C|C', '1', 10, 7, '255-255-255', 'TLB|TLB|LTBR', 'C|C|C', '999|999|999', '0|0|0', '0|0|0', '0|0|0', 'select om_parametre.om_parametre as om_parametre,om_parametre.libelle as libelle,om_parametre.valeur as valeur from &DB_PREFIXEom_parametre where om_parametre.om_collectivite=''&idx''');

INSERT INTO om_lettretype (om_lettretype, om_collectivite, id, libelle, actif, orientation, format, logo, logoleft, logotop, titre, titreleft, titretop, titrelargeur, titrehauteur, titrefont, titreattribut, titretaille, titrebordure, titrealign, corps, corpsleft, corpstop, corpslargeur, corpshauteur, corpsfont, corpsattribut, corpstaille, corpsbordure, corpsalign, om_sql) VALUES
(1, 1, 'om_utilisateur', 'lettre aux utilisateurs', TRUE, 'P', 'A4', 'logo.png', 10, 10, 'le &datecourrier', 130, 16, 0, 10, 'arial', '', 14, '0', 'L', 'Nous avons le plaisir de vous envoyer votre login et votre mot de passevotre login [login] Vous souhaitant bonne receptionVotre administrateur', 40, 106, 110, 5, 'times', '', 10, '0', 'J', 'select nom,login,om_collectivite.libelle as collectivite from &DB_PREFIXEom_utilisateur inner join &DB_PREFIXEom_collectivite on om_collectivite.om_collectivite=om_utilisateur.om_collectivite where om_utilisateur= &idx');

SELECT pg_catalog.setval('om_collectivite_seq', 3, false);
SELECT pg_catalog.setval('om_parametre_seq', 2, true);
SELECT pg_catalog.setval('om_profil_seq', 5, true);
SELECT pg_catalog.setval('om_droit_seq', 20, true);
SELECT pg_catalog.setval('om_utilisateur_seq', 2, true);
SELECT pg_catalog.setval('om_etat_seq', 2, false);
SELECT pg_catalog.setval('om_sousetat_seq', 2, false);
SELECT pg_catalog.setval('om_lettretype_seq', 2, false);


--
-- PostgreSQL database dump complete
--
