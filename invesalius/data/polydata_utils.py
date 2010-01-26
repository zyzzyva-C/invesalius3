#--------------------------------------------------------------------------
# Software:     InVesalius - Software de Reconstrucao 3D de Imagens Medicas
# Copyright:    (C) 2001  Centro de Pesquisas Renato Archer
# Homepage:     http://www.softwarepublico.gov.br
# Contact:      invesalius@cti.gov.br
# License:      GNU - GPL 2 (LICENSE.txt/LICENCA.txt)
#--------------------------------------------------------------------------
#    Este programa e software livre; voce pode redistribui-lo e/ou
#    modifica-lo sob os termos da Licenca Publica Geral GNU, conforme
#    publicada pela Free Software Foundation; de acordo com a versao 2
#    da Licenca.
#
#    Este programa eh distribuido na expectativa de ser util, mas SEM
#    QUALQUER GARANTIA; sem mesmo a garantia implicita de
#    COMERCIALIZACAO ou de ADEQUACAO A QUALQUER PROPOSITO EM
#    PARTICULAR. Consulte a Licenca Publica Geral GNU para obter mais
#    detalhes.
#--------------------------------------------------------------------------

import vtk
import wx.lib.pubsub as ps

import vtk_utils as vu

# Update progress value in GUI
UpdateProgress = vu.ShowProgress()

def ApplyDecimationFilter(polydata, reduction_factor):
    """
    Reduce number of triangles of the given vtkPolyData, based on 
    reduction_factor.
    """
    # Important: vtkQuadricDecimation presented better results than
    # vtkDecimatePro
    decimation = vtk.vtkQuadricDecimation()
    decimation.SetInput(polydata)
    decimation.SetTargetReduction(reduction_factor)
    decimation.GetOutput().ReleaseDataFlagOn()
    decimation.AddObserver("ProgressEvent", lambda obj, evt:
                  UpdateProgress(decimation, "Reducing number of triangles..."))
    return decimation.GetOutput()

def ApplySmoothFilter(polydata, iterations, relaxation_factor):
    """
    Smooth given vtkPolyData surface, based on iteration and relaxation_factor.
    """
    smoother = vtk.vtkSmoothPolyDataFilter()
    smoother.SetInput(polydata)
    smoother.SetNumberOfIterations(iterations)
    smoother.SetFeatureAngle(80)
    smoother.SetRelaxationFactor(relaxation_factor)
    smoother.FeatureEdgeSmoothingOn()
    smoother.BoundarySmoothingOn()
    smoother.GetOutput().ReleaseDataFlagOn()    
    smoother.AddObserver("ProgressEvent", lambda obj, evt:
                         UpdateProgress(smoother, "Smoothing surface..."))
    
    return smoother.GetOutput()
    


def FillSurfaceHole(polydata):
    """
    Fill holes in the given polydata.
    """
    # Filter used to detect and fill holes. Only fill 
    print "Filling polydata"
    filled_polydata = vtk.vtkFillHolesFilter()
    filled_polydata.SetInput(polydata)
    filled_polydata.SetHoleSize(500)
    return filled_polydata.GetOutput()

def CalculateSurfaceVolume(polydata):
    """
    Calculate the volume from the given polydata
    """
    # Filter used to calculate volume and area from a polydata
    measured_polydata = vtk.vtkMassProperties()
    measured_polydata.SetInput(polydata)
    return measured_polydata.GetVolume()

def CalculateSurfaceArea(polydata):
    """
    Calculate the volume from the given polydata
    """
    # Filter used to calculate volume and area from a polydata
    measured_polydata = vtk.vtkMassProperties()
    measured_polydata.SetInput(polydata)
    return measured_polydata.GetSurfaceArea()

def Merge(polydata_list):
    append = vtk.vtkAppendPolyData()

    for polydata in polydata_list:
        triangle = vtk.vtkTriangleFilter()
        triangle.SetInput(polydata)
        append.AddInput(triangle.GetOutput())

    clean = vtk.vtkCleanPolyData()
    clean.SetInput(append.GetOutput())

    return append.GetOutput()

def Export(polydata, filename, bin=False):
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filename)
    if bin:
        writer.SetDataModeToBinary()
    else:
        writer.SetDataModeToAscii()
    writer.SetInput(polydata)
    writer.Write()

def Import(filename):
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()

def JoinSeedsParts(polydata, point_id_list):
    """
    The function require vtkPolyData and point id
    from vtkPolyData.
    """
    conn = vtk.vtkPolyDataConnectivityFilter()
    conn.SetInput(polydata)
    conn.SetExtractionModeToPointSeededRegions()
    for seed in point_id_list:
        conn.AddSeed(seed)
    conn.Update()

    result = vtk.vtkPolyData()
    result.DeepCopy(conn.GetOutput())
    result.Update()
    return result

def SelectLargestPart(polydata):
    """
    """
    conn = vtk.vtkPolyDataConnectivityFilter()
    conn.SetInput(polydata)
    conn.SetExtractionModeToLargestRegion()
    conn.Update()

    result = vtk.vtkPolyData()
    result.DeepCopy(conn.GetOutput())
    result.Update()
    return result

def SplitDisconectedParts(polydata):
    """
    """
    return [polydata]

