<p align="left">
  <img src="assets/raytracer_sP9_icon.ico" width="100" alt="Project Icon">
</p>

# EclipsePathPlot
Physical simulation written from scratch in C++ for personal educational purposes.

Finds dates and times of upcoming solar eclipses. Calculates and animates path of penumbra and umbra of moon during solar eclipses. Integrates coupled differential equations of newtonian 5 body problem (Venus,Sun,Jupiter,Earth,Moon) using Runge-Kutta-4 from a fixed reference date. Rudimentary raytracing is used to calculate intersection of tangents and animate path of shadow across hemisphere. Only depends on the "Eigen" library.

Animations created in python using matplotlib and cartopy.

Example animation of Eclipse on 2/10/2024 as of version 23/07/2025:

<p align="left">
  <img src="assets/example.gif" width="1000" alt="ExampleEclipse">
</p>
