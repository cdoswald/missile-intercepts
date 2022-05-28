# A Probabilistic Missile Intercept Model

**Project Goals:**

1) Develop a simplified missile intercept model and simulate the model in Google Earth

2) Investigate methods for predicting a missile's trajectory under various levels of 
uncertainty about the missile's launchpoint, intended target, position, velocity, etc.

<br>

<p>
  <a href="docs/images/KML_ex2.PNG">
  <img src="docs/images/KML_ex2.PNG" alt="KML Example 2" width="700"/>
  </a>
</p>

## Getting Started

### Setting Up a Conda Virtual Environment

The [environment.yml](docs/env/environment.yml) file contains all of the packages needed to run the code in this repository:

1. Open an Anaconda Prompt

2. Create a new virtual environment: `conda env create -f environment.yml`

3. Activate the virtual environment: `conda activate missile_env`

### Setting Model Parameters

All configuration parameters are set via the [Config](config/config.xlsx) file.

Parameter descriptions, formats, and datatypes are specified in the Config file.

<p>
  <a href="config/config.xlsx">
  <img src="docs/images/config_ex1.PNG" alt="Config Example 1" width="700"/>
  </a>
</p>

Additional missile simulations can be created by adding new columns to the right of the existing simulations.

## Methodology

### Ballistic Missile

* User specifies the latitude and longitude of the missile launchpoint (LP) and aimpoint (AP) and the missile's constant horizontal velocity (km/s), which are used to calculate the [great-circle distance](https://en.wikipedia.org/wiki/Haversine_formula) to the target (km) and total time-to-target (sec)
* The apogee of the ballistic trajectory is reached when the missile is halfway to the target (i.e., 0.5 * total time-to-target)
* The time-to-apogee (sec) is multiplied by the absolute value of the gravitational acceleration (km/s^2) to determine the missile's initial vertical velocity (km/s)
* Integrating the vertical velocity equation, the missile's altitude (km) at timestep *t* (sec) is calculated as `alt_km(t) = initial_vertical_velocity * t + 0.5 * gravitational_acceleration * t^2`

### Limitations 

The plan is to add complexity to the model over time. Currently, the model does not take into account any of the following:

- Aerodynamic drag
- Propulsive thrust
- Changes in missile mass (e.g., after burning fuel)
- Rotation of the Earth

## Sources

- Trajectory Equations
  - [NASA Glenn Research Center](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/ballistic-flight-equations/)
  - [University of Florida Department of Mechanical & Aerospace Engineering](https://mae.ufl.edu/~uhk/ICBM.pdf)
  - [MIT Department of Aeronautics and Astronautics](https://web.mit.edu/16.unified/www/FALL/systems/Lab_Notes/traj.pdf)

- Geodetic Equations
  - Chris Veness, Movable-Type Scripts ([Spherical Trigonometry](https://www.movable-type.co.uk/scripts/latlong.html) and [Vector-Based Methods](https://www.movable-type.co.uk/scripts/latlong-vectors.html))

- Creating 3D Models in COLLADA Format
  - [Blender](https://www.blender.org/)
