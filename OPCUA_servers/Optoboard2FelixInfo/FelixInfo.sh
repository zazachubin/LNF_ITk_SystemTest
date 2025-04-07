#!/bin/bash
#
export ITK_DAQ_BASE=/home/felix/opt
export FELIXSWDIR=${ITK_DAQ_BASE}/felix-distribution
export FELIX_BUS=${FELIXSWDIR}/bus
export REGMAP_VERSION=0x0500

#source ${FELIXSWDIR}/setup.sh
source /cvmfs/atlas-online-nightlies.cern.ch/felix/nightlies/felix-master-rm5-stand-alone/x86_64-el9-gcc13-opt/setup.sh
export PYTHONPATH=${ITK_DAQ_BASE}/felix-distribution/${BINARY_TAG}/ic-over-netio-From-NSW-Felixcore:${PYTHONPATH}
export PYTHONPATH=${ITK_DAQ_BASE}/lpgbt-com-next/${BINARY_TAG}:${PYTHONPATH}

flx-info link | grep Aligned
flx-config list | grep DECODING_LINK_ALIGNED_0
