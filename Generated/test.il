
.assembly extern mscorlib {}
.assembly extern utils {}
.assembly test {}
.module test.exe

.class private Program extends [mscorlib]System.Object {
  .method public static void Main(string[] args) cil managed {
    .locals init (
      int64   _rax_i8,
      float64 _rax_r8,
      int32 USERVAR_boris,
      int64 USERVAR_age,
      float64 USERVAR_number 
    )
    
    .entrypoint
    call void [utils]Utils.Reader::ChangeGlobalization()
    ldloca USERVAR_boris
    ldstr "Does 12 + 12 equal to yellow?"
    call bool [utils]Utils.Reader::ReadBool(string)
    stind.i4
    ldloc USERVAR_boris
    brfalse label0
    ldstr "Crazy init?\n"
    call void [mscorlib]System.Console::Write(string)
    br label1
    label0:
    label1:
    ldloca USERVAR_age
    ldstr "Enter your agge: "
    call int64 [utils]Utils.Reader::ReadInt(string)
    stind.i8
    ldstr "Your age is "
    call void [mscorlib]System.Console::Write(string)
    ldloc USERVAR_age
    call void [mscorlib]System.Console::Write(int64)
    ldstr "\n"
    call void [mscorlib]System.Console::Write(string)
    ldloca USERVAR_number
    ldstr "Enter number beetwen 0 and 1: "
    call float64 [utils]Utils.Reader::ReadFloat(string)
    stind.r8
    ldstr "Your number is "
    call void [mscorlib]System.Console::Write(string)
    ldloc USERVAR_number
    call void [mscorlib]System.Console::Write(float64)

    ret    
  }
}

