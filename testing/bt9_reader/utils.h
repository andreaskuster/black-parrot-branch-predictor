///////////////////////////////////////////////////////////////////////
//  Copyright 2015 Samsung Austin Semiconductor, LLC.                //
///////////////////////////////////////////////////////////////////////


#ifndef UTILS_H
#define UTILS_H

#include <string>
#include <iostream>
#include <cstdio>
#include <cstdlib>

using namespace std;

#define UINT32      unsigned int
#define INT32       int
#define UINT64      unsigned long long
#define COUNTER     unsigned long long


#define NOT_TAKEN 0
#define TAKEN 1

#define FAILURE 0
#define SUCCESS 1

typedef enum {
  OPTYPE_OP=0,

  OPTYPE_RET_UNCOND=1,
  OPTYPE_JMP_DIRECT_UNCOND=2,
  OPTYPE_JMP_INDIRECT_UNCOND=3,
  OPTYPE_CALL_DIRECT_UNCOND=4,
  OPTYPE_CALL_INDIRECT_UNCOND=5,

  OPTYPE_RET_COND=6,
  OPTYPE_JMP_DIRECT_COND=7,
  OPTYPE_JMP_INDIRECT_COND=8,
  OPTYPE_CALL_DIRECT_COND=9,
  OPTYPE_CALL_INDIRECT_COND=10,

  OPTYPE_ERROR=11,

  OPTYPE_MAX=12
} OpType;


#endif

