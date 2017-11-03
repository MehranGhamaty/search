#ifndef BRANCHANDCUT_HPP
#define BRANCHANDCUT_HPP

#include <queue>
#include <random>
#include "simplex.hpp"

namespace tableau { 
    template<typename N >
    std::tuple< tab<N>, tab<N>> branch(const tab<N>& t, int loc, N nonintegral, bool verbose=false) {
        tab<N> leftcut(t); 
        tab<N> rightcut(t); 
        N leftval = std::ceil(nonintegral);
        N rightval = std::floor(nonintegral); 

        if(verbose) std::cout << "left / right " << leftval << " / " << rightval << std::endl;

        std::vector<N> leftnewrow(leftcut.tableau.at(0).size());
        leftnewrow.at(leftnewrow.size()-1) = leftval; leftnewrow.at(loc) = 1;

        std::vector<N> rightnewrow(rightcut.tableau.at(0).size());
        rightnewrow.at(rightnewrow.size()-1) = rightval; rightnewrow.at(loc) = 1;

        leftcut.tableau.insert(leftcut.tableau.end()-1, leftnewrow);
        rightcut.tableau.insert(rightcut.tableau.end()-1, rightnewrow);

        addslackvariable(leftcut, leftcut.tableau.size()-2, -1.);
        addslackvariable(rightcut, rightcut.tableau.size()-2, 1.);

        if(verbose) {
            printtableau(leftcut);
            printtableau(rightcut);

        }

        return std::make_tuple(leftcut,rightcut);
    }


    template<typename N>
    tab<N> cut(const tab<N>& origt, const tab<N>& modt, int row, int col, N nonintegral, bool verbose=false) {
        tab<N> cut(origt); 


        std::vector<N> newconstraint(modt.tableau.at(0).size(), 0);
        newconstraint.at(col) = 1;
        newconstraint.at(newconstraint.size()-1) = std::floor(nonintegral);

        //auto findnonzero = []() 
        if(verbose) {
            std::cout << "subtacting:\n";
            for(const auto& e: modt.tableau.at(row)) {std::cout << e << "\t";} std::cout << std::endl;
            for(const auto& e: newconstraint) {std::cout << e << "\t";} std::cout << std::endl;
        }
        newconstraint = add(newconstraint, -1., modt.tableau.at(row), 1.);

        //now add the new constraint to our cuttableau, but first....
        //lets do some algebra
        std::vector<N> transformedconstraint(newconstraint);
        if(verbose) {
            std::cout << "transformed constraint:\n";
            for(const auto& e: transformedconstraint) {std::cout << e << "\t";} std::cout << std::endl;
        }
        for(int c = 0;c < newconstraint.size()-1; ++c) {
            //get first N columns where s appear in new constraint
            if(newconstraint.at(c) != 0) {
                //find another column in cuttableau where this column is 1
                //Tc - N 
                row = c-cut.n;
                                
                transformedconstraint = add(transformedconstraint, 1., cut.tableau.at(row), -1. * newconstraint.at(c)); 
                transformedconstraint.at(c) = 0;
            }
        }

        cut.tableau.insert(cut.tableau.end()-1, transformedconstraint);
        //add a slack variable
        addslackvariable(cut, cut.tableau.size()-2, -1.); //TODO is it 1 or -1
        if(cut.tableau.at(cut.tableau.size()-2).at( cut.tableau.at(cut.tableau.size()-2).size()-1 ) < 0) {
            for(int c = 0; c < cut.tableau.at(cut.tableau.size()-2).size(); ++c) {
                cut.tableau.at(cut.tableau.size()-2).at(c) *= -1.;
            }
        }

        return cut;
    }

    template<typename N>
    std::tuple<bool, bool, tab<N>> branchandcut(const tab<N>& t, bool verbose=false) {
        auto tmp(t); 
        bool bounded = true, feasible = true;
        std::mt19937 gen(std::random_device{}());
        std::uniform_real_distribution<> dis(0.0,1.0);
        double thresholdforbranching = 0.1; //heavily prefer cutting over branching initially 
        
        std::queue<tab<N>> solutions;
        solutions.emplace(tmp);

        if(verbose) {
            std::cout << "starting branch and cut with:\n";
            printtableau(tmp); 
        }
 
        auto findnonintegral = [] (std::vector<N> searchingthrough) -> std::tuple<bool, int>
        {
            bool integral = true; int loc = -1;
            for(int i = 0; i < searchingthrough.size() and integral; ++i) {
                if( not isintegral(searchingthrough.at(i))) {
                    integral = false;
                    loc = i;
                }
            }
            return std::make_tuple(integral, loc);
        };
            
        int i = 0;
        bool integral; int col; int row; std::vector<N> solution;
        while(not solutions.empty()){
            if(verbose) {
                std::cout << "queue size is " << solutions.size() <<std::endl;
            }

            tab<N> checking = solutions.front();solutions.pop();
            tab<N> reduced;

            std::tie(bounded,reduced) = simplex(checking, verbose);++i;
            if(not bounded) {
                if(verbose) {std::cout << "solution not bounded, number of tableaus solved: "<< i << std::endl;}
                return std::make_tuple(false, true, checking);
            }
            
            std::tie(feasible, solution) = getsolution(reduced);
            if(not feasible) {
                if(verbose) {std::cout << "solution not feasible, number of tableaus solved:  "<< i << std::endl;}
                return std::make_tuple(true, false, checking);
            }

            std::tie(integral, col) = findnonintegral(solution);
            if(integral) {
                if(verbose) {std::cout << "solution is integral, number of tableaus solved:  " << i << std::endl;}
                return std::make_tuple(true, true, reduced);
            }

            
            double v = dis(gen);
            if(verbose) std::cout << "rng: " << v << std::endl;
            if(thresholdforbranching>v) {
            //if(false) {
                if(verbose) {
                    std::cout << "branching" << std::endl;
                }
                auto toreduce = branch<N>(checking, col, solution.at(col), verbose);
                solutions.emplace(std::get<0>(toreduce)); 
                solutions.emplace(std::get<1>(toreduce)); 
            } else {
                if(verbose) {
                    std::cout << "cutting" << std::endl;
                }
                //the row is 
                for(int r=0; r < reduced.tableau.size(); ++r) {
                    if(reduced.tableau.at(r).at(reduced.tableau.at(r).size()-1) == solution.at(col)) {
                        row = r;
                        break;
                    }
                }
                if(verbose) {std::cout << "selected row is " << row << std::endl;}
                solutions.emplace(cut<N>(checking, reduced, row, col, solution.at(col), verbose));
                thresholdforbranching *= 2;
            }

        }        
    }
}
#endif
