import vtkplotlib as vpl
from stl.mesh import Mesh

path = "test.stl"

mesh = Mesh.fromfile(path)
vpl.mesh_plot(mesh)
vpl.show()