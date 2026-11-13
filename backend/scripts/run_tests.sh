#!/usr/bin/env bash
# Test-Runner für Phase 0 + Phase 1.
set -uo pipefail

cd /root/mietverwaltung-saas/backend

echo "==> Redis-Cache leeren ..."
redis-cli FLUSHDB
redis-cli -n 15 FLUSHDB

PYTEST="/root/mietverwaltung-saas/backend/.venv/bin/pytest"
CONFIG="pytest_phase0_phase1.ini"

echo "==> Phase 0 Tests laufen ..."
"$PYTEST" -c "$CONFIG" tests/phase0/ -v --tb=short 2>&1 | tee /tmp/phase0_tests.log
PHASE0_STATUS=${PIPESTATUS[0]}

echo "==> Phase 1 Tests laufen ..."
"$PYTEST" -c "$CONFIG" tests/phase1/ -v --tb=short 2>&1 | tee /tmp/phase1_tests.log
PHASE1_STATUS=${PIPESTATUS[0]}

PHASE0_PASSED=$(grep -oP '\d+(?= passed)' /tmp/phase0_tests.log | tail -1 || echo 0)
PHASE0_FAILED=$(grep -oP '\d+(?= failed)' /tmp/phase0_tests.log | tail -1 || echo 0)
PHASE1_PASSED=$(grep -oP '\d+(?= passed)' /tmp/phase1_tests.log | tail -1 || echo 0)
PHASE1_FAILED=$(grep -oP '\d+(?= failed)' /tmp/phase1_tests.log | tail -1 || echo 0)

echo ""
echo "=============================="
echo "TEST SUMMARY"
echo "=============================="
echo "Phase 0: passed=${PHASE0_PASSED}, failed=${PHASE0_FAILED} (exit=${PHASE0_STATUS})"
echo "Phase 1: passed=${PHASE1_PASSED}, failed=${PHASE1_FAILED} (exit=${PHASE1_STATUS})"
echo "=============================="

if [ "$PHASE0_STATUS" -ne 0 ] || [ "$PHASE1_STATUS" -ne 0 ]; then
    echo "RESULT: FAILURE"
    exit 1
fi

echo "RESULT: SUCCESS"
exit 0
