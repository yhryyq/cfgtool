package com;
import java.lang.String;
import java.lang.Fuck;
import str.t2;
public class t1{
    static {
            System.loadLibrary("hello"); // Load native library at runtime
        }
    private native String string2CStr(String s);
    public static void main(String[] args){
        String a = string2CStr("123");
        hello();
        System.out.println(a);
    }
}