import radiopropa
import numpy as np
#from ObserverPlane import ObserverPlane 




class TransmissiveLayer(radiopropa.Module):
    """
    A layer defined by point X0 and vectors V1, V2. Part of a candidate
    crossing the layer is reflected. 
    Future propagation in scalar field will take care of directivity change automatically???
    """
    def __init__(self, X0, V1, V2, transmisionCoefficient):
        radiopropa.Module.__init__(self)
        self.__x0 = X0
        self.__v1 = V1.getUnitVector()
        self.__v2 = V2.getUnitVector()
        n = V1.cross(V2)
        self.__normal = n.getUnitVector()
        self.__transmisionCoefficient = transmisionCoefficient

    def distanceToPlane(self, X):
        """
        Always positive for one side of plane and negative for the other side.
        """
        # much nicer with future Vector3 ...
        dX = [X.x - self.__x0[0], X.y - self.__x0[1], X.z - self.__x0[2]]
#        V = np.linalg.det([self.__v1, self.__v2, dX]) !np too slow!
        D =       self.__v1[0] * self.__v2[1] * dX[2] + self.__v1[1] * self.__v2[2] * dX[0] + self.__v1[2] * self.__v2[0] * dX[1]  - self.__v1[2] * self.__v2[1] * dX[0] - self.__v1[0] * self.__v2[2] * dX[1] - self.__v1[1] * self.__v2[0] * dX[2]

        return D

    def process(self, candidate):

        currentDistance = self.distanceToPlane(candidate.current.getPosition())
        previousDistance = self.distanceToPlane(candidate.previous.getPosition())

        if np.sign(currentDistance) == np.sign(previousDistance):
            candidate.limitNextStep(abs(currentDistance))
        else:
            E = candidate.current.getAmplitude()

            # The secondary propagates further, while the candidate is
            # reflected: legacy from CRPropa interface as secondaries have same
            # direction as parents.
            candidate.addSecondary(0, self.__transmisionCoefficient * E, 1)
            candidate.current.setAmplitude((1-self.__transmisionCoefficient) * E)

            V = candidate.current.getDirection()
            u = self.__normal * (V.dot(self.__normal))
            new_direction = V - u*2
            candidate.current.setDirection(new_direction)

            # update position slightly to move on correct side of plane
            X = candidate.current.getPosition()

            candidate.current.setPosition(X + new_direction * candidate.getCurrentStep())
            # update position (this is a hack to avoid double scatter)
            #candidate.previous.setPosition(candidate.current.getPosition())




# simulation setup
sim = radiopropa.ModuleList()
sim.add(radiopropa.SimplePropagation(.1*radiopropa.meter, 1*radiopropa.meter))




#obs = radiopropa.Observer()
#obs.add(ObserverPlane(np.asarray([0.,0., 3. * kilo*radiopropa.meter]),np.asarray([10.,0, 0]), np.asarray([0,10., 0])))

#obs = radiopropa.Observer()
#obs.add(radiopropa.ObserverLargeSphere(radiopropa.Vector3d(0,0,0), 99*radiopropa.meter))
output = radiopropa.HDF5Output('output_traj.h5', radiopropa.Output.Trajectory3D)
output.enableProperty('frequency', 0., 'Frequency for RadioPropa')

#obs.onDetection(output)
#obs.setDeactivateOnDetection(True)
sim.add(output)

source = radiopropa.Source()

source.add(radiopropa.SourcePosition(radiopropa.Vector3d(0, 0, 0)))
source.add(radiopropa.SourceParticleType(radiopropa.nucleusId(1, 1)))
source.add(radiopropa.SourceAmplitude(1))


#source.add(radiopropa.SourceIsotropicEmission())
source.add(radiopropa.SourceDirection(radiopropa.Vector3d(.3,0,1)))


# Not constructiong this outside the add method will cause segfault
source.add(radiopropa.SourceFrequency(1E6))

#Two transmissive layers at +/- 10 m
L1 = TransmissiveLayer(radiopropa.Vector3d(0,0,5),radiopropa.Vector3d(1,0,0),radiopropa.Vector3d(0,1,0), .2)
L2 = TransmissiveLayer(radiopropa.Vector3d(0,0,-5),radiopropa.Vector3d(1,0,0),radiopropa.Vector3d(0,1,0), .2)

sim.add(L1)
sim.add(L2)
sim.add(radiopropa.MinimumAmplitude(1E-2))

boundary = radiopropa.SphericalBoundary(radiopropa.Vector3d(0, 0, 0), 100*radiopropa.meter)
sim.add(boundary)



sim.setShowProgress(True)
sim.run(source, 1)
#print rf
