- same length
- syntax same result var | different const           - choose if only one correct
- semantic different for var - same for non-declared - choose any correct

### Impossible combinations
1. (1.0, 1.0) 
2. (0.0, 0.0) 
3. (1.1, a.b) 
4. (a.b, 1.1) 
5. (1.1, 1.1) 
6. (1.0, 0.1)
7. (0.1, 1.0)

<pre>
1.0   | 0.1   | 0.1 x | 0.0 x | 0.0 x | m 
0.0 x | 0.0 x | 0.1 x | 1.0   | 0.1   | l 
</pre>

0 - no error, 1 - error, x - correct option

if not 0.0m - can choose l