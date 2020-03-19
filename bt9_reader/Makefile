# Copyright 2015 Samsung Austin Semiconductor, LLC.

# Description: Makefile for building a cbp 2016 submission.
#
# The following commands and Makefile worked for CENTOS v7:
# =========================================================
# yum install gcc-c++
# yum install boost
# yum install boost-devel.x86_64
#
# The following commands worked for Ubuntu:
#==========================================
#  sudo apt-get update
#  sudo apt-get install g++ libboost-all-dev
#
#

# include path to Boost area on local machine
export BOOST    := /usr/

ifndef BOOST
$(error "You must define BOOST")
endif

export CBP_BASE := $(CURDIR)/..
CXX := g++

OBJDIR := $(CBP_BASE)/bin
SRC    := $(CBP_BASE)/sim
VPATH  := $(SRC)

LDLIBS   += -lboost_iostreams

LDFLAGS += -L$(BOOST)/lib -Wl,-rpath $(BOOST)/lib

CPPFLAGS := -O3 -Wall -std=c++11 -Wextra -Winline -Winit-self -Wno-sequence-point\
           -Wno-unused-function -Wno-inline -fPIC -W -Wcast-qual -Wpointer-arith -Woverloaded-virtual\
           -I$(CBP_BASE) -I/usr/include -I/user/include/boost/ -I/usr/include/boost/iostreams/ -I/usr/include/boost/iostreams/device/

PROGRAMS := bt9_reader

objects = main.o

all: $(PROGRAMS)

bt9_reader : $(objects)
	$(CXX) $(CPPFLAGS) $(LDFLAGS) -o $@ $^ $(LDLIBS)

dbg: clean
	$(MAKE) DBG_BUILD=1 all

clean:
	rm -f $(PROGRAMS) $(objects)
