# -*- coding: utf-8 -*-

import sys, os

class GetMultiPolygonFromVec(object):
  __slots__ = ( 'listPar', 'listPfe', 'listFea', 'mapLyFea', 'mapFeaPfe', 'mapPfePar', 'mapParCor', 'mapParPno', 'mapPnoPar', 'path' )

  def __init__( self ) :
    self.listPar = []
    self.listPfe = []
    self.listFea = []
    self.mapLyFea = {}
    self.mapFeaPfe = {}
    self.mapPfePar = {}
    self.mapParCor = {}
    self.mapParPno = {}
    self.mapPnoPar = {}
    self.path = None

  def __call__( self, path ) :
    self.listPar = []
    self.listPfe = []
    self.listFea = []
    self.mapLyFea = {}
    self.mapFeaPfe = {}
    self.mapPfePar = {}
    self.mapParCor = {}
    self.mapParPno = {}
    self.mapPnoPar = {}
    self.path = os.path.abspath(path)
    if not self.__features__(): return {}
    if not self.__layers__(): return {}
    if not self.__arcs__(): return {}
    if not self.__coords__(): return {}
    if not self.__nodes__(): return {}
    mapPfePoly = self.__polygons__()

    mapLyFeaMulti = {}
    for ly,feas in self.mapLyFea.items() :
      mapLyFeaMulti[ ly ] ={}
      for fea in feas :
        multipolygon = []
        for pfe in self.mapFeaPfe[ fea ] :
          multipolygon += mapPfePoly[ pfe ]
        mapLyFeaMulti[ ly ][ fea ] = 'MULTIPOLYGON('+', '.join(['('+', '.join(['('+'),('.join([','.join([str(x)+' '+str(y) for x,y in ring ])])+')' for ring in poly])+')' for poly in multipolygon])+')'
    return mapLyFeaMulti

  def __features__( self ) :
    """ Find features with more than 1 faces """
    if not self.path : return False

    f = open( self.path, 'r' )
    if not f :return False

    osRTY = ''
    osRID = ''
    osSCP = ''
    lnkNb = 0
    lnkStartType = ''
    lnkStartName = ''
    lnkFaces = []
    for line in f :
      line = line.replace('\n', '').replace('\r', '')
      if len( line ) < 8 :
        continue;
      if line[:5] == 'RTYSA':
        osRTY = line[8:]
        osRID = ''
        osSCP = ''
        lnkNb = 0
        lnkStartType = ''
        lnkStartName = ''
        lnkFaces = []
      elif osRTY == 'LNK' and line[:5] == 'RIDSA':
        osRID = line[8:]
      elif osRTY == 'LNK' and line[:5] == 'SCPCP':
        osSCP = line[8:]
      elif osRTY == 'LNK' and line[:5] == 'FTCSN':
        lnkNb = int( line[8:] )
      elif osRTY == 'LNK' and lnkNb > 2 and line[:5] == 'FTPCP':
        lnkArray = line[8:].split(';')
        if not lnkStartType:
          lnkStartType = lnkArray[2]
          lnkStartName = lnkArray[3]
        elif lnkStartType and lnkStartType == 'FEA' and lnkArray[2] == 'PFE':
          lnkFaces.append( lnkArray[3] )
      elif osRTY == 'LNK' and lnkNb > 2 and len( lnkFaces ) == lnkNb-1 :
        lnkNb = 0
        self.mapFeaPfe[ lnkStartName ] = lnkFaces
        self.listPfe += lnkFaces
        self.listFea.append( lnkStartName )
    f.close()
    if not self.listFea : return False
    return True

  def __layers__( self ) :
    """ Find the layers for the features """
    if not self.path : return False

    f = open( self.path, 'r' )
    if not f :return False

    osRTY = ''
    osRID = ''
    for line in f :
      line = line.replace('\n', '').replace('\r', '')
      if len( line ) < 8 :
        continue;
      if line[:5] == 'RTYSA':
        osRTY = line[8:]
        osRID = ''
      elif osRTY == 'FEA' and line[:5] == 'RIDSA':
        osRID = line[8:]
      elif osRTY == 'FEA' and line[:5] == 'SCPCP':
        osSCP = line[8:]
      elif osRTY == 'FEA' and osRID in self.listFea and osSCP :
        scpArray = osSCP.split(';')
        ly = scpArray[3]
        if ly in self.mapLyFea :
          self.mapLyFea[ly].append( osRID )
        else :
          self.mapLyFea[ly] = [osRID]
        osRID = ''
    f.close()
    return True

  def __arcs__( self ) :
    """ Find the arcs for the faces """
    if not self.path : return False

    f = open( self.path, 'r' )
    if not f :return False

    osRTY = ''
    osRID = ''
    osSCP = ''
    lnkStartType = ''
    lnkStartName = ''
    lnkEndType = ''
    lnkEndName = ''
    for line in f :
      line = line.replace('\n', '').replace('\r', '')
      if len( line ) < 8 :
        continue;
      if lnkStartType == 'PAR' and lnkEndType == 'PFE' and lnkEndName in self.listPfe :
        if lnkEndName in self.mapPfePar :
          self.mapPfePar[ lnkEndName ].append( lnkStartName )
        else :
          self.mapPfePar[ lnkEndName ] = [ lnkStartName ]
        if lnkStartName not in self.listPar :
          self.listPar.append( lnkStartName )
        lnkStartType = ''
        lnkStartName = ''
        lnkEndType = ''
        lnkEndName = ''
      if line[:5] == 'RTYSA':
        osRTY = line[8:]
        osRID = ''
        osSCP = ''
        lnkStartType = ''
        lnkStartName = ''
        lnkEndType = ''
        lnkEndName = ''
      elif osRTY == 'LNK' and line[:5] == 'RIDSA':
        osRID = line[8:]
      elif osRTY == 'LNK' and line[:5] == 'SCPCP':
        osSCP = line[8:]
      elif osRTY == 'LNK' and line[:5] == 'FTPCP':
        lnkArray = line[8:].split(';')
        if not lnkStartType:
          lnkStartType = lnkArray[2]
          lnkStartName = lnkArray[3]
        else:
          lnkEndType = lnkArray[2]
          lnkEndName = lnkArray[3]
    f.close()
    return True

  def __coords__( self ):
    """ Find the coords for the arcs """
    if not self.path : return False

    f = open( self.path, 'r' )
    if not f :return False

    osRTY = ''
    osRID = ''
    for line in f :
      line = line.replace('\n', '').replace('\r', '')
      if len( line ) < 8 :
        continue;
      if line[:5] == 'RTYSA':
        osRTY = line[8:]
        osRID = ''
      elif osRTY == 'PAR' and line[:5] == 'RIDSA':
        osRID = line[8:]
      elif osRTY == 'PAR' and osRID in self.listPar and line[:5] == 'CORCC':
        pts = line[8:].split(';')
        if osRID in self.mapParCor :
          self.mapParCor[ osRID ].append([float(pts[0]), float(pts[1])])
        else :
          self.mapParCor[ osRID ] = [ [float(pts[0]), float(pts[1])] ]
    f.close()
    return True

  def __nodes__( self ) :
    """ Find the noeuds for the arcs """
    if not self.path : return False

    f = open( self.path, 'r' )
    if not f :return False

    osRTY = ''
    osRID = ''
    osSCP = ''
    lnkStartType = ''
    lnkStartName = ''
    lnkEndType = ''
    lnkEndName = ''
    for line in f :
      line = line.replace('\n', '').replace('\r', '')
      if len( line ) < 8 :
        continue;
      if osRTY == 'LNK' and lnkStartType == 'PAR' and lnkStartName in self.listPar and lnkEndType == 'PNO' :
        if lnkEndName in self.mapPnoPar :
          self.mapPnoPar[ lnkEndName ].append( lnkStartName )
        else :
          self.mapPnoPar[ lnkEndName ] = [ lnkStartName ]
        if lnkStartName in self.mapParPno :
          self.mapParPno[ lnkStartName ].append( lnkEndName )
        else :
          self.mapParPno[ lnkStartName ] = [ lnkEndName ]
        lnkStartType = ''
        lnkStartName = ''
        lnkEndType = ''
        lnkEndName = ''
      if osRTY == 'LNK' and lnkStartType == 'PNO' and lnkEndType == 'PAR' and lnkEndName in self.listPar :
        if lnkEndName in self.mapParPno :
          self.mapParPno[ lnkEndName ].append( lnkStartName )
        else :
          self.mapParPno[ lnkEndName ] = [ lnkStartName ]
        if lnkStartName in self.mapPnoPar :
          self.mapPnoPar[ lnkStartName ].append( lnkEndName )
        else :
          self.mapPnoPar[ lnkStartName ] = [ lnkEndName ]
        lnkStartType = ''
        lnkStartName = ''
        lnkEndType = ''
        lnkEndName = ''
      if line[:5] == 'RTYSA':
        osRTY = line[8:]
        osRID = ''
        osSCP = ''
        lnkStartType = ''
        lnkStartName = ''
        lnkEndType = ''
        lnkEndName = ''
      elif osRTY == 'LNK' and line[:5] == 'RIDSA':
        osRID = line[8:]
      elif osRTY == 'LNK' and line[:5] == 'SCPCP':
        osSCP = line[8:]
      elif osRTY == 'LNK' and line[:5] == 'FTPCP':
        lnkArray = line[8:].split(';')
        if not lnkStartType:
          lnkStartType = lnkArray[2]
          lnkStartName = lnkArray[3]
        else:
          lnkEndType = lnkArray[2]
          lnkEndName = lnkArray[3]
    f.close()
    return True

  def __polygons__( self ) :
    """ Face to polygon """
    mapPfePoly = {}
    for face in self.listPfe :
      arcs = self.mapPfePar[ face ][:]
      rings = self.__getRings__( arcs )
      if len( rings ) == 1 :
        mapPfePoly[ face ] = [rings]
      elif len( rings ) > 1 :
        bboxes = []
        bboxRing = {}
        for ring in rings :
          coords = ring[:]
          coord = coords.pop(0)
          minx = coord[0]
          maxx = coord[0]
          miny = coord[1]
          maxy = coord[1]
          while coords :
            coord = coords.pop(0)
            if coord[0] < minx :
              minx = coord[0]
            elif coord[0] > maxx :
              maxx = coord[0]
            if coord[1] < miny :
              miny = coord[1]
            elif coord[1] > maxy :
              maxy = coord[1]
          bboxes.append((minx, miny, maxx, maxy))
          bboxRing[(minx, miny, maxx, maxy)] = ring
        bboxes.sort()
        bbox = bboxes.pop(0)
        bboxPolygons = [[bbox]]
        while bboxes :
          bbox = bboxes.pop(0)
          inserted = False
          for p in bboxPolygons :
            extBbox = p[0]
            if bbox[0] >= extBbox[0] and bbox[1] >= extBbox[1] and bbox[2] <= extBbox[2] and bbox[3] <= extBbox[3] :
              p.append( bbox )
              inserted = True
              break
            elif extBbox[0] >= bbox[0] and extBbox[1] >= bbox[1] and extBbox[2] <= bbox[2] and extBbox[3] <= bbox[3] :
              p.insert(0, bbox)
              inserted = True
              break
          if not inserted :
            bboxPolygons.append( [bbox] )
        polygons = []
        for bboxes in bboxPolygons :
          polygon = []
          for bbox in bboxes :
            polygon.append( bboxRing[bbox] )
          polygons.append( polygon )
        mapPfePoly[ face ] = polygons
    return mapPfePoly

  def __concatArc__( self, arc, ring ) :
    coords = self.mapParCor[ arc ][:]
    if ring[-1] == coords[0] :
      ring = ring[:] + coords[1:]
    elif ring[0] == coords[-1] :
      ring = coords[:-1] + ring[:]
    elif ring[-1] == coords[-1] :
      coords = coords[:-1]
      coords.reverse()
      ring = ring[:] + coords[:]
    elif ring[0] == coords[0] :
      coords = coords[1:]
      coords.reverse()
      ring = coords[:] + ring[:]
    return ring

  def __getRings__( self, aArcs ) :
    rings = []
    if not aArcs or not isinstance(aArcs, list) :
      return rings
    arcs = aArcs[:]
    while arcs :
      arc = arcs.pop(0)
      if arc not in self.mapParPno :
        rings.append( self.mapParCor[ arc ][:] )
        continue
      ring = self.mapParCor[ arc ][:]
      pnos = self.mapParPno[ arc ]
      if len( pnos ) < 2:
        rings.append( ring )
        continue
      pno = pnos[0]
      pnoUsed = []
      pnoArcs = self.mapPnoPar[ pno ][:]
      while pnoArcs :
        pnoArc = pnoArcs.pop(0)
        if pnoArc in arcs :
          arcs.pop( arcs.index( pnoArc ) )
          arc = pnoArc
          ring = self.__concatArc__( arc, ring )
          pnoUsed.append( pno )
          pnos = self.mapParPno[ arc ]
          for p in pnos :
            if p not in pnoUsed :
              pno = p
          pnoArcs = self.mapPnoPar[ pno ][:]
      rings.append( ring )
    return rings

#import glob
#getMultiPolygon = GetMultiPolygonFromVec()
#for path in glob.glob('*/*/*.VEC') :
#  getMultiPolygon( path )
