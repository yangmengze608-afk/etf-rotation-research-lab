import unittest

from agent_core import (
    _heuristic_plan,
    build_evidence,
    load_dataset,
    tool_risk_guardrails,
    tool_strategy_comparison,
)


class AgentCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_dataset()

    def test_strategy_comparison_all_window(self):
        result = tool_strategy_comparison(self.data, "比较全样本三个策略")
        self.assertEqual(result["window"], "all")
        self.assertGreaterEqual(len(result["rows"]), 3)
        self.assertIn("highest_historical_return", result)

    def test_strategy_comparison_120_window(self):
        result = tool_strategy_comparison(self.data, "比较 120 天收益和回撤")
        self.assertEqual(result["window"], "120")
        self.assertGreaterEqual(len(result["rows"]), 3)

    def test_risk_guardrails_never_expose_broker_action(self):
        result = tool_risk_guardrails(self.data, "能不能直接买？")
        joined = " ".join(result["hard_guardrails"]).lower()
        self.assertIn("no broker", joined)
        self.assertIn("no personalized", joined)

    def test_heuristic_plan_selects_minimum_relevant_tools(self):
        plan = _heuristic_plan("比较策略收益、回撤和风险")
        self.assertIn("strategy_comparison", plan)
        self.assertIn("risk_guardrails", plan)
        self.assertLessEqual(len(plan), 3)

    def test_build_evidence_only_runs_selected_tools(self):
        evidence = build_evidence(self.data, "比较全样本策略", ["strategy_comparison"])
        self.assertEqual(list(evidence), ["strategy_comparison"])


if __name__ == "__main__":
    unittest.main()
