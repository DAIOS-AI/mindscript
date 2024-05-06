# "Given a fun description, create a fun that computes it.
The programming language allows defining funs with a single
parameter, and looks as follows:

let factorial = fun(n: Int) -> Int do
    if n==0 then
        return(1)
    else
        return( n*factorial(n-1) )
    end
end

let sum = fun(arg: [Int, Int]) -> Int do
    [x, y] = arg
    return(x + y)
end

let x = (factorial(10) * 2 == 100) or (factorial(1) == 0) 
"
let makeFunction = fun(description: Str) -> Str oracle

