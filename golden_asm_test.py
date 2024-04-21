import pytest
import tempfile
import os
import contextlib
import io

import translator
import simulation


@pytest.mark.golden_test("tests/*_asm.yml")
def test_golden(golden):
    with tempfile.TemporaryDirectory() as tmpdirname:
        source = os.path.join(tmpdirname, "source.asm")
        input_stream = os.path.join(tmpdirname, golden.path.name[:-8] + ".txt")
        target = os.path.join(tmpdirname, golden.path.name[:-7] + "machine.txt")

        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["input"])

        translator.main(source, target)
        with open(target, "r", encoding="utf-8") as file:
            code = file.read()
        assert code == golden["machine_code"]
        #
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            simulation.main(target, input_stream)
            out = stdout.getvalue().replace("\x00", "")
            assert out == golden["output"]

        with open(target, "r", encoding="utf-8") as file:
            code = file.read()
        assert code == golden["machine_code"]

        with open("machine/logs/processor.txt") as file:
            proc_log = file.read()
            assert proc_log == golden.out["out_processor"]

        with open("machine/logs/spi.txt") as file:
            spi_log = file.read().replace("\x00", " ")
            assert spi_log == golden.out["out_spi"]
