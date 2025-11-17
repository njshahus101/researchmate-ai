"""
Quick validation script for Report Generator integration
"""

import sys
from pathlib import Path

print("="*80)
print("REPORT GENERATOR VALIDATION")
print("="*80)

# Check 1: Files exist
print("\n[CHECK 1] Verifying files exist...")
files_to_check = [
    "adk_agents/report_generator/__init__.py",
    "adk_agents/report_generator/agent.py",
    "test_report_generator.py",
    "REPORT_GENERATOR_INTEGRATION.md"
]

all_exist = True
for file_path in files_to_check:
    exists = Path(file_path).exists()
    status = "OK" if exists else "MISSING"
    print(f"  [{status}] {file_path}")
    all_exist = all_exist and exists

if not all_exist:
    print("\nERROR: Some files are missing!")
    sys.exit(1)

# Check 2: Import Report Generator agent
print("\n[CHECK 2] Importing Report Generator agent...")
try:
    from adk_agents.report_generator.agent import agent as report_generator_agent
    print(f"  [OK] Agent name: {report_generator_agent.name}")
    print(f"  [OK] Agent description: {report_generator_agent.description[:60]}...")
except Exception as e:
    print(f"  [FAILED] Import error: {e}")
    sys.exit(1)

# Check 3: Import orchestrator with Report Generator
print("\n[CHECK 3] Importing orchestrator with Report Generator...")
try:
    from adk_agents.orchestrator.agent import agent as orchestrator_agent
    print(f"  [OK] Orchestrator name: {orchestrator_agent.name}")
    print(f"  [OK] Orchestrator has tools: {len(orchestrator_agent.tools) > 0}")
except Exception as e:
    print(f"  [FAILED] Import error: {e}")
    sys.exit(1)

# Check 4: Verify pipeline steps in orchestrator
print("\n[CHECK 4] Verifying pipeline includes Report Generator...")
try:
    from adk_agents.orchestrator import agent as orch_module
    source_code = Path("adk_agents/orchestrator/agent.py").read_text()

    checks = {
        "STEP 6 present": "STEP 6:" in source_code,
        "Report Generator imported": "report_generator_agent" in source_code,
        "A2A call to Report Generator": "report_runner = InMemoryRunner(agent=report_generator_agent)" in source_code,
        "Final report returned": "final_report" in source_code,
        "6/6 step numbering": "[STEP 6/6]" in source_code,
    }

    all_passed = True
    for check_name, passed in checks.items():
        status = "OK" if passed else "FAILED"
        print(f"  [{status}] {check_name}")
        all_passed = all_passed and passed

    if not all_passed:
        print("\n  ERROR: Some pipeline checks failed!")
        sys.exit(1)

except Exception as e:
    print(f"  [FAILED] Verification error: {e}")
    sys.exit(1)

# Check 5: Agent instruction includes all report types
print("\n[CHECK 5] Verifying Report Generator instructions...")
try:
    agent_code = Path("adk_agents/report_generator/agent.py").read_text(encoding='utf-8')

    instruction_checks = {
        "Factual format": "FACTUAL QUERIES" in agent_code,
        "Comparative format": "COMPARATIVE QUERIES" in agent_code,
        "Exploratory format": "EXPLORATORY QUERIES" in agent_code,
        "Citation guidelines": "CITATION FORMATTING RULES" in agent_code,
        "Weighted scoring": "WEIGHTED SCORING" in agent_code,
        "Follow-up questions": "FOLLOW-UP QUESTIONS GENERATION" in agent_code,
        "Markdown formatting": "MARKDOWN FORMATTING" in agent_code,
    }

    all_passed = True
    for check_name, passed in instruction_checks.items():
        status = "OK" if passed else "FAILED"
        print(f"  [{status}] {check_name}")
        all_passed = all_passed and passed

    if not all_passed:
        print("\n  ERROR: Some instruction checks failed!")
        sys.exit(1)

except Exception as e:
    print(f"  [FAILED] Verification error: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("VALIDATION COMPLETE - ALL CHECKS PASSED!")
print("="*80)
print("\nReport Generator is successfully integrated!")
print("\nNext steps:")
print("  1. Run full integration tests: python test_report_generator.py")
print("  2. Test via ADK UI: venv\\Scripts\\adk.exe web adk_agents --port 8000")
print("  3. Check documentation: REPORT_GENERATOR_INTEGRATION.md")
print("="*80)
