#include <iostream>
#include <vector>
#include <tuple>

#include "tableau.hpp"
#include "simplex.hpp"

using namespace std;
using namespace tableau;

int main(int argc, char* argv[]) {
    if(not(argc == 2 or argc == 3)){
        cerr << "Usage: " + string(argv[0]) + " inputpath [outputpath]" << endl;
        return -1;
    }
    string inputpath = string(argv[1]);
    string outputpath = "simplex.out";
    if(argc == 3) {
        outputpath = string(argv[2]);
    }

    bool verbose = false;
    auto printrow = [] (auto v) {for(const auto& e:v){cout<< e << "\t\t|";}cout<< endl;};
    auto mapfun = [] (auto f, auto v) {for(const auto& e:v){f(e);}};

    tab<double> tableau = readfile<double>(inputpath);
    //auto[tableau, m, n] = readfile<double>(string(argv[1])); //:( need a newer compiler

    if(verbose) {
        printtableau(tableau);
    }

    bool bounded, feasible=true;
    tie(bounded, tableau) = simplex(tableau);

    if(verbose) {
        cout << "reduced:" << endl;
        printtableau(tableau);
    }

    writeresults(tableau, bounded, feasible, outputpath);
    return 0;
}
