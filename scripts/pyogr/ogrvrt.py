# Based on ogr2vrt.py implementation by Frank Warmerdam included in GDAL/OGR
###############################################################################
# Copyright (c) 2009, Frank Warmerdam <warmerdam@pobox.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################

from osgeo import ogr, gdal
from string import Template
import tempfile

def GeomType2Name( type ):
    if type == ogr.wkbUnknown:
        return 'wkbUnknown'
    elif type == ogr.wkbPoint:
        return 'wkbPoint'
    elif type == ogr.wkbLineString:
        return 'wkbLineString'
    elif type == ogr.wkbPolygon:
        return 'wkbPolygon'
    elif type == ogr.wkbMultiPoint:
        return 'wkbMultiPoint'
    elif type == ogr.wkbMultiLineString:
        return 'wkbMultiLineString'
    elif type == ogr.wkbMultiPolygon:
        return 'wkbMultiPolygon'
    elif type == ogr.wkbGeometryCollection:
        return 'wkbGeometryCollection'
    elif type == ogr.wkbNone:
        return 'wkbNone'
    elif type == ogr.wkbLinearRing:
        return 'wkbLinearRing'
    else:
        return 'wkbUnknown'

#############################################################################
def Esc(x):
    return gdal.EscapeString( x, gdal.CPLES_XML )

def transformed_template(template, substitutions):
    vrt_templ = Template(open(template).read())
    vrt_xml = vrt_templ.substitute(substitutions)
    vrt = tempfile.mktemp( '.vrt',  'ogr_',  '/vsimem')
    # Create in-memory file
    gdal.FileFromMemBuffer(vrt, vrt_xml)
    return vrt

def free_template(vrt):
    # Free memory associated with the in-memory file
    gdal.Unlink(vrt)

def transformed_datasource(template, substitutions):
    vrt = transformed_template(template, substitutions)
    ds = ogr.Open(vrt)
    return ds

def close_datasource(ds):
   if ds is not None:
       ds.Destroy()

def ogr2vrt(infile,
            outfile = None,
            layer_list = [],
            relative = "0",
            schema=0):

    #############################################################################
    # Open the datasource to read.

    src_ds = ogr.Open( infile, update = 0 )

    if src_ds is None:
        return None

    if schema:
        infile = '@dummy@'

    if len(layer_list) == 0:
        for layer in src_ds:
            layer_list.append( layer.GetLayerDefn().GetName() )

    #############################################################################
    # Start the VRT file.

    vrt = '<OGRVRTDataSource>\n'

    #############################################################################
    #	Process each source layer.

    for name in layer_list:
        layer = src_ds.GetLayerByName(name)
        layerdef = layer.GetLayerDefn()

        vrt += '  <OGRVRTLayer name="%s">\n' % Esc(name)
        vrt += '    <SrcDataSource relativeToVRT="%s" shared="%d">%s</SrcDataSource>\n' \
               % (relative,not schema,Esc(infile))
        if schema:
            vrt += '    <SrcLayer>@dummy@</SrcLayer>\n'
        else:
            vrt += '    <SrcLayer>%s</SrcLayer>\n' % Esc(name)
        vrt += '    <GeometryType>%s</GeometryType>\n' \
               % GeomType2Name(layerdef.GetGeomType())
        srs = layer.GetSpatialRef()
        if srs is not None:
            vrt += '    <LayerSRS>%s</LayerSRS>\n' \
                   % (Esc(srs.ExportToWkt()))

        # Process all the fields.
        for fld_index in range(layerdef.GetFieldCount()):
            src_fd = layerdef.GetFieldDefn( fld_index )
            if src_fd.GetType() == ogr.OFTInteger:
                type = 'Integer'
            elif src_fd.GetType() == ogr.OFTString:
                type = 'String'
            elif src_fd.GetType() == ogr.OFTReal:
                type = 'Real'
            elif src_fd.GetType() == ogr.OFTStringList:
                type = 'StringList'
            elif src_fd.GetType() == ogr.OFTIntegerList:
                type = 'IntegerList'
            elif src_fd.GetType() == ogr.OFTRealList:
                type = 'RealList'
            elif src_fd.GetType() == ogr.OFTBinary:
                type = 'Binary'
            elif src_fd.GetType() == ogr.OFTDate:
                type = 'Date'
            elif src_fd.GetType() == ogr.OFTTime:
                type = 'Time'
            elif src_fd.GetType() == ogr.OFTDateTime:
                type = 'DateTime'
            else:
                type = 'String'

            vrt += '    <Field name="%s" type="%s"' \
                   % (Esc(src_fd.GetName()), type)
            if not schema:
                vrt += ' src="%s"' % Esc(src_fd.GetName())
            if src_fd.GetWidth() > 0:
                vrt += ' width="%d"' % src_fd.GetWidth()
            if src_fd.GetPrecision() > 0:
                vrt += ' precision="%d"' % src_fd.GetPrecision()
            vrt += '/>\n'

        vrt += '  </OGRVRTLayer>\n'

    vrt += '</OGRVRTDataSource>\n'

    if outfile is not None:
        f = open(outfile, "w")
        f.write(vrt)
        f.close()

    return vrt
