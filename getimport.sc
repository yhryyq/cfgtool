@main def exec(outFile: String) = {
   importCpg("/home/kali/桌面/cfgtool/cfgtool/cfgtool_new/cfgtool/cpg.bin")
   cpg.imports.code.l #> outFile
}