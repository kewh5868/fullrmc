# standard libraries imports
import os

# external libraries imports
from pdbParser.pdbParser import pdbParser
from pdbParser.Utilities.BoundaryConditions import PeriodicBoundaries
from pdbParser.Utilities.Geometry import orient, translate

# fullrmc library imports
from fullrmc.Globals import LOGGER
from fullrmc.Engine import Engine
from fullrmc.Core.MoveGenerator import MoveGeneratorCollector
from fullrmc.Constraints.DistanceConstraints import InterMolecularDistanceConstraint
from fullrmc.Generators.Rotations import RotationGenerator
from fullrmc.Generators.Translations import TranslationTowardsCenterGenerator


# shut down logging
LOGGER.set_log_file_basename("fullrmc")
LOGGER.set_minimum_level(30)

# create system
pdbPath = "thf_single_molecule.pdb" 
pdb = pdbParser(pdbPath)
orient(pdb.indexes, pdb, axis=[1,0,0], records_axis=[1,1,1])
translate(pdb.indexes, pdb, [1.,1.,3])
original = pdbParser(pdbPath)
translate(original.indexes, original, [-1.,-1.,-3])
for rec in original.records:
    rec["sequence_number"]=2
pdb.concatenate( original )
pdb.set_boundary_conditions(PeriodicBoundaries(15))
pdb.export_pdb("completeSystem.pdb")
#pdb.visualize()

# create engine
ENGINE = Engine(pdb=pdb, constraints=None)

# add inter-molecular distance constraint
EMD_CONSTRAINT = InterMolecularDistanceConstraint(engine=ENGINE, defaultDistance=1.75)
ENGINE.add_constraints([EMD_CONSTRAINT]) 

# set only one molecule group
ENGINE.set_groups_as_molecules() 
secMolIdxs = ENGINE.groups[1].indexes 
ENGINE.set_groups(ENGINE.groups[0])

# set move generator
for g in ENGINE.groups:
    t = TranslationTowardsCenterGenerator(center={'indexes': secMolIdxs},amplitude=0.15, angle=90)
    r = RotationGenerator(amplitude=10)
    mg = MoveGeneratorCollector(collection=[t,r], randomize=True, weights=[(0,1),(1,5)])
    g.set_move_generator(mg)

# set runtime params    
nsteps = 1000
xyzFrequency = 1

# run engine
xyzPath="trajectory.xyz"
if os.path.isfile(xyzPath): os.remove(xyzPath)
ENGINE.run(numberOfSteps=nsteps, saveFrequency=2*nsteps, xyzFrequency=xyzFrequency, xyzPath=xyzPath)

 
ENGINE.visualize()    
    
 






