# Chess Guru

## Quick use

```
export FLASK_APP=main.py
flask run
```

## Profiling
```
python3 -m cProfile -o output.pstats quick_test.py
gprof2dot -f pstats output.pstats | dot -Tpng -o output.png
```
