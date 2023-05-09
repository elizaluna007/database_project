def split_string_with_delimiters(string):
    result = []
    current_str = ""
    
    for char in string:
        if char == "," or char == ";" or char == "(" or char == ")" or char==" ":
            if (current_str != ""):
                result.append(current_str)
            if (char == "("):
                result.append("(")
            elif (char == ")"):
                result.append(")")
            current_str=""
        else:
            current_str=current_str+char
            
    if(current_str!=""):
        result.append(current_str)

    return result


# 示例用法
string = "use db"
delimiters = (",", ";", "(", ")")

result = split_string_with_delimiters(string)
print(result)
