# "Given a function description, create a function that computes it.
The programming language allows defining functions with a single
parameter, and looks as follows:

let factorial = function(n: Int) -> Int do
    if n==0 then
        return(1)
    else
        return( n*factorial(n-1) )
    end
end

let sum = function(arg: [Int, Int]) -> Int do
    [x, y] = arg
    return(x + y)
end

let x = (factorial(10) * 2 == 100) or (factorial(1) == 0) 
"
let makeFunction = function(description: Str) -> Str oracle

