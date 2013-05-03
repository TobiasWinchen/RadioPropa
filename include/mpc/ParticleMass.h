#ifndef MPC_PARTICLE_MASS_H_
#define MPC_PARTICLE_MASS_H_

namespace mpc {

/** Return the nucleus mass by lookup from a table.
 *  The masses are the atomic masses from the NIST database (http://www.nist.gov/pml/data/comp.cfm) minus electron masses, neglecting electron binding energies.
 *  Unmeasured atomic masses are taken to be A * amu minus electron masses.
 *  The data table is generated by mpc/data-tools/NuclearMass/createNuclearMassTable.
 */
double nucleusMass(int id);

} // namespace mpc

#endif // MPC_PARTICLE_MASS_H_