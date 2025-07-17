using namespace std;
using namespace Eigen;
using namespace std::chrono;
#define G 6.6743015e-11
#define M_e 5.9722e24
#define r_e 6378e3
#define R_e 149.60e9
#define M_s 1.98892e30
#define M_j 1.89813e27
#define M_m 7.346e22

using namespace std;
using namespace std::chrono;
using namespace Eigen;


using Eigen::MatrixXd;
using Eigen::VectorXd;
using Array13 = Array<double, 1, 3>;
using Array16 = Array<double, 1, 6>;

Array16 k2;
Array16 k3;
Array16 k4;
double inter;
double invr3;
Array13 r21;
int P = 3;

VectorXd g_acc(double x1, double y1, double z1, double x2, double y2, double z2, double m){ 
	// force points from r_1 to r_2. Mass m is mass of the central body whose acceleration is to be caculated.
	// mass m sits with this above convention at r_2.
	VectorXd out(3);
	double G_m_inv_r_3 = G * m * pow(pow(x2-x1,2)+pow(y2-y1,2)+pow(z2-z1,2),-3./2);
	out(0) = G_m_inv_r_3 * (x2-x1);
	out(1) = G_m_inv_r_3 * (y2-y1);
	out(2) = G_m_inv_r_3 * (z2-z1);
	return out;
}


Array13 vecg_acc(Array13 r1, Array13 r2, double m) {
	Array13 out(1,3);
	//double inter=
	inter = pow((r1-r2)(0),2)+pow((r1-r2)(1),2)+pow((r1-r2)(2),2); //TODO optimize!!! use eigen::functions to									      //calculate norm of 3,1-array!
	out = pow(inter,-3./2) * G * m * (r2-r1);
	

	return out;

}


Array16 flow_f(Array13 v, Array13 r1, Array13 r2, double m) {
	Array16 flow_f_out;
	double flow_f_invr3 = pow(pow((r1-r2)(0),2)+pow((r1-r2)(1),2)+pow((r1-r2)(2),2),-3./2); //TODO optimize using
												//Eigen library for
												//norm
	flow_f_out.segment(0,3) = G * m * flow_f_invr3 * (r2-r1);
	
	flow_f_out.segment(3,3) = v;	

	
	return flow_f_out;
}

Array<double,1,26> full_flow_f(Array<double,1,13> r, Array<double,1,13> v)  {
	// Sun(1,3), Earth(4,3), Moon(7,3), Jupiter(10,3)
	Array<double,1,26> output;
	//TODO optimization same positions are called multiple times, one could store it in variables pos_e,pos_m etc.
	//TODO diagonal interactions are calculated twice
	//Here the interaction terms can be manually added!
	//Sun
	output(0) = 0;
	output.segment(1,3) = vecg_acc(r.segment(1,3),r.segment(4,3),M_e)+vecg_acc(r.segment(1,3),r.segment(7,3),M_m)+		vecg_acc(r.segment(1,3),r.segment(10,3),M_j);
	//Earth
	output.segment(4,3) = vecg_acc(r.segment(4,3),r.segment(1,3),M_s)+vecg_acc(r.segment(4,3),r.segment(7,3),M_m)+		vecg_acc(r.segment(4,3),r.segment(10,3),M_j);
	//Moon
	output.segment(7,3) = vecg_acc(r.segment(7,3),r.segment(1,3),M_s)+vecg_acc(r.segment(7,3),r.segment(4,3),M_e)+		vecg_acc(r.segment(7,3),r.segment(10,3),M_j);
	//Jupiter
	output.segment(10,3) = vecg_acc(r.segment(10,3),r.segment(1,3),M_s);
	
	output.segment(13,13) = v;
	return output;	
		
}

void print_time(string ref_date,int nosec) {
	//Prints the time in UTC format, given a reference date and a number of seconds to add to it
	// ref_date: date in format "Jul 12 2024 00:00:00"
	// nosec: number of seconds to add to the reference date
	tm t;
	stringstream ss(ref_date);
	ss >> get_time(&t, "%b %d %Y %H:%M:%S ");
	system_clock::time_point init_date = chrono::system_clock::from_time_t(std::mktime(&t));
	system_clock::time_point init_date_plus = init_date + duration<int>(nosec);

	time_t tt = system_clock::to_time_t(init_date_plus);

	tm utc_tm = *gmtime(&tt);

	cout << utc_tm.tm_year + 1900 << "/" << setw(2) << setfill('0') << utc_tm.tm_mon + 1 << "/" 
	<< setw(2) << setfill('0') << utc_tm.tm_mday << " " 
	<< setw(2) << setfill('0') << utc_tm.tm_hour << ":" 
	<< setw(2) << setfill('0') << utc_tm.tm_min << ":" 
	<< setw(2) << setfill('0') << utc_tm.tm_sec << "UTC"; 


}



Vector3d cross_product(Vector3d a, Vector3d b) {
	Vector3d out;
	out(0) = a(1)*b(2)-a(2)*b(1);
	out(1) = a(2)*b(0)-a(0)*b(2);
	out(2) = a(0)*b(1)-a(1)*b(0);
	return out;
}

vector<int> count_blocks(vector<int> inputvec, double deltaseconds) {
	//Counts the number of blocks in a vector, i.e. the number of times 0 values changes to 1
	//Also prints out the times of the indices where the blocks start
	vector<int> outputvec(1,0);
	outputvec[0] = 0;
	int start_sec = 0;
	for (size_t i = 1; i < inputvec.size(); i++) {
		if (inputvec[i] == 1 && inputvec[i-1] == 0) {
			outputvec[0] += 1;
			start_sec = i*deltaseconds;
			outputvec.push_back(start_sec);
		}
	}

	return outputvec;
}

void print_vec_to_file(const string& filename, const vector<int>& vec) {
	//Helperfunction that prints vector to file, one value per line for debugging purposes
	ofstream file(filename);
	if (!file.is_open()) {
		cerr << "Error opening file: " << filename << endl;
		return;
	}
	int valuebefore = 0, idx = 0;
	vector<int> start_indices;
	for (const auto& value : vec) {
		idx += 1;
		
		file << value << endl;
		if (value == 1 && valuebefore == 0) {
			start_indices.push_back(idx);
		}
		valuebefore = value;
	}
	file << "Ones start at indices: ";
	for (const auto& start_idx : start_indices) {
		file << start_idx << " ";
	}

	file.close();
}