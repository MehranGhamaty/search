#ifndef SIMPLEX_HPP
#define SIMPLEX_HPP

#include "tableau.hpp"

namespace tableau {
    template<typename N> 
    std::tuple<N, int> findmininrow(std::vector<N> searchingthrough) {
        N minv = std::numeric_limits<N>::max();
        int minc = -1;
        
        for(int c = 0; c < searchingthrough.size(); ++c) {
            if(searchingthrough.at(c) < minv) {
                minv = searchingthrough.at(c);
                minc = c;
            }
        }

        return std::make_tuple(minv, minc);
    }

    template<typename N>
    std::tuple<N, int, N> findminratio(const tab<N>& t,int minc){
        N ratio, minrv = std::numeric_limits<N>::max(), minratio= std::numeric_limits<N>::max(); int minr = -1;

        for(int r = 0; r < t.tableau.size()-1; ++r ) {
            //only consider values where the last column is not negative
            if(t.tableau.at(r).at(minc) <= 0) continue;
            //calculate ratio
            ratio = t.tableau.at(r).at(t.tableau.at(r).size()-1) / t.tableau.at(r).at(minc);

            if(ratio < minratio) {
                minratio = ratio;
                minr = r;
                minrv = t.tableau.at(r).at(minc);
            }
        }

        return std::make_tuple(minratio, minr, minrv);

    }

    template<typename N>
    void normalizerow(std::vector<N>& row, N rowv) {
        if(rowv != 1) {
            for(auto& e: row) {
                e /=rowv;
            }
        }
    }

    template<typename N>
    std::tuple<bool, tab<N>> simplex(const tab<N>& tableau, bool verbose=false) {
        tab<N> tmp(tableau); 

        if(verbose) {
            std::cout << "about to start running simplex on \n";
            printtableau(tmp);
        }


        bool bounded = true;
        do {
            N minv; int minc;
            std::tie(minv, minc) = findmininrow(tmp.tableau.at(tmp.tableau.size()-1));
            if(minv >= 0) {
                if(verbose) { std::cout << "all constraints are positive, nothing to reduce" << std::endl;}
                break;
            }

            if(verbose) {
                std::cout << "found " << minv << " at column " << minc <<std::endl;
            }
            
            N minratio, minrv; int minr;
            std::tie(minratio, minr, minrv) = findminratio(tmp, minc);
            if(minr == -1) bounded = false;


            if(verbose) {
                std::cout << "Found min ratio " << minratio << " at row " << minr << " which has value " << minrv << std::endl;  
            }

            if(bounded) { 
                normalizerow(tmp.tableau.at(minr), minrv);

                for(int r = 0; r < tmp.tableau.size();++r) {
                    if(r == minr) continue;
                    N coef = -1. * tmp.tableau.at(r).at(minc) / tmp.tableau.at(minr).at(minc);
                    if(verbose) std::cout << "coef is "<< coef << " for row " << r << std::endl;
                    tmp.tableau.at(r) = add(tmp.tableau.at(r), 1., tmp.tableau.at(minr), coef);
                }


                if(verbose) {
                    std::cout << "after reducing this row" << std::endl;
                    printtableau(tmp);
                }
            }
        } while(bounded);

        if(verbose) {
            std::cout << "finished running simplex" << std::endl;
        }
        return std::make_tuple(bounded,tmp);
    }
}
#endif
