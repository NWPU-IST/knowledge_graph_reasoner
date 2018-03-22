#include <iostream>
#include <string>
#include <fstream>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/regex.hpp>
#include <boost/iostreams/filtering_stream.hpp>
#include <exception>
#include <set>
#include <stack>
#include <vector>
#include <algorithm>
#include <sstream>
#include <iterator>
#include <stdexcept>      // std::invalid_argument
#include <cmath>


#include "Util.h"


using namespace std;
using namespace boost;
namespace io = boost::iostreams;

#define global 0
#define local 1

//build
//g++ -g -std=c++11 lpmln2wc.cpp -o lpmln2wc -L /usr/lib -lboost_regex

// TODO: variables in unsat

set<string> findVariables(const string&);
set<string> findFreeVariables(const string&, const string&);

float GetFloatPrecision(float& x){
    //return (floor((value * pow(10, precision) + 0.5)) / pow(10, precision));
    x = x + 2;
    x = ceilf(x * 10000) / 10000;
    x = x - 2;
    return x;
}

set<string> separateHeadDisjunction(const string& head){
	int posStart = 0;
	int posEnd = -1;

	set<string> returnSet;
	unsigned int i = 0;

	for(i=0;i<head.length();i++){
		if(head.at(i) == '{'){
			while(head.at(i) != '}')
				i++;
		}

		else if(head.at(i) == '('){
			while(head.at(i) != ')')
				i++;
		}

		else if(head.at(i) == ';'){

			returnSet.insert(head.substr(posStart, i-posStart == 0? 1 : i-posStart));
			posStart = i+1;
		}
	}

	returnSet.insert(head.substr(posStart, i-posStart == 0? 1 : i-posStart));
	return returnSet;
}

set<string> findVariables(const string& head){

	set<string> sGlobal;
	set<string> sLocal;
	set<string> result;

	//switch
	int area = global;

	stack<int> stack;
	for(unsigned int i=0;i<head.length();i++){
		if(head.at(i) == '('){
			stack.push(0);
		}

		else if(head.at(i) == '#' || head.at(i) == '{'){
			while(head.at(i) != '}')
				i++;
			// area = local;
			i++;
		}

		else if(head.at(i) == ':'){
			while(head.at(i) != ',' && head.at(i) != ';' && head.at(i) != '.' && head.at(i) != '-'){
				i++;
				if(i >= head.length()) break;
				// area = local;
			}
			i++;
		}

		string tempStr;
		while(!stack.empty()){
			i++;
			if(i == head.length()) break;

			if( (int)head.at(i) >= 65 && // A
				(int)head.at(i) <= 90 && // Z
				( 	(int)head.at(i-1) == 44 || //comma
					(int) head.at(i-1) == 40 ||  // opening paren
					(int) head.at(i-1) == 32 )
				) { //space
				bool areaSwitch = false;
				while(true){

					tempStr += head.at(i);
					i++;

					if(i == head.length()){
						break;
					}

					if(head.at(i) == ',')
						break;

					if(head.at(i) == '('){
						stack.push(0);
					}

					if(head.at(i) == ')'){
						stack.pop();
						break;
					}

					if(head.at(i) == '}'){
						areaSwitch = true;
						break;
					}
				}

				if(area == global && !areaSwitch)
					sGlobal.insert(tempStr);
				else
					sLocal.insert(tempStr);
				tempStr = "";
			}

			if(!stack.empty() && head.at(i) == ')'){
				area = global;
				stack.pop();
			}
		}
	}
	set_difference(sGlobal.begin(), sGlobal.end(), sLocal.begin(), sLocal.end(),inserter(result, result.end()));



	return result;
}

void printHelp(){
	cerr << "Usage: lpmln2cl <file_name> <options>\n"
			"Options:\n"
			"	--tr-hr=false 			Hard rules are not translated\n"
			"	--tr-hr=true			Hard Rules are translated\n"
			"	--infer-type=map 		Map estimation\n"
			"	--infer-type=query		Probability Calculation\n"
			"	--h 				Print help\n"
			"For the option infer-type=query, the program will prompt you for query input. The system halts untill an input is provided. The user can choose to not provide any input by hitting return key.\n";
}

set<string> findFreeVariables(const string& head,const string& body){
	set<string> s = findVariables(head);
	set<string> s1 = findVariables(body);
	// set<string> intersect;
	// set_intersection(s.begin(), s.end(), s1.begin(), s1.end(),inserter(intersect, intersect.begin()));
	s.insert(s1.begin(), s1.end());
	// return intersect;
	s.insert(s1.begin(), s1.end());
	// cout << "global:" ;
	// for(auto iter=s.begin(); iter!=s.end();++iter) { cout << *iter << " ";}cout << endl;
	return s;
}


int main(int argc, char **argv){

	ifstream file(argv[1], ios_base::in | ios_base::binary);

	// int mode = 0;

	// if(argc == 3)
	// 	mode = *argv[2] - '0';

	int unsatcount = 1;
	int ignorecount = 1;
	string str;

	int mf = 1;


	//Default mode is 0, which translates all rules.
	//Mode 1 translates only soft rules.
	int mode = 1;

	if(argc >= 3){
		std::stringstream ss(argv[2]);
		ss >> mode;
		if(mode != 0 && mode != 1){
			cout << "Invalid 3rd argument. Can be either 0 or 1.\n";
			exit(1);
		}

	}

	if(file){

	    try{
			io::filtering_istream in;

			in.push(file);
			bool f = false;
			for(str; getline(in, str); ){

				if(str.length() == 0) continue;

				if(str[0] == '%'){
					//ignore comments
					cout<<str+"\n";
					continue;
				}




				std::size_t found;
				if(!f){
					found = str.find("python");
					if(found != std::string::npos) {
						f = true;
					}
				}


				if(f){
					cout<<str + "\n";
					found = str.find("end");
					if(found != std::string::npos)
						f = false;
					continue;
				}

				trim(str);
				//splits the rule to head and body
				vector<string> splitVec;


				boost::algorithm::split_regex(splitVec, str, regex(":-"));
				//splits the head into weight part and rule part
				vector<string> splitVecSpace;
				float weight = 0;

				bool isFuncUsed = false;
				string funcValue = "";
				string funcVar = "";

				bool issoft = false;
				//even if size is 2 it could be possibe that the first one is a function.
				//check for this condition.
				// if(splitVec.size() != 1){
				// 	if (splitVec[0].find("@") == 0){
				// 		/* code */
				// 		isFuncUsed = true;
				// 		// funcValue = splitVec[0];
				// 		// splitVec.erase(splitVec.begin());
				// 		// funcVar = funcValue.substr(funcValue.find("(")+1, 1);
				// 		issoft = true;
				// 	}
				// }



				if(splitVec.size() == 1 && !issoft){
					//process it if its of the form
					// W H. or H.

					split(splitVecSpace, splitVec[0], is_any_of(" "), token_compress_on);
					//Process soft rules of form W H.
					try{
						std::string::size_type sz;
						float floatVal = 0;
						//Cnotrols how weight is printed inside unsat atoms.
						bool weightSwitch = false;

						//Check if it is a function.
						if(splitVecSpace[0].find("@") == 0){

							// weightSwitch = true;
							std::string temp = splitVecSpace[0].substr(1, splitVecSpace[0].length()-1);
							float floatTemp  = Util::getValue(temp);
							if(isinf(floatTemp) || isnan(floatTemp)) {
								std::cerr<< "resulting value infinity or NAN for rule number " << unsatcount + 1<< "\n.";
								exit(1);
							}
							weight = GetFloatPrecision(floatTemp);

						}
						else{
							floatVal = stof(splitVecSpace[0],&sz);
							if(isinf(floatVal) || isnan(floatVal) || sz != splitVecSpace[0].length())
								throw std::runtime_error("inf/nan error");

							weight = floatVal;
						}


						string newStr;

						for(unsigned int i=1;i<splitVecSpace.size();i++){
							newStr += splitVecSpace[i] + " ";
						}
						string tempstr;

						set<string> s = findVariables(newStr);
						string vars;
						for(auto itr = s.begin(); itr!=s.end();++itr)
							vars += *itr + ",";
						if(vars.length() != 0){
							vars.pop_back();
							vars = "," + vars;
						}

						splitVecSpace[1].pop_back();
						trim(newStr);
						newStr.pop_back();

						string oldVars = vars;
						if(weightSwitch)
							vars = "," + splitVecSpace[0] + vars ;
						else
							vars = ",\""+ to_string(weight) + "\"" + vars ;

						string count;
					  if (str.find("ignore") >= 0) {
							count = "\"ig" + to_string(ignorecount++) + "\"";
						} else {
							count = to_string(unsatcount++);
						}
						
						replace_all(vars, ".", "$");
						
						tempstr = "unsat(" + count + vars + ") :-";

						set<string> headStr = separateHeadDisjunction(newStr);
						string newHeadStr;
						if(headStr.size() > 0){
							for(auto itr = headStr.begin(); itr != headStr.end(); ++itr){
								if((*itr).length() > 0){
									newHeadStr += "not " + *itr + ",";
								}
							}
						}

						if(newHeadStr.length() > 0)
							newHeadStr = newHeadStr.substr(0, newHeadStr.length() - 1);

						tempstr +=  newHeadStr + ".\n" + newStr + ":-" ;

						tempstr += "not unsat(" + count + vars + ")";
						if(weightSwitch)
							tempstr +=  ".\n:~ unsat(" + count + vars +"). [" + splitVecSpace[0] + "@0,"+ count+ oldVars +"]\n";
						else
							tempstr +=  ".\n:~ unsat(" + count + vars +"). [" + to_string((int)(weight*mf)) + "@0,"+ count+ oldVars +"]\n";

						cout<<tempstr;

					}
					//Process hard rules of form H.
					catch(const std::exception& ex){
						// It could be of type H. Process it.

						//additional check for @ clingo funcitons


						if(mode == 1){
							//Hard facts are untouched in Mode 1
							cout << str + "\n";
							continue;
						}

						//Remove . at the end
						str.pop_back();

						set<string> s = findVariables(str);
						string vars;
						for(auto itr = s.begin(); itr!=s.end();++itr){
							if(isFuncUsed && (*itr).compare(funcVar) == 0)
								vars += funcValue + ",";
							else
								vars += *itr + ",";
						}
						if(vars.length() != 0){
							vars.pop_back();
							vars = "," + vars;
						}

						string oldVars = vars;
						vars = ",\"a\"" + vars ;

						set<string> headStr = separateHeadDisjunction(str);
						string newHeadStr;
						if(headStr.size() > 0){
							for(auto itr = headStr.begin(); itr != headStr.end(); ++itr){
								if((*itr).length() > 0){
									newHeadStr += "not " + *itr + ",";
								}
							}
						}

						if(newHeadStr.length() > 0)
							newHeadStr = newHeadStr.substr(0, newHeadStr.length() - 1);

						string tempstr = "unsat("+to_string(unsatcount)+vars+") :- "+ newHeadStr + ".\n" +
											str + " :- not unsat(" + to_string(unsatcount) +vars+ ").\n" +
											":~ unsat(" + to_string(unsatcount) +vars+"). [1@1," + to_string(unsatcount) + oldVars + "]";
								unsatcount++;
						cout << tempstr + "\n";

					}


					// dont process it
					// cout<<str + "\n";
				}
				else{
					trim(splitVec[0]);
					split(splitVecSpace, splitVec[0], is_any_of(" "), token_compress_on);

					string newStr;



					for(unsigned int i=1;i<splitVecSpace.size();i++){
						newStr += splitVecSpace[i] + " ";
					}

					string tempstr;
					string weightString;
					set<string> s;
					issoft = false;
					bool weightSwitch = false;


					try{
						std::string::size_type sz;
						//Cnotrols how weight is printed inside unsat atoms.

						//Check if it is a function.
						if(splitVecSpace[0].find("@") == 0){
							// weightSwitch = true;

							// weightString = splitVecSpace[0];

							std::string temp = splitVecSpace[0].substr(1, splitVecSpace[0].length()-1);
							float floatTemp  = Util::getValue(temp);
							if(isinf(floatTemp) || isnan(floatTemp)) {
								std::cerr<< "resulting value infinity or NAN for rule number " << unsatcount + 1<< "\n.";
								exit(1);
							}
							weight = GetFloatPrecision(floatTemp);

						}
						else{
							float floatVal = stof(splitVecSpace[0],&sz);
							if(isinf(floatVal) || isnan(floatVal) || sz != splitVecSpace[0].length())
								throw std::runtime_error("inf/nan error");

							weight = (floatVal);
							// weightString = to_string((int)(weight*mf)) + "@0";
						}

						weightString = to_string((int) (weight * mf)) + "@0" ;


						issoft = true;
						s = findFreeVariables(newStr, splitVec[1]);
					}
					catch (const std::invalid_argument& ia) {
						weightString = "1@1";
						s = findFreeVariables(splitVec[0], splitVec[1]);
						splitVecSpace.clear();
						newStr = splitVec[0];
					}
					catch(...){
						weightString = "1@1";
						s = findFreeVariables(splitVec[0], splitVec[1]);
						splitVecSpace.clear();
						newStr = splitVec[0];
					};

					// set<string> s = findFreeVariables(newStr, splitVec[1]);
					string vars;
					for(auto itr = s.begin(); itr!=s.end();++itr)
						vars += *itr + ",";
					if(vars.length() != 0){
						vars.pop_back();
						vars = "," + vars;
					}


					splitVec[1].pop_back();
					string probString = "";

					if(issoft && !weightSwitch)
						probString += ",\""+to_string(weight)+"\"";
					else if(weightSwitch)
						probString += "," + splitVecSpace[0];
					else
						probString += ",\"a\"";

					string oldVars = vars;
					vars = probString + vars;
					replace_all(vars, ".", "$");

					//If it is a constraint newStr is empty,
					//newStr holds value of splitVec[0] which is empty in case of a constraint.
					// if(newStr.length() != 0){
					// 	newStr = ", not " + newStr;
					// }

					if(splitVecSpace.size() == 1){
						//W :- B
						//weighted constraints
						// cout << "366\n";
						tempstr = "unsat(" + to_string(unsatcount) + vars + ") :- " + splitVec[1]+ ".\n" +
										+ ":- " + splitVec[1] + ", not " + "unsat(" + to_string(unsatcount) + vars + ").\n"
										+ ":~ "+ "unsat(" + to_string(unsatcount) + vars + ")." + "["+ weightString +","+ to_string(unsatcount)+ oldVars +"]\n" ;

						// tempstr = ":~ "+ splitVec[1]+ "." + "["+ weightString +","+ to_string(unsatcount)+ oldVars +"]\n" ;

					}
					// Hard rules/constraints are ignored.
					else{
						//This is a constraint.
						if(newStr.empty()){
							//if soft rule translate it irrespective of the mode.
							if(issoft || (!issoft && mode == 0)){
								// tempstr = "unsat(" +
								// cout << "377\n";
								tempstr = "unsat(" + to_string(unsatcount) + vars + ") :- " + splitVec[1]+ ".\n" +
										+ ":- " + splitVec[1] + ", not " + "unsat(" + to_string(unsatcount) + vars + ").\n"
										+ ":~ "+ "unsat(" + to_string(unsatcount) + vars + ")." + "["+ weightString +","+ to_string(unsatcount)+ oldVars +"]\n" ;

								// "["+ weightString +","+ to_string(unsatcount)+ oldVars +"]\n" ;
								// tempstr = ":~ "+ splitVec[1]+ "." + "["+ weightString +","+ to_string(unsatcount)+ oldVars +"]\n" ;
							}
							else{
								tempstr = str + "\n";
							}
						}
						else if(issoft || (!issoft && mode == 0)){
							//Soft rules are translated irespective of the mode
							//Hard rules are translated only in mode 0
							set<string> headStr = separateHeadDisjunction(newStr);
							string newHeadStr;
							if(headStr.size() > 0){
								for(auto itr = headStr.begin(); itr != headStr.end(); ++itr){
									if((*itr).length() > 0){
										newHeadStr += "not " + *itr + ",";
									}
								}
							}

							if(newHeadStr.length() > 0)
								newHeadStr = newHeadStr.substr(0, newHeadStr.length() - 1);


							tempstr = "unsat(" + to_string(unsatcount) + vars + ") :-" + splitVec[1] + "," + newHeadStr + ".\n"
							+ newStr + ":-" + splitVec[1] + ", " + "not unsat(" + to_string(unsatcount) + vars + ")" + ".\n"
							+":~" + "unsat(" + to_string(unsatcount) + vars +")." + " [" + weightString + ","+ to_string(unsatcount)+ oldVars +"]\n";
						}
						else if(!issoft && mode == 1){
							//Hard rules are translated only in mode 0
							// cout << str + "\n";
							tempstr = str + "\n";
              unsatcount--;
						}
					}
					cout<<tempstr;

					unsatcount++;
				}
			}
		}
		catch(const std::exception& ia) {
	    	cout<<"Error: "<<ia.what();
	    	return -1;
    	}
    }
    else{
    	if(string(argv[1]) != "--h")
    		cerr << "Some error ocurred while processing this file!\n";
    	printHelp();
    	return 0;
    }
}
