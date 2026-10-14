#!/bin/bash
cd "$(dirname "$0")"; PROJ=$(pwd); NP=${NP:-4}
cont(){ echo "===== $(date +%F_%T) CONTINUE $1 (NP=$NP) ====="; cd "$PROJ/$1" || return 1
  mpirun -np $NP buoyantPimpleFoam -parallel >> log.run 2>&1
  reconstructPar -latestTime >> log.reconstruct 2>&1
  echo "===== $(date +%F_%T) DONE $1 (last $(ls -d [0-9]* 2>/dev/null | sort -g | tail -1)) ====="; cd "$PROJ"; }
cont caseB_set
cont caseC_set
echo "########## CONT ALL DONE $(date +%F_%T) ##########"
