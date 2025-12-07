import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bdfeasyinput.ai.planner.task_planner import TaskPlanner


class FakeClient:
    def is_available(self) -> bool:
        return True

    def chat(self, messages, temperature=0.7, max_tokens=None, **kwargs) -> str:
        return (
            "task:\n"
            "  type: energy\n"
            "molecule:\n"
            "  charge: 0\n"
            "  multiplicity: 1\n"
            "  coordinates:\n"
            "    - O 0.0000 0.0000 0.0000\n"
            "  units: angstrom\n"
            "method:\n"
            "  type: dft\n"
            "  functional: pbe0\n"
            "  basis: cc-pvdz\n"
        )

    def stream_chat(self, messages, temperature=0.7, max_tokens=None, **kwargs):
        text = self.chat(messages, temperature=temperature, max_tokens=max_tokens, **kwargs)
        for ch in text:
            yield ch


def test_task_planner_basic():
    planner = TaskPlanner(ai_client=FakeClient(), validate_output=True)
    result = planner.plan("测试")
    assert result["task"]["type"] == "energy"
    assert result["method"]["type"] == "dft"
    assert result["method"]["basis"] == "cc-pvdz"


def test_task_planner_streaming():
    planner = TaskPlanner(ai_client=FakeClient(), validate_output=False)
    chunks = []
    for chunk in planner.plan_streaming("测试"):
        chunks.append(chunk)
    assembled = "".join(chunks)
    assert "task:" in assembled
    assert "method:" in assembled
