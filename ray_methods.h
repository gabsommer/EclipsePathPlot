#include <ctime>
#include <iostream>
#include "eigen-3.4.0/Eigen/Dense"
#include <cmath>

using namespace std;
using namespace Eigen;


//time of initial condition (get these eventually from a file outside)
int init_year,init_month,init_day,init_hour,init_min,init_second;



void print_vector(const Vector3d& inp) {
    cout << "x: " << inp(0) << ", y: " << inp(1) << ", z: " << inp(2) << endl;
}

double time_equation(const int& y, const int& d) {
    //y: current year
    //d: days since Jan. 1st in that year [0,364]
    
    //returns time in minutes
    
    double out, D;

    D = (6.24004077 + 0.01720197*(365.25*(y-2000)+d)); //ADD .25 to 365!!!!

    out = -7.659*sin(D)+9.863*sin((2*D+3.5932));
    return out;

}

void print_lines(Eigen::ArrayXXd input,Eigen::ArrayXXd input2) {
    //Helperfunction to print lines in Mathematica format
    int cols = input.cols();
    cout << "ls = ParametricPlot3D[{";
    for (size_t i = 0; i < cols; i++) {
        
            cout <<"{" << input(0,i) << "," << input(1,i) << "," <<  input(2,i) << "}+t*{" << input2(0,i) << "," << input2(1,i) << "," <<  input2(2,i) << "},";
    }
    cout << "},{t, -22, 10}, PlotRange -> {{-22, 22}, {-22, 22}, {-22, 22}}];" << endl;
}

void print_points(Eigen::ArrayXXd input) {
    //Helperfunction to print points in Mathematica format
    int cols = input.cols();
    
    for (size_t i = 0; i < cols; i++) {
        cout << "p" << i+1 << " = Graphics3D[{Red, PointSize[0.01], Point[{{" << input(0,i) << "," << input(1,i) << "," <<  input(2,i) <<"}}]}];" << endl;
    }

}

ArrayXXd umbrapar(const Eigen::Vector3d& m1, const Eigen::Vector3d& m2, const double& r1, const double& r2, int n, const char& setting,const char& option) {
    //m1: cetner of first sphere (i.e. moon)
    //m2: center of second sphere (i.e. sun)
    //r1: radius of first sphere
    //r2: radius of second sphere
    //n: number of evenly spaced rays (e.g. n=4 means angle between tangent rays form (m1-m2)-connecting line is 90°)
    //setting: 'p' for starting points, 'u' for direction vectors, so the ray is: r(t) = p + t*u

    //returns Array with n columns being p or u of the straight-line parameter-equation r(t) = p + t*u, 
    //depending on setting 




    //defining increment angle for rotation of tangent

    double phi = 2*3.141/n;
    
    //Creating new basis with x-axis being connecting vetor of two spheres (direction: m1 -> m2) and y axis.
    //Both define plane that cut spheres into circular shapes, z-axis is perpendicular to these circles.

    Vector3d m12 = m1-m2;
    Vector3d bx = m12.normalized();
    Vector3d by, bz, tangent, ab;
    Matrix3d Rot, Trafo;
    bool set = false;

    //Essentially I solve the following system of equation:
    //bx(0)by(0)+bx(1)by(1)+bx(2)by(2) = 0
    //sqrt(by(0)^2+by(1)^2+by(2)^2) = 1
    //bx is already known to be the normalized vector m1-m2
    //I first choose freely by(2) to be zero initially, but depending on how close i am to dividing by 0 I choose other 
    //components of by to be zero. 
    //I try to avoid any numerical intabilities (e.g. dividing by zero) in case the connecting vector fails to have a large enough
    //component in one of the directions by using different orientations of my new bx,by,bz-basis

    if (abs(bx(1))>0.001) {
        by(0) = 1./(sqrt(1+pow((bx(0)/bx(1)),2))); //Since I divide by bx(1) =>  bx(1) != 0 
        by(1) = -1*(bx(0)/bx(1))*by(0);
        by(2) = 0;

        bz = bx.cross(by);
        //bz(0) = bx(1)*by(2)-bx(2)*by(1);
        //bz(1) = bx(2)*by(0)-bx(0)*by(2);
        //bz(2) = bx(0)*by(1)-bx(1)*by(0);

    }
    else if (abs(bx(2))>0.001) {
        set = true;
        by(0) = 1./(sqrt(1+pow((bx(0)/bx(2)),2))); //Since I divide by bx(2) => bx(2) != 0
        by(2) = -1*(bx(0)/bx(2))*by(0);
        by(1) = 0;

        bz = bx.cross(by);
        //bz(0) = bx(1)*by(2)-bx(2)*by(1);
        //bz(1) = bx(2)*by(0)-bx(0)*by(2);
        //bz(2) = bx(0)*by(1)-bx(1)*by(0);

    }
    //If m1-m2 is roughly perpendicualr to both remaining coordinate axes I use an arbitrary initial 45° angle 
    //(so iby(0)=1,iby(1)=1) between the remaining axes. From that I again solve the system of equation from above 
    else {
        set = true;
        cout << "WARNING: CONDITION MET! Two Spheres (almost) align with one coordinate axis" << endl;
        Vector3d iby;
        iby(0) = 1;
        iby(1) = 1;
        iby(0) = (bx(1)*by(1)+bx(2)*by(2))/bx(0); //If both bx(1) & bx(2) are close to zero, bx(0) can't be.
        by = iby.normalized();

        bz = bx.cross(by);   
        //bz(0) = bx(1)*by(2)-bx(2)*by(1);
        //bz(1) = bx(2)*by(0)-bx(0)*by(2);
        //bz(2) = bx(0)*by(1)-bx(1)*by(0);
    }


    
    //Calculating tangent in the x,z-plane of the (bx,by,bz)-coordinate system where one sphere is located 
    //at the origin and the other one is located somwhere along the x-axis (being the (m1-m2)-vector) of this
    //coordinate frame. The ab-vector is here the normal vector to that tangent. They are normalized. 
    //(See: https://en.wikipedia.org/wiki/Tangent_lines_to_circles#Tangent_lines_to_two_circles)
    double R;
    if (option == 'o') {
        R = (r2-r1)/(m2-m1).norm();
    }
    else if (option == 'i')
    {
        R = (r2+r1)/(m2-m1).norm();
    }
    
    
    ab(0) = R;
    ab(1) = 0;
    ab(2) = sqrt(1-pow(R,2));

    //Rotation of 90degrees in the x,z-plane, to get the tangent direction
    tangent(0) = -1*ab(2);
    tangent(1) = 0;
    tangent(2) = ab(0);

    //Here the transformation back to the fixed (outer) coordinate system is defined
    Trafo.col(0) = bx;
    Trafo.col(1) = by;
    Trafo.col(2) = bz;


    ArrayXXd abs = ArrayXXd::Zero(3,n);
    ArrayXXd tangents = ArrayXXd::Zero(3,n);

    ArrayXXd ps = ArrayXXd::Zero(3,n);
    ArrayXXd us = ArrayXXd::Zero(3,n);

    //Now first the solutions ab, and tangent are rotated n times about the by axis (still inside the 
    //(bx,by,bz)-coordinate frame). These vectors (ab and tangent) after that are transfered back to the
    // fixed coordinate frame. We now have n equations for n lines of the form s(t) = p + u*t with p being
    // a space point on the line, u the direction and t the parameter.




    //Below Code Block inside /*...*/ split up and included in the following if-statments for efficiency

    /*ps.col(0) = m2 + r2*Trafo*ab;
    us.col(0) = Trafo*tangent;

    for (size_t i = 1; i < n; i++) {
        Rot << 1,0,0,
         0,cos(phi*i),-1*sin(phi*i),
         0,sin(phi*i),cos(phi*i);
        
        ps.col(i) = m2+r2*(Trafo*(Rot*ab));
        us.col(i) = Trafo*(Rot*tangent);
   
    }
    */

    if (setting == 'u') {
        ArrayXXd us = ArrayXXd::Zero(3,n);
        us.col(0) = Trafo*tangent;
        for (size_t i = 1; i < n; i++) {
            Rot << 1,0,0,
            0,cos(phi*i),-1*sin(phi*i),
            0,sin(phi*i),cos(phi*i);
        
            us.col(i) = Trafo*(Rot*tangent);
        }
        return us;
    }
    else if (setting == 'p')
    {
        ArrayXXd ps = ArrayXXd::Zero(3,n);
        ps.col(0) = m2 + r2*Trafo*ab;
        for (size_t i = 1; i < n; i++) {
            Rot << 1,0,0,
            0,cos(phi*i),-1*sin(phi*i),
            0,sin(phi*i),cos(phi*i);
        
            ps.col(i) = m2+r2*(Trafo*(Rot*ab));
        }
        return ps;
    }

    //Return us by default
    return us;
}

ArrayXXd umbraisx(ArrayXXd p, ArrayXXd u, const Eigen::Vector3d& m, const double& R) {
    //p: Space points of n tangents from the umbrapar function (i.e. one point on the tangentline from where the direction will be added)
    //u: Direction vectors of the n tangents from the umbrapar function
    //m: Center of sphere whose intersection with the tangent vectors should be calculated (i.e. pos of earth)
    //R: Radius of sphere whose intersection with the tangent vectors should be calculated (i.e. radius of earth)

    //returns Array with n columns being intersection coordinates of lines (p,u) with the sphere at m with radius R 
    
    
    
    
    int pcols = static_cast<int>(p.cols());
    int ucols = static_cast<int>(u.cols());
    
    //TODO: check if pcols = ucols

    double a,b,c,disc,t1,t2;
    ArrayXXd isx = ArrayXXd::Zero(3,pcols);

    //The solution to this problem mathematically is straigh forward. We have the parameter equation r(t) = p + t*u
    //of the tangents and an implicit equation for a circle. We plug in the r(t) components into the circle equation
    //which yields (r_x(t)-m_x)^2+(r_y(t)-m_y)^2+(r_z(t)-m_z)^2 = R^2. This equation only has one unknown (i.e. t). We expand
    //it, sort it for powers in t and get a quadratic equation: a*t^2+b*t+c. It can be solved with any known formula.
    //Here (m_x,m_y,m_z) is the center of the sphere.

    for (size_t i = 0; i < pcols; i++) {
        a = 0;
        b = 0;
        c = 0;
        for (size_t j = 0; j < 3; j++) {
            a += pow(u(j,i),2);
            b += (p(j,i)-m(j))*u(j,i);
            c += pow(p(j,i)-m(j),2);
        }
        b = 2*b;
        c = c-pow(R,2);
        //a = pow(u(0,i),2) + pow(u(1,i),2) + pow(u(2,i),2);
        //b = 2 * ((p(0,i)-m(0))*u(0,i) + (p(1,i)-m(1))*u(1,i) + (p(2,i)-m(2))*u(2,i));
        //c = pow(p(0,i)-m(0),2) + pow(p(1,i)-m(1),2) + pow(p(2,i)-m(2),2) - pow(R,2);
        disc = pow(b,2)-4*a*c;
        //If the discriminant is greater than zero, two intersections exist. we only pick the one which is
        //closest to the point p (i.e. at the moon), so we need the absolut value of our two solutions (Abs(t1) 
        //& Abs(t2)).
        if (disc > 0) {
            t1 = (-1.*b+sqrt(disc))/2*a;
            t2 = (-1.*b-sqrt(disc))/2*a;
            if (abs(t1) < abs(t2)) {
                isx.col(i) = p.col(i)+t1*u.col(i); 
            }
            else {
                isx.col(i) = p.col(i)+t2*u.col(i); 
            }
        }

        //If the discriminant is less or rqual to zero we will define it to be as a case where no intersection is 
        //found (eventhough mathematically a disciminant of 0 would be equivalent to a tangent does solve the
        //quadratic above)
        else if (disc <= 0)
        {
            //cout << "WARNING: disc less than 0, no intersection" << endl;
            //isx.col(i) << 0,0,0;

            isx.col(i) << NAN,NAN,NAN;
        }
    //Later the umbraisx output can be checked for NAN when plotting.
    }
    return isx;
}

Vector2d lonlat(const Vector3d& pos_isx, const Vector3d& position_e, const Vector3d& position_s, const Vector3d& omega, const double& sec_sinceinit) {
    //pos_isx: Coordinates of intersection from umbraisx
    //position_e: position of earth
    //position_s: position of sun
    //omega: orientation of axis of rotation of earth
    //sec_sinceint: time in seconds since the point in time of the initial conditions

    //returns Eigen::Vector2d with first value being longditude and second value being latitude.
    //Positive longditude/latitude corresposnds to eastern/northern longditude/latitude, negative values vice versa
    //correspond to western/southern longditude/latitude




    
    double omega_s, omega_gw;
    omega_s = 0.0000114155251142; //360deg per year
    omega_gw = 0.00417827; //360deg per siderial day
    Vector2d out;
    Vector3d es = position_s-position_e; //vector points to sun
    Vector3d e_x,e_y,e_z,relative_isx;
    
    int end_month,end_day,end_hour,end_min,end_sec,end_year,end_dlst; //Date at the end of calculation after sec_sinceint

    //Basically Gram-Schmidt orthogonalisation, to project earth sun distance onto equatorial plane with normal
    //vector to this plane being omega. Coordinate Frame of earth with x-axix pointing to the sun (but projected onto 
    //equatorial plane). So x-axis at this time points to longditude that is under astronomical noon.
    
    e_z = omega.normalized();

    e_x = es-(es.dot(e_z))*e_z;
    e_x = e_x.normalized();

    e_y = e_z.cross(e_x);

    //cout << "e_x" << endl;
    //print_vector(e_x);
    //cout << "e_y" << endl;
    //print_vector(e_y);
    //cout << "e_z" << endl;
    //print_vector(e_z);//CORRECT!

    //Now we convert intersection points to spherical coordiantes with respect to e_x,e_y,e_z frame, centered at
    //earth
    
    
    //First: Define Transformation Matrix T:
    Matrix3d T_inv;

    T_inv.col(0) = e_x;
    T_inv.col(1) = e_y;
    T_inv.col(2) = e_z;

    Matrix3d T = T_inv.inverse();

    //Second: Shifting Intersection points relative to earth frame.
    //Third: Transformation of relative_isx into rotated earth frame via matrix multiplication with T:
    relative_isx = T*(pos_isx-position_e);

    //cout << "pos_isx-position_e: " << endl;
    //print_vector(pos_isx-position_e); //CORRECT!

    //cout << "relative_isx: " << endl;
    //print_vector(relative_isx);
    //cout << "relative_isx.norm(): " << relative_isx.norm() << endl; //CORRECT!

    //Fourth: Use transformation formulas of spherical coordinates to retrive r,theta & phi:
    double r,theta,phi,latitude,longditude;

    r = sqrt(pow(relative_isx(0),2)+pow(relative_isx(1),2)+pow(relative_isx(2),2));
    theta = acos(relative_isx(2)/r);

    //phi is a bit more complicated than just phi=atan(x/y) when considering all possibilities.
    //See: https://en.wikipedia.org/wiki/Spherical_coordinate_system#Cartesian_coordinates
    if (relative_isx(0) > 0){
        phi = atan(relative_isx(1)/relative_isx(0));
    }
    else if (relative_isx(0)=0)
    {
        if (relative_isx(1) < 0) {
            phi = -3.1415926535897*0.5;
        }
        else if (relative_isx(1) > 0) {
            phi = 3.1415926535897*0.5;
        }
    }
    else if (relative_isx(0) < 0)
    {
        if (relative_isx(1) < 0) {
            phi = atan(relative_isx(1)/relative_isx(0)) - 3.141592653589792;
        }
        else if (relative_isx(1) >= 0) {
            phi = atan(relative_isx(1)/relative_isx(0)) + 3.141592653589792;
        }
    }

    phi = phi*360/(2*3.141592653589792);

    //Calculating the latitude from theta is straightforward
    //positive latitude means northern hemisphere, negative southern hemispere
    latitude = 90 - (theta*360/(2*3.14159));

    //Now phi needs to be adjusted depending on the time to match earths longditude, since earths orientation
    //rotates under phi.

    //We know that the angle phi describes the angular distance to the current location that is under 
    //astronomical noon

    //With the time equation we can calculate the distance of Greenwich to the astronomical noon in time/degree.
    //See: https://de.wikipedia.org/wiki/Sonnenzeit#Ermittlung_der_Wahren_Sonnen-_bzw._Ortszeit_aus_der_Zonenzeit_und_der_Zeitgleichung
    //phi + greenwhich offset = the actual latitude,
    //Here negative offset means noon still to come for that day, positive offset means already past noon

    //Here we first initialize tm_ic & tm_ec (tm struct for initial condition and for end condition)
    struct tm tm_ic = {};
    struct tm* tm_ec = {};

    tm_ic.tm_year = init_year - 1900; // tm_year is years since 1900
    tm_ic.tm_mon = init_month - 1;    // tm_mon is months since January (0-11)
    tm_ic.tm_mday = init_day;         // tm_mday is the day of the month (1-31)
    tm_ic.tm_hour = init_hour;
    tm_ic.tm_min = init_min;
    tm_ic.tm_sec = init_second;



    time_t t_ic = mktime(&tm_ic); //seconds since Unix Epoch for initial condition
    
   
    time_t t_ec = t_ic + sec_sinceinit; //seconds since Unix Epoch for end condition

    //cout << t_ec-t_ic << endl;

    //Converting seconds since Unix Epoch for end condition back to tm_ec, yielding a year,month,day,etc.
    tm_ec = localtime(&t_ec); //Note that localtime() returns a pointer

    end_year = tm_ec->tm_year + 1900;
    end_month = tm_ec->tm_mon + 1;     // tm_mon is months since January (0–11)
    end_day = tm_ec->tm_mday;
    end_hour = tm_ec->tm_hour;
    end_min = tm_ec->tm_min;
    end_sec = tm_ec->tm_sec;
    

    //cout << "day: " << end_day << " hour: " << end_hour << endl; //CORRECT!

    //Thise tm_ec.tm_year, tm_ec.tm_day, etc. values are now the time at the end of the calculation (so the 
    //intersection time).
    //Now to these we manually add the time equation. First we evaluate deltaT of the equation fo time.

    Array<int, 1, 12> daysinmon;
    daysinmon << 0,31,59,90,120,151,181,212,243,273,304,334;
    int idx = end_month - 1;
    double deltat = time_equation(end_year,daysinmon(idx)+end_day); //returns minutes, so deltat is time in minutes

    //cout << "end_year: " << end_year << endl; 
    //cout << "daysinmon(idx)+end_day: " << daysinmon(idx)+end_day << endl;
    //cout << "deltat: " << deltat << endl; //CORRECT!!

    //Now we add or subtract this delta to our end_time which gives us the exact sundial time of greenwhich
    // so we update t_ec

    t_ec = t_ec + deltat*60; //Manually Adding time eqation to t_ec, to correct for offset to mean solar time
    tm_ec = localtime(&t_ec);//Converting again back to tm_ec to retrieve an exact solar hour in the day

    end_hour = tm_ec->tm_hour;
    end_min = tm_ec->tm_min;
    end_sec = tm_ec->tm_sec;
    end_dlst = tm_ec->tm_isdst;

    //If daylightsaving time is in effect we need to subtract 1 hour, to yield the correct solar time
    if (end_dlst > 0) {
        end_hour--;
    }
    //} else if (end_dlst == 0) {
    //    std::cout << "Daylight saving time is not in effect." << std::endl;
    //} else {
    //    std::cout << "Daylight saving time information is not available." << std::endl;
    //}

    //Since sun is moving as well during siderial rotation of greenwich, the difference in angular velocity is used
    double gwo = (omega_gw-omega_s)*(12*3600-(3600*end_hour+60*end_min+end_sec)); //greenwhich offset to e_x axis in degree
    //TODO what happens when time equation pushes offset beyond midnight ?
    
    //cout << "end_hour: " << end_hour << endl;
    //cout << "end_min: " << end_min << endl;
    //cout << "gwoff: " << gwo << endl; //CORRECT!!!

                                                                          
            
            
    //Now here we can caculate the true longditude (=angle relative to greenwich) by using the 
    //greenwich offset form the x axis. longditude is positive for eastern and negative for western hemisphere.
    longditude = phi + gwo;

    // cout << "phi: " << phi << endl; //CORRECT!
    
    out << longditude,latitude;
    return out;
}

/*
int main() {

    Vector3d r_s,r_e,r_m,r_isx,omega;
    double deltatime = 198000;
    init_year = 2024;
    init_month = 9;
    init_day = 30;
    init_hour = 12;
    init_min = 0;
    init_second = 0;

    int n = 6;

    r_s << -9.508086328426406E+05, -6.781351825436755E+05,  2.832438166907258E+04;
    r_e << 1.466004019114228E+08,  2.462631199170237E+07,  2.609139532133006E+04;
    r_m << 1.461998323247219E+08,  2.455707687435411E+07,  2.379667880138569E+04;
    omega << 1.54277026861935e1, 2.528775803839025e3, 5.832096956033017e3;

    double radius_sun = 695508;
    double radius_moon = 1737.5;
    double radius_earth = 6371;
    ArrayXXd p_parameters1900 = umbrapar(r_s,r_m,radius_sun,radius_moon,n,'p');
    ArrayXXd u_parameters1900 = umbrapar(r_s,r_m,radius_sun,radius_moon,n,'u');
    ArrayXXd earth_isx1900 = umbraisx(p_parameters1900,u_parameters1900,r_e,radius_earth);

    Vector3d testisx;

    Vector2d sol;
    for (size_t i = 0; i < n; i++)
    {
        testisx = earth_isx1900.col(i);
        sol = longlat(testisx,r_e,r_s,omega,deltatime);
        cout << "(lat,long): " << sol(1) << "," << sol(0) << endl;
    }
 
   

    return 0;
}

*/