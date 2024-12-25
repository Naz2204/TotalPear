
.assembly extern mscorlib {}
.assembly extern utils {}
.assembly test {}
.module test.exe

.class private Program extends [mscorlib]System.Object {
  .method public static void Main(string[] args) cil managed {
    .locals init (
      int64   _rax_i8,
      float64 _rax_r8,
      int64 USERVAR_i,
      int64 USERVAR_x 
    )

    .entrypoint
    call void [utils]Utils.Reader::ChangeGlobalization()
    label0:
    ldloc USERVAR_x
    ldloc USERVAR_i
    clt
    brfalse label1
    ldstr "*"
    call void [mscorlib]System.Console::Write(string)
    ldloca USERVAR_x
    ldloc USERVAR_x
    ldc.i8 1
    add
    stind.i8
    br label0
    label1:
    ldloca USERVAR_i
    ldc.i8 1
    stind.i8
    label2:
    ldloc USERVAR_i
    ldc.i8 12
    clt
    brfalse label3
    br label4
    label5:
    ldloca USERVAR_i
    ldloc USERVAR_i
    ldc.i8 1
    add
    stind.i8
    br label2
    label4:
    ldloca USERVAR_x
    ldc.i8 0
    stind.i8
    label6:
    ldloc USERVAR_x
    ldloc USERVAR_i
    clt
    brfalse label7
    ldstr "*"
    call void [mscorlib]System.Console::Write(string)
    ldloca USERVAR_x
    ldloc USERVAR_x
    ldc.i8 1
    add
    stind.i8
    br label6
    label7:
    ldstr "\n"
    call void [mscorlib]System.Console::Write(string)
    br label5
    label3:

    ret    
  }
}
