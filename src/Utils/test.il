.assembly extern mscorlib {}
.assembly extern utils {}

.assembly test {} 
.module test.exe

.method public static void Main() cil managed
{   
    .locals (
        int32 Mew
    )
    .entrypoint
    call void [utils]Utils.Reader::ChangeGlobalization()

    // Call the external function
    ldstr "Are you pizza enjoyer?: "
    call bool [utils]Utils.Reader::ReadBool(string)
    stloc Mew
    ldloc Mew
    call void [mscorlib]System.Console::WriteLine(bool)

    ret
}
