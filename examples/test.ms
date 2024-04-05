print("# Assigning [let x, let x] = [0, 1].\n# Should print: [0, 1]");
[let x, let y] = [0, 1];
print([x, y]);

print("# Distinguishing calls from bracket expressions.\n# Should print: true");
let x = false;
(let x = true);
print(x);

print("# Closure test.\n # Should print: outer");
let x = "global";
let outer = function() do {
  let x = "outer";
  let inner = function()
    print(x);
  inner();
};

outer();


print("# Closure test.\n# Should print: local");
let makeClosure = function() do {
    let local = "local";
    let closure = function() print(local);
    return closure;
};

let closure = makeClosure();
closure();

'
# print("# Closure test and callback: Creating an adder function.\n# Should print: 8");
let createAdder = function(n: Int) -> Int do{
    return function(m: Int) -> Int (n + m);
};

let adder = createAdder(5);
print(adder(3));
';