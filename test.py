filename = "hello"
print("""
.assembly extern mscorlib {}
// use name
.assembly %s {}
// use name
.module %s.exe

.class private Program extends [mscorlib]System.Object {
  .method public static void Main(string[] args) cil managed {
    .locals (
    // local variables 
    )
    .entrypoint
    // code 
    
    ret    
  }
}

"""%(filename, filename))

print