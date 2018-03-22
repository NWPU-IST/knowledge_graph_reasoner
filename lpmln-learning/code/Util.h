#pragma once

#include <algorithm>
#include <string>

#include <stdio.h>
#include <stdlib.h>

#include "exptrk.h"

class Util
{
public:
	Util();
	~Util();

	static void toLower(std::string& str){
		transform(str.begin(), str.end(), str.begin(), tolower);
	}

	static void toUpper(std::string& str){
		transform(str.begin(), str.end(), str.begin(), toupper);
	}

	static void merge(std::string fname1, std::string fname2, std::string fname3){
		std::string str = "cat " + fname1 + " " + fname2 + " > " + fname3;
		system(str.c_str());
	}

	static void replace(std::string& str, const std::string& from, const std::string& to) {
	    size_t start_pos = str.find(from);
	    while(start_pos != std::string::npos){
		    str.replace(start_pos, from.length(), to);
		    start_pos = str.find(from);
		}
	}

	static float getValue(std::string str){
	   typedef exprtk::symbol_table<float> symbol_table_t;
	   typedef exprtk::expression<float>     expression_t;
	   typedef exprtk::parser<float>             parser_t;

	   symbol_table_t symbol_table;
	   symbol_table.add_constants();

	   expression_t expression;
	   expression.register_symbol_table(symbol_table);

	   parser_t parser;
	   parser.compile(str,expression);

	   float y = expression.value();
	   return y;
	}


};
