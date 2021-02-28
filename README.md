# Ballistic Missile Intercept Model

The goal of this project is to simulate a hit-to-kill ballistic missile intercept in Google Earth.

### Methodology

The plan is to start by developing a simplified model and then to build on that model over time. The first model iteration
does not take into account any of the following (for either the ballistic or interceptor missiles):

- Aerodynamic drag
- Propulsive thrust
- Changes in missile mass (e.g., after burning fuel)
- Rotation of the Earth
- Uncertainty in ballistic missile trajectory

### Sources

- Trajectory Equations
  - [University of Florida Department of Mechanical & Aerospace Engineering](https://mae.ufl.edu/~uhk/ICBM.pdf)
  - [MIT Department of Aeronautics and Astronautics](https://web.mit.edu/16.unified/www/FALL/systems/Lab_Notes/traj.pdf)
  - [NASA Glenn Research Center](https://www.grc.nasa.gov/www/k-12/airplane/ballflght.html)

- Geodetic Equations
  - Chris Veness, Movable-Type Scripts ([Spherical Trigonometry](https://www.movable-type.co.uk/scripts/latlong.html) and [Vector-Based Methods](https://www.movable-type.co.uk/scripts/latlong-vectors.html))

- Creating 3D Models in COLLADA Format
  - [Blender](https://www.blender.org/)
