
# "

  TEST SCRIPT.

" null

print("\n# Assigning [let x, let x] = [0, 1].\n# Should print: [0, 1]")
[let x, let y] = [0, 1]
print([x, y])

print("\n# Distinguishing calls from bracket expressions.\n# Should print: true")
let x = false
(let x = true)
print(x)

print("\n# Closure test.\n # Should print: outer")
let x = "global"
let outer = function() do
  let x = "outer"
  let inner = function() do
    print(x)
  end
  inner()
end

outer()


print("\n# Closure test.\n# Should print: local")
let makeClosure = function() do
    let local = "local"
    let closure = function() do print(local) end
    return(closure)
end

let closure = makeClosure()
closure()


print("\n# Closure test and callback: Creating an adder function.\n# Should print: 8")
let createAdder = function(n: Int) -> Int do
    function(m: Int) -> Int do (n + m) end
end

let adder = createAdder(5)
print(adder(3))


print("\n# Creating a point structure and adder function.\n")
let Point = type {"x": Num, "y": Num}
print(Point)

let point = function(x: Num, y: Num) -> Point do
  {"x": x, "y": y}
end
print(point)

let point_add = function(p: Point, q: Point) -> Point do
  {"x": p.x + q.x, "y": p.y + q.y}
end
print(point_add)

[let p, let q] = [point(1, -1), point(-1, 1)]
print(p)
print(q)

let r = point_add(p, q)
print(r)

print("Should be [0, 0]")

print("\nTesting annotations.")
# "The speed of light in m/s"
let speed = 300000000
print(speed)

# "\ncomputes the factorial of a given integer."
let factorial = function(n: Int) -> Int do
  if n==0 or n==1 then 1
  else n*factorial(n-1)
  end
end
print(factorial)