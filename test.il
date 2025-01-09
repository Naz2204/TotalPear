
.assembly extern mscorlib {}
.assembly extern utils {}
.assembly test {}
.module test.exe

.class private Program extends [mscorlib]System.Object {
  .method public static void Main(string[] args) cil managed {
    .locals init (
      int64   _rax_i8,
      float64 _rax_r8,
      int64 USERVAR_x,
      int64 USERVAR_div,
      int64 USERVAR_res 
    )

    .entrypoint
    call void [utils]Utils.Reader::ChangeGlobalization()
    ldstr "===============\n"
    call void [mscorlib]System.Console::Write(string)
    ldstr "Test of parity\n"
    call void [mscorlib]System.Console::Write(string)
    ldstr "===============\n"
    call void [mscorlib]System.Console::Write(string)
    ldloca USERVAR_x
    ldstr "Input integer: "
    call int64 [utils]Utils.Reader::ReadInt(string)
    stind.i8
    ldloca USERVAR_div
    ldloc USERVAR_x
    ldc.i8 2
    stloc _rax_i8
    conv.r8
    ldloc _rax_i8
    conv.r8
    div
    conv.i8
    stind.i8
    ldloca USERVAR_res
    ldloc USERVAR_x
    ldloc USERVAR_div
    ldc.i8 2
    mul
    sub
    stind.i8
    ldloc USERVAR_res
    ldc.i8 0
    ceq
    brfalse label0
    ldloc USERVAR_x
    call void [mscorlib]System.Console::Write(int64)
    ldstr " is even\n"
    call void [mscorlib]System.Console::Write(string)
    br label1
    label0:
    ldloc USERVAR_x
    call void [mscorlib]System.Console::Write(int64)
    ldstr " is odd\n"
    call void [mscorlib]System.Console::Write(string)
    label1:

    ret    
  }
}
