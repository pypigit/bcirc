# Boolean circuits package

This Python 3 package implements Boolean circuits for my complexity theory class.

Example:

```python
from bcirc import variables, AndGate, MultiOrGate, BooleanCircuit

a, b, c = variables(3)
d, e, f = AndGate(a, b), AndGate(a, c), AndGate(b, c)
g = MultiOrGate(d, e, f)
bc = BooleanCircuit((a, b, c), g)
print(bc(True, True, False))
```
