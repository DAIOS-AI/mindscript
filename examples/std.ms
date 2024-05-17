# "Standard library" null



# "Iterator tools." null

# "Applies a function to an iterator."
let map = fun(f: Any -> Any, iterator: Null -> Any) -> (Null -> Any) do
    fun() -> Any do
        let value = iterator()
        if value == null then null 
        else f(value)
        end        
    end
end

# "Filters an iterator using a condition."
let filter = fun(cond: Any -> Bool, iterator: Null -> Any) -> (Null -> Any) do
    fun() -> Any do
        for value in iterator do
            if cond(value) then
                break(value)
            end
        end
    end
end

# "Reduces an iterator using a binary function."
let reduce = fun(f: Any -> Any -> Any, iterator: Null -> Any) -> Any do
    let accum = iterator()
    if accum == null then [] end
    for value in iterator do
        accum = f(accum, value)
    end
end

