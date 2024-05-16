
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
let outer = fun() do
  let x = "outer"
  let inner = fun() do
    print(x)
  end
  inner()
end

outer()


print("\n# Closure test.\n# Should print: local")
let makeClosure = fun() do
    let local = "local"
    let closure = fun() do print(local) end
    return(closure)
end

let closure = makeClosure()
closure()


print("\n# Closure test and callback: Creating an adder fun.\n# Should print: 8")
let createAdder = fun(n: Int) -> Int -> Int do
    fun(m: Int) -> Int do (n + m) end
end

let adder = createAdder(5)
print(adder(3))

print("\n# Creating a point structure and adder fun.\n")
let Point = type {"x": Num, "y": Num}
print(Point)

let point = fun(point: [Num, Num]) -> Point do
  {"x": point[0], "y": point[1]}
end
print(point)

let point_add = fun(points: [Point, Point]) -> Point do
  [let p, let q] = points
  {"x": p.x + q.x, "y": p.y + q.y}
end
print(point_add)

[let p, let q] = [point([1., -1.]), point([-1., 1.])]
print(p)
print(q)

let r = point_add([p, q])
print(r)

print("Should be [0, 0]")

print("\n# Testing annotations.")
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

print("# Trying oracle funs.")
# "Determine the distance of the planet to the sun in astronomical units."
let au = oracle(planet: Str) -> Num

print("AU Mercury      : " + str(au("Mercury")))
print("AU Venus        : " + str(au("Venus")))
print("AU Earth        : " + str(au("Earth")))

print("# Testing for subtypes.")
assert(issubtype(type [Int], type Array))
assert(issubtype(type Array, type Array))
assert(issubtype(type [], type Array))

assert(issubtype(type Object, type Object))
assert(issubtype(type {}, type Object))
