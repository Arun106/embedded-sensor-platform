import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("gate",ROOT/"scripts/gate.py")
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
POLICY=json.loads((ROOT/"config/test-policy.json").read_text())

class GateTests(unittest.TestCase):
    def evaluate(self,n=21,failed=(),skipped=(),errors=(),missing=None):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            suites={name:ET.Element("testsuite") for name in POLICY["required_frameworks"]}
            for i in range(n):
                framework=POLICY["required_frameworks"][i%3]
                module=POLICY["required_modules"][i%len(POLICY['required_modules'])]
                name=module+("__critical__" if i==0 else "__")+str(i)
                case=ET.SubElement(suites[framework],"testcase",name=name)
                if i in failed: ET.SubElement(case,"failure")
                if i in skipped: ET.SubElement(case,"skipped")
                if i in errors: ET.SubElement(case,"error")
            for name,tree in suites.items():
                if name!=missing: ET.ElementTree(tree).write(root/(name+".xml"))
            return gate.evaluate(root,POLICY,[])
    def test_all_pass(self): self.assertTrue(self.evaluate()["gate_passed"])
    def test_above_90_noncritical_failure(self): self.assertTrue(self.evaluate(failed=(18,))["gate_passed"])
    def test_exactly_90_blocks(self): self.assertFalse(self.evaluate(n=30,failed=(27,28,29))["gate_passed"])
    def test_critical_failure_blocks(self): self.assertFalse(self.evaluate(failed=(0,))["gate_passed"])
    def test_critical_skip_blocks(self): self.assertFalse(self.evaluate(skipped=(0,))["gate_passed"])
    def test_missing_framework_blocks(self): self.assertFalse(self.evaluate(missing="robot")["gate_passed"])
    def test_execution_error_blocks(self): self.assertFalse(self.evaluate(errors=(18,))["gate_passed"])
    def test_incomplete_suite_blocks(self): self.assertFalse(self.evaluate(n=20)["gate_passed"])

if __name__=="__main__": unittest.main()
