#!/bin/bash
# Unattended batch: run the three setpoint cases to equilibrium in parallel (4 cores each), sequentially.
cd "$(dirname "$0")"; PROJ="$(pwd)"
NP=4   # MPI ranks; bump to 6 if you have the physical cores
run_set () {
  echo "===== $(date +%F_%T)  START $1 ====="
  cd "$PROJ/$1" || return 1
  rm -rf 0 processor* postProcessing log.run log.decompose log.reconstruct
  cp -r 0.orig 0
  decomposePar -force          > log.decompose   2>&1
  mpirun -np $NP buoyantPimpleFoam -parallel > log.run 2>&1
  reconstructPar -latestTime   > log.reconstruct 2>&1
  echo "===== $(date +%F_%T)  DONE  $1 (last reconstructed: $(ls -d [0-9]* 2>/dev/null | sort -g | tail -1)) ====="
  cd "$PROJ"
}
run_set caseA_set
run_set caseB_set
run_set caseC_set
echo "########## ALL DONE $(date +%F_%T) ##########"
