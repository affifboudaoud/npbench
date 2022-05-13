import timeit
import numpy as np

from npbench.infrastructure import Framework
from typing import Any, Callable, Dict, Sequence, Tuple

from npbench.infrastructure.measure.metric import Metric

class Timer(Metric):

    timeit_tmpl = """
def inner(_it, _timer{init}):
    {setup}
    _t0 = _timer()
    for _i in _it:
        {stmt}
    _t1 = _timer()
    return _t1 - _t0, {output}
"""

    def __init__(self) -> None:
        super().__init__()

    def execute(self, bench, frmwrk: Framework, impl: Callable, impl_name: str, mode: str, bdata: Dict[str, Any], repeat: int, **kwargs) -> Tuple[Any, Sequence[float]]:
        report_str = frmwrk.info["full_name"] + " - " + impl_name 
        
        try:
            copy = frmwrk.copy_func()
            setup_str = frmwrk.setup_str(bench, impl)
            exec_str = frmwrk.exec_str(bench, impl)
        except Exception as e:
            print("Failed to load the {} implementation.".format(report_str))
            print(e)
            return None, None
        
        ldict = {'__npb_impl': impl, '__npb_copy': copy, **bdata}
        
        try:
            out, timelist = self.benchmark(
                stmt=exec_str,
                setup=setup_str,
                out_text=report_str + " - " + mode,
                repeat=repeat,
                context=ldict,
                output='__npb_result'
            )
        except Exception as e:
            print("Failed to execute the {} implementation.".format(report_str))
            print(e)
            return None, None
        
        if out is not None:
            if isinstance(out, (tuple, list)):
                out = list(out)
            else:
                out = [out]
        else:
            out = []
        if "out_args" in bench.info.keys():
            out += [ldict[a] for a in self.frmwrk.args(bench)]
        
        return out, timelist

    def benchmark(
        self,
        stmt,
        setup="pass",
        out_text="",
        repeat=1,
        context={},
        output=None,
        verbose=True
    ):
        timeit.template = Timer.timeit_tmpl.format(
            init='{init}',
            setup='{setup}',
            stmt='{stmt}',
            output=output
        )

        ldict = {**context}
        output = timeit.repeat(
            stmt,
            setup=setup,
            repeat=repeat,
            number=1,
            globals=ldict
        )
        
        res = output[0][1]
        raw_time_list = [a for a, _ in output]
        raw_time = np.median(raw_time_list)
        ms_time = _time_to_ms(raw_time)
        
        if verbose:
            print("{}: {}ms".format(out_text, ms_time))
        
        return res, raw_time_list

def _time_to_ms(raw: float) -> int:
    return int(round(raw * 1000))