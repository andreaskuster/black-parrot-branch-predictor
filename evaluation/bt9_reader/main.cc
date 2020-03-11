///////////////////////////////////////////////////////////////////////
//  Copyright 2015 Samsung Austin Semiconductor, LLC.                //
///////////////////////////////////////////////////////////////////////

//Description : Main file for CBP2016 

#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>
#include <fstream>
#include <map>

using namespace std;

#include "utils.h"
//#include "bt9.h"
#include "bt9_reader.h"


int main(int argc, char *argv[]) {

    if (argc != 3) {
        printf("usage: %s <trace> <out>\n", argv[0]);
        exit(-1);
    }

    ////////////////////////////
    // read each trace record
    ////////////////////////////

    std::string trace_path;
    trace_path = argv[1];
    bt9::BT9Reader bt9_reader(trace_path);


    ofstream myfile;
    myfile.open(argv[2]);


    UINT64 PC;
    bool branchTaken;
    UINT64 branchTarget;


    for (auto it = bt9_reader.begin(); it != bt9_reader.end(); ++it) {

        PC = it->getSrcNode()->brVirtualAddr();
        branchTaken = it->getEdge()->isTakenPath();
        branchTarget = it->getEdge()->brVirtualTarget();
        OpType opType;


        bt9::BrClass br_class = it->getSrcNode()->brClass();
        opType = OPTYPE_ERROR;

        if ((br_class.type == bt9::BrClass::Type::UNKNOWN) && (it->getSrcNode()->brNodeIndex())) {
            opType = OPTYPE_ERROR; //sanity check
        } else if (br_class.type == bt9::BrClass::Type::RET) {
            if (br_class.conditionality == bt9::BrClass::Conditionality::CONDITIONAL)
                opType = OPTYPE_RET_COND;
            else if (br_class.conditionality == bt9::BrClass::Conditionality::UNCONDITIONAL)
                opType = OPTYPE_RET_UNCOND;
            else {
                opType = OPTYPE_ERROR;
            }
        } else if (br_class.directness == bt9::BrClass::Directness::INDIRECT) {
            if (br_class.type == bt9::BrClass::Type::CALL) {
                if (br_class.conditionality == bt9::BrClass::Conditionality::CONDITIONAL)
                    opType = OPTYPE_CALL_INDIRECT_COND;
                else if (br_class.conditionality == bt9::BrClass::Conditionality::UNCONDITIONAL)
                    opType = OPTYPE_CALL_INDIRECT_UNCOND;
                else {
                    opType = OPTYPE_ERROR;
                }
            } else if (br_class.type == bt9::BrClass::Type::JMP) {
                if (br_class.conditionality == bt9::BrClass::Conditionality::CONDITIONAL)
                    opType = OPTYPE_JMP_INDIRECT_COND;
                else if (br_class.conditionality == bt9::BrClass::Conditionality::UNCONDITIONAL)
                    opType = OPTYPE_JMP_INDIRECT_UNCOND;
                else {
                    opType = OPTYPE_ERROR;
                }
            } else {
                opType = OPTYPE_ERROR;
            }
        } else if (br_class.directness == bt9::BrClass::Directness::DIRECT) {
            if (br_class.type == bt9::BrClass::Type::CALL) {
                if (br_class.conditionality == bt9::BrClass::Conditionality::CONDITIONAL) {
                    opType = OPTYPE_CALL_DIRECT_COND;
                } else if (br_class.conditionality == bt9::BrClass::Conditionality::UNCONDITIONAL) {
                    opType = OPTYPE_CALL_DIRECT_UNCOND;
                } else {
                    opType = OPTYPE_ERROR;
                }
            } else if (br_class.type == bt9::BrClass::Type::JMP) {
                if (br_class.conditionality == bt9::BrClass::Conditionality::CONDITIONAL) {
                    opType = OPTYPE_JMP_DIRECT_COND;
                } else if (br_class.conditionality == bt9::BrClass::Conditionality::UNCONDITIONAL) {
                    opType = OPTYPE_JMP_DIRECT_UNCOND;
                } else {
                    opType = OPTYPE_ERROR;
                }
            } else {
                opType = OPTYPE_ERROR;
            }
        } else {
            opType = OPTYPE_ERROR;
        }


        printf("%llx %d\n", PC, branchTaken);
        myfile << PC << " " << branchTaken << "\n";
    }

    myfile.close();

}

