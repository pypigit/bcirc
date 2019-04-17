# Boolean circuits package

This Python 3 package implements Boolean circuits for my complexity theory class.

Example:

```python
from bcirc import InputGates, AndGate, MultiOrGate, BooleanCircuit

a, b, c = InputGates(3)
d, e, f = AndGate(a, b), AndGate(a, c), AndGate(b, c)
g = MultiOrGate(d, e, f)
bc = BooleanCircuit((a, b, c), g)
print(bc(True, True, False))

h = a & ~(b | c)
a.set(True)
b.set(False)
c.set(False)
print(h.value())
```
