
def get_first(arr):
    """O(1) - array access"""
    return arr[0] if arr else None

def simple_math(x, y):
    """O(1) - arithmetic operations"""
    return x + y * 2 + len([1,2,3])  # len on literal is O(1)

def dict_lookup(d, key):
    """O(1) - hash table lookup"""
    return d.get(key, 0)

# Test calls
arr = [1, 2, 3, 4, 5]
first = get_first(arr)
math_result = simple_math(10, 20)
lookup = dict_lookup({"a": 1}, "a")
