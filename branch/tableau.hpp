
#ifndef TABLEAU_HPP
#define TABLEAU_HPP

#include <iostream>
#include <fstream>
#include <vector>
#include <limits>   //numeric_limits<N>::max()
#include <tuple>
#include <numeric>
#include <string>   //stod
#include <cmath>     //abs floor
#include <cassert>


namespace tableau {
    template<typename N>
    struct tab {
        std::vector<std::vector<N>> tableau;
        int m, n;
    };

    template<typename N>
    void printtableau(tab<N> t) {
        auto printrow = [] (auto v) {for(const auto& e:v){std::cout<< e << "\t\t|";}std::cout<< "\n";};
        auto mapfun = [] (auto f, auto v) {for(const auto& e:v){f(e);}};
        mapfun(printrow, t.tableau);
        std::cout << std::endl;        
    }

    std::vector<std::string> split(std::string line, std::string delim=" ") {
        while(line.size() > 0 and isspace(line.at(0))) line.erase(0,1);
        while(line.size() > 0 and isspace(line.at(line.size()-1))) line.erase(line.size()-1,1);
        std::vector<std::string> str; int start = 0;
        for(int i = 0; i < line.size(); ++i) {
            for(int j = 0; j < delim.size(); ++j) {
                if(i+j < line.size()-1 and line.at(i+j) != delim.at(j)) break;
                if(j == delim.size()-1) {
                    str.emplace_back(i==line.size()-1?line.substr(start,i-start+1):line.substr(start, i-start));
                    start = i+delim.size();
                }
            }
        }
        return str;
    }

    template<typename N>
    bool close_enough(N v0, N v1,double eps=0.0000001) {
        return std::abs(v0-v1) < eps;    
    }

    template<typename N>
    bool isintegral(N v, double eps=0.0000001) {
        return close_enough(std::floor(v), v) or close_enough(std::ceil(v), v);

    }

    template<typename N>
    tab<N> readfile(std::string filename){
        std::vector<std::string> splitres; std::string row;
        tab<N> t;

        std::ifstream file(filename);
        getline(file, row); splitres = split(row);
        t.m = stoi(splitres.at(0)); 
        t.n = stoi(splitres.at(1));

        //std::vector will be of size m + 1 * n+m+1
        t.tableau.resize(t.m+1 , std::vector<N>(t.n + t.m +1,0));
        
        //b
        getline(file, row); splitres = split(row); 
        assert(splitres.size() == t.m);
        for(int j = 0; j < splitres.size(); ++j) { 
            t.tableau.at(j).at(t.tableau.at(0).size()-1) = stod(splitres.at(j)); 
        }
        //c
        getline(file, row); splitres = split(row); 
        assert(splitres.size() == t.n);
        for(int j = 0; j < splitres.size(); ++j) { 
            t.tableau.at(t.tableau.size()-1).at(j) = -stod(splitres.at(j)); 
        }
       
        //a
        int i = 0;
        while(getline(file,row)) {
            splitres = split(row); 
            assert(splitres.size() == t.n); 
            for(int j = 0; j < splitres.size(); ++j) { 
                t.tableau.at(i).at(j) = stod(splitres.at(j)); 
            }
            ++i; 
        }
        file.close(); 
        assert(i == t.m);
        
        //i
        for(int i = 0; i < t.m ; ++i) {
            t.tableau.at(i).at(i+t.n) = 1;
        }
        
        return t; 
    }

    template<typename N>
    bool isfeasible(tab<N> t) {
        bool feasible; std::vector<N> coef;
        std::tie(feasible, coef) = getsolution(t); 
        return feasible;
    }

    template<typename N>
    void writeresults(tab<N> t, bool bounded, bool feasible, std::string filename){
        std::ofstream file(filename);
        if(not bounded) {
            file << "+inf";
        } else if (not feasible) {
            file << "bounded-infeasible\n";
        } else {
            std::vector<N> coef;
            std::tie(feasible, coef) = getsolution(t);
            file << t.tableau.at(t.tableau.size()-1).at(t.tableau.at(0).size()-1) << "\n";
            for(int i = 0; i < t.n; ++i) {
                file << coef.at(i) << "\n";
            }
        }
        file.close();
    }

    template<typename N>
    std::vector<N> add(const std::vector<N>& op0, N coef0, const std::vector<N>& op1, N coef1) { 
        assert(op0.size() == op1.size());
        std::vector<N> solution(op0.size(), 0);

        for(int c = 0; c < op0.size(); ++c) {
            solution.at(c) = coef0*op0.at(c) + coef1*op1.at(c);
        }
        
        return solution;
    }

    template<typename N>
    void subtract(const std::vector<N>& minued, std::vector<N>& subtrahend, N coef=1.) {
        for(int c = 0; c < subtrahend.size(); ++c) {
           subtrahend.at(c) -= coef*minued.at(c); 
        }
    }


    //this should be moved inside the branch code for performance reasons
    template<typename N> 
    void addslackvariable(tab<N>& t, int row, N value) {
        for(int i = 0; i < t.tableau.size(); ++i) {
            if(i == t.tableau.size()-2) {    
               t.tableau.at(i).insert(t.tableau.at(i).end()-2, value);
            } else {
               t.tableau.at(i).insert(t.tableau.at(i).end()-2 , 0);
            }
        }
    }


    template<typename N>
    std::tuple<bool, std::vector<N>> getsolution(tab<N> t) {
        std::vector<N> coef;
        N res;
        bool feasible = true;
        for(int c = 0; c < t.tableau.at(0).size()-1 and feasible; ++c) {
            for(int r = 0; r < t.tableau.size()-1 and feasible; ++r) {
                if(t.tableau.at(r).at(c) == 1) {
                    res = t.tableau.at(r).at(t.tableau.at(r).size()-1);
                    feasible = res >= 0;
                    coef.emplace_back(res);
                }
            }
        }
        return make_tuple(feasible, coef); 
    }

    /*
    template<typename O>
    auto invertoperator(O unaryoperator) {
        auto f = [=](auto v) {return not unaryoperator(v);};
        return f;
    }

    template<typename N, typename O>
    int findandreturn(std::vector<N> searchingthrough, O unaryoperator) {
        bool found = false;
        int loc = -1;
        for(int i = 0; i < searchingthrough.size(); ++i) {
            if(unaryoperator(searchingthrough.at(i))) {
                found = true;
                loc = i;
            }
        }
        return loc;   
    }
    */

}

#endif

