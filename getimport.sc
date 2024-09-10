@main def exec(cpgFile: String, outFile: String) = {
   importCpg(cpgFile)
   cpg.imports.code.l #> outFile
}

