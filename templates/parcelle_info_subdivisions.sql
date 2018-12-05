SELECT

'<table class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3 width="100p">' ||
    '<tr>' ||
        '<th>Lettre</th>' ||
        '<th>Groupe</th>' ||
        '<th>Sous-Groupe</th>' ||
        '<th>Nature</th>' ||
        '<th>Classe</th>' ||
        '<th>Contenance</th>' ||
        '<th>Revenu cadastral</th>' ||
    '</tr>' ||
    string_agg(Coalesce(line, ''), '') ||
'</table>'


FROM (
    SELECT
    '<tr>' ||
        '<td>' || Coalesce(s.ccosub, '') || '</td>' ||
        '<td>' || Coalesce(cgrnum_lib, '') || '</td>' ||
        '<td>' || Coalesce(dsgrpf_lib, '') || '</td>' ||
        '<td>' || Coalesce(s.cnatsp, '') || '</td>' ||
        '<td>' || Coalesce(s.dclssf, '') || '</td>' ||
        '<td>' || s.dcntsf || ' m²</td>' ||
        '<td>' || s.drcsuba || '</td>' ||
    '</tr>'
    AS line
    FROM suf s
    LEFT JOIN "cgrnum" ON s.cgrnum = cgrnum.cgrnum
    LEFT JOIN "dsgrpf" ON s.dsgrpf = dsgrpf.dsgrpf
    WHERE 2>1 AND s.parcelle = '%s'
) foo

