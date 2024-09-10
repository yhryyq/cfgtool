@main def exec(outFile: String, language: String, cpgFile: String) = {
    importCpg(cpgFile)
    if (language == "java") {
          println(s"Processing $language code...");
          cpg.method.foreach { method =>
          val methodName = language + "_" + method.fullName // 获取方法名称
          val dotContent = method.dotCpg14.l.head // 获取方法的 dot 内容
          // val directory = "/home/kali/桌面/cfgtool/cfgtool/cfgtool_new/out_dir"
          val fileName = outFile + "/" + methodName + ".dot" // 定义文件名
          val file = new java.io.File(fileName)
          java.nio.file.Files.createDirectories(java.nio.file.Paths.get(outFile))
          java.nio.file.Files.write(file.toPath, dotContent.getBytes) // 写入文件
          println(s"Generated dot file for method: $methodName")
      }
      } else if (language == "c")
      {
        println(s"Processing $language code...");
          cpg.method.foreach { method =>
          val methodName = language + "_" + method.filename + "_" + method.fullName // 获取方法名称
          val dotContent = method.dotCpg14.l.head // 获取方法的 dot 内容
          // val directory = "/home/kali/桌面/cfgtool/cfgtool/cfgtool_new/out_dir"
          val fileName = outFile + "/" + methodName + ".dot" // 定义文件名
          val file = new java.io.File(fileName)
          java.nio.file.Files.createDirectories(java.nio.file.Paths.get(outFile))
          java.nio.file.Files.write(file.toPath, dotContent.getBytes) // 写入文件
          println(s"Generated dot file for method: $methodName")
      }
      }
      else
      {
          // 如果不是这两种语言，打印消息并退出
          println("Unsupported language. Exiting.")
      }
    
}