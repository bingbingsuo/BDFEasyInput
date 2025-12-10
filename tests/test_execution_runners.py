import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bdfeasyinput.execution.bdf_direct import BDFDirectRunner
from bdfeasyinput.execution.bdfautotest import BDFAutotestRunner


def test_bdf_direct_runner_paths_and_env(monkeypatch, tmp_path):
    # Prepare fake BDF home with executable
    bdf_home = tmp_path / "bdfhome"
    (bdf_home / "sbin").mkdir(parents=True)
    bdf_exe = bdf_home / "sbin" / "bdf.drv"
    bdf_exe.write_text("#!/bin/sh\necho stub\n")

    # Prepare input file
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    input_file = work_dir / "test.inp"
    input_file.write_text("$COMPASS\n$END\n")

    captured = {}

    def fake_run(cmd, cwd=None, env=None, stdout=None, stderr=None, **kwargs):
        captured["cmd"] = cmd
        captured["cwd"] = cwd
        captured["env"] = env
        if stdout:
            stdout.write("ok\n")
        if stderr:
            stderr.write("")
        class Proc:
            returncode = 0
        return Proc()

    monkeypatch.setattr("subprocess.run", fake_run)

    runner = BDFDirectRunner(
        bdf_home=str(bdf_home),
        bdf_tmpdir=str(tmp_path / "tmpdir"),
        omp_num_threads=4,
        omp_stacksize="256M",
    )

    result = runner.run(str(input_file), timeout=10, use_debug_dir=False)

    assert result["status"] == "success"
    assert Path(result["bdf_workdir"]) == work_dir
    assert Path(result["bdf_tmpdir"]).name == "tmpdir"
    assert result["command"].endswith("bdf.drv -r test.inp")
    assert captured["cwd"] == str(work_dir)
    assert captured["env"]["BDFHOME"] == str(bdf_home)
    assert captured["env"]["BDF_WORKDIR"] == str(work_dir)
    assert captured["env"]["BDF_TMPDIR"].endswith("tmpdir")
    assert captured["env"]["OMP_NUM_THREADS"] == "4"
    assert captured["env"]["OMP_STACKSIZE"] == "256M"


def test_bdfautotest_runner_command_and_copy(monkeypatch, tmp_path):
    # Prepare fake BDFAutotest tree
    root = tmp_path / "BDFAutoTest"
    (root / "config").mkdir(parents=True)
    (root / "src").mkdir(parents=True)
    (root / "config" / "config.yaml").write_text("dummy: true\n")
    (root / "src" / "orchestrator.py").write_text("# stub\n")

    # Prepare input
    input_dir = tmp_path / "inputs"
    input_dir.mkdir()
    input_file = input_dir / "sample.inp"
    input_file.write_text("$COMPASS\n$END\n")

    output_dir = tmp_path / "outdir"

    captured = {}
    log_path = output_dir / "sample.log"
    err_path = output_dir / "sample.err"

    def fake_run(cmd, cwd=None, env=None, capture_output=None, text=None, timeout=None, check=None):
        captured["cmd"] = cmd
        captured["cwd"] = cwd
        captured["env"] = env
        output_dir.mkdir(parents=True, exist_ok=True)
        log_path.write_text("log")
        err_path.write_text("err")
        class Proc:
            returncode = 0
            stdout = "ok"
            stderr = ""
        return Proc()

    monkeypatch.setattr("subprocess.run", fake_run)

    runner = BDFAutotestRunner(bdfautotest_path=str(root))
    result = runner.run(str(input_file), output_dir=str(output_dir), timeout=5)

    assert result["status"] == "success"
    assert captured["cwd"] == str(root)
    assert captured["cmd"][:5] == ["python3", "-m", "src.orchestrator", "run-input", str(input_file)]
    assert captured["cmd"][5:] == ["--config", str(root / "config" / "config.yaml")]
    assert captured["env"]["PYTHONPATH"].startswith(str(root))
    assert Path(result["output_file"]) == log_path
    assert Path(result.get("error_file", err_path)) == err_path or not result.get("error_file")

