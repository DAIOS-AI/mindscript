
# "

  TEST SCRIPT.

" null

print("Equality.\n")
assert(true == true)
assert(true != false)
assert(1 == 1)
assert(1. == 1.)
assert(1 == 1.)
assert("a string" == "a string")
assert("a string" != "another string")
assert([0, 1] == [0, 1])
assert([] != [0, 1])
assert({name: "name", age: 21} == {name: "name", age: 21})
assert({name: "name", age: 21} != {name: "name", age: 21, hobbies: null})
assert(let MyType = type [Int, Str] == type [Int, Str])
let f = fun(n) do n end
let g = fun(n) do n end
let h = f 
assert(f == f)
assert(f == h)
assert(f != g)

print("Assignments.\n")
[let x, let y] = [0, 1]
assert(x == 0 and y == 1)

print("Distinguish parenthesized expressions from calls.\n")
let x = false
(let x = true)
assert(x == true)

print("Testing closures 1.\n")
let x = "global"
let outer = fun() do
  let x = "outer"
  let inner = fun() do
    print(x)
  end
  inner()
end

assert(outer() == "outer")

print("Testing closures 2.\n")
let makeClosure = fun() do
    let local = "local"
    let closure = fun() do print(local) end
    return(closure)
end

let closure = makeClosure()
assert(closure() == "local")

print("Testing closures 3.\n")
let createAdder = fun(n: Int) -> Int -> Int do
    fun(m: Int) -> Int do (n + m) end
end

let adder = createAdder(5)
assert(adder(3) == 8)

print("Point objects and point adding functions.\n")
let Point = type {"x": Num, "y": Num}
print(Point)

let point = fun(x: Num, y: Num) -> Point do
  {"x": x, "y": y}
end

let point_add = fun(p: Point, q: Point) -> Point do
  point(p.x + q.x, p.y + q.y)
end

[let p, let q] = [point(1., -1.), point(-1., 1.)]
assert(p == {x: 1., y: -1.})
assert(q == {x: -1., y: 1.})

let r = point_add(p, q)
assert(r == {x: 0., y: 0.})

print("Annotations.\n")
# "The speed of light in m/s"
let speed = 300000000
print(speed)


# "computes the factorial of a given integer."
let factorial = fun(n: Int) -> Int do
  if n==0 or n==1 then 1
  else n*factorial(n-1)
  end
end
print(factorial)

print("\n# Testing for loops.")
let range = fun(start: Int, stop: Int) -> (Null -> Int?) do
  fun() -> Int? do
    if start<stop then
      let value = start
      start = start + 1
      return(value)
    else
      return(null)
    end
  end
end

print("\nLoops over arrays.")
for let x in iter(["1", "2", "3"]) do print(x) end

print("\nLoops over objects.")
for let x in iter({"x": 1, "y": 2, "z": 3}) do print(x) end

print("\nLoops over iterators.")
for let x in range(1, 4) do print(x) end

print("\n# Type checking.")
let obj = {
  "name": "Pedro", 
  "sayname": fun() do
      print(this.name)
  end
}

print("Should print the object.")
print(obj)

print("Should print the type of the object.")
let ObjType = typeof(obj)
print(ObjType)

let show_age = fun(arg: {"name": Str, "age": Int}) -> Int do
  {"age": let age} = arg
  return(age)
end
let age = show_age({"age": 45, "name": "something"})
print("Should print '45': " + str(age))

print("# Trying oracle functions.")
# "Determine the distance of the planet to the sun in astronomical units."
let au = oracle(planet: Str) -> Num

print("AU Earth        : " + str(au("Earth")))

print("# Testing for subtypes.")
assert(issubtype(type [Int], type Array))
assert(issubtype(type Array, type Array))
assert(issubtype(type [], type Array))

assert(issubtype(type Object, type Object))
assert(issubtype(type {}, type Object))

